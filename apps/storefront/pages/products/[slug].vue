<script setup lang="ts">
import type { ProductDetail } from "~/types/catalog"
import { formatMoney } from "~/utils/format"

const route = useRoute()
const slug = computed(() => String(route.params.slug))
const catalog = useCatalogStore()

const { data: product, pending } = await useAsyncData(
  `product-${slug.value}`,
  () => catalog.fetchProduct(slug.value),
)

const notFound = computed(() => !pending.value && product.value === null)

useSeoMeta({
  title: () =>
    product.value ? `${product.value.name} — Vitron Store` : "Product — Vitron Store",
  description: () => product.value?.summary ?? "Product details",
  ogTitle: () => product.value?.name,
  ogDescription: () => product.value?.summary ?? undefined,
})

const priceLabel = computed(() => formatMoney(product.value?.price))
const activeImage = ref(0)
const images = computed(() => product.value?.images ?? [])
const mainImage = computed(() => images.value[activeImage.value]?.url ?? null)
</script>

<template>
  <div class="mx-auto max-w-6xl px-4 py-8">
    <UiSpinner v-if="pending" label="Loading product…" />

    <EmptyState
      v-else-if="notFound"
      title="Product not found"
      description="This product may have been removed or the link is incorrect."
    >
      <NuxtLink to="/products" class="text-sm text-blue-700 hover:underline">
        ← Back to all products
      </NuxtLink>
    </EmptyState>

    <template v-else-if="product">
      <nav class="mb-6 text-sm text-gray-500" aria-label="Breadcrumb">
        <NuxtLink to="/products" class="hover:text-gray-900">Products</NuxtLink>
        <span v-if="product.category" class="mx-1">/</span>
        <NuxtLink
          v-if="product.category"
          :to="`/categories/${product.category.slug}`"
          class="hover:text-gray-900"
        >
          {{ product.category.name }}
        </NuxtLink>
      </nav>

      <div class="grid gap-8 lg:grid-cols-2">
        <!-- Gallery -->
        <div>
          <div class="flex aspect-square items-center justify-center overflow-hidden rounded-lg border border-gray-200 bg-gray-100">
            <img
              v-if="mainImage"
              :src="mainImage"
              :alt="product.name"
              class="h-full w-full object-cover"
            />
            <span v-else class="text-sm text-gray-400" aria-hidden="true">No image</span>
          </div>
          <div v-if="images.length > 1" class="mt-3 flex gap-2">
            <button
              v-for="(img, i) in images"
              :key="i"
              class="h-16 w-16 overflow-hidden rounded border"
              :class="i === activeImage ? 'border-blue-500 ring-1 ring-blue-500' : 'border-gray-200'"
              :aria-label="`View image ${i + 1}`"
              @click="activeImage = i"
            >
              <img :src="img.url" :alt="img.alt_text ?? product.name" class="h-full w-full object-cover" />
            </button>
          </div>
        </div>

        <!-- Details -->
        <div>
          <p v-if="product.brand" class="text-sm font-medium uppercase tracking-wide text-gray-500">
            {{ product.brand.name }}
          </p>
          <h1 class="mt-1 text-2xl font-bold text-gray-900 sm:text-3xl">{{ product.name }}</h1>
          <p v-if="product.model_number" class="mt-1 text-sm text-gray-500">
            Model: {{ product.model_number }}
          </p>

          <p class="mt-4 text-3xl font-bold text-gray-900">{{ priceLabel }}</p>
          <p class="mt-1 text-sm">
            <span v-if="product.in_stock === true" class="text-green-700">In stock</span>
            <span v-else-if="product.in_stock === false" class="text-gray-500">Out of stock</span>
            <span v-else class="text-gray-400">Availability to be confirmed</span>
          </p>

          <p v-if="product.summary" class="mt-4 text-gray-600">{{ product.summary }}</p>

          <div class="mt-6">
            <UiButton variant="primary" disabled>
              Add to cart — coming soon
            </UiButton>
            <p class="mt-2 text-xs text-gray-400">
              Online checkout arrives in a later phase.
            </p>
          </div>
        </div>
      </div>

      <section v-if="product.description" class="mt-10">
        <h2 class="text-lg font-bold text-gray-900">Description</h2>
        <p class="mt-2 whitespace-pre-line text-gray-600">{{ product.description }}</p>
      </section>

      <section v-if="product.attributes.length" class="mt-10">
        <h2 class="text-lg font-bold text-gray-900">Specifications</h2>
        <dl class="mt-3 divide-y divide-gray-200 rounded-lg border border-gray-200 bg-white">
          <div
            v-for="attr in product.attributes"
            :key="attr.key"
            class="flex justify-between px-4 py-2 text-sm"
          >
            <dt class="text-gray-500">{{ attr.label }}</dt>
            <dd class="font-medium text-gray-900">
              {{ attr.value }}<span v-if="attr.unit" class="text-gray-500"> {{ attr.unit }}</span>
            </dd>
          </div>
        </dl>
      </section>
    </template>
  </div>
</template>
