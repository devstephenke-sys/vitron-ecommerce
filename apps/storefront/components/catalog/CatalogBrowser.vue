<script setup lang="ts">
import type { CatalogQuery } from "~/types/catalog"
import { DEFAULT_PAGE_SIZE } from "~/utils/catalog"

/**
 * Reusable catalogue browser: toolbar (search/sort), product grid,
 * pagination and API state handling. Used by /products, /brands/[slug]
 * and /categories/[slug]; filter state is mirrored into the URL query.
 */
const props = withDefaults(
  defineProps<{
    brand?: string
    category?: string
    heading?: string
    description?: string
  }>(),
  { heading: "All products", description: "" },
)

const route = useRoute()
const router = useRouter()
const catalog = useCatalogStore()

const search = ref("")
const sort = ref<string>("relevance")
const page = ref(1)
const pageSize = DEFAULT_PAGE_SIZE

let debounceTimer: ReturnType<typeof setTimeout> | null = null

function currentQuery(): CatalogQuery {
  return {
    q: search.value.trim() || undefined,
    brand: props.brand,
    category: props.category,
    sort: sort.value as CatalogQuery["sort"],
    page: page.value,
    page_size: pageSize,
  }
}

async function load() {
  await catalog.fetchProducts(currentQuery())
  syncUrl()
}

function syncUrl() {
  const query: Record<string, string> = {}
  const q = search.value.trim()
  if (q) query.q = q
  if (sort.value !== "relevance") query.sort = sort.value
  if (page.value > 1) query.page = String(page.value)
  // Preserve unrelated query params (e.g. utm) but drop stale page when
  // filters change — page resets to 1 on filter changes anyway.
  router.replace({ query })
}

function onSearchChanged() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    page.value = 1
    load()
  }, 300)
}

function onSortChanged() {
  page.value = 1
  load()
}

function onPageChanged(p: number) {
  page.value = p
  load()
  window.scrollTo({ top: 0, behavior: "smooth" })
}

// External navigation (header search, back/forward) updates local state.
watch(
  () => route.query.q,
  (q) => {
    const next = typeof q === "string" ? q : ""
    if (next !== search.value) {
      search.value = next
      page.value = 1
      load()
    }
  },
)

onMounted(() => {
  const q = route.query.q
  if (typeof q === "string") search.value = q
  const s = route.query.sort
  if (typeof s === "string") sort.value = s
  const p = Number(route.query.page)
  if (Number.isInteger(p) && p > 0) page.value = p
  load()
})

onBeforeUnmount(() => {
  if (debounceTimer) clearTimeout(debounceTimer)
})
</script>

<template>
  <div class="mx-auto max-w-6xl px-4 py-8">
    <header class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">{{ heading }}</h1>
      <p v-if="description" class="mt-1 text-sm text-gray-500">{{ description }}</p>
    </header>

    <CatalogToolbar
      v-model:search="search"
      v-model:sort="sort"
      class="mb-6"
      @search="onSearchChanged"
      @sort="onSortChanged"
    />

    <UiSpinner v-if="catalog.status === 'loading' || catalog.status === 'idle'" label="Loading products…" />
    <UiAlert v-else-if="catalog.status === 'error'" variant="warning">
      The catalogue is temporarily unavailable. Please check back soon.
    </UiAlert>
    <template v-else>
      <p v-if="catalog.total" class="mb-4 text-sm text-gray-500">
        {{ catalog.total }} product{{ catalog.total === 1 ? "" : "s" }}
      </p>
      <ProductGrid v-if="catalog.items.length" :products="catalog.items" />
      <EmptyState
        v-else
        title="No products found"
        description="Try adjusting your search or filters."
      />
      <Pagination
        :page="catalog.page"
        :page-size="catalog.pageSize"
        :total="catalog.total"
        @change="onPageChanged"
      />
    </template>
  </div>
</template>
