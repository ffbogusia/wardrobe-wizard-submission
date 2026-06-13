# Manual Test Plan

This file contains simple manual test cases for Wardrobe Wizard.

The goal is to make sure the MVP features work before I''ll make a demo video.

## Test Area 1 — App Startup

### Test 1.1 — Open the app

**Steps:**

1. Run the Streamlit app.
2. Open the app in the browser.

**Expected result:**

* The app shows the title `Wardrobe Wizard ✨`.
* The app shows a short project description.
* The app does not show a Python error.

## Test Area 2 — View Wardrobe

### Test 2.1 — View all wardrobe items

**Steps:**

1. Open the `View Wardrobe` tab.
2. Select `All items` in the category filter.
3. Select `All style tags` in the style tag filter.
4. Leave the search field empty.

**Expected result:**

* The app shows all wardrobe items from the current session.
* The table includes item name, category, color, style tags, season, comfort, weather, and notes.

### Test 2.2 — Filter by category

**Steps:**

1. Open the `View Wardrobe` tab.
2. Select one category, for example `shoes`.

**Expected result:**

* The table shows only items from the selected category.

### Test 2.3 — Filter by style tag

**Steps:**

1. Open the `View Wardrobe` tab.
2. Select one style tag, for example `office-friendly`.

**Expected result:**

* The table shows only items that include the selected style tag.

### Test 2.4 — Search wardrobe

**Steps:**

1. Open the `View Wardrobe` tab.
2. Type a search word, for example `black`, `rainy`, or `office`.

**Expected result:**

* The table shows only items matching the search text.
* If no items match, the app shows a friendly warning.

## Test Area 3 — Add One Item

### Test 3.1 — Add a single item

**Steps:**

1. Open the `Add Items` tab.
2. Open `Add one item`.
3. Paste this example: Pink satin top, feminine, spring/summer, medium comfort, date night
4. Check the preview.
5. Click `Add this item to wardrobe`.
6. Open the `View Wardrobe` tab.
7. Search for `pink`.

**Expected result:**

* The item appears in the preview before adding.
* After clicking the button, the item is added to the current session wardrobe.
* The new item appears in `View Wardrobe`.
* The item ID starts with `custom_`.

## Test Area 4 — Add Multiple Items

### Test 4.1 — Add multiple items

**Steps:**

1. Open the `Add Items` tab.
2. Open `Add multiple items`.
3. Paste these example lines:

   * Navy blazer, office-friendly, autumn, medium comfort
   * Cream knit sweater, cozy, winter, high comfort
   * Black loafers, elegant, office, medium comfort
4. Check the preview table.
5. Click `Add all items to wardrobe`.
6. Open the `View Wardrobe` tab.
7. Search for `navy`, `cream`, or `loafers`.

**Expected result:**

* The app creates structured wardrobe items from each line.
* The added items appear in the current session wardrobe.
* The total item count increases.
* The added items are not saved permanently to `data/wardrobe.json`.

## Test Area 5 — MVP Limitations

### Test 5.1 — Session-only storage

**Steps:**

1. Add a custom item.
2. Restart or refresh the app session.

**Expected result:**

* The custom item may disappear after the session resets.
* This is expected for v0.1.
* Added items are stored only in Streamlit session state.
