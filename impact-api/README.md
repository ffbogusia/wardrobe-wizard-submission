# Rewear Impact Mini API

This is the TypeScript + Express mini API used by Wardrobe Wizard to calculate educational Rewear Impact estimates.

It compares rewearing items from the current wardrobe with a simplified estimate of producing similar new items.

It is not a certified carbon or water calculator.

## Endpoints

```text
GET /health
POST /api/rewear-impact
```

## Local setup

```bash
npm install
npm run build
npm start
```

By default, the API listens on port `8080`.

## Health check

```bash
curl http://localhost:8080/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "wardrobe-wizard-impact-api"
}
```

## Impact estimate

```bash
curl -X POST http://localhost:8080/api/rewear-impact \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      { "name": "Blue jeans", "category": "bottom", "favorite": true },
      { "name": "White shirt", "category": "top", "favorite": false }
    ]
  }'
```

The response includes:

- number of reused items,
- number of favorite items reused,
- estimated water litres,
- estimated CO₂e kilograms,
- per-item estimate details,
- an educational disclaimer.

## Deployment

The API is designed for Docker and Azure Container Apps.

```bash
docker build -t wardrobe-wizard-impact-api .
docker run -p 8080:8080 wardrobe-wizard-impact-api
```

The Streamlit app calls this service when `IMPACT_API_URL` is configured. If the API is unavailable, the Python fallback in `src/impact_client.py` keeps the feature working.

## Methodology

See:

```text
docs/sustainability_methodology.md
```
