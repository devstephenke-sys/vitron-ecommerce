/**
 * Central API client for the admin application.
 * Mirrors the storefront client; kept separate so the two apps can
 * evolve their API usage independently.
 */

export interface ApiError {
  code: string
  message: string
  requestId?: string
}

export function useApi() {
  const config = useRuntimeConfig()

  const baseURL = computed(() =>
    import.meta.server
      ? (config.apiBaseServer as string) || (config.public.apiBase as string)
      : (config.public.apiBase as string),
  )

  async function apiFetch<T>(path: string, options: Record<string, unknown> = {}): Promise<T> {
    try {
      return await $fetch<T>(path, {
        baseURL: baseURL.value,
        ...options,
      })
    } catch (error) {
      const err = error as {
        data?: { error?: { code?: string; message?: string; request_id?: string } }
        message?: string
      }
      const apiError: ApiError = {
        code: err.data?.error?.code ?? "request_failed",
        message: err.data?.error?.message ?? err.message ?? "Request failed",
        requestId: err.data?.error?.request_id,
      }
      throw apiError
    }
  }

  return { apiFetch, baseURL }
}
