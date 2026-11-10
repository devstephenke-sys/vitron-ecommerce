import { defineStore } from "pinia"

export interface AuthUser {
  id: string
  email: string
  displayName: string
}

/**
 * Authentication state foundation.
 *
 * Phase 1 provides the state shape, permission checks and route-guard
 * hooks only. Login/session endpoints and token handling are implemented
 * in the identity phase; nothing here fabricates an authenticated user.
 */
export const useAuthStore = defineStore("auth", () => {
  const user = ref<AuthUser | null>(null)
  const permissions = ref<string[]>([])
  const accessToken = ref<string | null>(null)

  const isAuthenticated = computed(() => user.value !== null && accessToken.value !== null)

  function hasPermission(permission: string): boolean {
    return permissions.value.includes(permission)
  }

  function hasAnyPermission(required: string[]): boolean {
    return required.some((p) => hasPermission(p))
  }

  function setSession(payload: { user: AuthUser; permissions: string[]; accessToken: string }) {
    user.value = payload.user
    permissions.value = payload.permissions
    accessToken.value = payload.accessToken
  }

  function clearSession() {
    user.value = null
    permissions.value = []
    accessToken.value = null
  }

  return {
    user,
    permissions,
    accessToken,
    isAuthenticated,
    hasPermission,
    hasAnyPermission,
    setSession,
    clearSession,
  }
})
