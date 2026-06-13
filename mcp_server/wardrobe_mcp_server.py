from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("Wardrobe Wizard MCP")


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WARDROBE_PATH = PROJECT_ROOT / "data" / "wardrobe.json"

SENSITIVE_PATTERNS = {
    "identity recognition": [
        r"\bthis is\b",
        r"\bi recognize\b",
        r"\bthe person is\b",
        r"\blooks like [A-Z][a-z]+\b",
    ],
    "body or attractiveness comment": [
        r"\battractive\b",
        r"\bbeautiful body\b",
        r"\bbody shape\b",
        r"\bslim\b",
        r"\boverweight\b",
        r"\bskinny\b",
        r"\bsexy\b",
        r"\bhot\b",
    ],
    "sensitive personal inference": [
        r"\bage\b",
        r"\bethnicity\b",
        r"\brace\b",
        r"\bgender\b",
        r"\bdisabled\b",
        r"\bdisability\b",
        r"\bhealth condition\b",
        r"\bpregnant\b",
        r"\breligion\b",
        r"\bincome\b",
        r"\bprofession\b",
    ],
}


CATEGORY_TARGETS = {
    "top": 4,
    "bottom": 4,
    "dress": 3,
    "jacket": 3,
    "shoes": 3,
    "accessory": 3,
}


STYLE_TARGETS = {
    "casual": 4,
    "office-friendly": 3,
    "elegant": 3,
    "travel-friendly": 3,
    "practical": 3,
    "cozy": 2,
}


def load_wardrobe(path: str | None = None) -> list[dict[str, Any]]:
    wardrobe_path = Path(path) if path else DEFAULT_WARDROBE_PATH

    if not wardrobe_path.is_absolute():
        wardrobe_path = PROJECT_ROOT / wardrobe_path

    with wardrobe_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Wardrobe data must be a JSON list.")

    return data


def safe_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if value:
        return [str(value).strip()]

    return []


def count_categories(wardrobe: list[dict[str, Any]]) -> Counter:
    return Counter(str(item.get("category", "unknown")) for item in wardrobe)


def count_style_tags(wardrobe: list[dict[str, Any]]) -> Counter:
    counter = Counter()

    for item in wardrobe:
        for tag in safe_list(item.get("style_tags", [])):
            counter[tag] += 1

    return counter


def create_gap_recommendation(label: str, current: int, target: int) -> str:
    missing = target - current

    if missing <= 0:
        return f"{label}: enough coverage for the current demo wardrobe."

    if missing == 1:
        return f"{label}: consider adding 1 versatile sample item later, only if it improves demo clarity."

    return f"{label}: consider adding {missing} versatile sample items later, but avoid unnecessary shopping logic."


@mcp.tool()
def closet_gap_detector(wardrobe_path: str = "data/wardrobe.json") -> dict[str, Any]:
    """Detect simple category and style gaps in the sample wardrobe."""
    wardrobe = load_wardrobe(wardrobe_path)
    category_counts = count_categories(wardrobe)
    style_counts = count_style_tags(wardrobe)

    category_gaps = []
    style_gaps = []

    for category, target in CATEGORY_TARGETS.items():
        current = category_counts.get(category, 0)

        if current < target:
            category_gaps.append(
                {
                    "category": category,
                    "current_count": current,
                    "target_count": target,
                    "recommendation": create_gap_recommendation(category, current, target),
                }
            )

    for style_tag, target in STYLE_TARGETS.items():
        current = style_counts.get(style_tag, 0)

        if current < target:
            style_gaps.append(
                {
                    "style_tag": style_tag,
                    "current_count": current,
                    "target_count": target,
                    "recommendation": create_gap_recommendation(style_tag, current, target),
                }
            )

    return {
        "tool": "closet_gap_detector",
        "total_items": len(wardrobe),
        "category_counts": dict(category_counts),
        "style_tag_counts": dict(style_counts),
        "category_gaps": category_gaps,
        "style_gaps": style_gaps,
        "sustainability_note": (
            "This tool looks for demo coverage, not shopping pressure. "
            "The safest recommendation is to remix existing wardrobe items before suggesting new purchases."
        ),
    }


@mcp.tool()
def privacy_safety_auditor(ai_output_text: str) -> dict[str, Any]:
    """Check wardrobe assistant text for unsafe personal or body-related claims."""
    findings = []
    lowered_text = ai_output_text.lower()

    for rule_name, patterns in SENSITIVE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, ai_output_text, flags=re.IGNORECASE):
                findings.append(
                    {
                        "rule": rule_name,
                        "matched_pattern": pattern,
                    }
                )

    if findings:
        safe_rewrite = (
            "I can help with visible clothing only: colors, layers, formality, "
            "comfort, weather fit, and occasion fit. I will not identify the "
            "person or infer body, health, identity, or other sensitive traits."
        )
    else:
        safe_rewrite = ai_output_text

    return {
        "tool": "privacy_safety_auditor",
        "is_safe": len(findings) == 0,
        "finding_count": len(findings),
        "findings": findings,
        "safe_rewrite": safe_rewrite.strip(),
        "project_rule": (
            "Wardrobe Wizard should analyze clothing only and avoid identity, body, "
            "attractiveness, age, gender, ethnicity, health, disability, or other sensitive inferences."
        ),
    }


@mcp.tool()
def outfit_debug_report(
    outfit_description: str,
    scenario: str = "everyday use",
    low_energy_mode: bool = True,
) -> dict[str, Any]:
    """Debug an outfit description like code and suggest the smallest safe swap."""
    text = outfit_description.lower()
    issues = []

    if "rain" in scenario.lower() and not any(word in text for word in ["jacket", "coat", "boots", "umbrella", "waterproof"]):
        issues.append("Rain scenario detected, but no clear rain-safe layer or footwear was mentioned.")

    if "office" in scenario.lower() and any(word in text for word in ["flip flop", "hoodie", "gym", "beach"]):
        issues.append("Office scenario detected, but one item may be too casual for work context.")

    if "travel" in scenario.lower() and any(word in text for word in ["heels", "tight", "delicate"]):
        issues.append("Travel scenario detected, but one item may reduce comfort during movement.")

    if "date" in scenario.lower() and not any(word in text for word in ["dress", "elegant", "blazer", "skirt", "nice", "soft"]):
        issues.append("Date scenario detected, but the outfit may need one more intentional or polished element.")

    if not issues:
        issues.append("No major outfit bug detected. The outfit sounds usable for the stated scenario.")

    smallest_swap = "Keep the outfit, but adjust one item only: choose the shoes or outer layer that best matches the scenario."

    if "rain" in scenario.lower():
        smallest_swap = "Smallest safe swap: add a rain-friendly jacket or waterproof shoes."
    elif "office" in scenario.lower():
        smallest_swap = "Smallest safe swap: replace the most casual item with a blazer, smart shoes, or a cleaner neutral layer."
    elif "travel" in scenario.lower():
        smallest_swap = "Smallest safe swap: choose the most comfortable shoes and keep the rest unchanged."
    elif "date" in scenario.lower():
        smallest_swap = "Smallest safe swap: add one polished accessory or a softer elegant layer."

    low_energy_choice = smallest_swap if low_energy_mode else "Low-energy mode was not requested."

    return {
        "tool": "outfit_debug_report",
        "signature": "Debug your outfit like code.",
        "scenario": scenario,
        "main_issue": issues[0],
        "all_detected_issues": issues,
        "smallest_safe_swap": smallest_swap,
        "low_energy_choice": low_energy_choice,
        "reassurance": "You do not need to rebuild the whole outfit. One small change is enough.",
    }


if __name__ == "__main__":
    mcp.run()