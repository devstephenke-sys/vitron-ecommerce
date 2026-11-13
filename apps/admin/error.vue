<script setup lang="ts">
const props = defineProps<{
  error: { statusCode: number; statusMessage?: string; message?: string }
}>()

const handleError = () => clearError({ redirect: "/" })
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 px-4">
    <div class="text-center">
      <p class="text-6xl font-bold text-gray-300">{{ error.statusCode }}</p>
      <p class="mt-4 text-gray-600">
        {{ error.statusMessage || error.message || "Something went wrong" }}
      </p>
      <button
        class="mt-6 rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
        @click="handleError"
      >
        Back to dashboard
      </button>
    </div>
  </div>
</template>
