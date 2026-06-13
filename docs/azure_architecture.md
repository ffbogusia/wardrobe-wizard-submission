# Azure Architecture

Wardrobe Wizard uses Azure for one real runtime component: the Rewear Impact mini API deployed to Azure Container Apps.

The core Streamlit app remains usable without Azure. If the mini API is unavailable, the Python fallback keeps the Rewear Impact feature working.

## Active Azure runtime path

```text
Streamlit app
→ src/impact_client.py
→ IMPACT_API_URL
→ Azure Container Apps
→ TypeScript + Express mini API
→ POST /api/rewear-impact
```

## Mini API

Folder:

```text
impact-api/
```

Endpoints:

```text
GET /health
POST /api/rewear-impact
```

Technology:

- TypeScript
- Node.js
- Express
- Docker multi-stage build
- Azure Container Apps

## Cost-aware settings

Recommended settings for the hackathon demo period:

```text
min replicas = 0
max replicas = 1
```

This allows the container app to scale to zero when idle and keeps the API small and cost-aware.

## Fallback behavior

If `IMPACT_API_URL` is not configured or the Azure endpoint is unavailable:

```text
src/impact_client.py
→ calculate_local_rewear_impact()
→ local Python educational estimate
```

The UI displays the calculation mode so the user can see whether the mini API or fallback was used.

## Foundry IQ / Azure AI Search status

A Foundry IQ / Azure AI Search proof-of-concept existed earlier. It showed that project knowledge files could be used by a Foundry agent for wardrobe guidance.

Current status:

- The Azure AI Search / Foundry IQ Search Service was intentionally deleted for cost control.
- Foundry IQ is not required for the current Streamlit MVP.
- Foundry IQ is documented as a possible future architecture path, not as an active runtime dependency.
- The `knowledge/` files remain in the repository for future recreation if needed.

## GitHub Models

GitHub Models is used by the application when a token is configured:

- `src/ai_client.py` for outfit explanations
- `src/photo_analyzer.py` for clothing-only photo analysis

Both paths have local/safe fallbacks.

## Cleanup after judging

After the contest evaluation period, the safest cost cleanup is to delete the whole resource group that contains the Container App, its environment, the container registry if created, and Log Analytics resources.

Example command, only after confirming the resource group name:

```bash
az group delete --name <resource-group-name> --yes --no-wait
```

Before deleting, export or save:

- the Container App URL,
- screenshots needed for the README or submission,
- any deployment commands you want to keep,
- cost screenshots if useful for portfolio notes.
