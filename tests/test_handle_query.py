"""
Test script for handle_query() function in app.py

Tests all UI paths: happy path, no results, empty wardrobe, empty query
"""

from app import handle_query
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

print("=" * 70)
print("TEST SUITE: handle_query()")
print("=" * 70)

print("\n[TEST 1] Happy Path with Example Wardrobe")
listing, outfit, fitcard = handle_query(
    user_query="vintage graphic tee under $30",
    wardrobe_choice="Example wardrobe",
)

assert len(listing) > 0, "Listing should not be empty"
assert len(outfit) > 0, "Outfit should not be empty"
assert len(fitcard) > 0, "Fit card should not be empty"
assert "Graphic Tee" in listing, "Should find graphic tee"
print("[PASS] All three panels populated")
print(f"  Listing: {len(listing)} chars")
print(f"  Outfit: {len(outfit)} chars")
print(f"  Fit card: {len(fitcard)} chars")

print("\n[TEST 2] No Results Path")
listing2, outfit2, fitcard2 = handle_query(
    user_query="designer ballgown size XXS under $5",
    wardrobe_choice="Example wardrobe",
)

assert "No items" in listing2, "Should show error"
assert outfit2 == "", "Outfit should be empty"
assert fitcard2 == "", "Fit card should be empty"
print("[PASS] Error in listing, other panels empty")
print(f"  Error message: {listing2[:80]}...")

print("\n[TEST 3] Empty Wardrobe Path")
listing3, outfit3, fitcard3 = handle_query(
    user_query="vintage graphic tee under $30",
    wardrobe_choice="Empty wardrobe (new user)",
)

assert "wardrobe" in listing3.lower(), "Should mention wardrobe"
assert outfit3 == "", "Outfit should be empty"
assert fitcard3 == "", "Fit card should be empty"
print("[PASS] Error about wardrobe")
print(f"  Error message: {listing3[:80]}...")

print("\n[TEST 4] Empty Query")
listing4, outfit4, fitcard4 = handle_query(
    user_query="",
    wardrobe_choice="Example wardrobe",
)

assert "Please enter" in listing4, "Should prompt for input"
assert outfit4 == "", "Outfit should be empty"
assert fitcard4 == "", "Fit card should be empty"
print("[PASS] Guard against empty query")
print(f"  Error message: {listing4[:80]}...")

print("\n" + "=" * 70)
print("ALL TESTS PASSED")
print("=" * 70)
