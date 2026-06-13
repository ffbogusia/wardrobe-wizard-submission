"""Simple parser for Wardrobe Wizard clothing items."""

from __future__ import annotations

import re


CATEGORIES = {
    "shoes": [
        "shoes",
        "sneakers",
        "boots",
        "loafers",
        "sandals",
        "heels",
        "slippers",
        "slipper",
        "flip-flops",
        "flip flops",
        "flats",
    ],
    "other": [
        "underwear",
        "underpants",
        "briefs",
        "panties",
        "bra",
        "bralette",
        "lingerie",
        "socks",
        "tights",
        "stockings",
        "swimsuit",
        "bodysuit",
    ],
    "dress": ["dress", "jumpsuit", "one-piece"],
    "bottom": ["jeans", "trousers", "pants", "skirt", "shorts", "leggings"],
    "jacket": ["jacket", "coat", "blazer", "cardigan", "trench", "bomber"],
    "accessory": ["bag", "scarf", "belt", "earrings", "cap", "hat", "necklace"],
    "top": ["top", "shirt", "t-shirt", "tee", "blouse", "sweater", "knit", "hoodie"],
}

COLORS = [
    "black",
    "white",
    "grey",
    "gray",
    "beige",
    "brown",
    "blue",
    "navy",
    "green",
    "red",
    "pink",
    "purple",
    "yellow",
    "orange",
    "cream",
    "silver",
    "gold",
]

STYLE_TAGS = [
    "neutral",
    "feminine",
    "masculine",
    "streetwear",
    "elegant",
    "casual",
    "cozy",
    "office-friendly",
    "romantic",
    "minimalist",
    "sporty",
    "travel-friendly",
    "classic",
    "practical",
    "date-night",
]

SEASONS = ["spring", "summer", "autumn", "winter", "all-season"]

WEATHER_TAGS = [
    "warm",
    "mild",
    "cold",
    "rainy",
    "windy",
    "indoor",
    "travel",
]

FORMALITY_KEYWORDS = {
    "office": ["office", "work", "business"],
    "elegant": ["elegant", "formal", "party", "wedding"],
    "smart-casual": ["smart-casual", "smart casual", "date", "dinner", "polished"],
    "casual": ["casual", "everyday", "relaxed", "streetwear", "travel"],
}

COMFORT_LEVELS = ["high", "medium", "low"]

STYLE_NORMALIZATION_HINTS = {
    "stylish": ["elegant", "classic"],
    "classy": ["classic", "elegant"],
    "put together": ["classic", "elegant"],
    "polished": ["elegant", "classic"],
    "cute": ["cozy", "romantic"],
    "soft girl": ["feminine", "romantic", "cozy"],
    "princess": ["feminine", "romantic"],
    "airport princess": ["travel-friendly", "practical", "cozy"],
    "airport outfit": ["travel-friendly", "practical", "cozy"],
    "airport": ["travel-friendly", "practical"],
    "plane": ["travel-friendly", "practical"],
    "flight": ["travel-friendly", "practical"],
    "long-haul": ["travel-friendly", "practical", "cozy"],
    "travel": ["travel-friendly", "practical"],
    "lolita": ["romantic", "feminine"],
    "lolita-inspired": ["romantic", "feminine"],
    "kawaii": ["romantic", "feminine"],
    "concert tee": ["casual", "streetwear"],
    "band tee": ["casual", "streetwear"],
    "iron maiden": ["casual", "streetwear"],
    "concert": ["casual", "streetwear"],
    "goth": ["streetwear", "date-night"],
    "gothic": ["streetwear", "date-night"],
    "edgy": ["streetwear", "date-night"],
    "preppy": ["classic", "office-friendly"],
    "business casual": ["office-friendly", "classic"],
    "date night": ["date-night", "romantic"],
    "date-night": ["date-night", "romantic"],
    "sexy": ["date-night", "elegant"],
}

WEATHER_NORMALIZATION_HINTS = {
    "airport": ["travel", "indoor"],
    "plane": ["travel", "indoor"],
    "flight": ["travel", "indoor"],
    "long-haul": ["travel", "indoor"],
    "travel": ["travel", "indoor"],
    "home": ["indoor"],
    "indoors": ["indoor"],
    "house": ["indoor"],
    "rainproof": ["rainy"],
    "waterproof": ["rainy"],
    "wet weather": ["rainy"],
    "chilly": ["cold"],
    "freezing": ["cold"],
    "snow": ["cold"],
    "hot": ["warm"],
    "sunny": ["warm"],
}

SEASON_NORMALIZATION_HINTS = {
    "fall": ["autumn"],
    "year round": ["all-season"],
    "year-round": ["all-season"],
    "all year": ["all-season"],
    "all season": ["all-season"],
}

NOTE_PHRASES = [
    "lolita",
    "lolita-inspired",
    "kawaii",
    "airport princess",
    "concert tee",
    "band tee",
    "iron maiden",
    "goth",
    "gothic",
    "edgy",
    "preppy",
    "favorite",
    "very me",
]


def add_unique(target: list[str], values: list[str]) -> None:
    """Append values without duplicates."""
    for value in values:
        if value not in target:
            target.append(value)


def find_first_match(text: str, options: list[str], default: str) -> str:
    """Return the first option found in text, otherwise return a default value."""
    for option in options:
        if option in text:
            return option

    return default


def contains_keyword(text: str, keyword: str) -> bool:
    """Match a category keyword as a complete phrase, not inside another word."""
    pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"
    return re.search(pattern, text) is not None


def detect_category(text: str) -> str:
    """Detect a controlled category or return other when no category is clear."""
    normalized_text = text.strip().lower()

    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if contains_keyword(normalized_text, keyword):
                return category

    return "other"


def collect_normalized_matches(
    text: str,
    phrase_map: dict[str, list[str]],
) -> tuple[list[str], list[str]]:
    """Return controlled values and human-readable parser hints from phrase mappings."""
    detected_values = []
    parser_hints = []

    for phrase, mapped_values in phrase_map.items():
        if phrase in text:
            add_unique(detected_values, mapped_values)
            parser_hints.append(f"{phrase} → {', '.join(mapped_values)}")

    return detected_values, parser_hints


def detect_style_tags(text: str) -> tuple[list[str], list[str]]:
    """Detect controlled style tags from direct tags and normalized custom phrases."""
    detected_tags = []
    parser_hints = []

    for tag in STYLE_TAGS:
        if tag in text:
            add_unique(detected_tags, [tag])

    normalized_tags, normalized_hints = collect_normalized_matches(
        text,
        STYLE_NORMALIZATION_HINTS,
    )

    add_unique(detected_tags, normalized_tags)
    parser_hints.extend(normalized_hints)

    if not detected_tags:
        detected_tags.append("neutral")

    return detected_tags[:4], parser_hints


def detect_seasons(text: str) -> list[str]:
    """Detect seasons from a description."""
    detected_seasons = []

    for season in SEASONS:
        if season in text:
            add_unique(detected_seasons, [season])

    normalized_seasons, _ = collect_normalized_matches(
        text,
        SEASON_NORMALIZATION_HINTS,
    )

    add_unique(detected_seasons, normalized_seasons)

    if not detected_seasons:
        detected_seasons.append("all-season")

    return detected_seasons


def detect_weather(text: str) -> list[str]:
    """Detect controlled weather/context tags from direct tags and normalized phrases."""
    detected_weather = []

    for weather in WEATHER_TAGS:
        if weather in text:
            add_unique(detected_weather, [weather])

    normalized_weather, _ = collect_normalized_matches(
        text,
        WEATHER_NORMALIZATION_HINTS,
    )

    add_unique(detected_weather, normalized_weather)

    if not detected_weather:
        detected_weather.append("indoor")

    return detected_weather


def detect_formality(text: str) -> str:
    """Detect formality from a description."""
    for formality, keywords in FORMALITY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return formality

    return "casual"


def detect_comfort(text: str) -> str:
    """Detect comfort level from a description."""
    if (
        "high comfort" in text
        or "comfortable" in text
        or "comfy" in text
        or "soft" in text
        or "cozy" in text
    ):
        return "high"

    if "medium comfort" in text:
        return "medium"

    if "low comfort" in text:
        return "low"

    return "medium"


def clean_item_name(description: str) -> str:
    """Create a readable item name from the user description."""
    first_part = description.split(",")[0].strip()

    if not first_part:
        return "Custom wardrobe item"

    return first_part[:80]


def build_notes(cleaned_description: str, text: str, parser_hints: list[str]) -> str:
    """Keep the original user description and add gentle normalization hints."""
    notes = cleaned_description

    personal_phrases = [
        phrase
        for phrase in NOTE_PHRASES
        if phrase in text and phrase not in cleaned_description.lower()
    ]

    if personal_phrases:
        notes += " | Personal description: " + ", ".join(personal_phrases)

    if parser_hints:
        notes += " | Parser hints: " + "; ".join(parser_hints[:4])

    return notes


def parse_item_description(description: str, item_id: str) -> dict:
    """Parse one clothing item description into wardrobe item data."""
    cleaned_description = description.strip()
    text = cleaned_description.lower()

    color = find_first_match(text, COLORS, "unknown")
    category = detect_category(text)
    style_tags, parser_hints = detect_style_tags(text)
    season = detect_seasons(text)
    weather = detect_weather(text)
    formality = detect_formality(text)
    comfort = detect_comfort(text)

    return {
        "id": item_id,
        "name": clean_item_name(cleaned_description),
        "category": category,
        "color": color,
        "style_tags": style_tags,
        "season": season,
        "formality": formality,
        "comfort": comfort,
        "weather": weather,
        "notes": build_notes(cleaned_description, text, parser_hints),
    }


def parse_multiple_item_descriptions(text: str, start_number: int) -> list[dict]:
    """Parse multiple item descriptions, one item per line."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    parsed_items = []

    for index, line in enumerate(lines, start=start_number):
        item_id = f"custom_{index:03d}"
        parsed_items.append(parse_item_description(line, item_id))

    return parsed_items