<script setup lang="ts">
const config = useRuntimeConfig()
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <header class="bg-white border-b border-gray-200">
      <div class="mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
        <NuxtLink to="/" class="text-xl font-bold text-gray-900">
          {{ config.public.appName }}
        </NuxtLink>
        <nav class="flex items-center gap-6 text-sm text-gray-600">
          <NuxtLink to="/" class="hover:text-gray-900">Home</NuxtLink>
        </nav>
      </div>
    </header>

    <main class="flex-1">
      <slot />
    </main>

    <footer class="bg-white border-t border-gray-200">
      <div class="mx-auto max-w-6xl px-4 py-6 text-sm text-gray-500">
        &copy; {{ new Date().getFullYear() }} Vitron. All rights reserved.
      </div>
    </footer>
  </div>
</template>
