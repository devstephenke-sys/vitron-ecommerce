<script setup lang="ts">
import { SORT_OPTIONS } from "~/utils/catalog"

const search = defineModel<string>("search", { default: "" })
const sort = defineModel<string>("sort", { default: "relevance" })

const emit = defineEmits<{ search: []; sort: [] }>()

function onSearchInput() {
  emit("search")
}
function onSortChange() {
  emit("sort")
}
</script>

<template>
  <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
    <div class="relative flex-1 sm:max-w-sm">
      <label for="catalog-search" class="sr-only">Search products</label>
      <input
        id="catalog-search"
        v-model="search"
        type="search"
        placeholder="Search products…"
        class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        @input="onSearchInput"
      />
    </div>
    <div class="flex items-center gap-2">
      <label for="catalog-sort" class="text-sm text-gray-600">Sort by</label>
      <select
        id="catalog-sort"
        v-model="sort"
        class="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
        @change="onSortChange"
      >
        <option v-for="option in SORT_OPTIONS" :key="option.value" :value="option.value">
          {{ option.label }}
        </option>
      </select>
    </div>
  </div>
</template>
