"""
Style Profile Memory — persistent user style preferences.

Saves and loads user style profiles across interactions, allowing the agent
to remember style preferences from previous sessions and apply them to new searches.
"""

import json
import os
from pathlib import Path


PROFILES_FILE = "style_profiles.json"


def _ensure_profiles_file():
    """Create profiles.json if it doesn't exist."""
    if not os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, "w") as f:
            json.dump({}, f, indent=2)


def extract_style_preferences(wardrobe: dict) -> dict:
    """
    Extract style preferences from a user's wardrobe items.

    Args:
        wardrobe: User's wardrobe dict with 'items' list

    Returns:
        Dict with:
        - style_tags: Most common style tags in wardrobe
        - colors: Most common colors
        - categories: Most common categories
        - profile_summary: Human-readable description
    """
    items = wardrobe.get("items", [])
    if not items:
        return {
            "style_tags": [],
            "colors": [],
            "categories": [],
            "profile_summary": "No wardrobe items to extract preferences from"
        }

    # Count occurrences of each style tag, color, category
    style_counts = {}
    color_counts = {}
    category_counts = {}

    for item in items:
        # Count style tags
        for tag in item.get("style_tags", []):
            style_counts[tag] = style_counts.get(tag, 0) + 1

        # Count colors
        for color in item.get("colors", []):
            color_counts[color] = color_counts.get(color, 0) + 1

        # Count categories
        category = item.get("category", "unknown")
        category_counts[category] = category_counts.get(category, 0) + 1

    # Get top 3 of each
    top_styles = sorted(style_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    top_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]

    style_tags = [tag for tag, count in top_styles]
    colors = [color for color, count in top_colors]
    categories = [cat for cat, count in top_categories]

    # Create human-readable summary
    style_str = ", ".join(style_tags) if style_tags else "varied"
    color_str = ", ".join(colors) if colors else "varied"
    summary = f"Prefers {style_str} style in {color_str} colors"

    return {
        "style_tags": style_tags,
        "colors": colors,
        "categories": categories,
        "profile_summary": summary
    }


def save_profile(profile_name: str, wardrobe: dict, search_history: list = None) -> dict:
    """
    Save a user's style profile for future reference.

    Args:
        profile_name: Name to save profile under (e.g., "casual_user")
        wardrobe: User's wardrobe dict
        search_history: Optional list of recent searches

    Returns:
        Saved profile dict with metadata
    """
    _ensure_profiles_file()

    # Extract style preferences from wardrobe
    preferences = extract_style_preferences(wardrobe)

    # Create profile with metadata
    profile = {
        "name": profile_name,
        "wardrobe_items_count": len(wardrobe.get("items", [])),
        "style_tags": preferences["style_tags"],
        "colors": preferences["colors"],
        "categories": preferences["categories"],
        "profile_summary": preferences["profile_summary"],
        "search_history": search_history or [],
        "created_at": str(Path(PROFILES_FILE).stat().st_mtime) if os.path.exists(PROFILES_FILE) else "now"
    }

    # Load existing profiles
    with open(PROFILES_FILE, "r") as f:
        profiles = json.load(f)

    # Save new profile
    profiles[profile_name] = profile

    # Write back to file
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=2)

    return profile


def load_profile(profile_name: str) -> dict:
    """
    Load a previously saved style profile.

    Args:
        profile_name: Name of profile to load

    Returns:
        Profile dict, or None if not found
    """
    _ensure_profiles_file()

    with open(PROFILES_FILE, "r") as f:
        profiles = json.load(f)

    return profiles.get(profile_name)


def list_profiles() -> list:
    """
    List all saved style profiles.

    Returns:
        List of profile names available
    """
    _ensure_profiles_file()

    with open(PROFILES_FILE, "r") as f:
        profiles = json.load(f)

    return list(profiles.keys())


def apply_profile_to_search(query: str, profile: dict) -> str:
    """
    Enhance a search query with style preferences from a saved profile.

    Args:
        query: Original search query
        profile: Loaded profile dict

    Returns:
        Enhanced query that includes style preferences
    """
    if not profile or not profile.get("style_tags"):
        return query

    # Add top style tag if not already in query
    top_style = profile["style_tags"][0] if profile["style_tags"] else None
    if top_style and top_style.lower() not in query.lower():
        query = f"{top_style} {query}"

    return query


def delete_profile(profile_name: str) -> bool:
    """
    Delete a saved style profile.

    Args:
        profile_name: Name of profile to delete

    Returns:
        True if deleted, False if not found
    """
    _ensure_profiles_file()

    with open(PROFILES_FILE, "r") as f:
        profiles = json.load(f)

    if profile_name not in profiles:
        return False

    del profiles[profile_name]

    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=2)

    return True


if __name__ == "__main__":
    # Demo
    from utils.data_loader import get_example_wardrobe

    wardrobe = get_example_wardrobe()

    # Extract and save profile
    prefs = extract_style_preferences(wardrobe)
    print(f"Extracted preferences: {prefs['profile_summary']}")

    # Save profile
    profile = save_profile("demo_user", wardrobe, ["vintage tee", "grunge"])
    print(f"Saved profile: {profile['name']}")

    # List profiles
    print(f"Available profiles: {list_profiles()}")

    # Load profile
    loaded = load_profile("demo_user")
    print(f"Loaded profile: {loaded['profile_summary']}")

    # Apply profile to search
    enhanced_query = apply_profile_to_search("graphic tee under $30", loaded)
    print(f"Enhanced query: {enhanced_query}")
