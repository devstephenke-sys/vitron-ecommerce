# Product Catalogue Baseline and Import Rules

Source: `C:\Users\DBTECH AFRICA\Downloads\Vitron_Sonar_Xiaomi_Product_Catalogue.docx`
Status: extracted, counter-checked and reviewed during Phase 0; not imported.

## 1. Source inventory

The document guide declares 10 category sections and 102 listed model/item entries. A table-level extraction of the DOCX confirms 102 data rows across 10 product tables, matching the declared total. A flattened catalogue listing supplied during review was also checked and contains the same 102 model/price rows across the same sections.

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
| **Total** | **102** | **102** | Row count reconciled; content still requires supplier validation |

## 2. Counter-check notes

- The earlier apparent shortage of 16 rows was an extraction artifact: the first pass read text lines rather than DOCX table rows, while each product row spans multiple text lines.
- Table-level parsing found one header row plus the declared data rows in each of the 10 product tables.
- The pasted flattened listing uses different ordering inside the audio sections and contains OCR/source artifacts such as `Systerm`, `WEBOS`, `ONAR` and truncated phrases like `New produc`. These artifacts must not be copied into structured product attributes.
- The DOCX descriptions are cleaner than the flattened paste but are still secondary representations of the source PDF. Treat both as catalogue references until supplier confirmation.

## 3. Data preservation rules

- Preserve exact source model/item text as `source_model` and a normalized `model_number` only when normalization is unambiguous.
- Preserve source descriptions verbatim in `source_description`; structured attributes must cite their source.
- Catalogue prices are stored as `catalogue_price` with `price_currency = 'KES'` (currency confirmed 2026-11-13). Do not label them sell prices until authoritative pricing is approved.
- `Not legible` prices must import as unavailable/unknown, never zero or estimated.
- Stock, warranty, dimensions, energy rating, connectivity, ports and images are unknown unless confirmed by supplier documentation.
- Image links/search-result references are reference metadata only. Do not publish them as verified product images.

## 4. Required normalization decisions

1. Currency: resolved — catalogue prices are KES (Kenyan Shilling, ISO-4217 `KES`), confirmed 2026-11-13.
2. Brand ownership: confirm whether every speaker/soundbar/dispenser model belongs to Vitron, Sonar, Xiaomi or is unbranded.
3. Category mapping: decide whether TV wall mounts are accessories or a separate accessory category.
4. Model corrections: resolve freezer/blender description mismatches and source typos with supplier.
5. Variant strategy: determine whether finish/capacity differences are variants or separate products.
6. Price authority: confirm whether catalogue prices are current shop selling prices or wholesale/reference prices.

## 5. Import pipeline proposal

1. Convert approved source into a versioned CSV/JSON extract with `source_row_id`, category, model, description, catalogue price, currency status and notes.
2. Run a dry-run validator that reports duplicate models, missing brand/category, invalid price, ambiguous model and unknown currency.
3. Create an import batch and row-level results; no catalogue records are published during import.
4. Review exceptions with the business/supplier.
5. Commit approved rows into draft products with source traceability.
6. Attach verified images/specifications and set approved commercial fields.
7. Publish through the admin publication workflow with audit history.
8. Export a reconciliation report comparing source rows, imported products and published products.

## 6. Publication blockers

- Currency and authoritative selling price not confirmed.
- Stock quantities and fulfilment availability not supplied.
- Product images are representative, not verified model-specific assets.
- Some model descriptions/specifications conflict or contain source typos.
- Legal warranty, returns and tax treatment are not present in the catalogue.
