import { describe, expect, it } from "vitest"
import { formatDate, formatMoney } from "~/utils/format"

describe("formatMoney", () => {
  it("formats KES amounts without a currency code prefix", () => {
    // Intl emits a non-breaking space between "Ksh" and the amount.
    expect(formatMoney({ amount: "1250", currency: "KES" })).toMatch(/^Ksh\s+1,250$/)
  })

  it("keeps two decimal places for fractional amounts", () => {
    const result = formatMoney({ amount: "99.99", currency: "KES" })
    expect(result).toContain("99.99")
  })

  it("falls back to code-prefixed formatting for other currencies", () => {
    expect(formatMoney({ amount: "10", currency: "USD" })).toContain("USD")
  })

  it("returns an em dash for missing or invalid money", () => {
    expect(formatMoney(null)).toBe("—")
    expect(formatMoney(undefined)).toBe("—")
    expect(formatMoney({ amount: "not-a-number", currency: "KES" })).toBe("—")
  })
})

describe("formatDate", () => {
  it("formats ISO strings", () => {
    expect(formatDate("2025-01-15T00:00:00Z")).toMatch(/Jan/)
  })

  it("returns an em dash for invalid input", () => {
    expect(formatDate("garbage")).toBe("—")
  })
})
