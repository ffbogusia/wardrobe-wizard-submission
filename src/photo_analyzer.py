import base64
import json
import os
import re
from typing import Any, Dict, List

import requests


GITHUB_MODELS_ENDPOINT = "https://models.github.ai/inference/chat/completions"

DEFAULT_VISION_MODEL = os.getenv(
    "GITHUB_VISION_MODEL_NAME",
    os.getenv("GITHUB_MODEL_NAME", "openai/gpt-4o-mini"),
)


AI_SAFETY_SCOPE = """
Wardrobe Wizard follows the safety principles documented in:
docs/ai_safety_and_privacy.md

The photo analyzer must:
- analyze visible clothing only,
- avoid identifying people,
- avoid face recognition,
- avoid body comments,
- avoid attractiveness judgments,
- avoid age, gender, ethnicity, disability, health, or identity inference,
- avoid emotional-state or social-status guesses,
- return practical clothing metadata only.
""".strip()


def analyze_outfit_photo(uploaded_file: Any) -> Dict[str, Any]:
    """
    Analyze one uploaded outfit photo using GitHub Models.

    This function is intentionally defensive:
    - no token = safe fallback
    - invalid JSON = safe fallback
    - API error = safe fallback
    - no permanent image storage
    - clothing-only analysis scope
    """

    if uploaded_file is None:
        return _fallback_result("No image was uploaded.")

    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")

    if not token:
        return _fallback_result(
            "Photo analysis is unavailable because no GitHub Models token was found."
        )

    try:
        image_bytes = uploaded_file.getvalue()
        mime_type = _get_mime_type(uploaded_file)
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        payload = {
            "model": DEFAULT_VISION_MODEL,
            "temperature": 0.2,
            "max_tokens": 800,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Wardrobe Wizard, a safe and practical wardrobe assistant. "
                        f"{AI_SAFETY_SCOPE} "
                        "Return strict JSON only. Do not use Markdown or code fences."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": _build_photo_prompt(),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            },
                        },
                    ],
                },
            ],
        }

        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        }

        response = requests.post(
            GITHUB_MODELS_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=45,
        )

        response.raise_for_status()

        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]

        parsed = _parse_json_response(content)
        return _normalize_photo_result(parsed)

    except Exception as exc:
        return _fallback_result(
            f"Photo analysis failed safely. Technical reason: {str(exc)}"
        )


def _build_photo_prompt() -> str:
    return """
Analyze this outfit photo for a wardrobe recommendation app.

Safety rules:
- Analyze visible clothing only.
- Do not identify the person.
- Do not describe face, body shape, attractiveness, age, gender, ethnicity, disability, health, or identity.
- Do not guess emotional state, income level, profession, or social status.
- If something is uncertain, use cautious language such as "possibly", "unclear", or "appears to be".
- Return strict JSON only.
- Do not use Markdown.
- Do not use code fences.

Return exactly this JSON structure:

{
  "outfit_summary": "Short practical summary of the visible outfit.",
  "detected_items": [
    {
      "name": "short item name",
      "category": "top | bottom | shoes | outerwear | dress | accessory | bag | other",
      "color": "main visible color",
      "style_tags": ["casual", "minimal", "smart", "sporty"],
      "season": ["spring", "summer", "autumn", "winter"],
      "formality": "casual | smart casual | business casual | formal",
      "comfort": "low | medium | high",
      "weather": ["indoor", "warm", "cold", "rainy", "windy", "travel"],
      "notes": "Short note about the item and how it could be used."
    }
  ],
  "best_occasions": ["occasion 1", "occasion 2", "occasion 3"],
  "occasion_explanation": "Explain why these occasions fit the outfit."
}
""".strip()


def _get_mime_type(uploaded_file: Any) -> str:
    file_type = getattr(uploaded_file, "type", None)
    file_name = getattr(uploaded_file, "name", "").lower()

    if file_type in {"image/jpeg", "image/png", "image/jpg"}:
        if file_type == "image/jpg":
            return "image/jpeg"
        return file_type

    if file_name.endswith(".png"):
        return "image/png"

    return "image/jpeg"


def _parse_json_response(content: str) -> Dict[str, Any]:
    cleaned = content.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")

    if first_brace == -1 or last_brace == -1:
        raise ValueError("Model response did not contain JSON.")

    json_text = cleaned[first_brace : last_brace + 1]
    return json.loads(json_text)


def _normalize_photo_result(data: Dict[str, Any]) -> Dict[str, Any]:
    detected_items = data.get("detected_items", [])

    if not isinstance(detected_items, list):
        detected_items = []

    normalized_items = []

    for item in detected_items:
        if isinstance(item, dict):
            normalized_items.append(_normalize_item(item))

    best_occasions = data.get("best_occasions", [])

    if not isinstance(best_occasions, list):
        best_occasions = []

    return {
        "analysis_ok": True,
        "error_message": "",
        "outfit_summary": str(data.get("outfit_summary", "")).strip(),
        "detected_items": normalized_items,
        "best_occasions": [str(occasion).strip() for occasion in best_occasions],
        "occasion_explanation": str(data.get("occasion_explanation", "")).strip(),
    }


def _normalize_item(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": str(item.get("name", "Detected clothing item")).strip(),
        "category": _safe_single_value(
            item.get("category"),
            allowed_values=[
                "top",
                "bottom",
                "shoes",
                "outerwear",
                "dress",
                "accessory",
                "bag",
                "other",
            ],
            fallback="other",
        ),
        "color": str(item.get("color", "unknown")).strip(),
        "style_tags": _safe_list(item.get("style_tags")),
        "season": _safe_list(item.get("season")),
        "formality": _safe_single_value(
            item.get("formality"),
            allowed_values=[
                "casual",
                "smart casual",
                "business casual",
                "formal",
            ],
            fallback="casual",
        ),
        "comfort": _safe_single_value(
            item.get("comfort"),
            allowed_values=["low", "medium", "high"],
            fallback="medium",
        ),
        "weather": _safe_list(item.get("weather")),
        "notes": str(item.get("notes", "")).strip(),
    }


def _safe_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, str) and value.strip():
        return [value.strip()]

    return []


def _safe_single_value(value: Any, allowed_values: List[str], fallback: str) -> str:
    if not isinstance(value, str):
        return fallback

    cleaned = value.strip().lower()

    if cleaned in allowed_values:
        return cleaned

    return fallback


def _fallback_result(message: str) -> Dict[str, Any]:
    return {
        "analysis_ok": False,
        "error_message": message,
        "outfit_summary": "Photo analysis is currently unavailable.",
        "detected_items": [],
        "best_occasions": [],
        "occasion_explanation": (
            "The app is still safe to use. You can continue with manual wardrobe items "
            "and rule-based outfit recommendations."
        ),
    }
