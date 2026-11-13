<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: "info" | "success" | "warning" | "error"
  }>(),
  { variant: "info" },
)

const variantClasses: Record<string, string> = {
  info: "bg-blue-50 text-blue-800 border-blue-200",
  success: "bg-green-50 text-green-800 border-green-200",
  warning: "bg-amber-50 text-amber-800 border-amber-200",
  error: "bg-red-50 text-red-800 border-red-200",
}

const roleByVariant: Record<string, string> = {
  info: "status",
  success: "status",
  warning: "alert",
  error: "alert",
}
</script>

<template>
  <div
    class="rounded-md border px-4 py-3 text-sm"
    :class="variantClasses[variant]"
    :role="roleByVariant[variant]"
  >
    <slot />
  </div>
</template>
