<script setup lang="ts">
import type { CatalogProduct } from "~/types/catalog"
import ProductCard from "./ProductCard.vue"

defineProps<{ products: CatalogProduct[] }>()
</script>

<template>
  <ul
    class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
    role="list"
  >
    <li v-for="product in products" :key="product.id">
      <ProductCard :product="product" />
    </li>
  </ul>
</template>
