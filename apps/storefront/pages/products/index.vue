<script setup lang="ts">
import CatalogBrowser from "~/components/catalog/CatalogBrowser.vue"

useSeoMeta({
  title: "All products — Vitron Store",
  description: "Browse the full Vitron catalogue: electronics and home appliances.",
})
</script>

<template>
  <CatalogBrowser heading="All products" description="Browse the full catalogue." />
</template>
