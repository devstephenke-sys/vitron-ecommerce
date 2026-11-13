import { defineStore } from "pinia"

export interface AuthUser {
  id: string
  email: string
  displayName: string
}

interface TokenResponse {
  access_token: string
  refresh_token: string
  expires_in: number
  user: {
    id: string
    email: string
    display_name: string | null
  }
  permissions: string[]
}

const STORAGE_KEY = "vitron.admin.session"

interface PersistedSession {
  accessToken: string | null
  refreshToken: string | null
  user: AuthUser | null
  permissions: string[]
}

/**
 * Authentication state for the admin app.
 *
 * This store is a UX convenience only — the FastAPI backend independently
 * authenticates and authorizes every request. The refresh token is kept in
 * localStorage so sessions survive reloads; the short-lived access token is
 * held in memory and refreshed on app start.
 */
export const useAuthStore = defineStore("auth", () => {
  const { apiFetch } = useApi()

  const user = ref<AuthUser | null>(null)
  const permissions = ref<string[]>([])
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)

  const isAuthenticated = computed(() => user.value !== null && accessToken.value !== null)

  function hasPermission(permission: string): boolean {
    return permissions.value.includes(permission)
  }

  function hasAnyPermission(required: string[]): boolean {
    return required.some((p) => hasPermission(p))
  }

  function _applySession(payload: TokenResponse) {
    user.value = {
      id: payload.user.id,
      email: payload.user.email,
      displayName: payload.user.display_name ?? payload.user.email,
    }
    permissions.value = payload.permissions
    accessToken.value = payload.access_token
    refreshToken.value = payload.refresh_token
    _persist()
  }

  function _persist() {
    if (!import.meta.client) return
    const session: PersistedSession = {
      accessToken: accessToken.value,
      refreshToken: refreshToken.value,
      user: user.value,
      permissions: permissions.value,
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(session))
  }

  /** Restore persisted session fields (does not validate the access token). */
  function restore() {
    if (!import.meta.client) return
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (!raw) return
      const saved = JSON.parse(raw) as PersistedSession
      user.value = saved.user
      permissions.value = saved.permissions ?? []
      accessToken.value = saved.accessToken
      refreshToken.value = saved.refreshToken
    } catch {
      localStorage.removeItem(STORAGE_KEY)
    }
  }

  async function login(email: string, password: string): Promise<void> {
    const payload = await apiFetch<TokenResponse>("/auth/login", {
      method: "POST",
      body: { email, password },
    })
    _applySession(payload)
  }

  /** Exchange the stored refresh token for a new access token. */
  async function refresh(): Promise<void> {
    if (!refreshToken.value) throw new Error("No refresh token")
    const payload = await apiFetch<TokenResponse>("/auth/refresh", {
      method: "POST",
      body: { refresh_token: refreshToken.value },
    })
    _applySession(payload)
  }

  async function logout(): Promise<void> {
    try {
      if (accessToken.value) {
        await apiFetch("/auth/logout", {
          method: "POST",
          body: { refresh_token: refreshToken.value },
        })
      }
    } finally {
      clearSession()
    }
  }

  function clearSession() {
    user.value = null
    permissions.value = []
    accessToken.value = null
    refreshToken.value = null
    if (import.meta.client) localStorage.removeItem(STORAGE_KEY)
  }

  return {
    user,
    permissions,
    accessToken,
    refreshToken,
    isAuthenticated,
    hasPermission,
    hasAnyPermission,
    restore,
    login,
    refresh,
    logout,
    clearSession,
  }
})
