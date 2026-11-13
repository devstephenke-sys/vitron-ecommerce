/**
 * Client-only auth hydration plugin.
 *
 * Runs before the app renders: restores the persisted session, then
 * exchanges the stored refresh token for a fresh access token. If the
 * refresh token is expired/revoked the session is cleared and the route
 * guard sends the user to /login.
 */
export default defineNuxtPlugin(async () => {
  const auth = useAuthStore()
  auth.restore()

  if (auth.refreshToken) {
    try {
      await auth.refresh()
    } catch {
      auth.clearSession()
    }
  }
})
