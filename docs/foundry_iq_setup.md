# Foundry IQ Proof-of-Concept Status

Wardrobe Wizard previously had a Foundry IQ / Azure AI Search proof-of-concept.

## What was proven

A Foundry project and knowledge setup were used to test whether project-specific wardrobe guidance files could support an assistant-style answer.

The relevant knowledge files remain in this repository:

```text
knowledge/outfit_matching_guide.md
knowledge/wardrobe_style_rules.md
knowledge/wardrobe_dataset_summary.md
```

## Current status

Foundry IQ is not an active runtime dependency of the current Streamlit app.

The Azure AI Search / Foundry IQ Search Service was intentionally deleted for cost control. This is not an application bug. The core app continues to work through:

- local rule-based recommendation,
- GitHub Models explanation/photo paths when configured,
- local fallbacks,
- the Rewear Impact mini API and Python fallback.

## How to describe it publicly

Safe wording:

> Foundry IQ was explored as a documented proof-of-concept knowledge layer. The current MVP does not require it at runtime; the Azure AI Search service was removed for cost control and can be recreated later if the project grows.

Avoid wording that suggests Foundry IQ is currently serving production responses.

## Possible future recreation

If the project needs a richer knowledge layer later:

1. Recreate Azure AI Search / Foundry IQ resources.
2. Upload the files from `knowledge/`.
3. Test with wardrobe guidance questions.
4. Update the architecture diagram only after the live integration is active again.

For the Creative Apps hackathon submission, the project can rely on GitHub Copilot as the required AI-assisted development tool while keeping Foundry IQ as documented future architecture.
