import { defineStore } from "pinia"
import type { paths } from "@vitron/contracts"

export type SystemStatus = "unknown" | "checking" | "ok" | "error"

type HealthLiveResponse =
  paths["/api/v1/health/live"]["get"]["responses"][200]["content"]["application/json"]

/**
 * Tracks backend API availability. Exercises the central API client,
 * Pinia state and generated contract types end-to-end.
 */
export const useSystemStatusStore = defineStore("systemStatus", () => {
  const status = ref<SystemStatus>("unknown")
  const lastCheckedAt = ref<Date | null>(null)

  async function check() {
    status.value = "checking"
    try {
      const { apiFetch } = useApi()
      const health = await apiFetch<HealthLiveResponse>("/api/v1/health/live")
      status.value = health.status === "ok" ? "ok" : "error"
    } catch {
      status.value = "error"
    } finally {
      lastCheckedAt.value = new Date()
    }
  }

  return { status, lastCheckedAt, check }
})
