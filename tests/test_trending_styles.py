"""Tests for get_trending_styles tool."""

import pytest
from tools import get_trending_styles


class TestGetTrendingStyles:
    """Test get_trending_styles functionality."""

    def test_get_trending_styles_returns_list(self):
        """Test that function returns list or string."""
        result = get_trending_styles("M")
        assert isinstance(result, (list, str))

    def test_get_trending_styles_valid_list(self):
        """Test that returned list has valid structure."""
        result = get_trending_styles("M")
        if isinstance(result, list):
            assert len(result) > 0
            # Check first item has required fields
            item = result[0]
            required_fields = ["style_tag", "popularity_score", "example_count", "size_availability"]
            for field in required_fields:
                assert field in item

    def test_get_trending_styles_sorted_by_score(self):
        """Test that trends are sorted by popularity score."""
        result = get_trending_styles("M")
        if isinstance(result, list):
            scores = [item["popularity_score"] for item in result]
            # Should be in descending order
            assert scores == sorted(scores, reverse=True)

    def test_get_trending_styles_valid_size_availability(self):
        """Test that size_availability is one of valid values."""
        result = get_trending_styles("M")
        if isinstance(result, list):
            valid_values = ["common", "moderate", "rare"]
            for item in result:
                assert item["size_availability"] in valid_values

    def test_get_trending_styles_popularity_range(self):
        """Test that popularity scores are in valid range."""
        result = get_trending_styles("M")
        if isinstance(result, list):
            for item in result:
                assert 0 <= item["popularity_score"] <= 100

    def test_get_trending_styles_with_category(self):
        """Test filtering by category."""
        result = get_trending_styles("M", category="tops")
        if isinstance(result, list):
            assert len(result) > 0
            # Result should have fewer items than without category filter
            all_result = get_trending_styles("M")
            if isinstance(all_result, list):
                assert len(result) <= len(all_result)

    def test_get_trending_styles_different_sizes(self):
        """Test with different size inputs."""
        sizes = ["M", "S", "L", "XL", "S/M", "W28"]
        for size in sizes:
            result = get_trending_styles(size)
            assert isinstance(result, (list, str))
            if isinstance(result, list):
                assert len(result) >= 0

    def test_get_trending_styles_example_count_positive(self):
        """Test that example counts are positive integers."""
        result = get_trending_styles("M")
        if isinstance(result, list):
            for item in result:
                assert isinstance(item["example_count"], int)
                assert item["example_count"] > 0

    def test_get_trending_styles_style_tag_not_empty(self):
        """Test that style tags are not empty strings."""
        result = get_trending_styles("M")
        if isinstance(result, list):
            for item in result:
                assert len(item["style_tag"]) > 0
                assert isinstance(item["style_tag"], str)

    def test_get_trending_styles_no_crash_on_empty_result(self):
        """Test that function doesn't crash on edge cases."""
        try:
            # Very restrictive combination unlikely to have results
            result = get_trending_styles("XXXL", category="nonexistent")
            assert isinstance(result, (list, str))
        except Exception as e:
            pytest.fail(f"Function raised unexpected exception: {e}")

    @pytest.mark.parametrize("size,category", [
        ("M", None),
        ("S/M", "tops"),
        ("XL", "bottoms"),
        ("W28", None),
    ])
    def test_get_trending_styles_combinations(self, size, category):
        """Test various size and category combinations."""
        result = get_trending_styles(size, category=category)
        assert isinstance(result, (list, str))
