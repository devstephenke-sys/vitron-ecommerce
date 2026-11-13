<script setup lang="ts">
const config = useRuntimeConfig()
const route = useRoute()

const searchInput = ref("")

// Keep the header search box in sync when navigating with ?q= already set.
watch(
  () => route.query.q,
  (q) => {
    searchInput.value = typeof q === "string" ? q : ""
  },
  { immediate: true },
)

function onSearch() {
  const query = searchInput.value.trim()
  navigateTo({ path: "/products", query: query ? { q: query } : {} })
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <header class="bg-white border-b border-gray-200 sticky top-0 z-10">
      <div class="mx-auto max-w-6xl px-4 py-4">
        <div class="flex items-center justify-between gap-4">
          <NuxtLink to="/" class="text-xl font-bold text-gray-900 shrink-0">
            {{ config.public.appName }}
          </NuxtLink>

          <form class="hidden flex-1 max-w-md sm:block" role="search" @submit.prevent="onSearch">
            <label for="header-search" class="sr-only">Search products</label>
            <input
              id="header-search"
              v-model="searchInput"
              type="search"
              placeholder="Search products…"
              class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </form>

          <nav class="flex items-center gap-4 text-sm text-gray-600">
            <NuxtLink to="/products" class="hover:text-gray-900">Shop</NuxtLink>
          </nav>
        </div>

        <form class="mt-3 sm:hidden" role="search" @submit.prevent="onSearch">
          <label for="header-search-mobile" class="sr-only">Search products</label>
          <input
            id="header-search-mobile"
            v-model="searchInput"
            type="search"
            placeholder="Search products…"
            class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </form>
      </div>
    </header>

    <main class="flex-1">
      <slot />
    </main>

    <footer class="bg-white border-t border-gray-200">
      <div class="mx-auto max-w-6xl px-4 py-8">
        <div class="flex flex-col gap-6 sm:flex-row sm:justify-between">
          <div>
            <p class="text-lg font-bold text-gray-900">{{ config.public.appName }}</p>
            <p class="mt-1 max-w-xs text-sm text-gray-500">
              Multi-brand electronics and home appliances.
            </p>
          </div>
          <nav class="flex gap-8 text-sm text-gray-600" aria-label="Footer">
            <NuxtLink to="/products" class="hover:text-gray-900">All products</NuxtLink>
            <NuxtLink to="/products?q=movers" class="hover:text-gray-900">Movers &amp; deals</NuxtLink>
          </nav>
        </div>
        <p class="mt-6 border-t border-gray-100 pt-4 text-xs text-gray-400">
          &copy; {{ new Date().getFullYear() }} Vitron. All rights reserved.
        </p>
      </div>
    </footer>
  </div>
</template>
