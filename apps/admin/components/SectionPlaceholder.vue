<script setup lang="ts">
/** Placeholder for admin sections whose backend arrives in later phases. */
defineProps<{
  title: string
  phase: string
  description?: string
}>()
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-900">{{ title }}</h1>
    <p class="mt-1 text-sm text-gray-500">
      {{ description ?? `This section is planned for ${phase}.` }}
    </p>
    <div class="mt-6 rounded-lg border border-dashed border-gray-300 bg-white p-10 text-center">
      <p class="text-sm font-medium text-gray-700">Coming in {{ phase }}</p>
      <p class="mt-1 text-xs text-gray-400">
        The UI shell and permission gating are in place; functionality lands with the backend module.
      </p>
    </div>
  </div>
</template>
