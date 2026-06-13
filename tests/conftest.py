"""Pytest configuration and shared fixtures."""

import pytest
from utils.data_loader import load_listings, get_example_wardrobe, get_empty_wardrobe


@pytest.fixture
def listings():
    """Load all listings from the dataset."""
    return load_listings()


@pytest.fixture
def example_wardrobe():
    """Load the example wardrobe."""
    return get_example_wardrobe()


@pytest.fixture
def empty_wardrobe():
    """Load the empty wardrobe template."""
    return get_empty_wardrobe()


@pytest.fixture
def sample_listing(listings):
    """Get a sample listing for testing."""
    return listings[1]  # Y2K Baby Tee


@pytest.fixture
def sample_item_for_comparison(listings):
    """Get an item with many comparables for price comparison."""
    return listings[5]  # Graphic Tee
