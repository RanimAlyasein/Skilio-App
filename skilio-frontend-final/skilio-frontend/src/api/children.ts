// src/api/children.ts
import apiClient from './client'
import type {
  Child,
  ChildCreate,
  ChildDashboard,
  ChildSummary,
  ChildUpdate,
  BadgeAward,
  Progress,
  ScenarioAttempt,
} from '@/types'

export const childrenApi = {
  /** GET /api/children/ */
  list: async (): Promise<ChildSummary[]> => {
    const { data } = await apiClient.get<ChildSummary[]>('/api/children/')
    return data
  },

  /** POST /api/children/ */
  create: async (payload: ChildCreate): Promise<Child> => {
    const { data } = await apiClient.post<Child>('/api/children/', payload)
    return data
  },

  /** GET /api/children/:id */
  get: async (id: number): Promise<Child> => {
    const { data } = await apiClient.get<Child>(`/api/children/${id}`)
    return data
  },

  /** PUT /api/children/:id */
  update: async (id: number, payload: ChildUpdate): Promise<Child> => {
    const { data } = await apiClient.put<Child>(`/api/children/${id}`, payload)
    return data
  },

  /** DELETE /api/children/:id */
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/children/${id}`)
  },

  /** GET /api/children/:id/summary */
  getSummary: async (id: number): Promise<ChildDashboard> => {
    const { data } = await apiClient.get<ChildDashboard>(`/api/children/${id}/summary`)
    return data
  },

  /** GET /api/children/:id/progress */
  getProgress: async (id: number): Promise<Progress[]> => {
    const { data } = await apiClient.get<Progress[]>(`/api/children/${id}/progress`)
    return data
  },

  /** GET /api/children/:id/badges */
  getBadges: async (id: number): Promise<BadgeAward[]> => {
    const { data } = await apiClient.get<BadgeAward[]>(`/api/children/${id}/badges`)
    return data
  },

  /** GET /api/children/:id/attempts */
  getAttempts: async (id: number): Promise<ScenarioAttempt[]> => {
    const { data } = await apiClient.get<ScenarioAttempt[]>(`/api/children/${id}/attempts`)
    return data
  },
}
