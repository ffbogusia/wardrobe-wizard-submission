# Wardrobe Wizard ✨

**An AI wardrobe assistant that helps people choose outfits from clothes they already own.**

Built for the **Microsoft Agents League Contest @ AI Skills Fest 2026** — Creative Apps track.

---

## Why this exists

Most mornings, the problem is not a lack of clothes. It is too many choices, too little energy, and a familiar feeling of having nothing to wear even when the wardrobe is full.

Wardrobe Wizard is a calm decision-support app. It helps a user pick one good-enough outfit, see a real alternative, and feel a little less tempted to buy something new just because choosing feels hard.

The app is intentionally practical: local rules first, AI where it adds value, human review where it matters, and fallbacks everywhere.

---

## What it does

### Outfit recommendation

- choose a scenario: Office rainy day, Date night, Travel day, or Custom scenario
- pick up to two style vibes
- set a comfort preference
- receive a Main Outfit and an Alternative Outfit
- optionally enable Low-Energy Decision Support for a calmer one-choice flow

The actual outfit selection is **local and rule-based**. It does not depend on a generative model.

### Travel day context

Travel day supports manually entered travel context:

- departure climate: `not specified`, `hot`, `warm`, `mild`, `cold`, `rainy`
- destination climate: `not specified`, `hot`, `warm`, `mild`, `cold`, `rainy`
- season: `not specified`, `spring`, `summer`, `autumn`, `winter`
- flight type: `not specified`, `short flight`, `long-haul flight`

There is **no live weather API**. The user controls the context, and local rules interpret it.

### Browse and edit wardrobe

- browse the 36-item synthetic sample wardrobe
- filter by category and style tag
- search by item name
- mark favorites
- edit wardrobe rows in the current session
- remove session additions
- restore the full sample wardrobe

All edits are **session-only**. Nothing is written back to `data/wardrobe.json`.

### Add items with human review

Users can add one item or multiple items by describing them in natural language. The parser converts text into structured wardrobe rows, then the app shows an editable review table before anything is added.

The app includes:

- controlled vocabulary for recommendation-critical fields,
- `other` category support,
- category mismatch warnings,
- duplicate prevention inside a batch and against the current session wardrobe.

### Analyze outfit photo

When GitHub Models is configured, the app can analyze a photo for visible clothing only.

The photo analysis flow is deliberately cautious:

- no identity recognition,
- no face analysis,
- no body or attractiveness comments,
- no age, gender, ethnicity, disability, health, income, or other sensitive inferences,
- editable human review before detected items can be added,
- no permanent image storage.

If the model is unavailable, the feature fails safely and the rest of the app continues to work.

### Rewear Impact

After an outfit recommendation, Wardrobe Wizard shows an educational no-buy comparison estimate: what rough new-production water and CO₂e impact might be avoided by rewearing current wardrobe items instead of buying similar new items.

The calculation uses a real **TypeScript + Express mini API** deployed to **Azure Container Apps** when `IMPACT_API_URL` is configured. If the API is unavailable, a local Python fallback keeps the feature working.

This is not a certified environmental calculator. The wording is intentionally careful: estimated impact, no-buy comparison, public-source benchmark, illustrative category estimate.

### MCP tools

The repository includes a standalone MCP server with three tools:

- `closet_gap_detector`
- `privacy_safety_auditor`
- `outfit_debug_report`

These tools are not called by the Streamlit app. They show how selected wardrobe logic can be exposed as agent-ready tooling without presenting the MVP as a fully autonomous agent.

---

## How the recommendation engine works

The engine lives in `src/recommendation_engine.py`.

Each wardrobe item is scored against the selected scenario, style vibes, weather tags, formality, comfort preference, and favorite status.

| Factor | Points |
|---|---:|
| Style vibe match | +4 per matched vibe |
| Scenario style tag match | +3 per matched tag |
| Weather tag match | +3 per matched tag |
| Formality match | +2 |
| High comfort preference + high-comfort item | +3 |
| Medium comfort preference + high/medium comfort item | +2 |
| No comfort preference | +1 |
| Favorite item | +2 |

The highest-scoring items are assembled into the Main Outfit. The Alternative Outfit uses the same scoring while excluding Main Outfit items.

For Date night, a dress is preferred when available. For rainy, travel, and cold scenarios, the engine prefers adding a jacket/layer.

GitHub Models can help write the explanation, but the outfit itself is selected by local rules.

More detail: `docs/recommendation_rules.md`

---

## Architecture

```text
User
→ Streamlit Cloud
→ app.py
→ Streamlit Session State + data/wardrobe.json
→ local rule-based recommendation_engine.py
→ GitHub Models explanation/photo paths when configured
→ local fallbacks when external AI is unavailable
→ impact_client.py
→ Azure Container Apps Rewear Impact mini API when configured
→ local Python Rewear Impact fallback when API is unavailable
```

Visual Mermaid diagram: `docs/architecture_diagram.md`

Technical architecture notes: `docs/architecture.md`

---

## Tech stack

| Layer | Technology |
|---|---|
| UI | Python, Streamlit |
| Data | JSON, Pandas, Streamlit Session State |
| Recommendation logic | Local Python rule engine |
| Natural-language item parsing | Local Python parser |
| AI explanations | GitHub Models when configured, local fallback otherwise |
| Photo analysis | Vision-capable model when configured, safe fallback otherwise |
| Rewear Impact service | TypeScript, Node.js, Express |
| API deployment | Docker, Azure Container Apps |
| Agent-ready tooling | FastMCP |
| Development AI | GitHub Copilot |

---

## Responsible AI choices

| Choice | Why it matters |
|---|---|
| Rule-based outfit selection | Keeps recommendations inspectable and predictable |
| Human review before adding parsed/photo items | User stays in control |
| Clothing-only photo analysis | Avoids identity, body, and sensitive-trait inference |
| Session-only storage | No persistent personal wardrobe data in the MVP |
| No live weather API | No location tracking; user provides context manually |
| Fallbacks for external services | The app remains usable when APIs are unavailable |
| Educational Rewear Impact wording | Avoids exaggerated environmental claims |
| Standalone MCP safety auditor | Demonstrates agent-ready safety tooling |

Safety and privacy policy: `docs/ai_safety_and_privacy.md`

---

## Rewear Impact mini API

The API lives in:

```text
impact-api/
```

Endpoints:

```text
GET  /health
POST /api/rewear-impact
```

Local run:

```bash
cd impact-api
npm install
npm run build
npm start
```

The Streamlit app calls this API when `IMPACT_API_URL` is set. If the API is unavailable, the Python fallback in `src/impact_client.py` returns the same style of educational estimate.

API documentation: `impact-api/README.md`

Methodology: `docs/sustainability_methodology.md`

---

## Local setup

Requirements: Python 3.10+

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app runs without API keys.

To enable GitHub Models explanations and clothing-only photo analysis:

```bash
cp .env.example .env
# Add your token to .env:
GITHUB_TOKEN=your_token_here
```

To connect the Rewear Impact mini API:

```text
IMPACT_API_URL=https://your-container-app-url
```

To run MCP tools locally:

```bash
pip install -r requirements-mcp.txt
python mcp_server/wardrobe_mcp_server.py
```

---

## Azure deployment

The Rewear Impact mini API is designed for Docker and Azure Container Apps.

Recommended hackathon cost-control settings:

```text
min replicas = 0
max replicas = 1
```

Deployment notes: `docs/deployment.md`

Azure architecture notes: `docs/azure_architecture.md`

---

## Project structure

```text
wardrobe-wizard/
├── app.py
├── data/wardrobe.json
├── src/
│   ├── recommendation_engine.py
│   ├── item_parser.py
│   ├── ai_client.py
│   ├── photo_analyzer.py
│   ├── impact_client.py
│   └── corgi_mascot.py
├── impact-api/
│   ├── src/server.ts
│   ├── src/impactEstimator.ts
│   └── Dockerfile
├── mcp_server/wardrobe_mcp_server.py
├── knowledge/
├── assets/
└── docs/
```

---

## Known limitations

- Wardrobe changes are session-only.
- There is no login or persistent database in the MVP.
- There is no live weather API.
- The sample wardrobe is synthetic and intentionally small.
- GitHub Models features require a valid token, but fallbacks keep the app usable.
- Rewear Impact is educational, not certified.
- Foundry IQ is documented as a proof-of-concept/future path, not an active runtime service.
- MCP tools are standalone tools, not currently wired into the Streamlit UI.

---

## Roadmap

Possible next steps:

- persistent wardrobe storage,
- user accounts,
- outfit history and wear-frequency tracking,
- calendar/occasion planning,
- richer season and travel rules,
- optional Foundry IQ knowledge layer recreation,
- deeper agent orchestration using the MCP tools.

---

## Hackathon context

Wardrobe Wizard was built for the **Microsoft Agents League Contest @ AI Skills Fest 2026**, Creative Apps track.

GitHub Copilot was part of the development workflow as an AI-assisted development tool. It is not a runtime backend and does not serve user-facing model responses.

The project demonstrates:

- local explainable recommendation logic,
- controlled use of AI for explanation and clothing-only photo analysis,
- human review before session changes,
- fallback design for external dependencies,
- a real TypeScript mini API deployed to Azure Container Apps,
- standalone MCP tooling for future agent workflows.

---

## License

MIT. See `LICENSE`.
