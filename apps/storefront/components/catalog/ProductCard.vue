<script setup lang="ts">
import { computed } from "vue"
import type { CatalogProduct } from "~/types/catalog"
import { formatMoney } from "~/utils/format"

const props = defineProps<{ product: CatalogProduct }>()

const priceLabel = computed(() => formatMoney(props.product.price))
const availabilityLabel = computed(() => {
  if (props.product.in_stock === true) return "In stock"
  if (props.product.in_stock === false) return "Out of stock"
  return null
})
</script>

<template>
  <NuxtLink
    :to="`/products/${product.slug}`"
    class="group flex flex-col overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm transition-shadow hover:shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
  >
    <div class="flex aspect-square items-center justify-center bg-gray-100">
      <img
        v-if="product.image_url"
        :src="product.image_url"
        :alt="product.name"
        class="h-full w-full object-cover"
        loading="lazy"
      />
      <span v-else class="text-sm text-gray-400" aria-hidden="true">No image</span>
    </div>
    <div class="flex flex-1 flex-col p-4">
      <p v-if="product.brand" class="text-xs font-medium uppercase tracking-wide text-gray-500">
        {{ product.brand.name }}
      </p>
      <h3 class="mt-1 line-clamp-2 text-sm font-semibold text-gray-900 group-hover:text-blue-700">
        {{ product.name }}
      </h3>
      <p v-if="product.summary" class="mt-1 line-clamp-2 text-xs text-gray-500">
        {{ product.summary }}
      </p>
      <div class="mt-auto flex items-center justify-between pt-3">
        <span class="text-base font-bold text-gray-900">{{ priceLabel }}</span>
        <span
          v-if="availabilityLabel"
          class="text-xs"
          :class="product.in_stock ? 'text-green-700' : 'text-gray-400'"
        >
          {{ availabilityLabel }}
        </span>
      </div>
    </div>
  </NuxtLink>
</template>
