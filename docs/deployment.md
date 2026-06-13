# Deployment Guide

## Streamlit Cloud (main app)

1. Push the repository to GitHub (public).
2. Go to https://share.streamlit.io and connect your repo.
3. Set `app.py` as the entry point.
4. Add secrets in the Streamlit Cloud settings panel:

```toml
GITHUB_TOKEN = "your_github_token"
IMPACT_API_URL = "https://your-container-app-url"
```

Do not commit `.streamlit/secrets.toml` to the repository.

---

## Azure Container Apps (Rewear Impact mini API)

### Prerequisites

- Azure CLI installed and logged in (`az login`)
- Docker installed
- An Azure resource group and Azure Container Registry

### Build and push

```bash
cd impact-api

# Option A: build locally and push
docker build -t wardrobe-wizard-impact-api .
docker tag wardrobe-wizard-impact-api <acr-name>.azurecr.io/wardrobe-wizard-impact-api:latest
az acr login --name <acr-name>
docker push <acr-name>.azurecr.io/wardrobe-wizard-impact-api:latest

# Option B: build directly in ACR (no local Docker needed)
az acr build --registry <acr-name> --image wardrobe-wizard-impact-api:latest .
```

### Create Container Apps environment

```bash
az containerapp env create \
  --name wardrobe-wizard-env \
  --resource-group <rg-name> \
  --location eastus
```

### Deploy

```bash
az containerapp create \
  --name wardrobe-wizard-impact-api \
  --resource-group <rg-name> \
  --environment wardrobe-wizard-env \
  --image <acr-name>.azurecr.io/wardrobe-wizard-impact-api:latest \
  --target-port 8080 \
  --ingress external \
  --min-replicas 0 \
  --max-replicas 1
```

### Verify

```bash
# Get the public URL
az containerapp show \
  --name wardrobe-wizard-impact-api \
  --resource-group <rg-name> \
  --query properties.configuration.ingress.fqdn \
  --output tsv

# Test health endpoint
curl https://<your-fqdn>/health
```

Expected response:
```json
{"status":"ok","service":"wardrobe-wizard-impact-api"}
```

---

## Tearing down (after submission period)

```bash
# Delete the entire resource group (removes all resources at once)
az group delete --name <rg-name> --yes --no-wait

# Verify nothing is left
az group list --output table
```

Check for any remaining paid resources before deleting:

```bash
az resource list --resource-group <rg-name> --output table
```

Potentially paid items to confirm are gone:
- Azure Container Apps environment
- Azure Container Registry
- Log Analytics workspace