# Project Scope

Wardrobe Wizard is a hackathon MVP for choosing outfits from a sample wardrobe while keeping the user in control.

## In scope

- Python + Streamlit application
- 36-item synthetic sample wardrobe in JSON
- Local rule-based outfit recommendation
- Main Outfit and Alternative Outfit
- Style vibes with a controlled vocabulary
- Office rainy day, Date night, Travel day, and Custom scenario
- Travel context entered manually by the user
- Low-Energy Decision Support
- Browse Wardrobe with filtering, search, favorites, and inline session editing
- Add one item or multiple items using natural language
- Human review before saving parsed items
- Duplicate prevention
- Clothing-only photo analysis when GitHub Models is configured
- Human review before adding photo-detected items
- Session-only wardrobe changes
- Rewear Impact educational estimates
- TypeScript Rewear Impact mini API
- Azure Container Apps deployment path
- Local fallback for external service failures
- Standalone MCP tools for agent-ready workflows

## Out of scope for this MVP

- User accounts and login
- Persistent database storage
- Real user wardrobe cloud sync
- Live weather API
- Shopping links or purchase recommendations
- Certified environmental impact calculation
- Autonomous long-running agent behavior
- Identity recognition or face analysis
- Body, attractiveness, health, age, gender, ethnicity, disability, income, or other sensitive inferences

## Design principle

The MVP is intentionally small and controlled. It favors reliability, explainability, privacy, and fallback behavior over large feature breadth.
