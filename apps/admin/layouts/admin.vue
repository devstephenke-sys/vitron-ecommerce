<script setup lang="ts">
const config = useRuntimeConfig()
const auth = useAuthStore()
const route = useRoute()

const navItems = computed(() =>
  visibleNavItems(auth.hasPermission, auth.hasAnyPermission),
)

const isActive = (to: string) => route.path === to

async function onLogout() {
  await auth.logout()
  await navigateTo("/login")
}
</script>

<template>
  <div class="min-h-screen bg-gray-100 flex">
    <aside class="w-60 shrink-0 bg-gray-900 text-gray-100 flex flex-col">
      <div class="px-5 py-5 border-b border-gray-800">
        <p class="text-lg font-bold">{{ config.public.appName }}</p>
      </div>
      <nav class="flex-1 px-3 py-4 space-y-1">
        <NuxtLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="block rounded-md px-3 py-2 text-sm"
          :class="isActive(item.to)
            ? 'bg-gray-800 text-white'
            : 'text-gray-300 hover:bg-gray-800 hover:text-white'"
        >
          {{ item.label }}
        </NuxtLink>
        <p v-if="navItems.length === 0" class="px-3 py-2 text-sm text-gray-500">
          No sections available for your permissions.
        </p>
      </nav>
      <div class="border-t border-gray-800 px-5 py-4">
        <p class="text-xs text-gray-400 truncate">{{ auth.user?.email ?? "Not signed in" }}</p>
        <button
          class="mt-2 text-xs text-gray-400 hover:text-white"
          @click="onLogout"
        >
          Sign out
        </button>
      </div>
    </aside>

    <div class="flex-1 flex flex-col min-w-0">
      <header class="bg-white border-b border-gray-200 px-6 py-4">
        <slot name="header" />
      </header>
      <main class="flex-1 p-6">
        <slot />
      </main>
    </div>
  </div>
</template>
