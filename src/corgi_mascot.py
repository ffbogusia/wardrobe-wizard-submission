"""Corgi mascot helper for Wardrobe Wizard."""

from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

STATIC_CORGI_PATH = PROJECT_ROOT / "assets" / "corgi-mascot-sticker.png"


@lru_cache(maxsize=2)
def load_asset_b64(path_text: str) -> str:
    """Load a local asset as base64 and cache it for Streamlit reruns."""
    path = Path(path_text)

    with path.open("rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def get_corgi_mascot_html(mood: str = "idle") -> str:
    """Return fixed-position static corgi mascot with magical sparkles."""
    safe_mood = mood if mood else "idle"

    if not STATIC_CORGI_PATH.exists():
        return ""

    image_b64 = load_asset_b64(str(STATIC_CORGI_PATH))

    style_html = """
<style>
.ww-corgi-wrap {
    position: fixed;
    right: 18px;
    bottom: 16px;
    width: 155px;
    max-width: 22vw;
    z-index: 999999;
    pointer-events: none;
    filter: drop-shadow(0 10px 24px rgba(76, 29, 149, 0.24));
    animation: ww-corgi-float 4.2s ease-in-out infinite;
}

.ww-corgi-img {
    display: block;
    width: 100%;
    height: auto;
    position: relative;
    z-index: 2;
}

.ww-corgi-sparkle {
    position: absolute;
    z-index: 3;
    font-size: 18px;
    line-height: 1;
    opacity: 0;
    filter: drop-shadow(0 0 6px rgba(250, 204, 21, 0.75));
    animation: ww-corgi-sparkle 2.4s ease-in-out infinite;
}

.ww-corgi-sparkle.one {
    top: 8px;
    left: 10px;
    animation-delay: 0.0s;
}

.ww-corgi-sparkle.two {
    top: 18px;
    right: 4px;
    font-size: 14px;
    animation-delay: 0.7s;
}

.ww-corgi-sparkle.three {
    bottom: 18px;
    left: 0px;
    font-size: 15px;
    animation-delay: 1.35s;
}

.ww-corgi-sparkle.four {
    bottom: 36px;
    right: 0px;
    font-size: 13px;
    animation-delay: 1.9s;
}

@keyframes ww-corgi-float {
    0%, 100% {
        transform: translateY(0px) rotate(0deg);
    }
    50% {
        transform: translateY(-7px) rotate(-1deg);
    }
}

@keyframes ww-corgi-sparkle {
    0%, 100% {
        opacity: 0;
        transform: scale(0.55) rotate(0deg);
    }
    45% {
        opacity: 1;
        transform: scale(1.25) rotate(18deg);
    }
    70% {
        opacity: 0.55;
        transform: scale(0.9) rotate(36deg);
    }
}

@media (max-width: 900px) {
    .ww-corgi-wrap {
        width: 108px;
        right: 10px;
        bottom: 10px;
    }

    .ww-corgi-sparkle {
        font-size: 13px;
    }
}
</style>
""".strip()

    mascot_html = (
        f'<div class="ww-corgi-wrap ww-corgi-{safe_mood}" aria-hidden="true">'
        '<span class="ww-corgi-sparkle one">✨</span>'
        '<span class="ww-corgi-sparkle two">⭐</span>'
        '<span class="ww-corgi-sparkle three">💫</span>'
        '<span class="ww-corgi-sparkle four">✨</span>'
        f'<img class="ww-corgi-img" src="data:image/png;base64,{image_b64}" alt="" />'
        "</div>"
    )

    return style_html + mascot_html