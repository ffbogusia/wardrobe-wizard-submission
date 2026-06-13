"""Rewear impact client for Wardrobe Wizard.

The app calls the TypeScript Rewear Impact mini API when IMPACT_API_URL is set.
If the API is unavailable, it falls back to local educational estimates.
"""

from __future__ import annotations

import json
import os
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen


IMPACT_ESTIMATES = {
    "top": {
        "waterLiters": 2700,
        "co2eKg": 4.3,
        "confidence": "public-source-benchmark",
    },
    "bottom": {
        "waterLiters": 3781,
        "co2eKg": 33.4,
        "confidence": "public-source-benchmark",
    },
    "dress": {
        "waterLiters": 3000,
        "co2eKg": 8.0,
        "confidence": "illustrative-category-estimate",
    },
    "jacket": {
        "waterLiters": 4000,
        "co2eKg": 15.0,
        "confidence": "illustrative-category-estimate",
    },
    "shoes": {
        "waterLiters": 2500,
        "co2eKg": 14.0,
        "confidence": "illustrative-category-estimate",
    },
    "accessory": {
        "waterLiters": 500,
        "co2eKg": 2.0,
        "confidence": "illustrative-category-estimate",
    },
}


CATEGORY_ALIASES = {
    "tops": "top",
    "shirt": "top",
    "t-shirt": "top",
    "tshirt": "top",
    "sweater": "top",
    "knit": "top",
    "pants": "bottom",
    "jeans": "bottom",
    "trousers": "bottom",
    "skirt": "bottom",
    "coat": "jacket",
    "blazer": "jacket",
    "cardigan": "jacket",
    "boots": "shoes",
    "sneakers": "shoes",
    "slippers": "shoes",
    "bag": "accessory",
    "scarf": "accessory",
    "necklace": "accessory",
}


def normalize_category(category: object) -> str:
    """Normalize wardrobe categories for impact estimates."""
    if not isinstance(category, str):
        return "accessory"

    cleaned = category.strip().lower().replace("_", "-")

    if cleaned in IMPACT_ESTIMATES:
        return cleaned

    return CATEGORY_ALIASES.get(cleaned, "accessory")


def round_one_decimal(value: float) -> float:
    """Round a number to one decimal place."""
    return round(value, 1)


def calculate_local_rewear_impact(items: list[dict]) -> dict:
    """Calculate local educational no-buy impact estimates."""
    safe_items = items if isinstance(items, list) else []

    item_impacts = []

    for item in safe_items:
        category = normalize_category(item.get("category"))
        estimate = IMPACT_ESTIMATES[category]

        item_impacts.append(
            {
                "id": item.get("id"),
                "name": item.get("name", "Unnamed wardrobe item"),
                "category": category,
                "favorite": bool(item.get("favorite", False)),
                "estimatedWaterLiters": estimate["waterLiters"],
                "estimatedCo2eKg": estimate["co2eKg"],
                "confidence": estimate["confidence"],
            }
        )

    water_liters = sum(item["estimatedWaterLiters"] for item in item_impacts)
    co2e_kg = sum(item["estimatedCo2eKg"] for item in item_impacts)
    favorite_items_used = len([item for item in item_impacts if item["favorite"]])

    return {
        "mode": "local Python fallback estimate",
        "impactKind": "estimated new-production impact avoided",
        "summary": {
            "itemsReused": len(item_impacts),
            "favoriteItemsUsed": favorite_items_used,
            "waterLiters": water_liters,
            "co2eKg": round_one_decimal(co2e_kg),
        },
        "spell": (
            "Rewear spell unlocked: you built a look from clothes already "
            "in the wardrobe."
        ),
        "noBuyMessage": (
            "This is a no-buy comparison estimate. It shows the potential "
            "impact of rewearing existing items instead of buying similar new ones."
        ),
        "disclaimer": (
            "This is not a certified carbon or water calculator. It uses simplified "
            "category-level estimates for education and demo storytelling."
        ),
        "itemImpacts": item_impacts,
    }


def calculate_rewear_impact(items: list[dict]) -> dict:
    """Call the mini API or fall back to local estimates."""
    api_url = os.getenv("IMPACT_API_URL", "").strip()

    if not api_url:
        return calculate_local_rewear_impact(items)

    endpoint = api_url.rstrip("/") + "/api/rewear-impact"
    payload = json.dumps({"items": items}).encode("utf-8")

    request = Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=5) as response:
            response_body = response.read().decode("utf-8")
            api_result = json.loads(response_body)
            api_result["mode"] = "mini API estimate"
            return api_result
    except (URLError, HTTPError, TimeoutError, json.JSONDecodeError):
        fallback_result = calculate_local_rewear_impact(items)
        fallback_result["mode"] = "local fallback estimate because mini API was unavailable"
        return fallback_result