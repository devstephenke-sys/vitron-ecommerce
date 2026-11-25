/**
 * Route guard — UX layer only.
 *
 * The FastAPI backend independently authenticates and authorizes every
 * API call; this middleware only controls what the admin UI renders.
 * Pages declare `definePageMeta({ permission: "x.y" })` (string or
 * string[] = any-of) and are hidden/redirected without it.
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

  const required = to.meta.permission as string | string[] | undefined
  if (required) {
    const perms = Array.isArray(required) ? required : [required]
    if (!perms.some((p) => auth.hasPermission(p))) {
      return navigateTo("/")
    }
  }
})
