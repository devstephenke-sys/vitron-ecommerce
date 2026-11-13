<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string
    description?: string
  }>(),
  {
    title: "Nothing here yet",
    description: "Check back soon — new products are on the way.",
  },
)
</script>

<template>
  <div class="rounded-lg border border-dashed border-gray-300 bg-white px-6 py-12 text-center">
    <p class="text-base font-medium text-gray-900">{{ title }}</p>
    <p class="mt-1 text-sm text-gray-500">{{ description }}</p>
    <div v-if="$slots.default" class="mt-4">
      <slot />
    </div>
  </div>
</template>
