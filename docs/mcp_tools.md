# Wardrobe Wizard MCP Tools

Wardrobe Wizard includes optional MCP tools that expose selected wardrobe logic as agent-ready capabilities.

These tools are not required for the Streamlit app to run. They are an optional portfolio and hackathon layer.

## Why MCP?

The Streamlit app is the user-facing wardrobe assistant.

The MCP server shows that the same project can also expose useful, responsible, tool-based logic for agents.

This supports the project story:

> Wardrobe Wizard is not only an app. It can also become a small wardrobe intelligence toolkit for agent workflows.

## Files

- `mcp_server/wardrobe_mcp_server.py`
- `requirements-mcp.txt`
- `docs/mcp_tools.md`

## Tools

### `closet_gap_detector`

Reads the sample wardrobe JSON file and checks whether the demo wardrobe has enough coverage across categories and style tags.

It returns:

- total item count,
- category counts,
- style tag counts,
- category gaps,
- style gaps,
- a sustainability note.

The goal is not to pressure the user to shop. The goal is to check demo coverage and encourage remixing existing wardrobe items first.

### `privacy_safety_auditor`

Checks AI-generated wardrobe text against the project's safety rules.

It flags risky content such as:

- identity recognition,
- body comments,
- attractiveness judgments,
- age/gender/ethnicity/health/disability or other sensitive inference.

It can also return a safer rewrite.

### `outfit_debug_report`

Analyzes an outfit description like a small debugging task.

Signature idea:

> Debug your outfit like code.

It returns:

- the main outfit issue,
- detected issues,
- the smallest safe swap,
- a low-energy choice,
- reassurance that the whole outfit does not need to be rebuilt.

## Local optional setup

Install MCP dependencies separately:

```bash
pip install -r requirements-mcp.txt