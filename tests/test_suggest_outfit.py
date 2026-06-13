"""Tests for suggest_outfit tool."""

import pytest
from tools import suggest_outfit


class TestSuggestOutfit:
    """Test suggest_outfit functionality."""

    def test_suggest_outfit_with_items(self, sample_listing, example_wardrobe):
        """Test outfit suggestion with populated wardrobe."""
        result = suggest_outfit(sample_listing, example_wardrobe)
        assert isinstance(result, str)
        assert len(result) > 0
        assert not result.startswith("You haven't added")

    def test_suggest_outfit_references_wardrobe_pieces(self, sample_listing, example_wardrobe):
        """Test that suggestion mentions pieces from wardrobe by name."""
        result = suggest_outfit(sample_listing, example_wardrobe)
        wardrobe_names = [item["name"].lower() for item in example_wardrobe["items"]]
        # Should reference at least one wardrobe piece
        assert any(name in result.lower() for name in wardrobe_names)

    def test_suggest_outfit_empty_wardrobe(self, sample_listing, empty_wardrobe):
        """Test that empty wardrobe is handled gracefully."""
        result = suggest_outfit(sample_listing, empty_wardrobe)
        assert isinstance(result, str)
        assert "haven't added" in result.lower() or "empty" in result.lower()

    def test_suggest_outfit_empty_wardrobe_no_crash(self, sample_listing, empty_wardrobe):
        """Test that empty wardrobe doesn't crash the function."""
        try:
            result = suggest_outfit(sample_listing, empty_wardrobe)
            assert result is not None
        except Exception as e:
            pytest.fail(f"Function raised unexpected exception: {e}")

    def test_suggest_outfit_returns_string(self, sample_listing, example_wardrobe):
        """Test that function always returns a string."""
        result = suggest_outfit(sample_listing, example_wardrobe)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_suggest_outfit_length_reasonable(self, sample_listing, example_wardrobe):
        """Test that suggestion is a reasonable length (2-3 sentences)."""
        result = suggest_outfit(sample_listing, example_wardrobe)
        # Count sentences (rough approximation)
        sentence_count = result.count(". ") + result.count("!") + result.count("?")
        assert 1 <= sentence_count <= 5  # Allow some variation

    def test_suggest_outfit_multiple_items(self, listings, example_wardrobe):
        """Test outfit suggestion with different items."""
        for item in listings[:3]:
            result = suggest_outfit(item, example_wardrobe)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_suggest_outfit_missing_wardrobe_key(self, sample_listing):
        """Test handling of wardrobe without 'items' key."""
        bad_wardrobe = {"some_other_key": []}
        try:
            result = suggest_outfit(sample_listing, bad_wardrobe)
            assert isinstance(result, str)
        except KeyError as e:
            pytest.fail(f"Function should handle missing 'items' key: {e}")
