<script setup lang="ts">
definePageMeta({ layout: "blank" })

const config = useRuntimeConfig()
const route = useRoute()

const redirectTo = computed(() => {
  const target = route.query.redirect
  return typeof target === "string" && target.startsWith("/") ? target : "/"
})
</script>

<template>
  <div class="w-full max-w-sm rounded-lg border border-gray-200 bg-white p-8 shadow-sm">
    <h1 class="text-xl font-bold text-gray-900">{{ config.public.appName }}</h1>
    <p class="mt-2 text-sm text-gray-600">
      Sign in to continue.
    </p>
    <p class="mt-4 rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-800">
      Authentication is not yet enabled — it is implemented in the identity
      phase. This screen exists to establish the auth-ready route structure.
    </p>
    <p class="mt-4 text-xs text-gray-400">
      Intended destination after sign-in: {{ redirectTo }}
    </p>
  </div>
</template>
