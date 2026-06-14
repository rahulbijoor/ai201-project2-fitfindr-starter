"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Complete tools.py and test each tool in isolation before implementing this file.

Usage (once implemented):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""

from tools import search_listings, suggest_outfit, create_fit_card, compare_price, get_trending_styles


# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.

    You may add fields to this dict as needed for your implementation.
    """
    return {
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "price_analysis": None,      # dict from compare_price (optional)
        "trending_styles": None,     # list from get_trending_styles (optional)
        "error": None,               # set if the interaction ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Main agent entry point. Runs the FitFindr planning loop for a single
    user interaction and returns the completed session dict.

    Args:
        query:    Natural language user request
                  (e.g., "vintage graphic tee under $30, size M")
        wardrobe: User's wardrobe dict — use get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py

    Returns:
        The session dict after the interaction completes. Check session["error"]
        first — if it is not None, the interaction ended early and the other
        output fields (outfit_suggestion, fit_card) will be None.

    Planning loop with stretch features:
    - Price comparison on selected item
    - Trend awareness when search returns no results
    - Retry logic with loosened constraints on zero results
    """
    import re

    # Step 1: Initialize session
    session = _new_session(query, wardrobe)

    # Step 2: Parse query to extract description, size, max_price
    parsed = {"description": query, "size": None, "max_price": None}

    # Extract price (e.g., "under $30" or "$30")
    price_match = re.search(r"(?:under\s+)?\$\s*(\d+(?:\.\d{2})?)", query)
    if price_match:
        parsed["max_price"] = float(price_match.group(1))
        # Remove the price part from description
        parsed["description"] = re.sub(
            r"(?:under\s+)?\$\s*(\d+(?:\.\d{2})?)", "", parsed["description"]
        ).strip()

    # Extract size (e.g., "size M", "in size XXS", "size 8")
    size_match = re.search(r"(?:in\s+)?size\s+([A-Za-z0-9/\s]+?)(?:\s+|$)", query, re.IGNORECASE)
    if size_match:
        parsed["size"] = size_match.group(1).strip()
        # Remove the size part from description
        parsed["description"] = re.sub(
            r"(?:in\s+)?size\s+([A-Za-z0-9/\s]+?)(?:\s+|$)", "", parsed["description"], flags=re.IGNORECASE
        ).strip()

    session["parsed"] = parsed

    # Step 3: Call search_listings with parsed parameters
    session["search_results"] = search_listings(
        description=parsed["description"],
        size=parsed["size"],
        max_price=parsed["max_price"],
    )

    # Branch A: No results — try retry logic with loosened constraints
    if not session["search_results"]:
        # Retry 1: Loosen price constraint (increase by 20)
        if parsed["max_price"] is not None:
            loosened_price = parsed["max_price"] * 1.2
            session["search_results"] = search_listings(
                description=parsed["description"],
                size=parsed["size"],
                max_price=loosened_price,
            )

        # Retry 2: Loosen size constraint (if specified)
        if not session["search_results"] and parsed["size"] is not None:
            session["search_results"] = search_listings(
                description=parsed["description"],
                size=None,  # Remove size filter
                max_price=parsed["max_price"],
            )

        # Retry 3: Use broader keywords (just first keyword)
        if not session["search_results"]:
            keywords = parsed["description"].split()
            if keywords:
                broader_description = keywords[0]
                session["search_results"] = search_listings(
                    description=broader_description,
                    size=parsed["size"],
                    max_price=parsed["max_price"],
                )

        # Still no results: show trending styles and error
        if not session["search_results"]:
            # Get trending styles as alternative recommendation
            trends = get_trending_styles(
                size=parsed["size"],
                category=None
            )

            # Store trends if successful (not an error message string)
            if isinstance(trends, list):
                session["trending_styles"] = trends

            session["error"] = (
                f"No items matching '{parsed['description']}' "
                f"{f'in size {parsed["size"]} ' if parsed['size'] else ''}"
                f"{'under $' + str(parsed['max_price']) if parsed['max_price'] else ''} found. "
                "Try a higher budget, different size, or broader style keywords. "
                "Check trending styles below for popular alternatives!"
            )
            return session
        else:
            # Retry succeeded: notify user which constraints were loosened
            # Also get trending styles to show alternatives
            trends = get_trending_styles(
                size=parsed["size"],
                category=None
            )
            if isinstance(trends, list):
                session["trending_styles"] = trends

            constraints_loosened = []
            if parsed["max_price"] is not None:
                constraints_loosened.append(f"increased budget to ${loosened_price:.0f}")
            if parsed["size"] is not None:
                constraints_loosened.append("relaxed size constraint")

            if constraints_loosened:
                session["error"] = (
                    f"No exact matches found. Showing results with {', '.join(constraints_loosened)}. "
                    "Feel free to adjust and search again!"
                )

    # Step 4: Select the top result
    session["selected_item"] = session["search_results"][0]

    # Step 5: Check wardrobe — if empty, return early with error
    wardrobe_items = wardrobe.get("items", [])
    if not wardrobe_items:
        session["error"] = (
            "You haven't added any items to your wardrobe yet. "
            "Once you set up your closet, I can suggest how to style this piece with your existing clothes."
        )
        return session

    # Step 6: Call suggest_outfit
    session["outfit_suggestion"] = suggest_outfit(
        new_item=session["selected_item"],
        wardrobe=wardrobe,
    )

    # Step 7: Call create_fit_card
    session["fit_card"] = create_fit_card(
        outfit=session["outfit_suggestion"],
        new_item=session["selected_item"],
    )

    # STRETCH FEATURE: Call compare_price on selected item (optional tool)
    price_analysis = compare_price(session["selected_item"])
    if price_analysis.get("rating"):  # Only store if we have enough comparables
        session["price_analysis"] = price_analysis

    # Step 8: Return the complete session
    return session


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nSelected item ID: {session['selected_item']['id']}")
        print(f"\nOutfit suggestion present: {bool(session['outfit_suggestion'])}")
        print(f"Outfit length: {len(session['outfit_suggestion'])} chars")
        print(f"Outfit snippet: {session['outfit_suggestion'][:100]}...")
        print(f"\nFit card present: {bool(session['fit_card'])}")
        print(f"Fit card length: {len(session['fit_card'])} chars")

    print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print(f"Error set: {session2['error'] is not None}")
    print(f"Selected item: {session2['selected_item']}")
    print(f"Fit card: {session2['fit_card']}")
    print(f"Error message: {session2['error'][:80]}...")
