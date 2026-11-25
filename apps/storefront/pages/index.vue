<script setup lang="ts">
import type { CatalogProduct } from "~/types/catalog"

const config = useRuntimeConfig()
const catalog = useCatalogStore()

useSeoMeta({
  title: () => config.public.appName as string,
  description: "Multi-brand electronics and home appliances — shop Vitron.",
})

// Featured products for the homepage; graceful when the catalogue API
// is not yet available (Phase 4).
const { data: featured, pending } = await useAsyncData("home-featured", async () => {
  await catalog.fetchProducts({ page_size: 8 })
  return catalog.items as CatalogProduct[]
})

const apiDown = computed(() => catalog.status === "error")
</script>

<template>
  <div>
    <section class="bg-white border-b border-gray-200">
      <div class="mx-auto max-w-6xl px-4 py-16 sm:py-20">
        <h1 class="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
          Electronics &amp; home appliances
        </h1>
        <p class="mt-4 max-w-2xl text-lg text-gray-600">
          Shop quality products from brands you trust — with honest prices in KES.
        </p>
        <div class="mt-8">
          <NuxtLink
            to="/products"
            class="inline-flex items-center rounded-md bg-gray-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-gray-800"
          >
            Browse all products
          </NuxtLink>
        </div>
      </div>
    </section>

    <section class="mx-auto max-w-6xl px-4 py-12">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-bold text-gray-900">Featured products</h2>
        <NuxtLink to="/products" class="text-sm text-blue-700 hover:underline">
          View all →
        </NuxtLink>
      </div>

      <div class="mt-6">
        <UiSpinner v-if="pending" label="Loading products…" />
        <UiAlert v-else-if="apiDown" variant="warning">
          The catalogue is temporarily unavailable. Please check back soon.
        </UiAlert>
        <ProductGrid v-else-if="featured?.length" :products="featured" />
        <EmptyState v-else title="No products yet" />
      </div>
    </section>
  </div>
</template>
