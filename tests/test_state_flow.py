"""
Test script for state flow through the planning loop

Verifies that state passes correctly between tools and that values
flow from one step to the next without loss
"""

from agent import run_agent
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

print("=" * 70)
print("TEST SUITE: State Flow Through Planning Loop")
print("=" * 70)

print("\n[TEST 1] Happy Path State Tracing")
print("-" * 70)

session = run_agent(
    query="vintage graphic tee under $30",
    wardrobe=get_example_wardrobe(),
)

# Verify state accumulation
print("\nState accumulation:")
print(f"  session['query']: {session['query']}")
assert session["query"] == "vintage graphic tee under $30"
print("  [OK]")

print(f"  session['parsed']: {session['parsed']}")
assert session["parsed"]["description"] == "vintage graphic tee"
assert session["parsed"]["max_price"] == 30.0
print("  [OK]")

print(f"  session['search_results']: {len(session['search_results'])} items found")
assert len(session["search_results"]) > 0
print("  [OK]")

print(f"  session['selected_item']: {session['selected_item']['id']}")
assert session["selected_item"] is not None
assert session["selected_item"] == session["search_results"][0]
print("  [OK] selected_item is results[0]")

print(f"  session['outfit_suggestion']: {len(session['outfit_suggestion'])} chars")
assert session["outfit_suggestion"] is not None
assert len(session["outfit_suggestion"]) > 0
print("  [OK]")

print(f"  session['fit_card']: {len(session['fit_card'])} chars")
assert session["fit_card"] is not None
assert len(session["fit_card"]) > 0
print("  [OK]")

print(f"  session['price_analysis']: {session['price_analysis'] is not None}")
if session["price_analysis"]:
    print("  [OK] Price analysis present")
else:
    print("  [OK] Price analysis optional")

print(f"  session['error']: {session['error']}")
assert session["error"] is None
print("  [OK] No errors")

print("\n[TEST 2] Branching Path: No Results")
print("-" * 70)

session2 = run_agent(
    query="designer ballgown size XXS under $5",
    wardrobe=get_example_wardrobe(),
)

print("\nState on no results:")
print(f"  session['search_results']: {len(session2['search_results'])} items")
assert len(session2["search_results"]) == 0

print(f"  session['selected_item']: {session2['selected_item']}")
assert session2["selected_item"] is None
print("  [OK] selected_item is None (not called)")

print(f"  session['outfit_suggestion']: {session2['outfit_suggestion']}")
assert session2["outfit_suggestion"] is None
print("  [OK] outfit_suggestion is None (not called)")

print(f"  session['fit_card']: {session2['fit_card']}")
assert session2["fit_card"] is None
print("  [OK] fit_card is None (not called)")

print(f"  session['error']: {session2['error'][:50]}...")
assert session2["error"] is not None
print("  [OK] Error message set")

print("\n[TEST 3] Branching Path: Empty Wardrobe")
print("-" * 70)

session3 = run_agent(
    query="vintage graphic tee under $30",
    wardrobe=get_empty_wardrobe(),
)

print("\nState on empty wardrobe:")
print(f"  session['search_results']: {len(session3['search_results'])} items")
assert len(session3["search_results"]) > 0
print("  [OK] Search completed")

print(f"  session['selected_item']: {session3['selected_item']['id']}")
assert session3["selected_item"] is not None
print("  [OK] Item selected")

print(f"  session['outfit_suggestion']: {session3['outfit_suggestion']}")
assert session3["outfit_suggestion"] is None
print("  [OK] outfit_suggestion is None (not called)")

print(f"  session['fit_card']: {session3['fit_card']}")
assert session3["fit_card"] is None
print("  [OK] fit_card is None (not called)")

print(f"  session['error']: {session3['error'][:50]}...")
assert "wardrobe" in session3["error"].lower()
print("  [OK] Wardrobe error set")

print("\n" + "=" * 70)
print("ALL STATE FLOW TESTS PASSED")
print("=" * 70)
print("""
State Management Verification:
✓ Happy path: All state accumulates correctly through all steps
✓ No results: State stops accumulating at search, downstream is None
✓ Empty wardrobe: State stops accumulating at wardrobe check, downstream is None
✓ Errors: Set at decision points, prevent downstream calls
✓ Session dict: Single source of truth for entire interaction
""")
