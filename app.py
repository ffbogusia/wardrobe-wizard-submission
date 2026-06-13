from collections import Counter
from pathlib import Path
import base64
import json
import re

import pandas as pd
import streamlit as st

from src.ai_client import generate_outfit_explanation
from src.item_parser import (
    detect_category,
    parse_item_description,
    parse_multiple_item_descriptions,
)
from src.photo_analyzer import analyze_outfit_photo
from src.recommendation_engine import recommend_outfits
from src.corgi_mascot import get_corgi_mascot_html
from src.impact_client import calculate_rewear_impact


DATA_PATH = Path("data/wardrobe.json")
HERO_IMAGE_PATH = Path("assets/corgi-wizard.png")

CATEGORY_OPTIONS = [
    "top",
    "bottom",
    "dress",
    "jacket",
    "shoes",
    "accessory",
    "other",
]

STYLE_TAG_OPTIONS = [
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

STYLE_VIBES = STYLE_TAG_OPTIONS

SEASON_OPTIONS = [
    "spring",
    "summer",
    "autumn",
    "winter",
    "all-season",
]

WEATHER_OPTIONS = [
    "warm",
    "mild",
    "cold",
    "rainy",
    "windy",
    "indoor",
    "travel",
]

FORMALITY_OPTIONS = [
    "casual",
    "office",
    "smart-casual",
    "elegant",
]

COMFORT_OPTIONS = [
    "low",
    "medium",
    "high",
]

CATEGORY_ALIASES = {
    "outerwear": "jacket",
    "coat": "jacket",
    "blazer": "jacket",
    "bag": "accessory",
    "hat": "accessory",
    "scarf": "accessory",
    "underwear": "other",
    "underpants": "other",
    "briefs": "other",
    "panties": "other",
    "bra": "other",
    "bralette": "other",
    "lingerie": "other",
    "socks": "other",
    "tights": "other",
    "stockings": "other",
    "other": "other",
}

FORMALITY_ALIASES = {
    "smart casual": "smart-casual",
    "business casual": "office",
    "formal": "elegant",
}

MAIN_TAB_LABELS = [
    "Recommend Outfit",
    "View Wardrobe",
    "Add Items",
    "Analyze Outfit Photo",
    "About",
]

ADD_ITEM_TAB_LABELS = ["Add one item", "Add multiple items"]


def load_wardrobe() -> list[dict]:
    """Load the sample wardrobe dataset from a JSON file."""
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def inject_custom_css() -> None:
    """Inject a light magical pastel theme that complements the corgi wizard branding."""
    st.markdown(
        """
        <style>
        /* === Wardrobe Wizard: Magical Pastel Theme === */

        /* Soft lavender app background */
        .stApp {
            background-color: #fdf8ff;
        }

        /* Metric cards — white with purple accent */
        [data-testid="metric-container"] {
            background-color: #ffffff;
            border: 1px solid #e8d8ff;
            border-radius: 14px;
            padding: 1rem 1.25rem;
            box-shadow: 0 2px 10px rgba(124, 58, 237, 0.08);
        }

        /* Primary buttons — rounded, purple outline style */
        .stButton > button {
            border-radius: 20px;
            border: 1.5px solid #8b5cf6;
            color: #7c3aed;
            background-color: #ffffff;
            font-weight: 500;
            transition: background-color 0.2s ease,
                        color 0.2s ease,
                        box-shadow 0.2s ease;
        }
        .stButton > button:hover {
            background-color: #7c3aed;
            color: #ffffff;
            border-color: #7c3aed;
            box-shadow: 0 4px 14px rgba(124, 58, 237, 0.28);
        }
        .stButton > button:active {
            background-color: #6d28d9;
            box-shadow: none;
        }

        /* === Tabs: soft glassmorphism navigation === */

        .stTabs {
            margin-top: 1.2rem;
            position: relative;
            z-index: 20;
            padding: 0 4px;
        }

        /* Frosted-glass tab bar */
        .stTabs [data-baseweb="tab-list"] {
            position: relative;
            background: rgba(255, 255, 255, 0.80);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            border-radius: 16px;
            padding: 7px 8px;
            gap: 6px;
            box-shadow: 0 8px 28px rgba(109, 40, 217, 0.22),
                        inset 0 0 0 1.5px rgba(255, 255, 255, 0.55);
        }

        /* Inactive tabs */
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            color: #7c3aed;
            font-weight: 500;
            background-color: transparent;
            padding: 7px 16px;
            transition: background-color 0.15s ease, color 0.15s ease;
        }

        /* Hover on inactive tab */
        .stTabs [data-baseweb="tab"]:hover {
            background-color: rgba(237, 233, 254, 0.85);
            color: #6d28d9;
        }

        /* Active tab — solid white pill that clearly stands out */
        .stTabs [aria-selected="true"] {
            background-color: #ffffff !important;
            color: #6d28d9 !important;
            font-weight: 650 !important;
            box-shadow: 0 2px 10px rgba(109, 40, 217, 0.18);
        }

        @keyframes ww-header-enter {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .ww-app-header {
            position: relative;
            animation: ww-header-enter 0.32s ease-out both;
            border: 1px solid rgba(232, 216, 255, 0.95);
            border-radius: 22px;
            padding: 1.35rem 1.55rem;
            margin: 0.4rem 0 0.8rem 0;
            background:
                radial-gradient(circle at 10% 20%, rgba(250, 204, 21, 0.18), transparent 28%),
                radial-gradient(circle at 82% 10%, rgba(192, 132, 252, 0.24), transparent 30%),
                linear-gradient(135deg, rgba(255,255,255,0.94), rgba(253,242,248,0.78));
            box-shadow: 0 10px 32px rgba(124, 58, 237, 0.10);
            overflow: hidden;
        }

        .ww-app-header h1 {
            margin: 0;
            color: #4c1d95;
            font-size: clamp(2rem, 4vw, 3.2rem);
            line-height: 1.05;
            letter-spacing: -0.03em;
        }

        .ww-app-header p {
            color: #5b466e;
            font-size: 1.05rem;
            margin: 0.55rem 0 0.85rem 0;
            max-width: 760px;
        }

        .ww-header-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
        }

        .ww-header-badge {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.32rem 0.72rem;
            background: rgba(255,255,255,0.80);
            border: 1px solid rgba(196, 181, 253, 0.68);
            color: #6d28d9;
            font-size: 0.84rem;
            font-weight: 650;
        }

        /* DataFrames — soft rounded border */
        [data-testid="stDataFrame"] {
            border-radius: 10px;
            border: 1px solid #e8d8ff;
            overflow: hidden;
            box-shadow: 0 1px 6px rgba(124, 58, 237, 0.06);
        }

        /* Expanders */
        [data-testid="stExpander"] {
            border: 1px solid #e8d8ff !important;
            border-radius: 10px !important;
        }

        /* === Splash screen: floating sparkle animations === */

        @keyframes ww-sparkle {
            0%, 100% { opacity: 0.15; transform: scale(0.6) rotate(0deg); }
            50%       { opacity: 1.00; transform: scale(1.5) rotate(30deg); }
        }

        @keyframes ww-float-btn {
            0%, 100% { transform: translateY(0px);
                        box-shadow: 0 6px 28px rgba(139, 92, 246, 0.50); }
            50%       { transform: translateY(-8px);
                        box-shadow: 0 12px 40px rgba(139, 92, 246, 0.75); }
        }

        .ww-sp {
            position: absolute;
            font-size: 2rem;
            animation: ww-sparkle 2.8s ease-in-out infinite;
            pointer-events: none;
            user-select: none;
            line-height: 1;
        }

        .ww-vibe-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            align-items: center;
            margin: 0.35rem 0 0.75rem 0;
        }

        .ww-vibe-chip {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.38rem 0.78rem;
            background: linear-gradient(135deg, #f5f3ff, #fdf2f8);
            border: 1px solid #d8b4fe;
            color: #6d28d9;
            font-size: 0.9rem;
            font-weight: 650;
        }

        .ww-outfit-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 0.75rem;
            margin: 0.35rem 0 0.9rem 0;
        }

        .ww-outfit-card {
            border: 1px solid rgba(216, 180, 254, 0.72);
            border-radius: 16px;
            padding: 0.9rem 1rem;
            background: rgba(255, 255, 255, 0.86);
            box-shadow: 0 4px 16px rgba(109, 40, 217, 0.08);
        }

        .ww-outfit-role {
            color: #7c3aed;
            font-size: 0.76rem;
            font-weight: 750;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
        }

        .ww-outfit-name {
            color: #3b1b5a;
            font-size: 1.02rem;
            font-weight: 650;
            line-height: 1.25;
        }

        .ww-edit-note {
            border-left: 4px solid #a78bfa;
            background: rgba(245, 243, 255, 0.72);
            border-radius: 10px;
            padding: 0.7rem 0.85rem;
            color: #5b466e;
            margin-bottom: 0.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def _load_hero_image_b64() -> str:
    """Load and cache the hero PNG as a base64 string.

    Uses st.cache_data so the 2 MB file is read from disk only once per
    session; every subsequent Streamlit rerun reuses the cached value.
    """
    with HERO_IMAGE_PATH.open("rb") as f:
        return base64.b64encode(f.read()).decode()


def display_splash_screen() -> None:
    """Full-viewport magical splash screen.

    Overrides Streamlit container padding to achieve true full-screen display.
    The image fills 100 vh with object-fit:contain so nothing is ever cropped.
    A native st.button() is pulled up over the image via CSS :has() selector
    (supported: Chrome 105+, Firefox 121+, Safari 15.4+) — no <a href> needed,
    so the app never opens in a new window.
    """
    if not HERO_IMAGE_PATH.exists():
        st.title("✨ Wardrobe Wizard ✨")
        st.write("Magically better outfits, every day.")
        if st.button("✨ Enter the Wardrobe ✨"):
            st.session_state["app_started"] = True
            st.rerun()
        return

    hero_b64 = _load_hero_image_b64()

    # ── Splash-only CSS ──────────────────────────────────────────────────────
    st.markdown(
        """
        <style>
        /* Hide Streamlit header and footer during splash */
        [data-testid="stHeader"] { display: none !important; }
        footer                    { display: none !important; }

        /* Remove ALL container padding and width cap → true full-width/height */
        .main .block-container,
        [data-testid="stMainBlockContainer"] {
            padding: 0 !important;
            max-width: 100% !important;
        }

        /* Pull the Enter-button columns row UP over the image.
           :has() is supported Chrome 105+, Firefox 121+, Safari 15.4+.
           margin-top: -15vh puts the button 15 % from the bottom of the image. */
        [data-testid="element-container"]:has(.ww-full-splash)
            ~ [data-testid="stHorizontalBlock"] {
            position: relative;
            z-index: 300;
            margin-top: -15vh;
        }

        /* Gradient pill style for the Enter button */
        .stButton > button {
            background: linear-gradient(135deg, #8b5cf6 0%, #c026d3 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 50px !important;
            font-size: 1.3em !important;
            font-weight: 700 !important;
            padding: 18px 58px !important;
            box-shadow: 0 8px 34px rgba(139, 92, 246, 0.62) !important;
            animation: ww-float-btn 2.2s ease-in-out infinite;
            letter-spacing: 0.5px;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #7c3aed 0%, #a21caf 100%) !important;
            box-shadow: 0 12px 42px rgba(139, 92, 246, 0.80) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    # ────────────────────────────────────────────────────────────────────────

    # Full-viewport hero image with animated sparkle overlay.
    # The class "ww-full-splash" is the :has() anchor used by the CSS above.
    st.markdown(
        f'<div class="ww-full-splash" style="position:relative;width:100%;line-height:0;">'
        f'<img src="data:image/png;base64,{hero_b64}"'
        f' style="width:100%;height:100vh;object-fit:contain;'
        f'object-position:center center;background:#fdf8ff;display:block;"'
        f' alt="Wardrobe Wizard — Magically better outfits, every day" />'
        # Sparkle overlay — pointer-events:none so clicks pass through to image
        f'<div style="position:absolute;top:0;left:0;right:0;bottom:0;'
        f'pointer-events:none;overflow:hidden;">'
        f'<span class="ww-sp" style="top:5%;left:5%;animation-delay:0.0s;">✨</span>'
        f'<span class="ww-sp" style="top:10%;right:6%;animation-delay:0.9s;font-size:1.6rem;">⭐</span>'
        f'<span class="ww-sp" style="top:52%;left:3%;animation-delay:1.6s;">💫</span>'
        f'<span class="ww-sp" style="top:68%;right:4%;animation-delay:2.3s;">✨</span>'
        f'<span class="ww-sp" style="top:28%;right:3%;animation-delay:0.5s;font-size:1.5rem;">🌟</span>'
        f'<span class="ww-sp" style="top:80%;left:7%;animation-delay:1.2s;font-size:1.5rem;">⭐</span>'
        f'<span class="ww-sp" style="top:40%;left:2%;animation-delay:2.0s;font-size:1.3rem;">💫</span>'
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Native st.button() — pulled up over the image by the CSS :has() rule above
    _, btn_col, _ = st.columns([1.5, 2, 1.5])
    with btn_col:
        if st.button("✨ Enter the Wardrobe ✨", width="stretch"):
            st.session_state["app_started"] = True
            st.rerun()


def display_app_header() -> None:
    """Display a clean in-app header after the user enters the wardrobe."""
    st.markdown(
        """
        <div class="ww-app-header">
            <h1>Wardrobe Wizard ✨</h1>
            <p>
                Your calm, privacy-safe AI wardrobe assistant for outfit recommendations,
                photo-based clothing review, and low-energy decision support.
            </p>
            <div class="ww-header-badges">
                <span class="ww-header-badge">Streamlit</span>
                <span class="ww-header-badge">GitHub Models</span>
                <span class="ww-header-badge">Human review</span>
                <span class="ww-header-badge">Session-only items</span>
                <span class="ww-header-badge">AI safety</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def initialize_session_state() -> None:
    """Initialize Streamlit session state for wardrobe data and UI navigation."""
    if "wardrobe" not in st.session_state:
        st.session_state["wardrobe"] = load_wardrobe()

    defaults = {
        "last_action_message": "",
        "photo_analysis_result": None,
        "photo_analysis_file_name": "",
        "photo_items_added_for_file": "",
        "corgi_mood": "idle",
        "main_app_tab": "Recommend Outfit",
        "add_items_tab": "Add one item",
        "style_vibes_editing": True,
        "single_item_description": "",
        "multiple_item_descriptions": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def apply_pending_ui_state() -> None:
    """Apply navigation and form changes before their widgets are created."""
    next_main_tab = st.session_state.pop("next_main_tab", None)
    if next_main_tab in MAIN_TAB_LABELS:
        st.session_state["main_app_tab"] = next_main_tab

    next_add_tab = st.session_state.pop("next_add_items_tab", None)
    if next_add_tab in ADD_ITEM_TAB_LABELS:
        st.session_state["add_items_tab"] = next_add_tab

    if st.session_state.pop("clear_single_item_description", False):
        st.session_state["single_item_description"] = ""

    if st.session_state.pop("clear_multiple_item_descriptions", False):
        st.session_state["multiple_item_descriptions"] = ""


def keep_user_on_tab(main_tab: str, add_tab: str | None = None) -> None:
    """Choose the tab that should be active after the next rerun."""
    st.session_state["next_main_tab"] = main_tab
    if add_tab:
        st.session_state["next_add_items_tab"] = add_tab


def set_action_message(message: str) -> None:
    """Queue one short toast notification for the next rerun."""
    st.session_state["last_action_message"] = message


def get_category_counts(wardrobe: list[dict]) -> Counter:
    """Count how many wardrobe items exist in each category."""
    return Counter(item["category"] for item in wardrobe)


def prepare_table_data(wardrobe: list[dict]) -> pd.DataFrame:
    """Prepare wardrobe data for a clean read-only table."""
    rows = []

    for item in wardrobe:
        rows.append(
            {
                "Favorite": "❤️" if item.get("favorite", False) else "",
                "Name": item.get("name", "Unnamed item"),
                "Category": item.get("category", "unknown"),
                "Color": item.get("color", "unknown"),
                "Style tags": ", ".join(item.get("style_tags", [])),
                "Season": ", ".join(item.get("season", [])),
                "Comfort": item.get("comfort", "medium"),
                "Weather": ", ".join(item.get("weather", [])),
                "Notes": item.get("notes", ""),
            }
        )

    return pd.DataFrame(rows)


def get_cell_values(value: object) -> list[str]:
    """Convert editor values into a clean list, supporting lists and comma text."""
    if value is None:
        return []

    if isinstance(value, list):
        raw_values = value
    else:
        raw_values = str(value).split(",")

    return [str(part).strip() for part in raw_values if str(part).strip()]


def normalize_option(
    value: object,
    allowed_values: list[str],
    default: str,
    aliases: dict[str, str] | None = None,
) -> str:
    """Keep one editor value inside a controlled vocabulary."""
    aliases = aliases or {}
    cleaned = str(value).strip().lower().replace("_", "-")
    cleaned = aliases.get(cleaned, cleaned)

    if cleaned in allowed_values:
        return cleaned

    return default


def normalize_controlled_values(
    value: object,
    allowed_values: list[str],
    default_values: list[str],
) -> list[str]:
    """Keep multi-value editor cells inside a controlled vocabulary."""
    normalized_values = []

    for raw_value in get_cell_values(value):
        cleaned = raw_value.lower().replace("_", "-")

        if cleaned in allowed_values and cleaned not in normalized_values:
            normalized_values.append(cleaned)

    if normalized_values:
        return normalized_values

    return default_values.copy()


def get_wardrobe_editor_column_config(
    include_favorite: bool = False,
    hide_id: bool = False,
) -> dict:
    """Return controlled editor columns for wardrobe review tables."""
    config = {
        "Category": st.column_config.SelectboxColumn(
            "Category",
            options=CATEGORY_OPTIONS,
            help="Controlled category used by the recommendation engine.",
        ),
        "Style tags": st.column_config.MultiselectColumn(
            "Style tags",
            options=STYLE_TAG_OPTIONS,
            help="Choose known recommendation tags. Put personal descriptions in Notes.",
        ),
        "Season": st.column_config.MultiselectColumn(
            "Season",
            options=SEASON_OPTIONS,
        ),
        "Formality": st.column_config.SelectboxColumn(
            "Formality",
            options=FORMALITY_OPTIONS,
        ),
        "Comfort": st.column_config.SelectboxColumn(
            "Comfort",
            options=COMFORT_OPTIONS,
        ),
        "Weather": st.column_config.MultiselectColumn(
            "Weather",
            options=WEATHER_OPTIONS,
        ),
    }

    if include_favorite:
        config["Favorite"] = st.column_config.CheckboxColumn(
            "Favorite",
            help="Favorite items receive a small recommendation bonus.",
            default=False,
        )

    if hide_id:
        config["ID"] = None

    return config


def prepare_photo_review_table(detected_items: list[dict]) -> pd.DataFrame:
    """Prepare detected photo items for human review and editing."""
    rows = []

    for item in detected_items:
        rows.append(
            {
                "Name": item.get("name", "Detected clothing item"),
                "Category": normalize_option(
                    item.get("category", "other"),
                    CATEGORY_OPTIONS,
                    "other",
                    CATEGORY_ALIASES,
                ),
                "Color": item.get("color", "unknown"),
                "Style tags": normalize_controlled_values(
                    item.get("style_tags", []),
                    STYLE_TAG_OPTIONS,
                    ["neutral"],
                ),
                "Season": normalize_controlled_values(
                    item.get("season", []),
                    SEASON_OPTIONS,
                    ["all-season"],
                ),
                "Formality": normalize_option(
                    item.get("formality", "casual"),
                    FORMALITY_OPTIONS,
                    "casual",
                    FORMALITY_ALIASES,
                ),
                "Comfort": normalize_option(
                    item.get("comfort", "medium"),
                    COMFORT_OPTIONS,
                    "medium",
                ),
                "Weather": normalize_controlled_values(
                    item.get("weather", []),
                    WEATHER_OPTIONS,
                    ["indoor"],
                ),
                "Notes": item.get("notes", ""),
            }
        )

    return pd.DataFrame(rows)

def prepare_custom_item_review_table(parsed_items: list[dict]) -> pd.DataFrame:
    """Prepare parsed manual items for human review and editing."""
    rows = []

    for item in parsed_items:
        rows.append(
            {
                "ID": item.get("id", ""),
                "Name": item.get("name", "Custom wardrobe item"),
                "Category": normalize_option(
                    item.get("category", "other"),
                    CATEGORY_OPTIONS,
                    "other",
                    CATEGORY_ALIASES,
                ),
                "Color": item.get("color", "unknown"),
                "Style tags": normalize_controlled_values(
                    item.get("style_tags", []),
                    STYLE_TAG_OPTIONS,
                    ["neutral"],
                ),
                "Season": normalize_controlled_values(
                    item.get("season", []),
                    SEASON_OPTIONS,
                    ["all-season"],
                ),
                "Formality": normalize_option(
                    item.get("formality", "casual"),
                    FORMALITY_OPTIONS,
                    "casual",
                    FORMALITY_ALIASES,
                ),
                "Comfort": normalize_option(
                    item.get("comfort", "medium"),
                    COMFORT_OPTIONS,
                    "medium",
                ),
                "Weather": normalize_controlled_values(
                    item.get("weather", []),
                    WEATHER_OPTIONS,
                    ["indoor"],
                ),
                "Notes": item.get("notes", ""),
            }
        )

    return pd.DataFrame(rows)


def prepare_wardrobe_edit_table(items: list[dict]) -> pd.DataFrame:
    """Prepare existing wardrobe items for inline session editing."""
    rows = []

    for item in items:
        rows.append(
            {
                "ID": item.get("id", ""),
                "Favorite": bool(item.get("favorite", False)),
                "Name": item.get("name", "Unnamed item"),
                "Category": normalize_option(
                    item.get("category", "other"),
                    CATEGORY_OPTIONS,
                    "other",
                    CATEGORY_ALIASES,
                ),
                "Color": item.get("color", "unknown"),
                "Style tags": normalize_controlled_values(
                    item.get("style_tags", []),
                    STYLE_TAG_OPTIONS,
                    ["neutral"],
                ),
                "Season": normalize_controlled_values(
                    item.get("season", []),
                    SEASON_OPTIONS,
                    ["all-season"],
                ),
                "Formality": normalize_option(
                    item.get("formality", "casual"),
                    FORMALITY_OPTIONS,
                    "casual",
                    FORMALITY_ALIASES,
                ),
                "Comfort": normalize_option(
                    item.get("comfort", "medium"),
                    COMFORT_OPTIONS,
                    "medium",
                ),
                "Weather": normalize_controlled_values(
                    item.get("weather", []),
                    WEATHER_OPTIONS,
                    ["indoor"],
                ),
                "Notes": item.get("notes", ""),
            }
        )

    return pd.DataFrame(rows)


def build_reviewed_item_from_row(row: pd.Series, item_id: str | None = None) -> dict | None:
    """Build one controlled wardrobe item from a reviewed editor row."""
    name = str(row.get("Name", "")).strip()

    if not name:
        return None

    item = {
        "name": name,
        "category": normalize_option(
            row.get("Category", "other"),
            CATEGORY_OPTIONS,
            "other",
            CATEGORY_ALIASES,
        ),
        "color": str(row.get("Color", "unknown")).strip() or "unknown",
        "style_tags": normalize_controlled_values(
            row.get("Style tags", []),
            STYLE_TAG_OPTIONS,
            ["neutral"],
        ),
        "season": normalize_controlled_values(
            row.get("Season", []),
            SEASON_OPTIONS,
            ["all-season"],
        ),
        "formality": normalize_option(
            row.get("Formality", "casual"),
            FORMALITY_OPTIONS,
            "casual",
            FORMALITY_ALIASES,
        ),
        "comfort": normalize_option(
            row.get("Comfort", "medium"),
            COMFORT_OPTIONS,
            "medium",
        ),
        "weather": normalize_controlled_values(
            row.get("Weather", []),
            WEATHER_OPTIONS,
            ["indoor"],
        ),
        "notes": str(row.get("Notes", "")).strip(),
    }

    if item_id is not None:
        item["id"] = item_id

    if "Favorite" in row.index:
        item["favorite"] = bool(row.get("Favorite", False))

    return item

def build_reviewed_photo_items(review_table: pd.DataFrame) -> list[dict]:
    """Convert the human-reviewed photo table back into wardrobe item dictionaries."""
    reviewed_items = []

    for _, row in review_table.iterrows():
        item = build_reviewed_item_from_row(row)

        if item:
            reviewed_items.append(item)

    return reviewed_items

def build_reviewed_custom_items(review_table: pd.DataFrame) -> list[dict]:
    """Convert reviewed manually parsed items back into wardrobe item dictionaries."""
    reviewed_items = []

    for _, row in review_table.iterrows():
        item_id = str(row.get("ID", "")).strip()
        item = build_reviewed_item_from_row(row, item_id=item_id)

        if item:
            reviewed_items.append(item)

    return reviewed_items

def find_category_mismatches(review_table: pd.DataFrame) -> list[dict]:
    """Find strong name/category conflicts without overriding the user."""
    mismatches = []

    for _, row in review_table.iterrows():
        item_id = str(row.get("ID", "")).strip()
        name = str(row.get("Name", "")).strip()
        selected_category = normalize_option(
            row.get("Category", "other"),
            CATEGORY_OPTIONS,
            "other",
            CATEGORY_ALIASES,
        )
        suggested_category = detect_category(name.lower())

        if (
            name
            and suggested_category != "other"
            and selected_category != suggested_category
        ):
            mismatches.append(
                {
                    "ID": item_id,
                    "Item": name,
                    "Selected category": selected_category,
                    "Suggested category": suggested_category,
                }
            )

    return mismatches


def apply_category_suggestions(
    review_table: pd.DataFrame,
    mismatches: list[dict],
) -> pd.DataFrame:
    """Apply accepted category suggestions to a copy of the editor table."""
    updated_table = review_table.copy()
    suggestions_by_id = {
        mismatch["ID"]: mismatch["Suggested category"]
        for mismatch in mismatches
        if mismatch.get("ID")
    }

    for row_index, row in updated_table.iterrows():
        item_id = str(row.get("ID", "")).strip()

        if item_id in suggestions_by_id:
            updated_table.at[row_index, "Category"] = suggestions_by_id[item_id]

    return updated_table


def save_wardrobe_review_table(review_table: pd.DataFrame) -> int:
    """Save changed rows from the inline wardrobe editor to session state."""
    reviewed_items = build_reviewed_custom_items(review_table)
    return sum(
        update_item_in_session(reviewed_item)
        for reviewed_item in reviewed_items
    )


def get_next_custom_number(wardrobe: list[dict]) -> int:
    """Return the next number for custom wardrobe item IDs."""
    custom_numbers = []

    for item in wardrobe:
        item_id = item.get("id", "")

        if item_id.startswith("custom_"):
            number_text = item_id.replace("custom_", "")

            if number_text.isdigit():
                custom_numbers.append(int(number_text))

    if not custom_numbers:
        return 1

    return max(custom_numbers) + 1


def get_next_photo_number(wardrobe: list[dict]) -> int:
    """Return the next number for photo-detected wardrobe item IDs."""
    photo_numbers = []

    for item in wardrobe:
        item_id = item.get("id", "")

        if item_id.startswith("photo_"):
            number_text = item_id.replace("photo_", "")

            if number_text.isdigit():
                photo_numbers.append(int(number_text))

    if not photo_numbers:
        return 1

    return max(photo_numbers) + 1


def normalize_duplicate_text(value: object) -> str:
    """Normalize item text for friendly duplicate detection."""
    cleaned = re.sub(r"[^a-z0-9]+", " ", str(value).strip().lower())
    return " ".join(cleaned.split())


def get_item_duplicate_key(item: dict) -> tuple[str, str, str]:
    """Build a conservative duplicate key from name, category, and color."""
    return (
        normalize_duplicate_text(item.get("name", "")),
        normalize_duplicate_text(item.get("category", "")),
        normalize_duplicate_text(item.get("color", "")),
    )


def split_unique_and_duplicate_items(
    candidate_items: list[dict],
    existing_items: list[dict],
) -> tuple[list[dict], list[dict]]:
    """Skip duplicates already in the session or repeated in one submitted batch."""
    known_keys = {
        get_item_duplicate_key(item)
        for item in existing_items
        if get_item_duplicate_key(item)[0]
    }
    unique_items = []
    duplicate_items = []

    for item in candidate_items:
        item_key = get_item_duplicate_key(item)
        if not item_key[0] or item_key in known_keys:
            duplicate_items.append(item)
            continue

        known_keys.add(item_key)
        unique_items.append(item)

    return unique_items, duplicate_items


def format_duplicate_names(items: list[dict], limit: int = 3) -> str:
    """Return a short readable list of duplicate item names."""
    names = [item.get("name", "Unnamed item") for item in items]
    visible_names = names[:limit]
    result = ", ".join(visible_names)

    if len(names) > limit:
        result += f" and {len(names) - limit} more"

    return result


def item_matches_search(item: dict, search_text: str) -> bool:
    """Check whether an item matches the user's search text."""
    if not search_text:
        return True

    searchable_text = " ".join(
        [
            item.get("name", ""),
            item.get("category", ""),
            item.get("color", ""),
            " ".join(item.get("style_tags", [])),
            " ".join(item.get("season", [])),
            item.get("comfort", ""),
            " ".join(item.get("weather", [])),
            item.get("notes", ""),
            "favorite" if item.get("favorite", False) else "",
        ]
    ).lower()

    return search_text.lower() in searchable_text


def filter_wardrobe(
    wardrobe: list[dict],
    selected_category: str,
    selected_style_tag: str,
    search_text: str,
) -> list[dict]:
    """Filter wardrobe items by category, style tag, and search text."""
    filtered_items = wardrobe

    if selected_category != "All items":
        filtered_items = [
            item for item in filtered_items if item["category"] == selected_category
        ]

    if selected_style_tag != "All style tags":
        filtered_items = [
            item
            for item in filtered_items
            if selected_style_tag in item.get("style_tags", [])
        ]

    filtered_items = [
        item for item in filtered_items if item_matches_search(item, search_text)
    ]

    return filtered_items


def add_item_to_session(item: dict) -> None:
    """Add a parsed item to the current Streamlit session wardrobe."""
    st.session_state["wardrobe"].append(item)


def add_multiple_items_to_session(items: list[dict]) -> None:
    """Add multiple parsed items to the current Streamlit session wardrobe."""
    st.session_state["wardrobe"].extend(items)


def add_detected_photo_items_to_session(detected_items: list[dict]) -> list[dict]:
    """Add human-reviewed photo-detected items to the current session wardrobe."""
    next_number = get_next_photo_number(st.session_state["wardrobe"])
    photo_items = []

    for index, item in enumerate(detected_items):
        photo_item = dict(item)
        photo_item["id"] = f"photo_{next_number + index:03d}"
        photo_items.append(photo_item)

    st.session_state["wardrobe"].extend(photo_items)

    return photo_items


def get_item_display_name(item: dict) -> str:
    """Create a readable display name for a wardrobe item."""
    item_id = item.get("id", "no_id")
    name = item.get("name", "Unnamed item")
    category = item.get("category", "unknown category")
    color = item.get("color", "unknown color")
    favorite_marker = "❤️ " if item.get("favorite", False) else ""

    return f"{favorite_marker}{name} — {category}, {color} ({item_id})"

def set_item_favorite_in_session(selected_item_id: str, is_favorite: bool) -> bool:
    """Mark or unmark one wardrobe item as favorite in the current session only."""
    if not selected_item_id:
        return False

    for item in st.session_state["wardrobe"]:
        if item.get("id") == selected_item_id:
            item["favorite"] = is_favorite
            return True

    return False

def get_editable_item_snapshot(item: dict) -> dict:
    """Return normalized values that can be changed in the wardrobe editor."""
    return {
        "id": str(item.get("id", "")).strip(),
        "name": str(item.get("name", "")).strip(),
        "category": str(item.get("category", "")).strip(),
        "color": str(item.get("color", "")).strip(),
        "style_tags": list(item.get("style_tags", [])),
        "season": list(item.get("season", [])),
        "formality": str(item.get("formality", "")).strip(),
        "comfort": str(item.get("comfort", "")).strip(),
        "weather": list(item.get("weather", [])),
        "notes": str(item.get("notes", "")).strip(),
        "favorite": bool(item.get("favorite", False)),
    }


def update_item_in_session(updated_item: dict) -> bool:
    """Update one changed wardrobe item in the current Streamlit session only."""
    updated_item_id = updated_item.get("id")

    if not updated_item_id:
        return False

    for index, current_item in enumerate(st.session_state["wardrobe"]):
        if current_item.get("id") != updated_item_id:
            continue

        merged_item = {**current_item, **updated_item}
        merged_item["favorite"] = bool(
            updated_item.get("favorite", current_item.get("favorite", False))
        )

        if get_editable_item_snapshot(current_item) == get_editable_item_snapshot(
            merged_item
        ):
            return False

        st.session_state["wardrobe"][index] = merged_item
        return True

    return False

def remove_item_from_session(selected_item_id: str) -> bool:
    """Remove one item from the current Streamlit session wardrobe."""
    original_count = len(st.session_state["wardrobe"])

    st.session_state["wardrobe"] = [
        item
        for item in st.session_state["wardrobe"]
        if item.get("id") != selected_item_id
    ]

    return len(st.session_state["wardrobe"]) < original_count


def restore_sample_wardrobe() -> None:
    """Restore the original sample wardrobe for the current session."""
    st.session_state["wardrobe"] = load_wardrobe()
    st.session_state["photo_analysis_result"] = None
    st.session_state["photo_analysis_file_name"] = ""
    st.session_state["photo_items_added_for_file"] = ""
    st.session_state["style_vibes_editing"] = True


def display_outfit(outfit: dict) -> None:
    """Display one outfit as clean user-facing cards without technical captions."""
    cards = []

    for role, item in outfit.items():
        if item is None:
            continue

        favorite_marker = " ❤️" if item.get("favorite", False) else ""
        cards.append(
            '<div class="ww-outfit-card">'
            f'<div class="ww-outfit-role">{role}</div>'
            f'<div class="ww-outfit-name">{item.get("name", "Unnamed item")}{favorite_marker}</div>'
            "</div>"
        )

    if cards:
        st.markdown(
            '<div class="ww-outfit-grid">' + "".join(cards) + "</div>",
            unsafe_allow_html=True,
        )


def get_outfit_items(outfit: dict) -> list[dict]:
    """Return all real wardrobe items from an outfit dictionary."""
    return [item for item in outfit.values() if item is not None]


def get_estimate_basis_label(value: object) -> str:
    """Translate internal estimate labels into user-friendly wording."""
    mapping = {
        "source-backed": "Public-source benchmark",
        "public-source-benchmark": "Public-source benchmark",
        "demo-assumption": "Illustrative category estimate",
        "illustrative-category-estimate": "Illustrative category estimate",
    }
    return mapping.get(str(value), "Illustrative category estimate")


def prepare_rewear_impact_table(item_impacts: list[dict]) -> pd.DataFrame:
    """Prepare clean, user-facing Rewear Impact details."""
    rows = []
    has_favorite = any(bool(item.get("favorite", False)) for item in item_impacts)

    for item in item_impacts:
        row = {
            "Name": item.get("name", "Unnamed item"),
            "Category": str(item.get("category", "unknown")).replace("-", " ").title(),
            "Estimated water (L)": item.get("estimatedWaterLiters", 0),
            "Estimated CO₂e (kg)": item.get("estimatedCo2eKg", 0),
            "Estimate basis": get_estimate_basis_label(
                item.get("estimateBasis", item.get("confidence", ""))
            ),
        }

        if has_favorite:
            row["Favorite"] = "❤️" if item.get("favorite", False) else ""

        rows.append(row)

    columns = ["Name", "Category"]
    if has_favorite:
        columns.append("Favorite")
    columns.extend(
        ["Estimated water (L)", "Estimated CO₂e (kg)", "Estimate basis"]
    )

    return pd.DataFrame(rows, columns=columns)


def display_rewear_impact(outfit: dict) -> None:
    """Display clean Rewear Impact estimates for the main outfit."""
    outfit_items = get_outfit_items(outfit)

    if not outfit_items:
        return

    impact = calculate_rewear_impact(outfit_items)
    summary = impact.get("summary", {})

    items_reused = summary.get("itemsReused", 0)
    water_liters = summary.get("waterLiters", 0)
    co2e_kg = summary.get("co2eKg", 0)
    favorite_items_used = summary.get("favoriteItemsUsed", 0)

    st.divider()
    st.subheader("🌍 Rewear Impact")
    st.success(impact.get("spell", "Rewear spell unlocked."))

    impact_col1, impact_col2, impact_col3 = st.columns(3)

    with impact_col1:
        st.metric("Items reused", items_reused)

    with impact_col2:
        st.metric("Water estimate", f"{water_liters:,} L")

    with impact_col3:
        st.metric("CO₂e estimate", f"{co2e_kg} kg")

    st.write(
        impact.get(
            "noBuyMessage",
            "This is a no-buy comparison estimate for rewearing existing clothes.",
        )
    )

    if favorite_items_used:
        st.caption(f"Favorite item(s) included in this look: {favorite_items_used} ❤️")

    with st.expander("How this estimate works"):
        st.write(
            impact.get(
                "disclaimer",
                "This is an educational estimate, not a certified impact calculation.",
            )
        )
        st.write(
            "The estimate compares rewearing items from the current wardrobe with the "
            "simplified impact of producing similar new items."
        )

        mode = impact.get("mode", "local fallback estimate")
        st.caption(f"Calculation mode: {mode}")

        item_impacts = impact.get("itemImpacts", [])
        if item_impacts:
            st.dataframe(
                prepare_rewear_impact_table(item_impacts),
                width="stretch",
                hide_index=True,
            )


def collapse_style_vibes_if_complete() -> None:
    """Collapse the style vibe selector after two choices without interrupting other widgets."""
    selected_vibes = st.session_state.get("recommend_style_vibes", [])

    if len(selected_vibes) == 2:
        st.session_state["style_vibes_editing"] = False


def display_style_vibes_selector() -> list[str]:
    """Hide the style dropdown after two vibes are chosen until the user edits them."""
    selected_vibes = list(st.session_state.get("recommend_style_vibes", []))

    if len(selected_vibes) < 2:
        st.session_state["style_vibes_editing"] = True

    if st.session_state.get("style_vibes_editing", True):
        st.multiselect(
            "Style vibes (optional — choose up to 2)",
            STYLE_VIBES,
            max_selections=2,
            key="recommend_style_vibes",
            help=(
                "Style vibes describe the mood of the outfit, not the user's "
                "gender or identity."
            ),
            on_change=collapse_style_vibes_if_complete,
        )
    else:
        chips = "".join(
            f'<span class="ww-vibe-chip">{vibe}</span>' for vibe in selected_vibes
        )
        st.markdown(
            '<div class="ww-vibe-row">'
            '<span style="color:#5b466e;font-weight:650;">Selected vibes:</span>'
            f"{chips}</div>",
            unsafe_allow_html=True,
        )

        if st.button("Change vibes", key="change_recommend_style_vibes"):
            st.session_state["style_vibes_editing"] = True
            st.rerun()

    return list(st.session_state.get("recommend_style_vibes", []))


def build_travel_context_text(
    departure_climate: str,
    destination_climate: str,
    travel_season: str,
    flight_type: str,
) -> str:
    """Build optional travel context for outfit recommendations."""
    travel_details = []

    if departure_climate != "not specified":
        travel_details.append(f"departure climate: {departure_climate}")

    if destination_climate != "not specified":
        travel_details.append(f"destination climate: {destination_climate}")

    if travel_season != "not specified":
        travel_details.append(f"travel season: {travel_season}")

    if flight_type != "not specified":
        travel_details.append(f"flight type: {flight_type}")

    if not travel_details:
        return ""

    return (
        "Travel details: "
        + "; ".join(travel_details)
        + ". Prioritize comfortable layers, practical shoes, airport comfort, "
        "and clothing that can handle temperature changes."
    )

def display_low_energy_pick(
    recommendation: dict,
    scenario: str,
    custom_scenario: str,
    comfort_preference: str,
) -> None:
    """Display a calm, low-energy outfit decision support card."""
    main_outfit = recommendation.get("main_outfit", {})

    outfit_items = [
        item["name"]
        for item in main_outfit.values()
        if item is not None and item.get("name")
    ]

    if not outfit_items:
        return

    situation = custom_scenario if scenario == "Custom scenario" else scenario

    st.divider()

    st.subheader("Low-Energy Pick ✨")

    st.write(
        "If you feel tired, overloaded, or simply do not want to overthink your outfit, "
        "use this as your easiest good-enough choice."
    )

    st.markdown("**Wear this:**")

    for item_name in outfit_items:
        st.write(f"- {item_name}")

    st.markdown("**Why this is enough:**")

    st.write(
        "This outfit already matches the selected situation, uses the current wardrobe, "
        "and keeps the decision simple."
    )

    if comfort_preference == "High comfort preferred":
        st.write(
            "It also respects your high-comfort preference, so it should feel easier "
            "to wear without needing extra styling decisions."
        )

    st.info(
        f"For **{situation}**, this is already a practical choice. "
        "You do not need to optimize more right now."
    )


def display_photo_analysis_result(result: dict) -> None:
    """Display the photo analysis result in the Streamlit UI."""
    if not result:
        return

    if result.get("analysis_ok"):
        st.success("Photo analysis completed.")
    else:
        st.warning(result.get("error_message", "Photo analysis is unavailable."))

    st.subheader("Outfit summary")
    st.write(result.get("outfit_summary", "No outfit summary was returned."))

    detected_items = result.get("detected_items", [])

    st.subheader("Detected clothing items")

    if detected_items:
        st.dataframe(
            prepare_table_data(detected_items),
            width="stretch",
            hide_index=True,
        )
    else:
        st.info(
            "No structured clothing items were detected. "
            "You can still use the manual Add Items tab."
        )

    best_occasions = result.get("best_occasions", [])

    st.subheader("Best occasions")

    if best_occasions:
        for occasion in best_occasions:
            st.write(f"- {occasion}")
    else:
        st.caption("No occasions were returned for this photo.")

    st.subheader("Occasion explanation")
    st.write(
        result.get(
            "occasion_explanation",
            "No occasion explanation was returned.",
        )
    )


def display_photo_review_flow(uploaded_photo_name: str, photo_result: dict) -> None:
    """Let the user review and edit detected photo items before adding them."""
    if not (
        photo_result
        and photo_result.get("analysis_ok")
        and photo_result.get("detected_items")
    ):
        return

    st.divider()
    st.subheader("Review detected items before adding")
    st.write(
        "The AI suggested these clothing items. You can edit the table before "
        "adding anything to the session wardrobe."
    )
    st.caption(
        "Choose known recommendation tags in the controlled fields. "
        "Use Notes for personal descriptions or custom aesthetics."
    )

    review_table = prepare_photo_review_table(photo_result["detected_items"])
    reviewed_table = st.data_editor(
        review_table,
        width="stretch",
        hide_index=True,
        num_rows="dynamic",
        key=f"photo_review_editor_{uploaded_photo_name}",
        column_config=get_wardrobe_editor_column_config(),
    )

    if st.session_state["photo_items_added_for_file"] == uploaded_photo_name:
        st.info("Reviewed items from this photo are already in the current session wardrobe.")
        return

    st.write(
        "When the table looks good, add the reviewed items to your session wardrobe. "
        "They will not be saved permanently to the JSON dataset."
    )

    if st.button(
        "Add reviewed items to wardrobe",
        key=f"add_reviewed_photo_items_{uploaded_photo_name}",
    ):
        reviewed_items = build_reviewed_photo_items(reviewed_table)

        if not reviewed_items:
            st.session_state["corgi_mood"] = "oops"
            st.warning("No reviewed items were added because the table is empty.")
            return

        unique_items, duplicate_items = split_unique_and_duplicate_items(
            reviewed_items,
            st.session_state["wardrobe"],
        )

        if not unique_items:
            st.session_state["corgi_mood"] = "oops"
            st.warning(
                "These items already exist in the current wardrobe: "
                + format_duplicate_names(duplicate_items)
            )
            return

        st.session_state["corgi_mood"] = "happy"
        added_items = add_detected_photo_items_to_session(unique_items)
        st.session_state["photo_items_added_for_file"] = uploaded_photo_name

        message = f"Added {len(added_items)} reviewed photo item(s)."
        if duplicate_items:
            message += (
                f" Skipped {len(duplicate_items)} duplicate(s): "
                f"{format_duplicate_names(duplicate_items)}."
            )

        set_action_message(message)
        keep_user_on_tab("Analyze Outfit Photo")
        st.rerun()


st.set_page_config(
    page_title="Wardrobe Wizard",
    page_icon="✨",
    layout="wide",
)

inject_custom_css()

# ── Splash gate ─────────────────────────────────────────────────────────────
# display_splash_screen() uses a native st.button(), so no query params needed.
if "app_started" not in st.session_state:
    st.session_state["app_started"] = False

if not st.session_state["app_started"]:
    display_splash_screen()
    st.stop()
# ────────────────────────────────────────────────────────────────────────────

try:
    initialize_session_state()
except FileNotFoundError:
    st.error("The wardrobe dataset was not found. Please check data/wardrobe.json.")
    st.stop()
except json.JSONDecodeError:
    st.error("The wardrobe dataset contains invalid JSON. Please check the file syntax.")
    st.stop()

display_app_header()
apply_pending_ui_state()

st.markdown(
    get_corgi_mascot_html(st.session_state.get("corgi_mood", "idle")),
    unsafe_allow_html=True,
)

if st.session_state["last_action_message"]:
    st.toast(
        st.session_state["last_action_message"],
        icon="✅",
        duration=10,
    )
    st.session_state["last_action_message"] = ""

wardrobe_items = st.session_state["wardrobe"]
category_counts = get_category_counts(wardrobe_items)

recommend_tab, wardrobe_tab, add_tab, photo_tab, about_tab = st.tabs(
    MAIN_TAB_LABELS,
    key="main_app_tab",
    on_change="rerun",
)

with recommend_tab:
    st.subheader("Recommend Outfit")
    st.write(
        "Choose a situation and Wardrobe Wizard will suggest a main outfit "
        "and an alternative outfit."
    )

    selected_vibes = display_style_vibes_selector()

    scenario = st.selectbox(
        "Choose a demo scenario",
        [
            "Office rainy day",
            "Date night",
            "Travel day",
            "Custom scenario",
        ],
        key="recommend_scenario",
    )

    custom_scenario = ""

    if scenario == "Travel day":
        with st.expander("Optional travel details"):
            st.caption(
                "Use this when your trip has a climate or season change. "
                "Leave the fields unspecified to use the default travel logic."
            )

            travel_col1, travel_col2 = st.columns(2)

            with travel_col1:
                departure_climate = st.selectbox(
                    "Departure climate",
                    ["not specified", "hot", "warm", "mild", "cold", "rainy"],
                    key="travel_departure_climate",
                )
                travel_season = st.selectbox(
                    "Travel season",
                    ["not specified", "spring", "summer", "autumn", "winter"],
                    key="travel_season",
                )

            with travel_col2:
                destination_climate = st.selectbox(
                    "Destination climate",
                    ["not specified", "hot", "warm", "mild", "cold", "rainy"],
                    key="travel_destination_climate",
                )
                flight_type = st.selectbox(
                    "Flight type",
                    ["not specified", "short flight", "long-haul flight"],
                    key="travel_flight_type",
                )

            custom_scenario = build_travel_context_text(
                departure_climate=departure_climate,
                destination_climate=destination_climate,
                travel_season=travel_season,
                flight_type=flight_type,
            )

            if custom_scenario:
                st.info(custom_scenario)

    elif scenario == "Custom scenario":
        custom_scenario = st.text_input(
            "Describe your own situation",
            placeholder="Example: casual dinner after work, cold evening, comfortable shoes",
            key="recommend_custom_scenario",
        )

    comfort_preference = st.selectbox(
        "Comfort preference",
        [
            "High comfort preferred",
            "Medium comfort is okay",
            "No comfort preference",
        ],
        key="recommend_comfort_preference",
    )

    low_energy_mode = st.checkbox(
        "Low-energy decision support",
        key="recommend_low_energy_mode",
        help=(
            "Show one calm, good-enough outfit choice for moments when too many "
            "options feel overwhelming."
        ),
    )

    if st.button("Recommend outfit", key="recommend_outfit_button"):
        st.session_state["corgi_mood"] = "celebrate"

        recommendation = recommend_outfits(
            wardrobe=wardrobe_items,
            scenario=scenario,
            custom_scenario=custom_scenario,
            selected_vibes=selected_vibes,
            comfort_preference=comfort_preference,
        )

        main_outfit = recommendation["main_outfit"]
        alternative_outfit = recommendation["alternative_outfit"]

        st.subheader("Main outfit")
        display_outfit(main_outfit)

        st.subheader("Alternative outfit")
        display_outfit(alternative_outfit)

        st.subheader("Why it works")
        ai_explanation = generate_outfit_explanation(
            recommendation=recommendation,
            scenario=scenario,
            custom_scenario=custom_scenario,
            selected_vibes=selected_vibes,
            comfort_preference=comfort_preference,
        )
        st.info(ai_explanation, icon="✨")

        if low_energy_mode:
            display_low_energy_pick(
                recommendation=recommendation,
                scenario=scenario,
                custom_scenario=custom_scenario,
                comfort_preference=comfort_preference,
            )

        display_rewear_impact(main_outfit)

with wardrobe_tab:
    st.subheader("Wardrobe summary")

    custom_items_count = sum(
        item.get("id", "").startswith("custom_") for item in wardrobe_items
    )
    photo_items_count = sum(
        item.get("id", "").startswith("photo_") for item in wardrobe_items
    )
    favorite_items_count = sum(
        bool(item.get("favorite", False)) for item in wardrobe_items
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total items", len(wardrobe_items))
    with col2:
        st.metric("Categories", len(category_counts))
    with col3:
        st.metric("Manual session items", custom_items_count)
    with col4:
        st.metric("Photo session items", photo_items_count)
    with col5:
        st.metric("Favorite items", favorite_items_count)

    st.subheader("Browse wardrobe")

    available_categories = ["All items"] + sorted(category_counts.keys())
    all_style_tags = sorted(
        {
            style_tag
            for item in wardrobe_items
            for style_tag in item.get("style_tags", [])
        }
    )
    available_style_tags = ["All style tags"] + all_style_tags

    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        selected_category = st.selectbox(
            "Filter by category",
            available_categories,
            key="wardrobe_category_filter",
        )
    with filter_col2:
        selected_style_tag = st.selectbox(
            "Filter by style tag",
            available_style_tags,
            key="wardrobe_style_filter",
        )
    with filter_col3:
        search_text = st.text_input(
            "Search wardrobe",
            placeholder="Example: black, rainy, office",
            key="wardrobe_search",
        )

    filtered_items = filter_wardrobe(
        wardrobe_items,
        selected_category,
        selected_style_tag,
        search_text,
    )

    st.write(f"Showing **{len(filtered_items)}** item(s).")

    edit_wardrobe = st.toggle(
        "Edit items and favorites",
        key="wardrobe_edit_mode",
        help=(
            "Turn this on to edit the visible wardrobe rows and mark items "
            "as favorites. Changes stay in the current session only."
        ),
    )

    if not filtered_items:
        st.warning(
            "No items match these filters yet. Try a different category, "
            "style tag, or search text."
        )
    elif edit_wardrobe:
        st.markdown(
            '<div class="ww-edit-note">Edit names, colors, controlled tags, and '
            'favorites directly below. Changes stay in this session only.</div>',
            unsafe_allow_html=True,
        )

        editor_key = (
            "browse_wardrobe_editor_"
            f"{selected_category}_{selected_style_tag}_{search_text}"
        )
        edited_visible_table = st.data_editor(
            prepare_wardrobe_edit_table(filtered_items),
            width="stretch",
            hide_index=True,
            num_rows="fixed",
            key=editor_key,
            column_config=get_wardrobe_editor_column_config(
                include_favorite=True,
                hide_id=True,
            ),
        )

        category_mismatches = find_category_mismatches(edited_visible_table)

        if category_mismatches:
            st.warning(
                "Wardrobe Wizard noticed a possible name/category mismatch. "
                "You can accept the suggested categories or keep your manual choices."
            )

            st.dataframe(
                pd.DataFrame(category_mismatches)[
                    ["Item", "Selected category", "Suggested category"]
                ],
                width="stretch",
                hide_index=True,
            )

            suggestion_col, manual_col = st.columns(2)

            with suggestion_col:
                if st.button(
                    "Apply suggestions and save",
                    key="apply_category_suggestions_and_save",
                ):
                    corrected_table = apply_category_suggestions(
                        edited_visible_table,
                        category_mismatches,
                    )
                    updated_count = save_wardrobe_review_table(corrected_table)

                    if updated_count:
                        st.session_state["corgi_mood"] = "happy"
                        set_action_message(
                            f"Updated {updated_count} wardrobe item(s) with category suggestions."
                        )
                        keep_user_on_tab("View Wardrobe")
                        st.rerun()
                    else:
                        st.session_state["corgi_mood"] = "oops"
                        st.warning("No visible rows were updated.")

            with manual_col:
                if st.button(
                    "Keep my categories and save",
                    key="keep_manual_categories_and_save",
                ):
                    updated_count = save_wardrobe_review_table(edited_visible_table)

                    if updated_count:
                        st.session_state["corgi_mood"] = "happy"
                        set_action_message(
                            f"Updated {updated_count} wardrobe item(s) with your category choices."
                        )
                        keep_user_on_tab("View Wardrobe")
                        st.rerun()
                    else:
                        st.session_state["corgi_mood"] = "oops"
                        st.warning("No visible rows were updated.")
        else:
            if st.button("Save wardrobe changes", key="save_visible_row_edits"):
                updated_count = save_wardrobe_review_table(edited_visible_table)

                if updated_count:
                    st.session_state["corgi_mood"] = "happy"
                    set_action_message(
                        f"Updated {updated_count} visible wardrobe item(s)."
                    )
                    keep_user_on_tab("View Wardrobe")
                    st.rerun()
                else:
                    st.session_state["corgi_mood"] = "oops"
                    st.warning("No visible rows were updated.")
    else:
        st.dataframe(
            prepare_table_data(filtered_items),
            width="stretch",
            hide_index=True,
        )

    st.divider()
    st.subheader("Simplify current session")
    st.write(
        "Temporarily remove an item when you want fewer choices on screen. "
        "The original sample wardrobe is not changed."
    )

    if not wardrobe_items:
        st.warning("The current session wardrobe is empty.")
    else:
        item_options = {
            get_item_display_name(item): item.get("id") for item in wardrobe_items
        }
        selected_item_label = st.selectbox(
            "Select an item to remove from the current session",
            list(item_options.keys()),
            key="remove_session_item_selectbox",
        )

        cleanup_col1, cleanup_col2 = st.columns(2)
        with cleanup_col1:
            if st.button(
                "Remove selected item from session",
                key="remove_selected_session_item",
            ):
                selected_item_id = item_options[selected_item_label]
                removed = remove_item_from_session(selected_item_id)

                if removed:
                    st.session_state["corgi_mood"] = "happy"
                    set_action_message(
                        f"Removed from this session: {selected_item_label}"
                    )
                    keep_user_on_tab("View Wardrobe")
                    st.rerun()
                else:
                    st.session_state["corgi_mood"] = "oops"
                    st.warning("The selected item could not be removed.")

        with cleanup_col2:
            if st.button(
                "Restore full sample wardrobe",
                key="restore_sample_wardrobe_button",
            ):
                st.session_state["corgi_mood"] = "sparkle"
                restore_sample_wardrobe()
                set_action_message("Restored the full sample wardrobe for this session.")
                keep_user_on_tab("View Wardrobe")
                st.rerun()

with add_tab:
    st.subheader("Add Items")
    st.write(
        "Add clothing items to the current Streamlit session. "
        "Wardrobe Wizard parses your text first, and you review it before saving."
    )
    st.caption(
        "Controlled fields help recommendations work reliably. Use Notes for "
        "personal descriptions or custom aesthetics."
    )

    single_tab, multiple_tab = st.tabs(
        ADD_ITEM_TAB_LABELS,
        key="add_items_tab",
        on_change="rerun",
    )

    with single_tab:
        single_description = st.text_area(
            "Single item description",
            placeholder="Example: white fluffy slippers, cozy, indoor, high comfort",
            height=100,
            key="single_item_description",
        )

        if single_description.strip():
            next_number = get_next_custom_number(st.session_state["wardrobe"])
            preview_id = f"custom_{next_number:03d}"
            preview_item = parse_item_description(single_description, preview_id)

            st.write("Review before adding:")
            reviewed_single_table = st.data_editor(
                prepare_custom_item_review_table([preview_item]),
                width="stretch",
                hide_index=True,
                num_rows="fixed",
                key=(
                    f"single_item_review_{preview_id}_"
                    f"{abs(hash(single_description.strip()))}"
                ),
                column_config=get_wardrobe_editor_column_config(hide_id=True),
            )

            with st.expander("Show technical parsed JSON"):
                st.json(preview_item)

            if st.button(
                "Add reviewed item to wardrobe",
                key="add_reviewed_single_item",
            ):
                reviewed_items = build_reviewed_custom_items(reviewed_single_table)

                if not reviewed_items:
                    st.session_state["corgi_mood"] = "oops"
                    st.warning("No item was added because the reviewed row is empty.")
                else:
                    unique_items, duplicate_items = split_unique_and_duplicate_items(
                        reviewed_items,
                        st.session_state["wardrobe"],
                    )

                    if not unique_items:
                        st.session_state["corgi_mood"] = "oops"
                        st.warning(
                            "This item already exists in the current wardrobe: "
                            + format_duplicate_names(duplicate_items)
                        )
                    else:
                        st.session_state["corgi_mood"] = "happy"
                        add_item_to_session(unique_items[0])
                        set_action_message(
                            f"Added item: {unique_items[0]['name']}"
                        )
                        st.session_state["clear_single_item_description"] = True
                        keep_user_on_tab("Add Items", "Add one item")
                        st.rerun()
        else:
            st.caption(
                "Write a short item description to see an editable preview before adding it."
            )

    with multiple_tab:
        multiple_description = st.text_area(
            "Multiple item descriptions",
            placeholder=(
                "Example:\n"
                "Navy blazer, office-friendly, autumn, medium comfort\n"
                "Cream knit sweater, cozy, winter, high comfort\n"
                "White fluffy slippers, cozy, indoor, high comfort"
            ),
            height=180,
            key="multiple_item_descriptions",
        )

        if multiple_description.strip():
            next_number = get_next_custom_number(st.session_state["wardrobe"])
            preview_items = parse_multiple_item_descriptions(
                multiple_description,
                start_number=next_number,
            )

            st.write("Review before adding:")
            reviewed_multiple_table = st.data_editor(
                prepare_custom_item_review_table(preview_items),
                width="stretch",
                hide_index=True,
                num_rows="dynamic",
                key=(
                    f"multiple_item_review_{next_number}_{len(preview_items)}_"
                    f"{abs(hash(multiple_description.strip()))}"
                ),
                column_config=get_wardrobe_editor_column_config(hide_id=True),
            )

            with st.expander("Show technical parsed JSON"):
                st.json(preview_items)

            if st.button(
                "Add reviewed items to wardrobe",
                key="add_reviewed_multiple_items",
            ):
                reviewed_items = build_reviewed_custom_items(reviewed_multiple_table)

                if not reviewed_items:
                    st.session_state["corgi_mood"] = "oops"
                    st.warning("No items were added because the reviewed table is empty.")
                else:
                    unique_items, duplicate_items = split_unique_and_duplicate_items(
                        reviewed_items,
                        st.session_state["wardrobe"],
                    )

                    if not unique_items:
                        st.session_state["corgi_mood"] = "oops"
                        st.warning(
                            "All submitted items are duplicates: "
                            + format_duplicate_names(duplicate_items)
                        )
                    else:
                        st.session_state["corgi_mood"] = "happy"
                        add_multiple_items_to_session(unique_items)

                        message = f"Added {len(unique_items)} item(s)."
                        if duplicate_items:
                            message += (
                                f" Skipped {len(duplicate_items)} duplicate(s): "
                                f"{format_duplicate_names(duplicate_items)}."
                            )

                        set_action_message(message)
                        st.session_state["clear_multiple_item_descriptions"] = True
                        keep_user_on_tab("Add Items", "Add multiple items")
                        st.rerun()
        else:
            st.caption(
                "Paste one item per line to see an editable preview before adding anything."
            )

with photo_tab:
    st.subheader("Analyze Outfit Photo")
    st.write(
        "Upload one outfit photo. Wardrobe Wizard analyzes visible clothing and "
        "suggests practical occasions for the outfit."
    )
    st.info(
        "Wardrobe Wizard analyzes visible clothing only. Photos are not stored "
        "permanently, and the app should not infer identity or sensitive traits."
    )

    uploaded_photo = st.file_uploader(
        "Upload an outfit photo",
        type=["jpg", "jpeg", "png"],
        help="Use a simple demo outfit photo up to 5 MB.",
        key="outfit_photo_uploader",
    )

    if uploaded_photo is None:
        st.session_state["photo_analysis_result"] = None
        st.session_state["photo_analysis_file_name"] = ""
        st.session_state["photo_items_added_for_file"] = ""
        st.caption("Upload a JPG or PNG image to start.")
    else:
        if st.session_state["photo_analysis_file_name"] != uploaded_photo.name:
            st.session_state["photo_analysis_result"] = None
            st.session_state["photo_analysis_file_name"] = uploaded_photo.name
            st.session_state["photo_items_added_for_file"] = ""

        st.image(
            uploaded_photo,
            caption="Uploaded outfit photo preview",
            width="stretch",
        )

        if st.button("Analyze photo", key="analyze_outfit_photo_button"):
            with st.spinner("Analyzing visible clothing..."):
                analysis_result = analyze_outfit_photo(uploaded_photo)

            st.session_state["photo_analysis_result"] = analysis_result
            st.session_state["corgi_mood"] = (
                "sparkle" if analysis_result.get("analysis_ok") else "oops"
            )

        display_photo_analysis_result(st.session_state["photo_analysis_result"])
        display_photo_review_flow(
            uploaded_photo_name=uploaded_photo.name,
            photo_result=st.session_state["photo_analysis_result"],
        )

with about_tab:
    st.subheader("About Wardrobe Wizard")
    st.write(
        "Wardrobe Wizard is a Python + Streamlit hackathon project that helps "
        "users choose outfits, reuse their wardrobe, and reduce decision fatigue."
    )
    st.write(
        "The app combines explainable local recommendation rules, GitHub Models "
        "for natural-language explanations, vision-based clothing analysis, "
        "human review, a TypeScript Rewear Impact mini API, and session-only data."
    )

    st.markdown(
        """
**Current MVP+ features:**
- Rule-based main and alternative outfit recommendations
- Optional travel climate and season context
- Low-Energy decision support
- Editable session wardrobe with direct favorite toggling
- Natural-language single and batch item parsing with duplicate protection
- Clothing-only photo analysis with human review
- Rewear Impact estimates through the mini API with a local fallback
- Privacy-conscious, session-only wardrobe changes

**Important limitations:**
- Session changes are not permanently written to `data/wardrobe.json`
- Uploaded photos are not permanently stored by the app
- Rewear Impact values are educational estimates, not certified calculations
- The app does not provide shopping advice or infer sensitive personal traits
"""
    )