<script setup lang="ts">
import CatalogBrowser from "~/components/catalog/CatalogBrowser.vue"

const route = useRoute()
const slug = computed(() => String(route.params.slug))
const brandName = computed(() => slug.value.replace(/-/g, " "))

useSeoMeta({
  title: () => `${brandName.value} — Vitron Store`,
  description: () => `Shop ${brandName.value} products at Vitron.`,
})
</script>

<template>
  <CatalogBrowser
    :brand="slug"
    :heading="brandName"
    :description="`Products from ${brandName}.`"
  />
</template>
