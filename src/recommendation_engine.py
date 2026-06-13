"""Rule-based outfit recommendation engine for Wardrobe Wizard.

This module does not call an AI model.
It uses clear scoring rules so the app can work without API keys, cloud setup, or extra cost.
"""

from __future__ import annotations


SCENARIO_RULES = {
    "Office rainy day": {
        "weather": ["rainy", "mild", "indoor"],
        "style_tags": ["office-friendly", "elegant", "practical"],
        "formality": ["office", "smart-casual"],
        "prefer_layer": True,
    },
    "Date night": {
        "weather": ["mild", "indoor"],
        "style_tags": ["elegant", "feminine", "romantic", "date-night"],
        "formality": ["smart-casual", "elegant"],
        "prefer_layer": False,
    },
    "Travel day": {
        "weather": ["travel", "mild", "indoor"],
        "style_tags": ["travel-friendly", "casual", "practical", "cozy"],
        "formality": ["casual", "smart-casual"],
        "prefer_layer": True,
    },
}


def get_item_id(item: dict | None) -> str:
    """Return an item ID or an empty string if the item is missing."""
    if not item:
        return ""

    return item.get("id", "")


def normalize_text(text: str) -> str:
    """Make text easier to compare by using lowercase and removing extra spaces."""
    return text.strip().lower()


def get_scenario_profile(scenario: str, custom_scenario: str) -> dict:
    """Return recommendation hints for a preset or custom scenario."""
    custom_text = normalize_text(custom_scenario)

    if scenario in SCENARIO_RULES:
        base_profile = SCENARIO_RULES[scenario]

        profile = {
            "weather": list(base_profile["weather"]),
            "style_tags": list(base_profile["style_tags"]),
            "formality": list(base_profile["formality"]),
            "prefer_layer": base_profile["prefer_layer"],
        }
    else:
        profile = {
            "weather": ["mild", "indoor"],
            "style_tags": ["neutral", "practical"],
            "formality": ["casual", "smart-casual"],
            "prefer_layer": False,
        }

    def add_unique(field_name: str, values: list[str]) -> None:
        for value in values:
            if value not in profile[field_name]:
                profile[field_name].append(value)

    if not custom_text:
        return profile

    if "rain" in custom_text or "rainy" in custom_text:
        add_unique("weather", ["rainy"])
        profile["prefer_layer"] = True

    if "cold" in custom_text or "winter" in custom_text:
        add_unique("weather", ["cold"])
        profile["prefer_layer"] = True

    if "hot" in custom_text or "warm" in custom_text or "summer" in custom_text:
        add_unique("weather", ["warm"])

    if "spring" in custom_text or "autumn" in custom_text or "fall" in custom_text:
        add_unique("weather", ["mild"])

    if "office" in custom_text or "work" in custom_text:
        add_unique("style_tags", ["office-friendly", "practical"])
        add_unique("formality", ["office"])

    if "date" in custom_text or "dinner" in custom_text:
        add_unique("style_tags", ["romantic", "date-night"])
        add_unique("formality", ["smart-casual"])

    if (
        "travel" in custom_text
        or "walking" in custom_text
        or "flight" in custom_text
        or "plane" in custom_text
        or "airport" in custom_text
        or "long-haul" in custom_text
    ):
        add_unique("style_tags", ["travel-friendly", "practical", "cozy"])
        add_unique("weather", ["travel", "indoor"])
        profile["prefer_layer"] = True

    if (
        "temperature change" in custom_text
        or "climate change" in custom_text
        or "from hot" in custom_text
        or "to cold" in custom_text
        or "layers" in custom_text
    ):
        add_unique("style_tags", ["travel-friendly", "practical"])
        add_unique("weather", ["warm", "cold", "travel"])
        profile["prefer_layer"] = True

    return profile


def score_item(
    item: dict,
    selected_vibes: list[str],
    scenario_profile: dict,
    comfort_preference: str,
) -> int:
    """Give points to one wardrobe item based on style, weather, comfort and formality."""
    score = 0

    item_style_tags = item.get("style_tags", [])
    item_weather = item.get("weather", [])
    item_formality = item.get("formality", "")
    item_comfort = item.get("comfort", "")
    item_is_favorite = bool(item.get("favorite", False))

    for vibe in selected_vibes:
        if vibe in item_style_tags:
            score += 4

    for scenario_tag in scenario_profile["style_tags"]:
        if scenario_tag in item_style_tags:
            score += 3

    for weather_tag in scenario_profile["weather"]:
        if weather_tag in item_weather:
            score += 3

    if item_formality in scenario_profile["formality"]:
        score += 2

    if comfort_preference == "High comfort preferred" and item_comfort == "high":
        score += 3
    elif comfort_preference == "Medium comfort is okay" and item_comfort in ["high", "medium"]:
        score += 2
    elif comfort_preference == "No comfort preference":
        score += 1

    if item_is_favorite:
        score += 2

    return score


def get_items_by_category(wardrobe: list[dict], category: str) -> list[dict]:
    """Return all items from one category."""
    return [item for item in wardrobe if item.get("category") == category]


def choose_best_item(
    items: list[dict],
    selected_vibes: list[str],
    scenario_profile: dict,
    comfort_preference: str,
    excluded_ids: set[str] | None = None,
) -> dict | None:
    """Choose the highest-scoring item from a list."""
    if excluded_ids is None:
        excluded_ids = set()

    available_items = [
        item for item in items if item.get("id", "") not in excluded_ids
    ]

    if not available_items:
        return None

    return max(
        available_items,
        key=lambda item: score_item(
            item,
            selected_vibes,
            scenario_profile,
            comfort_preference,
        ),
    )


def should_use_dress(
    dress: dict | None,
    top: dict | None,
    bottom: dict | None,
    scenario: str,
) -> bool:
    """Decide whether the outfit should use a dress instead of top + bottom."""
    if not dress:
        return False

    if not top or not bottom:
        return True

    if scenario == "Date night":
        return True

    return False


def build_outfit(
    wardrobe: list[dict],
    scenario: str,
    custom_scenario: str,
    selected_vibes: list[str],
    comfort_preference: str,
    excluded_ids: set[str] | None = None,
) -> dict:
    """Build one outfit from available wardrobe items."""
    if excluded_ids is None:
        excluded_ids = set()

    scenario_profile = get_scenario_profile(scenario, custom_scenario)

    tops = get_items_by_category(wardrobe, "top")
    bottoms = get_items_by_category(wardrobe, "bottom")
    dresses = get_items_by_category(wardrobe, "dress")
    jackets = get_items_by_category(wardrobe, "jacket")
    shoes = get_items_by_category(wardrobe, "shoes")
    accessories = get_items_by_category(wardrobe, "accessory")

    best_top = choose_best_item(
        tops, selected_vibes, scenario_profile, comfort_preference, excluded_ids
    )
    best_bottom = choose_best_item(
        bottoms, selected_vibes, scenario_profile, comfort_preference, excluded_ids
    )
    best_dress = choose_best_item(
        dresses, selected_vibes, scenario_profile, comfort_preference, excluded_ids
    )
    best_jacket = choose_best_item(
        jackets, selected_vibes, scenario_profile, comfort_preference, excluded_ids
    )
    best_shoes = choose_best_item(
        shoes, selected_vibes, scenario_profile, comfort_preference, excluded_ids
    )
    best_accessory = choose_best_item(
        accessories, selected_vibes, scenario_profile, comfort_preference, excluded_ids
    )

    outfit = {}

    if should_use_dress(best_dress, best_top, best_bottom, scenario):
        outfit["Dress"] = best_dress
    else:
        outfit["Top"] = best_top
        outfit["Bottom"] = best_bottom

    if scenario_profile["prefer_layer"] and best_jacket:
        outfit["Layer"] = best_jacket

    if best_shoes:
        outfit["Shoes"] = best_shoes

    if best_accessory:
        outfit["Accessory"] = best_accessory

    return outfit


def get_outfit_item_ids(outfit: dict) -> set[str]:
    """Collect item IDs used in an outfit."""
    return {
        get_item_id(item)
        for item in outfit.values()
        if item is not None
    }


def create_explanation(
    scenario: str,
    custom_scenario: str,
    selected_vibes: list[str],
    comfort_preference: str,
) -> str:
    """Create a simple rule-based explanation for the recommendation."""
    if scenario == "Custom scenario":
        scenario_text = custom_scenario or "custom scenario"
    elif custom_scenario:
        scenario_text = f"{scenario}. Extra context: {custom_scenario}"
    else:
        scenario_text = scenario

    vibes_text = ", ".join(selected_vibes) if selected_vibes else "balanced practical style"

    return (
        f"This recommendation is built for: {scenario_text}. "
        f"It prioritizes {vibes_text}, useful wardrobe categories, and the selected comfort preference: "
        f"{comfort_preference}. The outfit is generated with rule-based matching, so it works without an AI API."
    )


def recommend_outfits(
    wardrobe: list[dict],
    scenario: str,
    custom_scenario: str,
    selected_vibes: list[str],
    comfort_preference: str,
) -> dict:
    """Return a main outfit, an alternative outfit and a short explanation."""
    main_outfit = build_outfit(
        wardrobe,
        scenario,
        custom_scenario,
        selected_vibes,
        comfort_preference,
    )

    main_item_ids = get_outfit_item_ids(main_outfit)

    alternative_outfit = build_outfit(
        wardrobe,
        scenario,
        custom_scenario,
        selected_vibes,
        comfort_preference,
        excluded_ids=main_item_ids,
    )

    explanation = create_explanation(
        scenario,
        custom_scenario,
        selected_vibes,
        comfort_preference,
    )

    return {
        "main_outfit": main_outfit,
        "alternative_outfit": alternative_outfit,
        "explanation": explanation,
    }
