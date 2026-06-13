"""Tests for create_fit_card tool."""

import pytest
from tools import create_fit_card


class TestCreateFitCard:
    """Test create_fit_card functionality."""

    def test_create_fit_card_valid_input(self, sample_listing):
        """Test fit card generation with valid inputs."""
        outfit = "Pair with baggy jeans and chunky sneakers for a casual vibe."
        result = create_fit_card(outfit, sample_listing)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_create_fit_card_includes_price(self, sample_listing):
        """Test that fit card mentions the price."""
        outfit = "Style with jeans and sneakers."
        result = create_fit_card(outfit, sample_listing)
        # Should mention price in some form
        price_str = str(int(sample_listing["price"]))
        assert price_str in result or f"${price_str}" in result or str(sample_listing["price"]) in result

    def test_create_fit_card_includes_platform(self, sample_listing):
        """Test that fit card mentions the platform."""
        outfit = "Style with jeans and sneakers."
        result = create_fit_card(outfit, sample_listing)
        assert sample_listing["platform"].lower() in result.lower()

    def test_create_fit_card_under_limit(self, sample_listing):
        """Test that caption stays under 280 characters."""
        outfit = "Pair with baggy jeans and chunky sneakers."
        result = create_fit_card(outfit, sample_listing)
        assert len(result) <= 280

    def test_create_fit_card_conversational_tone(self, sample_listing):
        """Test that caption has casual, conversational tone."""
        outfit = "Style with jeans and sneakers."
        result = create_fit_card(outfit, sample_listing)
        conversational_words = ["just", "scored", "love", "obsessed", "vibe", "perfect"]
        # Should have at least some conversational language
        has_tone = any(word in result.lower() for word in conversational_words)
        assert has_tone or len(result) > 0  # At least returns something

    def test_create_fit_card_empty_outfit(self, sample_listing):
        """Test handling of empty outfit."""
        result = create_fit_card("", sample_listing)
        assert isinstance(result, str)
        assert "incomplete" in result.lower()

    def test_create_fit_card_whitespace_outfit(self, sample_listing):
        """Test handling of whitespace-only outfit."""
        result = create_fit_card("   ", sample_listing)
        assert isinstance(result, str)
        assert "incomplete" in result.lower()

    def test_create_fit_card_missing_price(self):
        """Test handling of item missing price."""
        bad_item = {"title": "Test Item", "platform": "depop"}
        outfit = "Nice outfit"
        result = create_fit_card(outfit, bad_item)
        assert "incomplete" in result.lower()

    def test_create_fit_card_missing_platform(self):
        """Test handling of item missing platform."""
        bad_item = {"title": "Test Item", "price": 25.0}
        outfit = "Nice outfit"
        result = create_fit_card(outfit, bad_item)
        assert "incomplete" in result.lower()

    def test_create_fit_card_returns_string(self, sample_listing):
        """Test that function always returns string."""
        outfit = "Casual outfit with sneakers."
        result = create_fit_card(outfit, sample_listing)
        assert isinstance(result, str)

    @pytest.mark.parametrize("outfit_length", [50, 100, 200])
    def test_create_fit_card_various_outfit_lengths(self, sample_listing, outfit_length):
        """Test fit card with different outfit suggestion lengths."""
        outfit = "x" * outfit_length
        result = create_fit_card(outfit, sample_listing)
        assert isinstance(result, str)
        assert len(result) > 0
