import { describe, expect, it } from "vitest"
import {
  buildCatalogQuery,
  filterByText,
  sortProducts,
  DEFAULT_PAGE_SIZE,
} from "~/utils/catalog"
import type { CatalogProduct } from "~/types/catalog"

function product(partial: Partial<CatalogProduct>): CatalogProduct {
  return {
    id: "p1",
    slug: "p1",
    name: "Product",
    summary: null,
    brand: null,
    category: null,
    price: null,
    image_url: null,
    in_stock: null,
    ...partial,
  }
}

describe("buildCatalogQuery", () => {
  it("omits empty values and defaults", () => {
    expect(buildCatalogQuery({})).toEqual({})
    expect(buildCatalogQuery({ q: "  ", page: 1, page_size: DEFAULT_PAGE_SIZE })).toEqual({})
  })

  it("includes only meaningful parameters", () => {
    expect(
      buildCatalogQuery({
        q: " phone ",
        brand: "samsung",
        sort: "price_asc",
        page: 2,
        page_size: 24,
      }),
    ).toEqual({ q: "phone", brand: "samsung", sort: "price_asc", page: 2, page_size: 24 })
  })

  it("drops relevance sort and page 1", () => {
    expect(buildCatalogQuery({ sort: "relevance", page: 1 })).toEqual({})
  })
})

describe("sortProducts", () => {
  const items = [
    product({ id: "a", name: "Beta", price: { amount: "300", currency: "KES" } }),
    product({ id: "b", name: "Alpha", price: { amount: "100", currency: "KES" } }),
    product({ id: "c", name: "Gamma", price: null }),
  ]

  it("sorts by price ascending, pushing priceless items last", () => {
    const sorted = sortProducts(items, "price_asc")
    expect(sorted.map((p) => p.id)).toEqual(["b", "a", "c"])
  })

  it("sorts by price descending", () => {
    const sorted = sortProducts(items, "price_desc")
    expect(sorted.map((p) => p.id)).toEqual(["a", "b", "c"])
  })

  it("sorts by name", () => {
    const sorted = sortProducts(items, "name")
    expect(sorted.map((p) => p.name)).toEqual(["Alpha", "Beta", "Gamma"])
  })

  it("returns a new array and does not mutate input for relevance", () => {
    const sorted = sortProducts(items, "relevance")
    expect(sorted).not.toBe(items)
    expect(sorted.map((p) => p.id)).toEqual(["a", "b", "c"])
  })
})

describe("filterByText", () => {
  const items = [
    product({ name: "Samsung Phone", brand: { slug: "samsung", name: "Samsung" } }),
    product({ name: "LG Fridge", category: { slug: "fridges", name: "Fridges" } }),
  ]

  it("returns all items for empty text", () => {
    expect(filterByText(items, "  ")).toHaveLength(2)
  })

  it("matches name, brand and category case-insensitively", () => {
    expect(filterByText(items, "samsung").map((p) => p.name)).toEqual(["Samsung Phone"])
    expect(filterByText(items, "fridge").map((p) => p.name)).toEqual(["LG Fridge"])
  })
})
