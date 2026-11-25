<script setup lang="ts">
definePageMeta({ layout: "admin", permission: "audit.read" })

interface AuditLogRow {
  id: string
  actor_user_id: string | null
  action: string
  entity_type: string
  entity_id: string | null
  correlation_id: string | null
  created_at: string
}

interface AuditLogsResponse {
  items: AuditLogRow[]
  total: number
  limit: number
  offset: number
}

const { apiFetch } = useApi()

const items = ref<AuditLogRow[]>([])
const total = ref(0)
const offset = ref(0)
const limit = 50
const status = ref<"loading" | "ready" | "error">("loading")
const errorMessage = ref<string | null>(null)

const hasPrev = computed(() => offset.value > 0)
const hasNext = computed(() => offset.value + limit < total.value)

async function load() {
  status.value = "loading"
  errorMessage.value = null
  try {
    const data = await apiFetch<AuditLogsResponse>("/admin/audit-logs", {
      query: { limit, offset: offset.value },
    })
    items.value = data.items
    total.value = data.total
    status.value = "ready"
  } catch (e) {
    const apiError = e as { message?: string }
    errorMessage.value = apiError.message ?? "Failed to load audit logs"
    status.value = "error"
  }
}

function prev() {
  offset.value = Math.max(0, offset.value - limit)
  load()
}
function next() {
  offset.value += limit
  load()
}

onMounted(load)

function formatTime(iso: string): string {
  const d = new Date(iso)
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString()
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Audit Logs</h1>
        <p class="mt-1 text-sm text-gray-500">
          Immutable record of security-relevant actions. {{ total }} entr{{ total === 1 ? "y" : "ies" }}.
        </p>
      </div>
      <button
        class="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
        @click="load"
      >
        Refresh
      </button>
    </div>

    <p v-if="status === 'error'" class="mt-4 rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">
      {{ errorMessage }}
    </p>

    <div v-else class="mt-6 overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
      <table class="min-w-full divide-y divide-gray-200 text-sm">
        <thead class="bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
          <tr>
            <th class="px-4 py-3">Time</th>
            <th class="px-4 py-3">Action</th>
            <th class="px-4 py-3">Entity</th>
            <th class="px-4 py-3">Actor</th>
            <th class="px-4 py-3">Request</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-if="status === 'loading'">
            <td colspan="5" class="px-4 py-8 text-center text-gray-400">Loading…</td>
          </tr>
          <tr v-else-if="!items.length">
            <td colspan="5" class="px-4 py-8 text-center text-gray-400">No audit entries yet.</td>
          </tr>
          <tr v-for="row in items" :key="row.id">
            <td class="whitespace-nowrap px-4 py-2.5 text-gray-600">{{ formatTime(row.created_at) }}</td>
            <td class="px-4 py-2.5 font-medium text-gray-900">{{ row.action }}</td>
            <td class="px-4 py-2.5 text-gray-600">
              {{ row.entity_type }}<span v-if="row.entity_id" class="text-gray-400"> #{{ row.entity_id.slice(0, 8) }}</span>
            </td>
            <td class="px-4 py-2.5 font-mono text-xs text-gray-500">
              {{ row.actor_user_id ? row.actor_user_id.slice(0, 8) : "—" }}
            </td>
            <td class="px-4 py-2.5 font-mono text-xs text-gray-400">
              {{ row.correlation_id ?? "—" }}
            </td>
          </tr>
        </tbody>
      </table>

      <div class="flex items-center justify-between border-t border-gray-200 px-4 py-3 text-sm text-gray-600">
        <span>Showing {{ offset + 1 }}–{{ Math.min(offset + limit, total) }} of {{ total }}</span>
        <div class="flex gap-2">
          <button
            class="rounded-md border border-gray-300 px-3 py-1 text-sm disabled:opacity-40"
            :disabled="!hasPrev"
            @click="prev"
          >
            Previous
          </button>
          <button
            class="rounded-md border border-gray-300 px-3 py-1 text-sm disabled:opacity-40"
            :disabled="!hasNext"
            @click="next"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
