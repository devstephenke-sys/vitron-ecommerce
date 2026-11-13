<script setup lang="ts">
definePageMeta({ layout: "blank" })

const config = useRuntimeConfig()
const route = useRoute()
const auth = useAuthStore()

const email = ref("")
const password = ref("")
const pending = ref(false)
const errorMessage = ref<string | null>(null)

const redirectTo = computed(() => {
  const target = route.query.redirect
  return typeof target === "string" && target.startsWith("/") ? target : "/"
})

async function onSubmit() {
  errorMessage.value = null
  pending.value = true
  try {
    await auth.login(email.value, password.value)
    await navigateTo(redirectTo.value)
  } catch (error) {
    const apiError = error as { message?: string; code?: string }
    errorMessage.value =
      apiError.code === "http_error" || apiError.code === "request_failed"
        ? apiError.message ?? "Sign-in failed"
        : "Unable to reach the server. Please try again."
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <div class="w-full max-w-sm rounded-lg border border-gray-200 bg-white p-8 shadow-sm">
    <h1 class="text-xl font-bold text-gray-900">{{ config.public.appName }}</h1>
    <p class="mt-2 text-sm text-gray-600">Sign in to continue.</p>

    <form class="mt-6 space-y-4" @submit.prevent="onSubmit">
      <div>
        <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
        <input
          id="email"
          v-model="email"
          type="email"
          required
          autocomplete="email"
          class="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
        />
      </div>
      <div>
        <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
        <input
          id="password"
          v-model="password"
          type="password"
          required
          autocomplete="current-password"
          class="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
        />
      </div>

      <p v-if="errorMessage" class="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
        {{ errorMessage }}
      </p>

      <button
        type="submit"
        :disabled="pending"
        class="w-full rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50"
      >
        {{ pending ? "Signing in…" : "Sign in" }}
      </button>
    </form>
  </div>
</template>
