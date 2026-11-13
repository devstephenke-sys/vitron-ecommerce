// Nuxt configuration for the Vitron customer storefront.
export default defineNuxtConfig({
  compatibilityDate: "2025-01-01",
  devtools: { enabled: false },

  modules: ["@pinia/nuxt", "@nuxtjs/tailwindcss"],

  css: ["~/assets/css/main.css"],

  runtimeConfig: {
    // Server-only value. Secrets must never be placed under `public`.
    apiBaseServer: "",
    public: {
      // Exposed to the browser; must only contain non-secret values.
      apiBase: "",
      appName: "Vitron Store",
    },
  },

  app: {
    head: {
      title: "Vitron Store",
      htmlAttrs: { lang: "en" },
      meta: [
        { name: "viewport", content: "width=device-width, initial-scale=1" },
        { name: "description", content: "Vitron multi-brand electronics store" },
      ],
    },
  },
})
