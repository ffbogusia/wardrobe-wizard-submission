"""Browser-side Closet Puzzle prototype for Wardrobe Wizard."""

from __future__ import annotations

import html
import json

import streamlit.components.v1 as components


PUZZLE_LEVELS = [
    {
        "id": "intro",
        "name": "Intro squeeze",
        "difficulty": "Intro",
        "target": "soft_knit",
        "exitRow": 2,
        "items": [
            {
                "id": "soft_knit",
                "label": "Soft knit",
                "type": "target",
                "x": 1,
                "y": 2,
                "w": 2,
                "h": 1,
                "axis": "h",
                "color": "#f472b6",
            },
            {
                "id": "denim",
                "label": "Denim",
                "x": 0,
                "y": 0,
                "w": 2,
                "h": 1,
                "axis": "h",
                "color": "#60a5fa",
            },
            {
                "id": "boots",
                "label": "Boots",
                "x": 0,
                "y": 3,
                "w": 1,
                "h": 2,
                "axis": "v",
                "color": "#a78bfa",
            },
            {
                "id": "scarf",
                "label": "Scarf",
                "x": 3,
                "y": 4,
                "w": 3,
                "h": 1,
                "axis": "h",
                "color": "#fbbf24",
            },
            {
                "id": "tote",
                "label": "Tote",
                "x": 5,
                "y": 0,
                "w": 1,
                "h": 2,
                "axis": "v",
                "color": "#34d399",
            },
        ],
        "solution": [{"id": "soft_knit", "delta": 3}],
    },
    {
        "id": "medium",
        "name": "Rainy rack",
        "difficulty": "Medium",
        "target": "red_dress",
        "exitRow": 2,
        "items": [
            {
                "id": "red_dress",
                "label": "Red dress",
                "type": "target",
                "x": 0,
                "y": 2,
                "w": 2,
                "h": 1,
                "axis": "h",
                "color": "#fb7185",
            },
            {
                "id": "trench",
                "label": "Trench",
                "x": 3,
                "y": 1,
                "w": 1,
                "h": 3,
                "axis": "v",
                "color": "#c4b5fd",
            },
            {
                "id": "loafers",
                "label": "Loafers",
                "x": 0,
                "y": 0,
                "w": 2,
                "h": 1,
                "axis": "h",
                "color": "#93c5fd",
            },
            {
                "id": "cardigan",
                "label": "Cardigan",
                "x": 1,
                "y": 4,
                "w": 1,
                "h": 2,
                "axis": "v",
                "color": "#f9a8d4",
            },
            {
                "id": "belt",
                "label": "Belt",
                "x": 4,
                "y": 0,
                "w": 2,
                "h": 1,
                "axis": "h",
                "color": "#fcd34d",
            },
            {
                "id": "bag",
                "label": "Bag",
                "x": 5,
                "y": 3,
                "w": 1,
                "h": 2,
                "axis": "v",
                "color": "#6ee7b7",
            },
        ],
        "solution": [
            {"id": "trench", "delta": 2},
            {"id": "red_dress", "delta": 4},
        ],
    },
    {
        "id": "hard",
        "name": "Backstep boutique",
        "difficulty": "Harder",
        "target": "star_blouse",
        "exitRow": 2,
        "items": [
            {
                "id": "star_blouse",
                "label": "Star blouse",
                "type": "target",
                "x": 2,
                "y": 2,
                "w": 2,
                "h": 1,
                "axis": "h",
                "color": "#f472b6",
            },
            {
                "id": "stacked_knits",
                "label": "Knits",
                "x": 2,
                "y": 0,
                "w": 1,
                "h": 2,
                "axis": "v",
                "color": "#a78bfa",
            },
            {
                "id": "top_shelf",
                "label": "Shelf",
                "x": 3,
                "y": 1,
                "w": 3,
                "h": 1,
                "axis": "h",
                "color": "#60a5fa",
            },
            {
                "id": "long_coat",
                "label": "Long coat",
                "x": 5,
                "y": 2,
                "w": 1,
                "h": 2,
                "axis": "v",
                "color": "#34d399",
            },
            {
                "id": "jeans",
                "label": "Jeans",
                "x": 0,
                "y": 0,
                "w": 2,
                "h": 1,
                "axis": "h",
                "color": "#93c5fd",
            },
            {
                "id": "boots",
                "label": "Boots",
                "x": 0,
                "y": 3,
                "w": 1,
                "h": 2,
                "axis": "v",
                "color": "#fbbf24",
            },
            {
                "id": "clutch",
                "label": "Clutch",
                "x": 3,
                "y": 5,
                "w": 2,
                "h": 1,
                "axis": "h",
                "color": "#fda4af",
            },
        ],
        "solution": [
            {"id": "star_blouse", "delta": -2},
            {"id": "stacked_knits", "delta": 3},
            {"id": "top_shelf", "delta": -1},
            {"id": "long_coat", "delta": -2},
            {"id": "star_blouse", "delta": 4},
        ],
    },
]


def _occupied_cells(items: list[dict], skip_id: str | None = None) -> set[tuple[int, int]]:
    cells = set()

    for item in items:
        if item["id"] == skip_id:
            continue

        for dx in range(item["w"]):
            for dy in range(item["h"]):
                cells.add((item["x"] + dx, item["y"] + dy))

    return cells


def _move_item(items: list[dict], item_id: str, delta: int, size: int = 6) -> None:
    item = next(piece for piece in items if piece["id"] == item_id)
    step = 1 if delta > 0 else -1

    for _ in range(abs(delta)):
        occupied = _occupied_cells(items, skip_id=item_id)
        next_x = item["x"] + (step if item["axis"] == "h" else 0)
        next_y = item["y"] + (step if item["axis"] == "v" else 0)

        if next_x < 0 or next_y < 0 or next_x + item["w"] > size or next_y + item["h"] > size:
            raise ValueError(f"{item_id} would leave the closet.")

        next_cells = {
            (next_x + dx, next_y + dy)
            for dx in range(item["w"])
            for dy in range(item["h"])
        }

        if next_cells & occupied:
            raise ValueError(f"{item_id} would collide with another item.")

        item["x"] = next_x
        item["y"] = next_y


def validate_puzzle_levels() -> None:
    """Validate board geometry and bundled solution paths."""
    for level in PUZZLE_LEVELS:
        items = [dict(item) for item in level["items"]]
        occupied = _occupied_cells(items)
        total_area = sum(item["w"] * item["h"] for item in items)

        if len(occupied) != total_area:
            raise ValueError(f"{level['id']} has overlapping starting items.")

        for item in items:
            if item["x"] < 0 or item["y"] < 0 or item["x"] + item["w"] > 6 or item["y"] + item["h"] > 6:
                raise ValueError(f"{level['id']} has an item outside the board.")

        for move in level["solution"]:
            _move_item(items, move["id"], move["delta"])

        target = next(item for item in items if item["id"] == level["target"])
        if target["x"] + target["w"] != 6 or target["y"] != level["exitRow"]:
            raise ValueError(f"{level['id']} solution does not free the target item.")


def render_closet_puzzle() -> None:
    """Render the playable puzzle as an embedded browser component."""
    validate_puzzle_levels()

    levels_json = html.escape(json.dumps(PUZZLE_LEVELS), quote=False)
    component_html = f"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
    :root {{
        --ink: #3b1b5a;
        --muted: #6b5878;
        --violet: #7c3aed;
        --pink: #db2777;
        --panel: rgba(255, 255, 255, 0.88);
        --line: rgba(167, 139, 250, 0.55);
        --cell: min(12.5vw, 76px);
    }}

    * {{ box-sizing: border-box; }}
    body {{
        margin: 0;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: var(--ink);
        background:
            radial-gradient(circle at 14% 12%, rgba(250, 204, 21, 0.18), transparent 26%),
            radial-gradient(circle at 84% 10%, rgba(244, 114, 182, 0.18), transparent 28%),
            linear-gradient(135deg, #fdf8ff, #fdf2f8 54%, #f8fafc);
    }}

    .shell {{
        min-height: 720px;
        padding: 18px;
    }}

    .topbar {{
        display: flex;
        gap: 16px;
        justify-content: space-between;
        align-items: flex-start;
        margin: 0 auto 16px;
        max-width: 1120px;
    }}

    .title h1 {{
        margin: 0;
        font-size: 32px;
        line-height: 1.05;
        letter-spacing: 0;
    }}

    .title p {{
        margin: 7px 0 0;
        color: var(--muted);
        max-width: 680px;
        font-size: 15px;
    }}

    .stats {{
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        justify-content: flex-end;
    }}

    .pill {{
        border: 1px solid var(--line);
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.78);
        padding: 8px 12px;
        font-weight: 750;
        color: #5b21b6;
        white-space: nowrap;
        box-shadow: 0 6px 18px rgba(124, 58, 237, 0.08);
    }}

    .layout {{
        display: grid;
        grid-template-columns: minmax(320px, 1fr) 280px;
        gap: 18px;
        align-items: start;
        max-width: 1120px;
        margin: 0 auto;
    }}

    .board-wrap {{
        position: relative;
        display: grid;
        place-items: center;
        min-height: calc(var(--cell) * 6 + 36px);
    }}

    .closet {{
        position: relative;
        width: calc(var(--cell) * 6);
        height: calc(var(--cell) * 6);
        border: 4px solid #6d28d9;
        border-radius: 18px;
        background:
            linear-gradient(rgba(124, 58, 237, 0.12) 1px, transparent 1px),
            linear-gradient(90deg, rgba(124, 58, 237, 0.12) 1px, transparent 1px),
            linear-gradient(135deg, rgba(255,255,255,0.94), rgba(245,243,255,0.82));
        background-size: var(--cell) var(--cell);
        box-shadow:
            0 22px 54px rgba(76, 29, 149, 0.18),
            inset 0 0 0 2px rgba(255, 255, 255, 0.68);
        overflow: visible;
        touch-action: none;
        user-select: none;
    }}

    .exit {{
        position: absolute;
        right: -20px;
        width: 24px;
        height: var(--cell);
        top: calc(var(--exit-row) * var(--cell));
        border-radius: 0 16px 16px 0;
        background: linear-gradient(90deg, rgba(34, 197, 94, 0.26), rgba(34, 197, 94, 0.92));
        box-shadow: 0 0 24px rgba(34, 197, 94, 0.42);
    }}

    .item {{
        position: absolute;
        left: 0;
        top: 0;
        width: calc(var(--w) * var(--cell) - 8px);
        height: calc(var(--h) * var(--cell) - 8px);
        transform: translate(calc(var(--x) * var(--cell) + 4px), calc(var(--y) * var(--cell) + 4px));
        border-radius: 12px;
        border: 2px solid rgba(87, 59, 128, 0.18);
        background:
            linear-gradient(135deg, rgba(255,255,255,0.82), rgba(255,255,255,0.28)),
            color-mix(in srgb, var(--color) 38%, white);
        color: #32124b;
        box-shadow: 0 10px 24px rgba(76, 29, 149, 0.18);
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 8px;
        font-weight: 850;
        font-size: 13px;
        line-height: 1.08;
        cursor: grab;
        transition: transform 150ms ease, box-shadow 150ms ease, filter 150ms ease;
    }}

    .item-art {{
        width: 84%;
        height: 84%;
        display: grid;
        place-items: center;
        pointer-events: none;
    }}

    .item-art svg {{
        width: 100%;
        height: 100%;
        display: block;
        overflow: visible;
    }}

    .item[data-axis="v"]::after,
    .item[data-axis="h"]::after {{
        content: attr(data-axis-label);
        position: absolute;
        right: 7px;
        bottom: 5px;
        width: 22px;
        height: 22px;
        border-radius: 999px;
        display: grid;
        place-items: center;
        background: rgba(255, 255, 255, 0.82);
        border: 1px solid rgba(91, 33, 182, 0.22);
        color: #5b21b6;
        font-size: 13px;
        line-height: 1;
        opacity: 0.92;
        box-shadow: 0 3px 8px rgba(76, 29, 149, 0.12);
    }}

    .item.target {{
        border-color: rgba(250, 204, 21, 0.96);
        outline: 3px solid rgba(250, 204, 21, 0.86);
        box-shadow:
            0 0 0 6px rgba(250, 204, 21, 0.20),
            0 0 28px rgba(250, 204, 21, 0.34),
            0 16px 32px rgba(219, 39, 119, 0.22);
    }}

    .item.dragging {{
        cursor: grabbing;
        z-index: 10;
        transition: none;
        filter: saturate(1.08);
        box-shadow: 0 20px 44px rgba(76, 29, 149, 0.24);
    }}

    .item.blocked {{
        animation: blocked 190ms ease;
    }}

    @keyframes blocked {{
        0%, 100% {{ filter: none; }}
        45% {{ filter: brightness(1.12) saturate(1.2); }}
    }}

    .closet.won .item.target {{
        filter: saturate(1.08) brightness(1.03);
    }}

    .side {{
        display: grid;
        gap: 12px;
    }}

    .panel {{
        border: 1px solid rgba(216, 180, 254, 0.74);
        border-radius: 16px;
        padding: 14px;
        background: var(--panel);
        box-shadow: 0 12px 34px rgba(124, 58, 237, 0.10);
    }}

    .panel h2 {{
        margin: 0 0 8px;
        font-size: 17px;
    }}

    .level-buttons, .controls {{
        display: grid;
        grid-template-columns: 1fr;
        gap: 8px;
    }}

    button {{
        appearance: none;
        border: 1px solid #a78bfa;
        border-radius: 12px;
        background: #ffffff;
        color: #5b21b6;
        font-weight: 800;
        padding: 10px 12px;
        cursor: pointer;
        box-shadow: 0 5px 14px rgba(124, 58, 237, 0.08);
    }}

    button:hover {{ background: #f5f3ff; }}
    button:disabled {{
        cursor: not-allowed;
        opacity: 0.48;
        box-shadow: none;
    }}

    button.active {{
        color: #ffffff;
        border-color: #7c3aed;
        background: linear-gradient(135deg, #7c3aed, #db2777);
    }}

    .message {{
        min-height: 42px;
        color: var(--muted);
        font-size: 14px;
        line-height: 1.35;
    }}

    .win {{
        display: none;
        position: absolute;
        inset: 0;
        place-items: center;
        z-index: 30;
        pointer-events: none;
        background: rgba(253, 248, 255, 0.35);
    }}

    .win.show {{
        display: grid;
    }}

    .win-card {{
        border-radius: 18px;
        padding: 18px 20px;
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid rgba(250, 204, 21, 0.72);
        color: var(--ink);
        text-align: center;
        box-shadow: 0 22px 54px rgba(76, 29, 149, 0.22);
        animation: pop 520ms ease both;
        pointer-events: auto;
        min-width: min(320px, 86vw);
    }}

    .win-card strong {{
        display: block;
        font-size: 26px;
        margin-bottom: 3px;
    }}

    .win-actions {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: 14px;
    }}

    .win-actions button:first-child {{
        color: #5b21b6;
        background: #ffffff;
    }}

    .win-actions button:last-child {{
        color: #ffffff;
        border-color: #7c3aed;
        background: linear-gradient(135deg, #7c3aed, #db2777);
    }}

    @keyframes pop {{
        from {{ opacity: 0; transform: translateY(10px) scale(.94); }}
        to {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}

    .confetti {{
        position: absolute;
        inset: 0;
        pointer-events: none;
        overflow: hidden;
    }}

    .confetti span {{
        position: absolute;
        top: -20px;
        font-size: 22px;
        animation: fall 1100ms ease-in forwards;
    }}

    @keyframes fall {{
        to {{ transform: translateY(520px) rotate(260deg); opacity: 0; }}
    }}

    @media (max-width: 820px) {{
        :root {{ --cell: min(14.2vw, 62px); }}
        .shell {{ padding: 12px; }}
        .topbar, .layout {{ grid-template-columns: 1fr; }}
        .topbar {{ display: grid; }}
        .stats {{ justify-content: flex-start; }}
        .side {{ grid-template-columns: 1fr; }}
    }}
</style>
</head>
<body>
<div class="shell">
    <div class="topbar">
        <div class="title">
            <h1>Closet Puzzle</h1>
            <p>Free the highlighted wardrobe item. Pieces slide only in their own direction, and the exit is on the glowing right edge.</p>
        </div>
        <div class="stats">
            <div class="pill" id="levelPill">Intro</div>
            <div class="pill">Moves: <span id="moves">0</span></div>
        </div>
    </div>

    <div class="layout">
        <div class="board-wrap">
            <div class="closet" id="closet" aria-label="Closet Puzzle board"></div>
            <div class="win" id="win">
                <div class="confetti" id="confetti"></div>
                <div class="win-card">
                    <strong>Outfit freed!</strong>
                    <span id="winText">The highlighted item made it out.</span>
                    <div class="win-actions">
                        <button id="winOkButton" type="button">OK</button>
                        <button id="winNextButton" type="button">Next level</button>
                    </div>
                </div>
            </div>
        </div>

        <div class="side">
            <section class="panel">
                <h2>Level</h2>
                <div class="level-buttons" id="levelButtons"></div>
            </section>
            <section class="panel">
                <h2>Controls</h2>
                <div class="controls">
                    <button id="undoButton" type="button">Undo move</button>
                    <button id="restartButton" type="button">Restart level</button>
                </div>
            </section>
            <section class="panel">
                <h2>Status</h2>
                <div class="message" id="message">Drag an item. The small arrows show whether it moves horizontally or vertically.</div>
            </section>
        </div>
    </div>
</div>

<script id="levelsData" type="application/json">{levels_json}</script>
<script>
(() => {{
    const levels = JSON.parse(document.getElementById("levelsData").textContent);
    const size = 6;
    const closet = document.getElementById("closet");
    const movesEl = document.getElementById("moves");
    const messageEl = document.getElementById("message");
    const levelPill = document.getElementById("levelPill");
    const levelButtons = document.getElementById("levelButtons");
    const undoButton = document.getElementById("undoButton");
    const restartButton = document.getElementById("restartButton");
    const win = document.getElementById("win");
    const winText = document.getElementById("winText");
    const winOkButton = document.getElementById("winOkButton");
    const winNextButton = document.getElementById("winNextButton");
    const confetti = document.getElementById("confetti");

    let levelIndex = 0;
    let state = null;
    let history = [];
    let moveCount = 0;
    let won = false;
    let winDismissed = false;
    let drag = null;

    const cloneItems = (items) => items.map((item) => ({{ ...item }}));
    const activeLevel = () => levels[levelIndex];
    const cellSize = () => closet.getBoundingClientRect().width / size;
    const itemById = (id) => state.find((item) => item.id === id);

    function cellsFor(item, x = item.x, y = item.y) {{
        const cells = [];
        for (let dx = 0; dx < item.w; dx += 1) {{
            for (let dy = 0; dy < item.h; dy += 1) {{
                cells.push(`${{x + dx}},${{y + dy}}`);
            }}
        }}
        return cells;
    }}

    function occupiedWithout(id) {{
        const occupied = new Set();
        state.forEach((item) => {{
            if (item.id !== id) cellsFor(item).forEach((cell) => occupied.add(cell));
        }});
        return occupied;
    }}

    function canPlace(item, x, y) {{
        if (x < 0 || y < 0 || x + item.w > size || y + item.h > size) return false;
        const occupied = occupiedWithout(item.id);
        return cellsFor(item, x, y).every((cell) => !occupied.has(cell));
    }}

    function legalRange(item) {{
        let min = item.axis === "h" ? item.x : item.y;
        let max = min;

        while (true) {{
            const next = min - 1;
            const x = item.axis === "h" ? next : item.x;
            const y = item.axis === "v" ? next : item.y;
            if (!canPlace(item, x, y)) break;
            min = next;
        }}

        while (true) {{
            const next = max + 1;
            const x = item.axis === "h" ? next : item.x;
            const y = item.axis === "v" ? next : item.y;
            if (!canPlace(item, x, y)) break;
            max = next;
        }}

        return {{ min, max }};
    }}

    function setMessage(text) {{
        messageEl.textContent = text;
    }}

    function itemKind(item) {{
        const id = item.id.toLowerCase();
        const label = item.label.toLowerCase();
        const text = `${{id}} ${{label}}`;

        if (text.includes("boot") || text.includes("loafer") || text.includes("shoe")) return "shoes";
        if (text.includes("denim") || text.includes("jean") || text.includes("pant")) return "pants";
        if (text.includes("tote") || text.includes("bag") || text.includes("clutch")) return "bag";
        if (text.includes("coat") || text.includes("trench")) return "coat";
        if (text.includes("dress")) return "dress";
        if (text.includes("scarf")) return "scarf";
        if (text.includes("belt")) return "belt";
        if (text.includes("shelf")) return "folded";
        return "sweater";
    }}

    function itemSvg(item) {{
        const kind = itemKind(item);
        const accent = item.color;
        const stroke = "#4b345f";
        const softStroke = "#6d557f";
        const common = `fill="${{accent}}" stroke="${{stroke}}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"`;

        if (kind === "pants") {{
            return `<svg viewBox="0 0 120 72" role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
                <path d="M38 10h44l6 52H68L60 29l-8 33H32z" ${{common}}/>
                <path d="M60 12v50" fill="none" stroke="${{stroke}}" stroke-width="4" stroke-linecap="round"/>
                <path d="M42 20h36" fill="none" stroke="${{softStroke}}" stroke-width="3"/>
                <circle cx="60" cy="19" r="2.6" fill="#fff7ed"/>
            </svg>`;
        }}

        if (kind === "shoes") {{
            return `<svg viewBox="0 0 120 92" role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
                <path d="M20 56c12 2 22-8 32-19 6 14 6 22 2 32H17c-5 0-7-9 3-13z" ${{common}}/>
                <path d="M66 56c12 2 22-8 32-19 6 14 6 22 2 32H63c-5 0-7-9 3-13z" ${{common}}/>
                <path d="M30 56h20M76 56h20" fill="none" stroke="#fff7ed" stroke-width="4" stroke-linecap="round"/>
            </svg>`;
        }}

        if (kind === "bag") {{
            return `<svg viewBox="0 0 104 104" role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
                <path d="M31 39c1-15 9-25 21-25s20 10 21 25" fill="none" stroke="${{stroke}}" stroke-width="5" stroke-linecap="round"/>
                <rect x="20" y="36" width="64" height="50" rx="12" ${{common}}/>
                <path d="M34 53h36M33 68h22" fill="none" stroke="#fff7ed" stroke-width="4" stroke-linecap="round"/>
            </svg>`;
        }}

        if (kind === "coat") {{
            return `<svg viewBox="0 0 96 128" role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
                <path d="M35 17h26l14 18-6 78H27l-6-78z" ${{common}}/>
                <path d="M36 17l12 24 12-24M48 42v70" fill="none" stroke="${{stroke}}" stroke-width="4" stroke-linecap="round"/>
                <path d="M32 55h10M54 55h10M33 76h10M54 76h10" fill="none" stroke="#fff7ed" stroke-width="4" stroke-linecap="round"/>
            </svg>`;
        }}

        if (kind === "dress") {{
            return `<svg viewBox="0 0 112 96" role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
                <path d="M44 11h24l7 18-10 12 18 41H29l18-41-10-12z" ${{common}}/>
                <path d="M44 11l12 15 12-15M40 42h32" fill="none" stroke="#fff7ed" stroke-width="4" stroke-linecap="round"/>
                <circle cx="56" cy="51" r="3" fill="#fff7ed"/>
            </svg>`;
        }}

        if (kind === "scarf") {{
            return `<svg viewBox="0 0 136 60" role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
                <rect x="17" y="20" width="86" height="22" rx="11" ${{common}}/>
                <path d="M93 20h19c9 0 14 5 14 12s-5 12-14 12H93z" ${{common}}/>
                <path d="M31 20v22M51 20v22M71 20v22M108 22v20" fill="none" stroke="#fff7ed" stroke-width="3" stroke-linecap="round"/>
            </svg>`;
        }}

        if (kind === "belt") {{
            return `<svg viewBox="0 0 132 56" role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
                <rect x="14" y="21" width="104" height="16" rx="8" ${{common}}/>
                <rect x="46" y="14" width="28" height="30" rx="7" fill="#fff7ed" stroke="${{stroke}}" stroke-width="4"/>
                <path d="M76 29h28" fill="none" stroke="${{stroke}}" stroke-width="4" stroke-linecap="round"/>
            </svg>`;
        }}

        if (kind === "folded") {{
            return `<svg viewBox="0 0 136 64" role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
                <rect x="18" y="14" width="100" height="18" rx="8" ${{common}}/>
                <rect x="28" y="30" width="84" height="18" rx="8" fill="#ffffff" stroke="${{stroke}}" stroke-width="4"/>
                <path d="M45 14c4 7 4 12 0 18M84 30c-4 7-4 12 0 18" fill="none" stroke="${{softStroke}}" stroke-width="3"/>
            </svg>`;
        }}

        return `<svg viewBox="0 0 120 82" role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
            <path d="M42 14h36l18 18-12 14-9-7v29H45V39l-9 7-12-14z" ${{common}}/>
            <path d="M47 16c3 10 23 10 26 0M48 52h24" fill="none" stroke="#fff7ed" stroke-width="4" stroke-linecap="round"/>
            <path d="M38 28l-9 7M82 28l9 7" fill="none" stroke="${{softStroke}}" stroke-width="3" stroke-linecap="round"/>
        </svg>`;
    }}

    function renderLevelButtons() {{
        levelButtons.innerHTML = "";
        levels.forEach((level, index) => {{
            const button = document.createElement("button");
            button.type = "button";
            button.textContent = `${{level.difficulty}}: ${{level.name}}`;
            button.className = index === levelIndex ? "active" : "";
            button.addEventListener("click", () => loadLevel(index));
            levelButtons.appendChild(button);
        }});
    }}

    function renderBoard() {{
        const level = activeLevel();
        closet.innerHTML = "";
        closet.classList.toggle("won", won);
        closet.style.setProperty("--exit-row", level.exitRow);

        const exit = document.createElement("div");
        exit.className = "exit";
        closet.appendChild(exit);

        state.forEach((item) => {{
            const el = document.createElement("div");
            el.className = `item${{item.id === level.target ? " target" : ""}}`;
            el.dataset.id = item.id;
            el.dataset.axis = item.axis;
            el.dataset.axisLabel = item.axis === "h" ? "↔" : "↕";
            el.setAttribute("aria-label", `${{item.label}}. Moves ${{item.axis === "h" ? "horizontally" : "vertically"}}.`);
            el.setAttribute("title", `${{item.label}}`);
            el.style.setProperty("--x", item.x);
            el.style.setProperty("--y", item.y);
            el.style.setProperty("--w", item.w);
            el.style.setProperty("--h", item.h);
            el.style.setProperty("--color", item.color);
            const art = document.createElement("div");
            art.className = "item-art";
            art.innerHTML = itemSvg(item);
            el.appendChild(art);
            el.addEventListener("pointerdown", onPointerDown);
            closet.appendChild(el);
        }});

        movesEl.textContent = moveCount;
        undoButton.disabled = history.length === 0 || won;
        levelPill.textContent = `${{level.difficulty}} · ${{level.name}}`;
        renderLevelButtons();
    }}

    function loadLevel(index) {{
        levelIndex = index;
        state = cloneItems(activeLevel().items);
        history = [];
        moveCount = 0;
        won = false;
        winDismissed = false;
        win.classList.remove("show");
        confetti.innerHTML = "";
        setMessage("Drag an item. The small arrows show whether it moves horizontally or vertically.");
        renderBoard();
    }}

    function onPointerDown(event) {{
        if (won) return;

        const el = event.currentTarget;
        const item = itemById(el.dataset.id);
        const range = legalRange(item);
        const rect = closet.getBoundingClientRect();
        const cell = cellSize();

        drag = {{
            id: item.id,
            el,
            axis: item.axis,
            startPointer: item.axis === "h" ? event.clientX : event.clientY,
            startCell: item.axis === "h" ? item.x : item.y,
            originX: item.x,
            originY: item.y,
            range,
            cell,
            blocked: false,
        }};

        el.classList.add("dragging");
        el.setPointerCapture(event.pointerId);
        window.addEventListener("pointermove", onPointerMove);
        window.addEventListener("pointerup", onPointerUp, {{ once: true }});
        event.preventDefault();
    }}

    function onPointerMove(event) {{
        if (!drag) return;

        const deltaPx = (drag.axis === "h" ? event.clientX : event.clientY) - drag.startPointer;
        const rawCell = drag.startCell + deltaPx / drag.cell;
        const clampedCell = Math.max(drag.range.min, Math.min(drag.range.max, rawCell));
        const blockedNow = Math.abs(rawCell - clampedCell) > 0.08;
        const item = itemById(drag.id);
        const x = drag.axis === "h" ? clampedCell : item.x;
        const y = drag.axis === "v" ? clampedCell : item.y;

        drag.el.style.transform = `translate(${{x * drag.cell + 4}}px, ${{y * drag.cell + 4}}px)`;
        drag.el.classList.toggle("blocked", blockedNow);

        if (blockedNow && !drag.blocked) {{
            setMessage("Blocked. Pieces cannot overlap or pass through the closet walls.");
        }}
        drag.blocked = blockedNow;
    }}

    function onPointerUp(event) {{
        if (!drag) return;

        window.removeEventListener("pointermove", onPointerMove);
        drag.el.releasePointerCapture?.(event.pointerId);
        drag.el.classList.remove("dragging", "blocked");

        const item = itemById(drag.id);
        const transform = drag.el.style.transform;
        const deltaPx = (drag.axis === "h" ? event.clientX : event.clientY) - drag.startPointer;
        const rawCell = drag.startCell + deltaPx / drag.cell;
        const nextCell = Math.max(drag.range.min, Math.min(drag.range.max, Math.round(rawCell)));
        const changed = nextCell !== drag.startCell;

        if (changed) {{
            history.push({{
                id: item.id,
                before: {{ x: drag.originX, y: drag.originY }},
                after: {{
                    x: drag.axis === "h" ? nextCell : item.x,
                    y: drag.axis === "v" ? nextCell : item.y,
                }},
            }});

            if (drag.axis === "h") item.x = nextCell;
            if (drag.axis === "v") item.y = nextCell;
            moveCount += 1;
            setMessage(`${{item.label}} moved. Nice closet choreography.`);
            checkWin();
        }} else {{
            setMessage("No move counted. Drag farther to slide an item into a new square.");
        }}

        drag = null;
        renderBoard();
    }}

    function checkWin() {{
        const level = activeLevel();
        const target = itemById(level.target);
        if (!won && target.y === level.exitRow && target.x + target.w === size) {{
            won = true;
            winDismissed = false;
            setMessage("Solved. The highlighted item is free.");
            winText.textContent = `${{target.label}} escaped in ${{moveCount}} move${{moveCount === 1 ? "" : "s"}}.`;
            winNextButton.textContent = levelIndex < levels.length - 1 ? "Next level" : "Play again";
            launchConfetti();
            window.setTimeout(() => {{
                if (!winDismissed) win.classList.add("show");
                closet.classList.add("won");
            }}, 120);
        }}
    }}

    function launchConfetti() {{
        confetti.innerHTML = "";
        const pieces = ["✦", "◆", "✧", "★", "•"];
        for (let i = 0; i < 26; i += 1) {{
            const span = document.createElement("span");
            span.textContent = pieces[i % pieces.length];
            span.style.left = `${{Math.random() * 96}}%`;
            span.style.color = ["#7c3aed", "#db2777", "#facc15", "#22c55e"][i % 4];
            span.style.animationDelay = `${{Math.random() * 260}}ms`;
            confetti.appendChild(span);
        }}
    }}

    undoButton.addEventListener("click", () => {{
        if (!history.length || won) return;
        const last = history.pop();
        const item = itemById(last.id);
        item.x = last.before.x;
        item.y = last.before.y;
        moveCount = Math.max(0, moveCount - 1);
        setMessage(`Undid ${{item.label}}.`);
        renderBoard();
    }});

    restartButton.addEventListener("click", () => {{
        loadLevel(levelIndex);
        setMessage("Level restarted.");
    }});

    winOkButton.addEventListener("click", () => {{
        winDismissed = true;
        win.classList.remove("show");
        confetti.innerHTML = "";
        setMessage("Solved board kept. Choose a level or restart whenever you like.");
    }});

    winNextButton.addEventListener("click", () => {{
        const nextIndex = levelIndex < levels.length - 1 ? levelIndex + 1 : 0;
        loadLevel(nextIndex);
    }});

    loadLevel(0);
}})();
</script>
</body>
</html>
"""

    components.html(component_html, height=780, scrolling=False)


if __name__ == "__main__":
    validate_puzzle_levels()
    print("puzzle validation ok")
