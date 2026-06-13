"""Tests for search_listings tool."""

import pytest
from tools import search_listings


class TestSearchListings:
    """Test search_listings functionality."""

    def test_search_returns_results(self):
        """Test that search returns results for valid query."""
        results = search_listings("vintage graphic tee", size="M", max_price=30.0)
        assert len(results) > 0
        assert isinstance(results, list)

    def test_search_filters_by_price(self):
        """Test that results respect max_price filter."""
        results = search_listings("denim", max_price=25.0)
        assert all(item["price"] <= 25.0 for item in results)

    def test_search_filters_by_size(self):
        """Test that size matching works (M matches S/M)."""
        results = search_listings("baby tee", size="M")
        # Should find items in M or S/M range
        assert len(results) > 0
        for item in results:
            size_parts = set(item["size"].lower().replace(" ", "/").split("/"))
            assert "m" in size_parts

    def test_search_no_results_returns_empty(self):
        """Test that impossible query returns empty list."""
        results = search_listings("dinosaur pet purple", size="XS", max_price=10.0)
        assert len(results) == 0
        assert results == []

    def test_search_scores_by_relevance(self):
        """Test that results are sorted by relevance (title > tags > description)."""
        results = search_listings("vintage")
        # First result should have "vintage" in title or tags
        if len(results) > 0:
            first = results[0]
            text = f"{first['title']} {' '.join(first['style_tags'])}".lower()
            assert "vintage" in text

    def test_search_handles_optional_parameters(self):
        """Test search with various parameter combinations."""
        # Without size or price
        r1 = search_listings("denim")
        assert isinstance(r1, list)

        # With size only
        r2 = search_listings("denim", size="M")
        assert isinstance(r2, list)

        # With price only
        r3 = search_listings("denim", max_price=50.0)
        assert isinstance(r3, list)

    @pytest.mark.parametrize("query,expected_min", [
        ("denim", 1),
        ("vintage", 1),
        ("y2k", 1),
    ])
    def test_search_common_queries(self, query, expected_min):
        """Test search with multiple common fashion queries."""
        results = search_listings(query)
        assert len(results) >= expected_min

    def test_search_results_contain_required_fields(self):
        """Test that search results have all required fields."""
        results = search_listings("vintage")
        assert len(results) > 0

        required_fields = ["id", "title", "price", "category", "style_tags", "size", "condition", "colors", "platform"]
        for item in results[:3]:
            for field in required_fields:
                assert field in item, f"Missing field: {field}"
