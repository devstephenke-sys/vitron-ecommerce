/**
 * Local catalogue types for Phase 3 UI work.
 *
 * These mirror the planned `/products` contract (docs/04-api-contracts.md §3).
 * When Phase 4 implements the catalogue API and regenerates
 * `packages/contracts`, these should be replaced by the generated types.
 */

export interface Money {
  amount: string // decimal string, never a float
  currency: string // ISO-4217, e.g. "KES"
}

export interface CatalogProduct {
  id: string
  slug: string
  name: string
  summary: string | null
  brand: { slug: string; name: string } | null
  category: { slug: string; name: string } | null
  price: Money | null
  image_url: string | null
  in_stock: boolean | null
}

export interface ProductDetail extends CatalogProduct {
  description: string | null
  model_number: string | null
  attributes: { key: string; label: string; value: string; unit: string | null }[]
  images: { url: string; alt_text: string | null }[]
}

export interface PagedResult<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface CatalogQuery {
  q?: string
  brand?: string
  category?: string
  sort?: "relevance" | "price_asc" | "price_desc" | "name"
  page?: number
  page_size?: number
}
