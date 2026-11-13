<script setup lang="ts">
const store = useSystemStatusStore()

useAsyncData("system-status", () => store.check())
</script>

<template>
  <div class="mx-auto max-w-6xl px-4 py-16">
    <section class="text-center">
      <h1 class="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
        Vitron Store
      </h1>
      <p class="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
        Multi-brand electronics and home appliances. The storefront is in its
        foundation phase — product catalogue, cart and checkout arrive in
        later phases.
      </p>
    </section>

    <section class="mt-12 flex justify-center">
      <div class="rounded-lg border border-gray-200 bg-white px-6 py-4 shadow-sm">
        <p class="text-sm text-gray-500">API status</p>
        <p class="mt-1 flex items-center gap-2 text-base font-medium">
          <span
            class="inline-block h-2.5 w-2.5 rounded-full"
            :class="{
              'bg-green-500': store.status === 'ok',
              'bg-red-500': store.status === 'error',
              'bg-yellow-400': store.status === 'checking',
              'bg-gray-300': store.status === 'unknown',
            }"
          />
          <span class="capitalize">{{ store.status }}</span>
        </p>
      </div>
    </section>
  </div>
</template>
