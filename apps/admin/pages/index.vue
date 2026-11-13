<script setup lang="ts">
definePageMeta({ layout: "admin" })

const config = useRuntimeConfig()
const auth = useAuthStore()

const stats = [
  { label: "Products", value: "—" },
  { label: "Orders", value: "—" },
  { label: "Customers", value: "—" },
]
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
    <p class="mt-1 text-sm text-gray-500">
      {{ config.public.appName }} — foundation phase. Operational modules
      arrive in later phases.
    </p>

    <div class="mt-6 grid gap-4 sm:grid-cols-3">
      <div
        v-for="stat in stats"
        :key="stat.label"
        class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm"
      >
        <p class="text-sm text-gray-500">{{ stat.label }}</p>
        <p class="mt-2 text-3xl font-semibold text-gray-900">{{ stat.value }}</p>
      </div>
    </div>

    <p class="mt-6 text-sm text-gray-500">
      Signed in as {{ auth.user?.email ?? "—" }}.
    </p>
  </div>
</template>
