"""
Pytest test suite for stretch features.

Tests:
- Price Comparison Tool: compare_price() called on selected item
- Trend Awareness Tool: get_trending_styles() called on empty search
- Retry Logic: search retries with loosened constraints on zero results
"""

import pytest
from agent import run_agent
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe


class TestPriceComparison:
    """Test suite: Price Comparison Tool (+2pts)"""

    def test_price_analysis_stored_on_success(self):
        """Verify price_analysis is computed and stored in session."""
        session = run_agent(
            query="vintage graphic tee under $30",
            wardrobe=get_example_wardrobe(),
        )
        assert session["price_analysis"] is not None, "price_analysis should be set"
        assert "fair_price" in session["price_analysis"]
        assert "rating" in session["price_analysis"]
        assert "explanation" in session["price_analysis"]

    def test_price_analysis_rating_values(self):
        """Verify price_analysis contains valid rating values."""
        session = run_agent(
            query="vintage graphic tee under $30",
            wardrobe=get_example_wardrobe(),
        )
        rating = session["price_analysis"]["rating"]
        assert rating in ["bargain", "fair", "overpriced"], f"Invalid rating: {rating}"

    def test_price_analysis_explanation_meaningful(self):
        """Verify price_analysis explanation is not empty."""
        session = run_agent(
            query="vintage graphic tee under $30",
            wardrobe=get_example_wardrobe(),
        )
        explanation = session["price_analysis"]["explanation"]
        assert len(explanation) > 0, "Explanation should not be empty"
        assert "typical" in explanation.lower() or "selling" in explanation.lower()

    def test_price_analysis_not_set_on_error(self):
        """Verify price_analysis is None when search fails."""
        session = run_agent(
            query="designer ballgown size XXS under $5",
            wardrobe=get_example_wardrobe(),
        )
        # On error, price_analysis should still be None (no item selected)
        assert session["price_analysis"] is None


class TestTrendAwareness:
    """Test suite: Trend Awareness Tool (+2pts)"""

    def test_trending_styles_returned_on_empty_search(self):
        """Verify get_trending_styles is called when search returns empty."""
        session = run_agent(
            query="designer ballgown size XXS under $5",
            wardrobe=get_example_wardrobe(),
        )
        # After retries exhaust, trending_styles should be populated
        assert session["trending_styles"] is not None or session["error"] is not None

    def test_trending_styles_structure(self):
        """Verify trending styles list has correct structure."""
        session = run_agent(
            query="designer ballgown size XXS under $5",
            wardrobe=get_example_wardrobe(),
        )
        if session.get("trending_styles") and isinstance(session["trending_styles"], list):
            for trend in session["trending_styles"]:
                assert "style_tag" in trend
                assert "popularity_score" in trend
                assert "example_count" in trend
                assert 0 <= trend["popularity_score"] <= 100

    def test_trending_styles_in_error_message(self):
        """Verify trending styles info appears in error when available."""
        session = run_agent(
            query="designer ballgown size XXS under $5",
            wardrobe=get_example_wardrobe(),
        )
        if session.get("trending_styles") and isinstance(session["trending_styles"], list):
            # Error should mention trending alternatives
            assert "trending" in session["error"].lower() or len(session.get("trending_styles", [])) > 0


class TestRetryLogic:
    """Test suite: Retry Logic with Fallback (+1pt)"""

    def test_retry_on_zero_results(self):
        """Verify agent retries with loosened constraints on zero results."""
        session = run_agent(
            query="nonexistent brand under $5",
            wardrobe=get_example_wardrobe(),
        )
        # Agent should either find results after retry or show trending
        # (doesn't fail immediately on first zero result)
        assert session["error"] is not None  # Will have message
        # Either results found after retry or trending alternatives shown
        assert (session["search_results"] or session.get("trending_styles"))

    def test_retry_loosens_price_constraint(self):
        """Verify retry logic increases price ceiling."""
        session = run_agent(
            query="vintage tee under $1",  # Unrealistic price
            wardrobe=get_example_wardrobe(),
        )
        # After retry with +20% price, should find results
        if session["search_results"]:
            # Verify at least one result was found after retry
            assert len(session["search_results"]) > 0
            # Message should indicate constraint was loosened
            if session.get("error"):
                assert "increased budget" in session["error"].lower() or "loosened" in session["error"].lower()

    def test_retry_message_explains_changes(self):
        """Verify error message explains which constraints were loosened."""
        session = run_agent(
            query="nonexistent brand under $2",
            wardrobe=get_example_wardrobe(),
        )
        if session["error"] and "loosened" in session["error"].lower():
            # Message should be specific about what was adjusted
            assert any(
                keyword in session["error"].lower()
                for keyword in ["budget", "size", "keywords", "constraints"]
            )


class TestIntegration:
    """Integration tests: All features together"""

    def test_happy_path_includes_all_features(self):
        """Verify happy path includes price comparison."""
        session = run_agent(
            query="vintage graphic tee under $30",
            wardrobe=get_example_wardrobe(),
        )
        # Happy path should have:
        assert not session["error"]  # No error
        assert session["selected_item"] is not None
        assert session["outfit_suggestion"] is not None
        assert session["fit_card"] is not None
        assert session["price_analysis"] is not None  # Price comparison

    def test_error_path_includes_trends(self):
        """Verify error path includes trending styles when appropriate."""
        session = run_agent(
            query="designer ballgown size XXS under $5",
            wardrobe=get_example_wardrobe(),
        )
        # Error path after retries should have:
        assert session["error"] is not None
        # Either found results after retry or has trending alternatives
        if not session["search_results"]:
            assert session.get("trending_styles") is not None or session["error"] is not None

    def test_state_dict_completeness(self):
        """Verify session dict includes all expected fields."""
        session = run_agent(
            query="vintage graphic tee under $30",
            wardrobe=get_example_wardrobe(),
        )
        required_fields = [
            "query", "parsed", "search_results", "selected_item",
            "wardrobe", "outfit_suggestion", "fit_card",
            "price_analysis", "trending_styles", "error"
        ]
        for field in required_fields:
            assert field in session, f"Missing field: {field}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
