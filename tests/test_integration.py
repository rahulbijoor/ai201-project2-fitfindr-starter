"""Integration tests for complete FitFindr flow."""

import pytest
from tools import (
    search_listings,
    suggest_outfit,
    create_fit_card,
    compare_price,
    get_trending_styles,
)


class TestCompleteFlow:
    """Test complete FitFindr workflows."""

    def test_flow_search_to_outfit_to_card(self, example_wardrobe):
        """Test complete flow: search → outfit → fit card."""
        # Step 1: Search
        results = search_listings("vintage graphic tee", size="M", max_price=30.0)
        assert len(results) > 0

        selected_item = results[0]

        # Step 2: Suggest outfit
        outfit = suggest_outfit(selected_item, example_wardrobe)
        assert len(outfit) > 0
        assert not outfit.startswith("You haven't")

        # Step 3: Create fit card
        caption = create_fit_card(outfit, selected_item)
        assert len(caption) > 0
        assert "incomplete" not in caption.lower()

    def test_flow_with_price_check(self, example_wardrobe):
        """Test flow including optional price comparison."""
        # Search
        results = search_listings("denim", max_price=50.0)
        assert len(results) > 0

        selected_item = results[0]

        # Price comparison (optional)
        price_info = compare_price(selected_item)
        assert "explanation" in price_info

        # Outfit suggestion
        outfit = suggest_outfit(selected_item, example_wardrobe)
        assert len(outfit) > 0

    def test_flow_no_results_fallback_to_trends(self):
        """Test fallback to trending styles when no search results."""
        # Search with impossible criteria
        results = search_listings("unicorn sequin disco", size="XS", max_price=10.0)
        assert len(results) == 0

        # Fall back to trending styles
        trends = get_trending_styles("XS")
        # Could be list or error message string
        assert isinstance(trends, (list, str))

    def test_flow_with_empty_wardrobe(self, empty_wardrobe):
        """Test that empty wardrobe is handled gracefully."""
        results = search_listings("vintage")
        assert len(results) > 0

        selected_item = results[0]

        # Should get error message for empty wardrobe
        outfit = suggest_outfit(selected_item, empty_wardrobe)
        assert "haven't added" in outfit.lower() or "empty" in outfit.lower()

    def test_all_tools_work_together(self, example_wardrobe):
        """Test that all 5 tools can be called in sequence."""
        # Tool 1: Search
        results = search_listings("vintage", size="M", max_price=50.0)
        assert len(results) > 0
        item = results[0]

        # Tool 2: Suggest outfit
        outfit = suggest_outfit(item, example_wardrobe)
        assert isinstance(outfit, str)

        # Tool 3: Create fit card
        caption = create_fit_card(outfit, item)
        assert isinstance(caption, str)

        # Tool 4: Compare price
        price = compare_price(item)
        assert isinstance(price, dict)

        # Tool 5: Get trends (as backup)
        trends = get_trending_styles("M")
        assert isinstance(trends, (list, str))

    def test_flow_produces_valid_outputs(self, example_wardrobe):
        """Test that all outputs meet quality standards."""
        results = search_listings("vintage", size="M", max_price=30.0)
        item = results[0]

        outfit = suggest_outfit(item, example_wardrobe)
        caption = create_fit_card(outfit, item)
        price = compare_price(item)

        # Validation checks
        assert len(outfit) > 0
        assert len(caption) > 0
        assert len(caption) <= 280  # Social media limit
        # Caption should mention the price in some form
        price_str = str(int(item["price"])) if item["price"] == int(item["price"]) else str(item["price"])
        assert price_str in caption or f"${price_str}" in caption
        assert item["platform"].lower() in caption.lower()
        assert isinstance(price, dict)
