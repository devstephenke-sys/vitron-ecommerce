<script setup lang="ts">
import { computed } from "vue"

const props = defineProps<{
  page: number
  pageSize: number
  total: number
}>()

const emit = defineEmits<{ change: [page: number] }>()

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))
const hasPrev = computed(() => props.page > 1)
const hasNext = computed(() => props.page < totalPages.value)

const pageNumbers = computed(() => {
  const pages: number[] = []
  const start = Math.max(1, props.page - 2)
  const end = Math.min(totalPages.value, props.page + 2)
  for (let p = start; p <= end; p++) pages.push(p)
  return pages
})
</script>

<template>
  <nav v-if="totalPages > 1" class="mt-8 flex items-center justify-center gap-1" aria-label="Pagination">
    <button
      class="rounded-md border border-gray-300 px-3 py-1.5 text-sm disabled:opacity-40"
      :disabled="!hasPrev"
      aria-label="Previous page"
      @click="emit('change', page - 1)"
    >
      ‹
    </button>
    <button
      v-for="p in pageNumbers"
      :key="p"
      class="rounded-md px-3 py-1.5 text-sm"
      :class="p === page ? 'bg-gray-900 text-white' : 'border border-gray-300 hover:bg-gray-50'"
      :aria-current="p === page ? 'page' : undefined"
      @click="emit('change', p)"
    >
      {{ p }}
    </button>
    <button
      class="rounded-md border border-gray-300 px-3 py-1.5 text-sm disabled:opacity-40"
      :disabled="!hasNext"
      aria-label="Next page"
      @click="emit('change', page + 1)"
    >
      ›
    </button>
  </nav>
</template>
