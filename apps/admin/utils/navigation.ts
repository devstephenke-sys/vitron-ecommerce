export interface NavItem {
  label: string
  to: string
  /** Permission required to see this item; null = any authenticated admin. */
  permission: string | null
  /** All of these permissions are required when set (alternative to `permission`). */
  permissions?: string[]
}

/**
 * Admin navigation registry. Items are filtered by the auth store's
 * permissions at render time, so adding a permission key here is all
 * that is needed to gate a new section. Permission keys match the
 * backend RBAC catalogue (app/modules/identity/permissions.py).
 */
export const ADMIN_NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", to: "/", permission: null },
  { label: "Audit Logs", to: "/audit-logs", permission: "audit.read" },
  { label: "Catalogue", to: "/catalog", permission: "catalog.read" },
  { label: "Orders", to: "/orders", permission: "orders.read" },
  { label: "Inventory", to: "/inventory", permission: "inventory.read" },
  { label: "Customers", to: "/customers", permission: "customers.read" },
  { label: "Users & Roles", to: "/users", permission: "users.read" },
]

export function visibleNavItems(
  hasPermission: (p: string) => boolean,
  hasAny: (ps: string[]) => boolean,
): NavItem[] {
  return ADMIN_NAV_ITEMS.filter((item) => {
    if (item.permissions?.length) return hasAny(item.permissions)
    if (item.permission) return hasPermission(item.permission)
    return true
  })
}
