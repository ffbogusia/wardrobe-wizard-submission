# Rewear Impact Methodology

Wardrobe Wizard's Rewear Impact feature is an educational no-buy comparison estimate.

It answers a simple demo question:

> If this outfit is built from clothes already in the wardrobe, what rough new-production impact might be avoided compared with buying similar new items?

It does **not** answer:

- the exact lifecycle footprint of the user's real clothing,
- washing, drying, ironing, repair, transport, or disposal impacts,
- the certified environmental impact of a specific garment,
- audited carbon accounting.

## Where the numbers live

The same category estimates are kept in two places so the app behaves consistently:

```text
impact-api/src/impactEstimator.ts
src/impact_client.py
```

The TypeScript mini API is the preferred calculation path when `IMPACT_API_URL` is configured. The Python version is the fallback.

## Current category estimates

| Category | Water estimate (L) | CO₂e estimate (kg) | Estimate basis |
|---|---:|---:|---|
| Top | 2,700 | 4.3 | Public-source benchmark |
| Bottom | 3,781 | 33.4 | Public-source benchmark |
| Dress | 3,000 | 8.0 | Illustrative category estimate |
| Jacket | 4,000 | 15.0 | Illustrative category estimate |
| Shoes | 2,500 | 14.0 | Illustrative category estimate |
| Accessory | 500 | 2.0 | Illustrative category estimate |

## Source notes

The benchmark-style values for tops and bottoms are based on widely cited public textile examples such as cotton T-shirt and jeans water/CO₂e estimates. WRAP's reporting on clothing impacts also emphasizes that clothing production and disposal have material carbon, water, and waste impacts, and that extending garment use is one practical sustainability lever.

The remaining categories are deliberately labelled as illustrative because a real environmental calculation would need garment material, weight, manufacturing location, supply chain, transport, use phase, and disposal assumptions.

## Language rules

Use careful wording:

- estimated new-production impact avoided,
- no-buy comparison estimate,
- public-source benchmark,
- illustrative category estimate,
- educational estimate.

Avoid exact-savings wording:

- "you saved exactly...",
- "certified impact",
- "verified carbon reduction",
- "environmental calculator".

## Why this feature exists

The goal is not to guilt the user. The goal is to make rewearing feel visible, rewarding, and a little more magical.

Wardrobe Wizard should encourage using what the user already owns before buying something new.
