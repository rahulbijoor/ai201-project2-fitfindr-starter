"""Tests for compare_price tool."""

import pytest
from tools import compare_price


class TestComparePrice:
    """Test compare_price functionality."""

    def test_compare_price_returns_dict(self, sample_listing):
        """Test that function returns a dictionary."""
        result = compare_price(sample_listing)
        assert isinstance(result, dict)

    def test_compare_price_has_required_fields(self, sample_listing):
        """Test that result has all required fields."""
        result = compare_price(sample_listing)
        required_fields = ["fair_price", "price_difference", "rating", "explanation"]
        for field in required_fields:
            assert field in result

    def test_compare_price_valid_rating(self, sample_listing):
        """Test that rating is valid when comparables exist."""
        result = compare_price(sample_listing)
        if result["rating"] is not None:
            assert result["rating"] in ["bargain", "fair", "overpriced"]

    def test_compare_price_explanation_exists(self, sample_listing):
        """Test that explanation is always provided."""
        result = compare_price(sample_listing)
        assert "explanation" in result
        assert len(result["explanation"]) > 0

    def test_compare_price_insufficient_comparables(self):
        """Test handling of unique item with insufficient comparables."""
        unique_item = {
            "id": "test_unique",
            "title": "Ultra Rare Item",
            "price": 500.0,
            "category": "outerwear",
            "condition": "fair",
            "brand": "Unknown",
            "style_tags": ["unique"],
            "colors": ["brown"],
        }
        result = compare_price(unique_item)
        assert result["rating"] is None
        assert "Not enough" in result["explanation"] or "unique" in result["explanation"].lower()

    def test_compare_price_math_correct(self, listings):
        """Test that price difference calculation is correct."""
        # Find an item with many comparables
        tops = [l for l in listings if l["category"] == "tops"]
        if len(tops) > 2:
            item = tops[0]
            result = compare_price(item)

            if result["fair_price"] is not None:
                expected_diff = item["price"] - result["fair_price"]
                assert abs(result["price_difference"] - expected_diff) < 0.01

    def test_compare_price_rating_boundaries(self, listings):
        """Test rating logic around boundaries."""
        tops = [l for l in listings if l["category"] == "tops"]
        for item in tops[:5]:
            result = compare_price(item)
            if result["rating"] is not None:
                # Bargain should have negative price difference
                if result["rating"] == "bargain":
                    assert result["price_difference"] < 0
                # Overpriced should have positive price difference
                elif result["rating"] == "overpriced":
                    assert result["price_difference"] > 0
                # Fair should be in middle range
                elif result["rating"] == "fair":
                    fair_price = result["fair_price"]
                    # Within roughly 10-15% is fair
                    assert abs(result["price_difference"]) <= fair_price * 0.15

    def test_compare_price_multiple_items(self, listings):
        """Test price comparison across different items."""
        test_items = [listings[0], listings[5], listings[10]]
        for item in test_items:
            result = compare_price(item)
            assert isinstance(result, dict)
            assert "explanation" in result
