// Nuxt configuration for the Vitron administration application.
// This app is deployed independently from the storefront.
export default defineNuxtConfig({
  compatibilityDate: "2025-01-01",
  devtools: { enabled: false },
  // Admin panel is a client-rendered SPA: no SEO requirement, and it
  // keeps token handling entirely in the browser where the route guard
  // and auth store live (server-side authorization is enforced by the
  // API regardless).
  ssr: false,

  modules: ["@pinia/nuxt", "@nuxtjs/tailwindcss"],

  css: ["~/assets/css/main.css"],

  runtimeConfig: {
    // Server-only value. Secrets must never be placed under `public`.
    apiBaseServer: "",
    public: {
      // Exposed to the browser; must only contain non-secret values.
      apiBase: "",
      appName: "Vitron Admin",
    },
  },

  app: {
    head: {
      title: "Vitron Admin",
      htmlAttrs: { lang: "en" },
      meta: [
        { name: "viewport", content: "width=device-width, initial-scale=1" },
        { name: "robots", content: "noindex, nofollow" },
      ],
    },
  },
})
