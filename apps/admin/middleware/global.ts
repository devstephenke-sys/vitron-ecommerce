/**
 * Route guard foundation.
 *
 * All admin routes except /login require an authenticated session.
 * Real authentication is implemented in the identity phase; until then
 * the store is never authenticated, so protected pages redirect to /login.
 */
export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore()

  if (to.path === "/login") {
    if (auth.isAuthenticated) return navigateTo("/")
    return
  }

  if (!auth.isAuthenticated) {
    return navigateTo({ path: "/login", query: { redirect: to.fullPath } })
  }
})
