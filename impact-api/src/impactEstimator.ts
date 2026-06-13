export type WardrobeItemInput = {
  id?: string;
  name?: string;
  category?: string;
  favorite?: boolean;
};

type CategoryEstimate = {
  waterLiters: number;
  co2eKg: number;
  confidence: "public-source-benchmark" | "illustrative-category-estimate";
  note: string;
};

const IMPACT_ESTIMATES: Record<string, CategoryEstimate> = {
  top: {
    waterLiters: 2700,
    co2eKg: 4.3,
    confidence: "public-source-benchmark",
    note: "Top estimate uses public textile examples such as cotton T-shirt water use and shirt CO2e examples.",
  },
  bottom: {
    waterLiters: 3781,
    co2eKg: 33.4,
    confidence: "public-source-benchmark",
    note: "Bottom estimate uses public jeans examples for water and CO2e impact.",
  },
  dress: {
    waterLiters: 3000,
    co2eKg: 8.0,
    confidence: "illustrative-category-estimate",
    note: "Simplified demo estimate for a dress-like garment.",
  },
  jacket: {
    waterLiters: 4000,
    co2eKg: 15.0,
    confidence: "illustrative-category-estimate",
    note: "Simplified demo estimate for an outer layer.",
  },
  shoes: {
    waterLiters: 2500,
    co2eKg: 14.0,
    confidence: "illustrative-category-estimate",
    note: "Simplified demo estimate for footwear.",
  },
  accessory: {
    waterLiters: 500,
    co2eKg: 2.0,
    confidence: "illustrative-category-estimate",
    note: "Simplified demo estimate for small accessories.",
  },
};

const CATEGORY_ALIASES: Record<string, string> = {
  tops: "top",
  shirt: "top",
  tshirt: "top",
  "t-shirt": "top",
  sweater: "top",
  knit: "top",
  pants: "bottom",
  jeans: "bottom",
  trousers: "bottom",
  skirt: "bottom",
  coat: "jacket",
  blazer: "jacket",
  cardigan: "jacket",
  boot: "shoes",
  boots: "shoes",
  sneaker: "shoes",
  sneakers: "shoes",
  slipper: "shoes",
  slippers: "shoes",
  bag: "accessory",
  scarf: "accessory",
  necklace: "accessory",
};

function normalizeCategory(category: unknown): string {
  if (typeof category !== "string") {
    return "accessory";
  }

  const cleaned = category.trim().toLowerCase().replace("_", "-");

  if (cleaned in IMPACT_ESTIMATES) {
    return cleaned;
  }

  return CATEGORY_ALIASES[cleaned] ?? "accessory";
}

function roundOneDecimal(value: number): number {
  return Math.round(value * 10) / 10;
}

export function calculateRewearImpact(items: WardrobeItemInput[]) {
  const safeItems = Array.isArray(items) ? items : [];

  const itemImpacts = safeItems.map((item) => {
    const category = normalizeCategory(item.category);
    const estimate = IMPACT_ESTIMATES[category];

    return {
      id: item.id ?? null,
      name: item.name ?? "Unnamed wardrobe item",
      category,
      favorite: Boolean(item.favorite),
      estimatedWaterLiters: estimate.waterLiters,
      estimatedCo2eKg: estimate.co2eKg,
      confidence: estimate.confidence,
      note: estimate.note,
    };
  });

  const waterLiters = itemImpacts.reduce(
    (total, item) => total + item.estimatedWaterLiters,
    0,
  );

  const co2eKg = itemImpacts.reduce(
    (total, item) => total + item.estimatedCo2eKg,
    0,
  );

  const favoriteItemsUsed = itemImpacts.filter((item) => item.favorite).length;

  return {
    mode: "local educational estimate",
    impactKind: "estimated new-production impact avoided",
    summary: {
      itemsReused: itemImpacts.length,
      favoriteItemsUsed,
      waterLiters,
      co2eKg: roundOneDecimal(co2eKg),
    },
    spell: "Rewear spell unlocked: you built a look from clothes already in the wardrobe.",
    noBuyMessage:
      "This is a no-buy comparison estimate. It shows the potential impact of rewearing existing items instead of buying similar new ones.",
    disclaimer:
      "This is not a certified carbon or water calculator. It uses simplified category-level estimates for education and demo storytelling.",
    itemImpacts,
  };
}