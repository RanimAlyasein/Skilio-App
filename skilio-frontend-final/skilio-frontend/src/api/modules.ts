// src/api/modules.ts
import apiClient from './client'
import type { SkillModule, SkillModuleWithLessons, Lesson } from '@/types'

export const modulesApi = {
  /** GET /api/modules/?age=N */
  list: async (age?: number): Promise<SkillModule[]> => {
    const { data } = await apiClient.get<SkillModule[]>('/api/modules/', {
      params: age ? { age } : {},
    })
    return data
  },

  /** GET /api/modules/:id */
  get: async (id: number): Promise<SkillModuleWithLessons> => {
    const { data } = await apiClient.get<SkillModuleWithLessons>(`/api/modules/${id}`)
    return data
  },
}

export const lessonsApi = {
  /** GET /api/lessons/:id */
  get: async (id: number): Promise<Lesson> => {
    const { data } = await apiClient.get<Lesson>(`/api/lessons/${id}`)
    return data
  },
}
