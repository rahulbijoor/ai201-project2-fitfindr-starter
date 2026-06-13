"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform

    TODO:
        1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts.

    Before writing code, fill in the Tool 1 section of planning.md.
    """
    listings = load_listings()

    # Filter by price
    if max_price is not None:
        listings = [l for l in listings if l["price"] <= max_price]

    # Filter by size - handle ranges like "S/M" matching "M"
    if size is not None:
        size_lower = size.lower()
        # Normalize: convert spaces to slashes for consistent splitting
        size_parts = set(
            s.strip()
            for s in size_lower.replace(" ", "/").split("/")
            if s.strip()
        )

        filtered = []
        for listing in listings:
            listing_size_lower = listing["size"].lower()
            listing_parts = set(
                s.strip()
                for s in listing_size_lower.replace(" ", "/").split("/")
                if s.strip()
            )

            # Check if there's any overlap between user size and listing size
            if size_parts & listing_parts:
                filtered.append(listing)

        listings = filtered

    # Score each listing by keyword relevance
    keywords = description.lower().split()
    scored = []

    for listing in listings:
        score = 0

        # Title matches (weight: 3) — highest relevance
        title_lower = listing["title"].lower()
        for keyword in keywords:
            if keyword in title_lower:
                score += 3

        # Style tags matches (weight: 2) — medium relevance
        for tag in listing["style_tags"]:
            tag_lower = tag.lower()
            for keyword in keywords:
                if keyword in tag_lower:
                    score += 2

        # Description matches (weight: 1) — lowest relevance
        desc_lower = listing["description"].lower()
        for keyword in keywords:
            if keyword in desc_lower:
                score += 1

        # Only keep listings with at least one keyword match
        if score > 0:
            scored.append((score, listing))

    # Sort by relevance score, highest first
    scored.sort(key=lambda x: x[0], reverse=True)

    # Return listing dicts without scores
    return [listing for _, listing in scored]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If empty: call the LLM with a prompt for general styling ideas
           (what kinds of items pair well, what vibe it suits, etc.).
        3. If not empty: format the wardrobe items into a prompt and ask
           the LLM to suggest specific outfit combinations using the new item
           and named pieces from the wardrobe.
        4. Return the LLM's response as a string.

    Before writing code, fill in the Tool 2 section of planning.md.
    """
    # Handle empty wardrobe case
    wardrobe_items = wardrobe.get("items", [])
    if not wardrobe_items:
        return (
            "You haven't added any items to your wardrobe yet. Once you set up "
            "your closet, I can suggest how to style this piece with your existing clothes."
        )

    # Format wardrobe items for the LLM prompt
    wardrobe_description = "\n".join(
        [
            f"- {item['name']} ({item['category']}, colors: {', '.join(item['colors'])}, "
            f"style: {', '.join(item['style_tags'])})"
            for item in wardrobe_items
        ]
    )

    # Build the prompt for the LLM
    prompt = f"""You are a personal stylist helping a user style a thrifted fashion item they're considering buying.

New item being considered:
- Title: {new_item['title']}
- Category: {new_item['category']}
- Colors: {', '.join(new_item['colors'])}
- Style tags: {', '.join(new_item['style_tags'])}
- Condition: {new_item['condition']}
- Brand: {new_item.get('brand', 'Unknown')}

User's existing wardrobe items:
{wardrobe_description}

Your task: Suggest how to style the new item with pieces from their existing wardrobe.

Consider:
1. Color coordination — what colors work well together
2. Style alignment — do the styles match (e.g., grunge with grunge, y2k with y2k)
3. Silhouette balance — how the proportions work together
4. Category balance — pair tops with bottoms and shoes appropriately

Provide a 2–3 sentence specific styling suggestion that:
- Mentions actual pieces from their wardrobe by name
- Explains the reasoning briefly (color match, style vibe, silhouette balance)
- Keeps a casual, authentic tone (like a friend giving style advice)
- Includes a specific styling tip if relevant (e.g., "Tuck the front corner for subtle shape")

Be concise and actionable."""

    # Call the LLM
    client = _get_groq_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300,
    )

    return response.choices[0].message.content.strip()


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)

    TODO:
        1. Guard against an empty or whitespace-only outfit string.
        2. Build a prompt that gives the LLM the item details and the outfit,
           and asks for a caption matching the style guidelines above.
        3. Call the LLM and return the response.

    Before writing code, fill in the Tool 3 section of planning.md.
    """
    # Validate required fields
    if not outfit or not outfit.strip():
        return (
            "Couldn't generate a caption with incomplete outfit or item data. "
            "Please make sure the item details and outfit suggestion are complete "
            "before creating a fit card."
        )

    required_fields = ["title", "price", "platform"]
    if not all(field in new_item and new_item[field] for field in required_fields):
        return (
            "Couldn't generate a caption with incomplete outfit or item data. "
            "Please make sure the item details and outfit suggestion are complete "
            "before creating a fit card."
        )

    # Build the prompt for the LLM
    prompt = f"""You are a fashion-savvy social media expert helping someone write an authentic Instagram/TikTok caption about a thrifted fashion find.

Item details:
- Title: {new_item['title']}
- Price: ${new_item['price']}
- Platform: {new_item['platform']}
- Condition: {new_item.get('condition', 'unknown')}
- Brand: {new_item.get('brand', 'unknown')}
- Colors: {', '.join(new_item.get('colors', []))}
- Style: {', '.join(new_item.get('style_tags', []))}

Outfit suggestion/context:
{outfit}

Your task: Write a casual, authentic Instagram/TikTok caption (2–4 sentences, ideally under 280 characters) that:
1. Mentions the item name, price, and platform naturally (exactly once each)
2. Captures the outfit vibe and styling energy
3. Feels like a real OOTD post written by a friend, not a product description
4. Includes 1–2 relevant emojis to match the vibe
5. Encourages interaction or sharing (optional, but nice to have)

Keep it genuine, enthusiastic, and concise. Don't use hashtags. Sound casual and conversational."""

    # Call the LLM with higher temperature for more varied outputs
    client = _get_groq_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,  # Higher temperature for more creative variation
        max_tokens=200,
    )

    return response.choices[0].message.content.strip()


# ── Tool 4: compare_price ────────────────────────────────────────────────────

def compare_price(item: dict) -> dict:
    """
    Analyze whether a listing's price is fair by comparing against similar items.

    Args:
        item: A listing dict with id, title, price, category, condition, brand,
              style_tags, colors.

    Returns:
        A dict with:
            - fair_price (float): Average price of comparable listings
            - price_difference (float): item.price - fair_price
            - rating (str): "bargain", "fair", or "overpriced" (or None if <2 comparables)
            - explanation (str): Human-readable explanation of the price analysis

        If fewer than 2 comparable listings exist, returns:
            - rating: None
            - explanation: Message explaining insufficient data

    Comparability is based on: category, condition, and brand (where available).
    """
    listings = load_listings()

    # Filter for comparables: same category, condition, and brand (if available)
    comparables = [
        l
        for l in listings
        if l["category"] == item["category"]
        and l["condition"] == item["condition"]
        and (
            item.get("brand") is None
            or l.get("brand") == item.get("brand")
            or item.get("brand") is None
        )
    ]

    # Need at least 2 comparables to estimate fair price
    if len(comparables) < 2:
        return {
            "fair_price": None,
            "price_difference": None,
            "rating": None,
            "explanation": (
                "Not enough comparable items to estimate fair price. This item is unique "
                "or rarely listed — use your judgment based on condition and brand."
            ),
        }

    # Calculate average price of comparables
    fair_price = sum(c["price"] for c in comparables) / len(comparables)
    price_difference = item["price"] - fair_price

    # Determine rating based on price difference (within 10% = fair)
    threshold_low = fair_price * 0.1
    threshold_high = fair_price * 0.1

    if price_difference < -threshold_low:
        rating = "bargain"
        saving_text = f"${abs(price_difference):.2f} less"
    elif price_difference > threshold_high:
        rating = "overpriced"
        saving_text = f"${price_difference:.2f} more"
    else:
        rating = "fair"
        saving_text = "about right"

    explanation = (
        f"This {item['category']} in {item['condition']} condition typically sells for "
        f"${fair_price:.2f}. You're paying ${item['price']:.2f}, which is {saving_text}. "
        f"({len(comparables)} comparables found)"
    )

    return {
        "fair_price": fair_price,
        "price_difference": price_difference,
        "rating": rating,
        "explanation": explanation,
    }


# ── Tool 5: get_trending_styles ──────────────────────────────────────────────

def get_trending_styles(size: str, category: str | None = None) -> list | str:
    """
    Get trending fashion styles for a given size.

    Since a real public API is out of scope, this uses mock trend data derived
    from the actual listings dataset to estimate popularity.

    Args:
        size: User's size (e.g., "M", "S/M", "W28") to filter trends.
        category: Optional category to filter (e.g., "tops", "bottoms").

    Returns:
        A list of trending items, each with:
            - style_tag (str): Style name (e.g., "y2k", "grunge", "vintage")
            - popularity_score (float): 0–100 popularity score
            - example_count (int): Number of listings with this style
            - size_availability (str): "common", "moderate", or "rare" in given size

        Returns error message string if trend data unavailable.
    """
    try:
        listings = load_listings()

        # Filter by size if provided
        if size:
            size_lower = size.lower()
            size_parts = set(s.strip() for s in size_lower.replace(" ", "/").split("/"))
            listings = [
                l
                for l in listings
                if any(
                    sp in l["size"].lower().replace(" ", "/").split("/")
                    for sp in size_parts
                )
            ]

        # Filter by category if provided
        if category:
            listings = [l for l in listings if l["category"] == category]

        if not listings:
            return "Trend data unavailable right now. Check back later or browse popular hashtags like #thrifted, #vintage, or #y2k for style inspiration."

        # Count occurrences of each style tag
        style_counts = {}
        style_sizes = {}  # Track size availability per style

        for listing in listings:
            for tag in listing["style_tags"]:
                style_counts[tag] = style_counts.get(tag, 0) + 1
                if tag not in style_sizes:
                    style_sizes[tag] = []
                style_sizes[tag].append(listing["size"])

        if not style_counts:
            return "Trend data unavailable right now. Check back later or browse popular hashtags like #thrifted, #vintage, or #y2k for style inspiration."

        # Calculate popularity scores (normalized 0-100)
        max_count = max(style_counts.values())
        min_count = min(style_counts.values())
        count_range = max_count - min_count if max_count > min_count else 1

        trends = []
        for style_tag, count in style_counts.items():
            # Popularity score based on frequency
            popularity_score = 50 + ((count - min_count) / count_range * 50)

            # Size availability based on proportion
            available_sizes = len(style_sizes.get(style_tag, []))
            total_available = len(listings)
            availability_ratio = available_sizes / max(total_available, 1)

            if availability_ratio >= 0.7:
                size_availability = "common"
            elif availability_ratio >= 0.4:
                size_availability = "moderate"
            else:
                size_availability = "rare"

            trends.append(
                {
                    "style_tag": style_tag,
                    "popularity_score": round(popularity_score, 1),
                    "example_count": count,
                    "size_availability": size_availability,
                }
            )

        # Sort by popularity score descending
        trends.sort(key=lambda x: x["popularity_score"], reverse=True)

        return trends

    except Exception as e:
        return f"Trend data unavailable right now. Check back later or browse popular hashtags like #thrifted, #vintage, or #y2k for style inspiration."
