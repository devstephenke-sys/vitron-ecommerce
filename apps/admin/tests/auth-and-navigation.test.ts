import { beforeEach, describe, expect, it, vi } from "vitest"
import { createPinia, setActivePinia } from "pinia"
import { ADMIN_NAV_ITEMS, visibleNavItems } from "~/utils/navigation"
import { useAuthStore } from "~/stores/auth"

describe("admin navigation registry", () => {
  it("includes the core sections", () => {
    const labels = ADMIN_NAV_ITEMS.map((i) => i.label)
    for (const expected of ["Dashboard", "Audit Logs", "Catalogue", "Orders", "Inventory", "Customers", "Users & Roles"]) {
      expect(labels).toContain(expected)
    }
  })

  it("filters items by permission", () => {
    const perms = new Set(["audit.read", "catalog.read"])
    const items = visibleNavItems(
      (p) => perms.has(p),
      (ps) => ps.some((p) => perms.has(p)),
    )
    const labels = items.map((i) => i.label)
    expect(labels).toContain("Dashboard")
    expect(labels).toContain("Audit Logs")
    expect(labels).toContain("Catalogue")
    expect(labels).not.toContain("Orders")
    expect(labels).not.toContain("Users & Roles")
  })

  it("always shows permission-free items", () => {
    const items = visibleNavItems(() => false, () => false)
    expect(items.map((i) => i.label)).toEqual(["Dashboard"])
  })
})

describe("auth store permission UX", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.unstubAllGlobals()
  })

  it("starts unauthenticated", () => {
    const auth = useAuthStore()
    expect(auth.isAuthenticated).toBe(false)
    expect(auth.hasPermission("audit.read")).toBe(false)
  })

  it("applies session and permissions after login", async () => {
    const payload = {
      access_token: "at",
      refresh_token: "rt",
      expires_in: 900,
      user: { id: "u1", email: "admin@vitron.test", display_name: "Admin" },
      permissions: ["audit.read", "catalog.read"],
    }
    vi.stubGlobal("useApi", () => ({ apiFetch: vi.fn().mockResolvedValue(payload) }))
    const auth = useAuthStore()
    await auth.login("admin@vitron.test", "pw")
    expect(auth.isAuthenticated).toBe(true)
    expect(auth.user?.email).toBe("admin@vitron.test")
    expect(auth.hasPermission("audit.read")).toBe(true)
    expect(auth.hasPermission("users.manage")).toBe(false)
    expect(auth.hasAnyPermission(["users.manage", "catalog.read"])).toBe(true)
  })

  it("clears permissions on clearSession", async () => {
    const payload = {
      access_token: "at",
      refresh_token: "rt",
      expires_in: 900,
      user: { id: "u1", email: "a@b.c", display_name: null },
      permissions: ["audit.read"],
    }
    vi.stubGlobal("useApi", () => ({ apiFetch: vi.fn().mockResolvedValue(payload) }))
    const auth = useAuthStore()
    await auth.login("a@b.c", "pw")
    auth.clearSession()
    expect(auth.isAuthenticated).toBe(false)
    expect(auth.hasPermission("audit.read")).toBe(false)
  })

  it("propagates login errors without applying a session", async () => {
    vi.stubGlobal("useApi", () => ({
      apiFetch: vi.fn().mockRejectedValue({ status: 401, message: "Invalid credentials" }),
    }))
    const auth = useAuthStore()
    await expect(auth.login("a@b.c", "bad")).rejects.toMatchObject({ status: 401 })
    expect(auth.isAuthenticated).toBe(false)
  })
})
