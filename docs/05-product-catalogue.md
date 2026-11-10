# Product Catalogue Baseline and Import Rules

Source: `C:\Users\DBTECH AFRICA\Downloads\Vitron_Sonar_Xiaomi_Product_Catalogue.docx`
Status: extracted and reviewed during Phase 0; not imported.

## 1. Source inventory

The document guide declares 10 category sections and 102 listed model/item entries. The extracted visible model rows total 86. This discrepancy must be resolved before treating the document as complete.

| Catalogue section | Declared entries | Extracted rows observed | Notes |
|---|---:|---:|---|
| Televisions — Vitron | 18 | 18 | Includes two prices marked not legible |
| Televisions — Xiaomi | 5 | 5 | Source description only; verify exact model numbers |
| TV wall mounts | 4 | 4 | Not included in the 10 requested product categories; classify as accessories after approval |
| Speakers & subwoofer systems | 24 | 24 | Mostly Vitron-coded models; brand mapping needs confirmation |
| Soundbars | 10 | 10 | Verify model/description consistency |
| Water dispensers | 17 | 17 | Preserve capacities only where stated |
| Refrigerators | 7 | 7 | `VDR128DS` source says 120 litres; verify before publication |
| Freezers | 2 | 2 | `VDF198SW` description appears to repeat `VDF198SG` |
| Blenders | 8 | 8 | `UX-2` and `NX-3` descriptions appear to repeat neighbouring model codes |
| Electric kettles | 7 | 7 | Material/litre/wattage only where stated |
| **Total visible rows** | — | **86** | Declared guide total is 102 |

## 2. Data preservation rules

- Preserve exact source model/item text as `source_model` and a normalized `model_number` only when normalization is unambiguous.
- Preserve source descriptions verbatim in `source_description`; structured attributes must cite their source.
- Catalogue prices are stored as `catalogue_price` with `price_currency = NULL` until currency is confirmed. Do not label them sell prices.
- `Not legible` prices must import as unavailable/unknown, never zero or estimated.
- Stock, warranty, dimensions, energy rating, connectivity, ports and images are unknown unless confirmed by supplier documentation.
- Image links/search-result references are reference metadata only. Do not publish them as verified product images.

## 3. Required normalization decisions

1. Currency: confirm whether catalogue prices are KES or another currency.
2. Brand ownership: confirm whether every speaker/soundbar/dispenser model belongs to Vitron, Sonar, Xiaomi or is unbranded.
3. Category mapping: decide whether TV wall mounts are accessories or a separate accessory category.
4. Model corrections: resolve freezer/blender description mismatches with supplier.
5. Variant strategy: determine whether finish/capacity differences are variants or separate products.
6. Missing entries: identify the 16 entries implied by the guide count but not visible in extraction.

## 4. Import pipeline proposal

1. Convert approved source into a versioned CSV/JSON extract with `source_row_id`, category, model, description, catalogue price, currency status and notes.
2. Run a dry-run validator that reports duplicate models, missing brand/category, invalid price, ambiguous model and unknown currency.
3. Create an import batch and row-level results; no catalogue records are published during import.
4. Review exceptions with the business/supplier.
5. Commit approved rows into draft products with source traceability.
6. Attach verified images/specifications and set approved commercial fields.
7. Publish through the admin publication workflow with audit history.
8. Export a reconciliation report comparing source rows, imported products and published products.

## 5. Publication blockers

- Currency and authoritative selling price not confirmed.
- Stock quantities and fulfilment availability not supplied.
- Product images are representative, not verified model-specific assets.
- Some model descriptions/specifications conflict or are incomplete.
- Legal warranty, returns and tax treatment are not present in the catalogue.
