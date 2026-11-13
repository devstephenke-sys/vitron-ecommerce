/** Display formatting helpers (pure functions — unit tested). */

const kesFormatter = new Intl.NumberFormat("en-KE", {
  style: "currency",
  currency: "KES",
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
})

/**
 * Format a Money object for display. Amounts arrive as decimal strings —
 * parse to Number only at the presentation boundary, never for math.
 */
export function formatMoney(money: { amount: string; currency: string } | null | undefined): string {
  if (!money) return "—"
  const amount = Number(money.amount)
  if (!Number.isFinite(amount)) return "—"
  if (money.currency === "KES") return kesFormatter.format(amount)
  return `${money.currency} ${amount.toLocaleString("en-KE", { maximumFractionDigits: 2 })}`
}

export function formatDate(iso: string | Date): string {
  const date = typeof iso === "string" ? new Date(iso) : iso
  if (Number.isNaN(date.getTime())) return "—"
  return date.toLocaleDateString("en-KE", { year: "numeric", month: "short", day: "numeric" })
}
