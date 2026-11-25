import { describe, expect, it, vi, beforeEach } from "vitest"
import { mount } from "@vue/test-utils"
import { createPinia, setActivePinia } from "pinia"
import ProductCard from "~/components/catalog/ProductCard.vue"
import Pagination from "~/components/catalog/Pagination.vue"
import UiAlert from "~/components/ui/UiAlert.vue"
import UiButton from "~/components/ui/UiButton.vue"
import EmptyState from "~/components/ui/EmptyState.vue"
import { useCatalogStore } from "~/stores/catalog"
import type { CatalogProduct } from "~/types/catalog"

const NuxtLinkStub = {
  props: ["to"],
  template: '<a :href="to"><slot /></a>',
}

function product(partial: Partial<CatalogProduct> = {}): CatalogProduct {
  return {
    id: "p1",
    slug: "test-phone",
    name: "Test Phone",
    summary: "A summary",
    brand: { slug: "samsung", name: "Samsung" },
    category: { slug: "phones", name: "Phones" },
    price: { amount: "25000", currency: "KES" },
    image_url: null,
    in_stock: true,
    ...partial,
  }
}

describe("ProductCard", () => {
  it("links to the product detail page and shows price/stock", () => {
    const wrapper = mount(ProductCard, {
      props: { product: product() },
      global: { stubs: { NuxtLink: NuxtLinkStub } },
    })
    const link = wrapper.find("a")
    expect(link.attributes("href")).toBe("/products/test-phone")
    expect(wrapper.text()).toContain("Test Phone")
    expect(wrapper.text()).toContain("Samsung")
    expect(wrapper.text()).toContain("In stock")
    expect(wrapper.text()).toMatch(/Ksh|KES/)
  })

  it("shows out-of-stock label and no stock label when unknown", () => {
    const out = mount(ProductCard, {
      props: { product: product({ in_stock: false }) },
      global: { stubs: { NuxtLink: NuxtLinkStub } },
    })
    expect(out.text()).toContain("Out of stock")

    const unknown = mount(ProductCard, {
      props: { product: product({ in_stock: null, price: null }) },
      global: { stubs: { NuxtLink: NuxtLinkStub } },
    })
    expect(unknown.text()).not.toContain("In stock")
    expect(unknown.text()).not.toContain("Out of stock")
  })

  it("renders an image when image_url is set", () => {
    const wrapper = mount(ProductCard, {
      props: { product: product({ image_url: "https://img.example/x.png" }) },
      global: { stubs: { NuxtLink: NuxtLinkStub } },
    })
    expect(wrapper.find("img").attributes("src")).toBe("https://img.example/x.png")
  })
})

describe("Pagination", () => {
  it("emits change with the target page", async () => {
    const wrapper = mount(Pagination, {
      props: { page: 2, pageSize: 12, total: 60 },
    })
    const buttons = wrapper.findAll("button")
    await buttons[buttons.length - 1]!.trigger("click") // Next
    expect(wrapper.emitted("change")?.[0]).toEqual([3])
  })

  it("disables Next on the last page", () => {
    const wrapper = mount(Pagination, {
      props: { page: 5, pageSize: 12, total: 60 },
    })
    const buttons = wrapper.findAll("button")
    expect((buttons[buttons.length - 1]!.element as HTMLButtonElement).disabled).toBe(true)
  })
})

describe("UI primitives", () => {
  it("UiAlert renders variant classes and message", () => {
    const wrapper = mount(UiAlert, { props: { variant: "warning" }, slots: { default: "Careful" } })
    expect(wrapper.text()).toContain("Careful")
    expect(wrapper.classes().join(" ")).toContain("amber")
  })

  it("UiButton renders a button and disables when asked", () => {
    const wrapper = mount(UiButton, { props: { disabled: true }, slots: { default: "Go" } })
    expect(wrapper.text()).toContain("Go")
    expect((wrapper.element as HTMLButtonElement).disabled).toBe(true)
  })

  it("EmptyState renders title and description", () => {
    const wrapper = mount(EmptyState, {
      props: { title: "Nothing here", description: "Try again" },
    })
    expect(wrapper.text()).toContain("Nothing here")
    expect(wrapper.text()).toContain("Try again")
  })
})

describe("catalog store", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.unstubAllGlobals()
  })

  it("starts idle with empty items", () => {
    const store = useCatalogStore()
    expect(store.status).toBe("idle")
    expect(store.items).toEqual([])
    expect(store.hasMore).toBe(false)
  })

  it("surfaces API errors into status/error without throwing", async () => {
    vi.stubGlobal("useApi", () => ({
      apiFetch: vi.fn().mockRejectedValue({ message: "API unavailable" }),
    }))
    const store = useCatalogStore()
    await store.fetchProducts({ q: "phone" })
    expect(store.status).toBe("error")
    expect(store.error).toBe("API unavailable")
    expect(store.items).toEqual([])
    expect(store.lastQuery).toEqual({ q: "phone" })
  })

  it("populates items on success", async () => {
    const result = {
      items: [product()],
      total: 1,
      page: 1,
      page_size: 12,
    }
    vi.stubGlobal("useApi", () => ({ apiFetch: vi.fn().mockResolvedValue(result) }))
    const store = useCatalogStore()
    await store.fetchProducts({ page: 2 })
    expect(store.status).toBe("ready")
    expect(store.items).toHaveLength(1)
    expect(store.total).toBe(1)
    expect(store.page).toBe(1)
  })

  it("fetchProduct returns null on failure instead of throwing", async () => {
    vi.stubGlobal("useApi", () => ({
      apiFetch: vi.fn().mockRejectedValue(new Error("404")),
    }))
    const store = useCatalogStore()
    await expect(store.fetchProduct("missing")).resolves.toBeNull()
  })
})
