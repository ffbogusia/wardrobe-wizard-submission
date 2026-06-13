# AI Safety and Privacy Policy

Wardrobe Wizard is designed as a wardrobe assistant, not a personal identity or body analysis system.

## Core safety rule

The app may analyze visible clothing.

It must not:

- identify a person,
- analyze faces,
- judge attractiveness,
- comment on body shape or weight,
- infer age, gender, ethnicity, disability, health, pregnancy, religion, income, profession, or other sensitive traits,
- store uploaded photos permanently.

## Outfit recommendation

Outfit selection is local and rule-based. The recommendation engine scores wardrobe items using visible and user-provided item metadata such as:

- category,
- style tags,
- weather tags,
- formality,
- comfort,
- favorite status.

No generative model chooses the actual outfit.

## AI explanations

When GitHub Models is configured, the app may use a model to write a warmer explanation of why an outfit works.

If the model is unavailable, the app uses a local fallback explanation.

## Photo analysis

The current photo analysis feature uses a clothing-only prompt. The model is instructed to describe garments and avoid identity, face, body, attractiveness, and sensitive-trait inferences.

Detected clothing items are not added automatically. They are shown in an editable human review table first.

## Session-only storage

Wardrobe additions and edits are stored only in Streamlit Session State. They are not written to `data/wardrobe.json` and disappear after the session is reset or reloaded.

## Rewear Impact

Rewear Impact is an educational no-buy comparison estimate. It is not a certified carbon or water calculator.

The UI should describe the result as:

- estimated new-production impact avoided,
- no-buy comparison estimate,
- illustrative category estimate,
- public-source benchmark.

It should not say that the user saved an exact amount of water or CO₂e.

## MCP safety tooling

The MCP server includes `privacy_safety_auditor`, a standalone tool for checking generated wardrobe text for unsafe personal or body-related claims.

This tool is not a replacement for careful prompt design or human review, but it demonstrates how safety checks can be exposed for future agent workflows.
