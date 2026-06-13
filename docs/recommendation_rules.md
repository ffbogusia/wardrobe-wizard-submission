# Wardrobe Wizard Recommendation Rules

Wardrobe Wizard uses a rule-based recommendation engine for the core outfit logic.

The goal is to keep outfit recommendations explainable, stable, and safe even when external AI services are unavailable.

## Why rule-based recommendations?

The app is designed for calm decision support.

A fully generative outfit system could produce inconsistent or hard-to-explain results. Wardrobe Wizard instead uses predictable matching rules first, and optional AI explanations second.

This gives the project a more trustworthy structure:

- the outfit selection is controlled by local Python logic,
- the user can understand why an outfit was selected,
- the app can still work without an API key,
- the assistant can support low-energy decisions without overwhelming the user.

## Main recommendation file

The main recommendation logic is stored in:

```text
src/recommendation_engine.py
```

## Input data

The recommendation engine works with wardrobe items from:

```text
data/wardrobe.json
```

Each wardrobe item includes fields such as:

- `id`
- `name`
- `category`
- `color`
- `style_tags`
- `season`
- `formality`
- `comfort`
- `weather`
- `notes`

## Outfit structure

The engine tries to build a usable outfit from available wardrobe categories.

Typical outfit components include:

- top,
- bottom,
- dress,
- jacket,
- shoes,
- accessory.

The app can return:

- a main outfit,
- an alternative outfit,
- a practical explanation.

## Matching signals

Wardrobe Wizard considers several signals when recommending an outfit.

### Scenario

The selected scenario gives the engine context.

Example scenarios:

- office rainy day,
- date night,
- travel day,
- custom user scenario.

The scenario can influence weather needs, formality level, and comfort expectations.

### Style vibes

The user can choose up to two style or vibe tags.

This keeps the interface simple and avoids overwhelming the user with too many choices.

Examples:

- feminine,
- streetwear,
- elegant,
- cozy,
- practical,
- office-friendly.

### Comfort preference

Comfort is treated as an important decision factor.

The app is not only trying to create a stylish outfit. It also tries to recommend something wearable and realistic for the user’s day.

### Weather fit

Weather-related tags help the app choose better layers and shoes.

For example, a rainy day scenario should prefer items that make sense in wet weather.

### Formality

Formality helps the app avoid mismatched outfits.

For example, an office scenario should lean toward more polished items than a relaxed weekend scenario.

## Low-Energy Decision Support

Wardrobe Wizard includes a Low-Energy decision support option.

When enabled, the app should reduce decision fatigue by making the recommendation feel simpler and calmer.

The goal is not to show every possible outfit combination.

The goal is to help the user choose one good enough outfit and move on.

Low-energy behavior should support:

- fewer choices,
- clearer recommendation,
- practical reassurance,
- no pressure to optimize everything.

## Main outfit and alternative outfit

The app provides a main outfit and an alternative outfit.

This gives the user flexibility without creating too many decisions.

The alternative outfit is useful when:

- the main outfit does not feel right,
- the weather changes,
- the user wants a slightly different vibe,
- one item is unavailable.

## AI explanation layer

Wardrobe Wizard can use GitHub Models to generate a more natural explanation.

However, the recommendation should not depend fully on external AI.

The safe design is:

```text
rule-based outfit selection first
optional AI explanation second
fallback explanation if AI is unavailable
```

This keeps the app usable even without a working API key.

## Human review principle

Wardrobe Wizard should not force AI decisions onto the user.

The user remains in control.

This is especially important in:

- outfit recommendations,
- photo analysis,
- adding detected items to the session wardrobe.

The app should support the user, not replace the user’s judgment.

## Safety principles

Recommendation logic should avoid:

- body comments,
- attractiveness judgments,
- identity recognition,
- age/gender/ethnicity/health/disability or other sensitive inference,
- pressure to buy new clothes.

The assistant should focus on:

- clothing,
- colors,
- layers,
- comfort,
- formality,
- weather fit,
- occasion fit.

## Sustainability principle

Wardrobe Wizard should prioritize remixing existing wardrobe items.

The app should not create unnecessary shopping pressure.

When gaps are detected, the recommendation should be framed carefully as optional wardrobe coverage, not as a demand to buy more.

## Design summary

Wardrobe Wizard recommendations should be:

- explainable,
- practical,
- calm,
- privacy-safe,
- low-pressure,
- useful even without external AI,
- friendly to users who experience decision fatigue.