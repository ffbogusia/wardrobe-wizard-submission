# Wardrobe Dataset Summary

Wardrobe Wizard uses a sample wardrobe dataset stored in `data/wardrobe.json`.

The dataset is used for demo purposes only. It does not contain private personal data, real customer data, company data, emails, meetings, documents, or photos.

## Dataset Purpose

The dataset helps demonstrate how Wardrobe Wizard can:

* load wardrobe items from JSON,
* show wardrobe items in a Streamlit UI,
* filter items by category and style tags,
* add temporary session items,
* recommend a main outfit and an alternative outfit,
* explain outfit choices using available wardrobe data.

## Item Fields

Each wardrobe item includes:

* `id`
* `name`
* `category`
* `color`
* `style_tags`
* `season`
* `formality`
* `comfort`
* `weather`
* `notes`

## Categories

Wardrobe items can belong to these categories:

* `top`
* `bottom`
* `dress`
* `jacket`
* `shoes`
* `accessory`

## Style Tags

Style tags describe the mood or practical direction of an outfit.

Examples:

* `neutral`
* `feminine`
* `masculine`
* `streetwear`
* `elegant`
* `casual`
* `cozy`
* `office-friendly`
* `romantic`
* `minimalist`
* `sporty`
* `travel-friendly`

Style tags are not identity labels. They are flexible user preferences for a specific outfit.

## Weather and Context Tags

Weather and context tags help the recommendation engine choose practical items.

Examples:

* `warm`
* `mild`
* `cold`
* `rainy`
* `windy`
* `indoor`
* `travel`

## MVP Storage Rule

The starting wardrobe is loaded from `data/wardrobe.json`.

Items added by the user during the demo are stored only in Streamlit session state.

Added items are not permanently written back to `data/wardrobe.json` in v0.1.

## Privacy Rule

The dataset should stay synthetic and demo-friendly.

Do not add:

* real private wardrobe photos,
* personal addresses,
* customer data,
* company data,
* API keys,
* tokens,
* passwords,
* private notes.
