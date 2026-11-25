<script setup lang="ts">
import CatalogBrowser from "~/components/catalog/CatalogBrowser.vue"

const route = useRoute()
const slug = computed(() => String(route.params.slug))
const categoryName = computed(() => slug.value.replace(/-/g, " "))

useSeoMeta({
  title: () => `${categoryName.value} — Vitron Store`,
  description: () => `Shop ${categoryName.value} at Vitron.`,
})
</script>

<template>
  <CatalogBrowser
    :category="slug"
    :heading="categoryName"
    :description="`Browse ${categoryName}.`"
  />
</template>
