/**
 * Pure catalogue helpers: query-string building, client-side sort/filter.
 * Kept free of Nuxt/Pinia dependencies so they are unit-testable.
 */

import type { CatalogProduct, CatalogQuery } from "~/types/catalog"

export const DEFAULT_PAGE_SIZE = 12
export const PAGE_SIZE_OPTIONS = [12, 24, 48] as const

export const SORT_OPTIONS = [
  { value: "relevance", label: "Relevance" },
  { value: "price_asc", label: "Price: low to high" },
  { value: "price_desc", label: "Price: high to low" },
  { value: "name", label: "Name A–Z" },
] as const

/** Build the `/products` query string, omitting empty values. */
export function buildCatalogQuery(query: CatalogQuery): Record<string, string | number> {
  const params: Record<string, string | number> = {}
  if (query.q?.trim()) params.q = query.q.trim()
  if (query.brand) params.brand = query.brand
  if (query.category) params.category = query.category
  if (query.sort && query.sort !== "relevance") params.sort = query.sort
  if (query.page && query.page > 1) params.page = query.page
  if (query.page_size && query.page_size !== DEFAULT_PAGE_SIZE) params.page_size = query.page_size
  return params
}

function priceValue(product: CatalogProduct): number {
  if (!product.price) return Number.NaN
  const n = Number(product.price.amount)
  return Number.isFinite(n) ? n : Number.NaN
}

/** Priceless/invalid-price items always sort last, in both directions. */
function compareByPrice(a: CatalogProduct, b: CatalogProduct, dir: 1 | -1): number {
  const pa = priceValue(a)
  const pb = priceValue(b)
  const aMissing = Number.isNaN(pa)
  const bMissing = Number.isNaN(pb)
  if (aMissing && bMissing) return 0
  if (aMissing) return 1
  if (bMissing) return -1
  return dir * (pa - pb)
}

/** Sort a product list in place-safe fashion (returns a new array). */
export function sortProducts(products: CatalogProduct[], sort: CatalogQuery["sort"]): CatalogProduct[] {
  const sorted = [...products]
  switch (sort) {
    case "price_asc":
      return sorted.sort((a, b) => compareByPrice(a, b, 1))
    case "price_desc":
      return sorted.sort((a, b) => compareByPrice(a, b, -1))
    case "name":
      return sorted.sort((a, b) => a.name.localeCompare(b.name))
    default:
      return sorted
  }
}

/** Client-side text filter used for instant filtering of loaded results. */
export function filterByText(products: CatalogProduct[], text: string): CatalogProduct[] {
  const needle = text.trim().toLowerCase()
  if (!needle) return products
  return products.filter((p) =>
    [p.name, p.summary, p.brand?.name, p.category?.name]
      .filter(Boolean)
      .some((field) => String(field).toLowerCase().includes(needle)),
  )
}
