"""Permission catalogue and system role definitions.

Permissions are dot-namespaced codes checked server-side on every
protected operation. Roles are bundles of permissions seeded by the
Phase 2 migration; authorization never checks role names directly.
"""

# (code, description)
PERMISSIONS: list[tuple[str, str]] = [
    ("catalog.read", "View catalogue, brands, categories and products"),
    ("catalog.write", "Create and edit catalogue content"),
    ("catalog.publish", "Publish/unpublish products"),
    ("catalog.import", "Run catalogue import batches"),
    ("catalog.export", "Export catalogue data"),
    ("inventory.read", "View stock levels and movements"),
    ("inventory.write", "Adjust stock and manage reservations"),
    ("orders.read", "View orders"),
    ("orders.write", "Create and edit orders"),
    ("orders.manage", "Perform order status transitions"),
    ("customers.read", "View customer records"),
    ("customers.write", "Edit customer records"),
    ("sales.read", "View quotations and sales data"),
    ("sales.write", "Create and manage quotations"),
    ("payments.read", "View payments"),
    ("payments.manage", "Reconcile, refund and manage payments"),
    ("shipments.read", "View shipments and delivery zones"),
    ("shipments.write", "Manage shipments"),
    ("promotions.read", "View coupons and promotions"),
    ("promotions.write", "Create and manage promotions"),
    ("reports.read", "View reports and dashboards"),
    ("audit.read", "View audit logs"),
    ("users.read", "View admin users and roles"),
    ("users.manage", "Create users and assign roles"),
    ("settings.manage", "Manage platform settings"),
]

PERMISSION_CODES = [code for code, _ in PERMISSIONS]

ALL_PERMISSIONS = list(PERMISSION_CODES)

# Role code -> permission codes. `customer` intentionally holds no
# admin permissions; storefront customers authenticate but are not
# authorized for any /admin operation.
ROLE_PERMISSIONS: dict[str, list[str]] = {
    "customer": [],
    "administrator": ALL_PERMISSIONS,
    "inventory_manager": [
        "catalog.read",
        "inventory.read",
        "inventory.write",
        "shipments.read",
        "reports.read",
    ],
    "sales_staff": [
        "catalog.read",
        "orders.read",
        "orders.write",
        "orders.manage",
        "customers.read",
        "customers.write",
        "sales.read",
        "sales.write",
        "payments.read",
        "shipments.read",
        "shipments.write",
        "promotions.read",
        "promotions.write",
        "reports.read",
    ],
}

ROLES: list[tuple[str, str, str]] = [
    ("customer", "Customer", "Storefront customer account"),
    ("administrator", "Administrator", "Full platform administration"),
    ("inventory_manager", "Inventory Manager", "Stock and fulfilment operations"),
    ("sales_staff", "Sales Staff", "Orders, customers, quotations and promotions"),
]
