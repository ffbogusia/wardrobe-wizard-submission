import cors from "cors";
import express from "express";
import { calculateRewearImpact, type WardrobeItemInput } from "./impactEstimator.js";

const app = express();

app.use(cors());
app.use(express.json({ limit: "1mb" }));

app.get("/health", (_request, response) => {
  response.json({
    status: "ok",
    service: "wardrobe-wizard-impact-api",
  });
});

app.post("/api/rewear-impact", (request, response) => {
  const items = request.body?.items;

  if (!Array.isArray(items)) {
    return response.status(400).json({
      error: "Invalid request body.",
      expected: {
        items: [
          {
            name: "Black tee",
            category: "top",
          },
        ],
      },
    });
  }

  const impact = calculateRewearImpact(items as WardrobeItemInput[]);

  return response.json(impact);
});

const port = Number(process.env.PORT ?? 8080);

app.listen(port, "0.0.0.0", () => {
  console.log(`Wardrobe Wizard Impact API is running on port ${port}`);
});