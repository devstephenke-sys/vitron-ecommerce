import { defineStore } from "pinia"
import { computed, ref } from "vue"
import type { CatalogProduct, CatalogQuery, PagedResult, ProductDetail } from "~/types/catalog"
import { buildCatalogQuery, DEFAULT_PAGE_SIZE } from "~/utils/catalog"

export type CatalogStatus = "idle" | "loading" | "ready" | "error"

/**
 * Catalogue browsing state for the storefront.
 *
 * Phase 3 builds the UI against the planned contract; the backend
 * catalogue endpoints arrive in Phase 4. Until then fetches surface the
 * API error and pages render their error/empty states.
 */
export const useCatalogStore = defineStore("catalog", () => {
  const items = ref<CatalogProduct[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref<number>(DEFAULT_PAGE_SIZE)
  const status = ref<CatalogStatus>("idle")
  const error = ref<string | null>(null)
  const lastQuery = ref<CatalogQuery>({})

  const hasMore = computed(() => page.value * pageSize.value < total.value)

  async function fetchProducts(query: CatalogQuery = {}) {
    status.value = "loading"
    error.value = null
    lastQuery.value = query
    try {
      const { apiFetch } = useApi()
      const params = buildCatalogQuery({ ...query, page: query.page ?? 1, page_size: query.page_size ?? pageSize.value })
      const result = await apiFetch<PagedResult<CatalogProduct>>("/products", {
        query: params,
      })
      items.value = result.items
      total.value = result.total
      page.value = result.page
      pageSize.value = result.page_size
      status.value = "ready"
    } catch (e) {
      const apiError = e as { message?: string }
      error.value = apiError.message ?? "Failed to load products"
      items.value = []
      total.value = 0
      status.value = "error"
    }
  }

  async function fetchProduct(slug: string): Promise<ProductDetail | null> {
    try {
      const { apiFetch } = useApi()
      return await apiFetch<ProductDetail>(`/products/${encodeURIComponent(slug)}`)
    } catch {
      return null
    }
  }

  function reset() {
    items.value = []
    total.value = 0
    page.value = 1
    status.value = "idle"
    error.value = null
    lastQuery.value = {}
  }

  return {
    items,
    total,
    page,
    pageSize,
    status,
    error,
    lastQuery,
    hasMore,
    fetchProducts,
    fetchProduct,
    reset,
  }
})
