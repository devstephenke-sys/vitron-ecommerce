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
 * that is needed to gate a new section.
 */
export const ADMIN_NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", to: "/", permission: null },
  // Future sections (catalogue, orders, inventory, users, settings)
  // are registered here in their respective phases with permission keys
  // matching the backend RBAC permission catalogue.
]

export function visibleNavItems(hasPermission: (p: string) => boolean, hasAny: (ps: string[]) => boolean): NavItem[] {
  return ADMIN_NAV_ITEMS.filter((item) => {
    if (item.permissions?.length) return hasAny(item.permissions)
    if (item.permission) return hasPermission(item.permission)
    return true
  })
}
