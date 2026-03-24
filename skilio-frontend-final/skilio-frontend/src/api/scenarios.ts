// src/api/scenarios.ts
import apiClient from './client'
import type {
  AttemptHistory,
  AttemptWithNode,
  ChoiceResult,
  ScenarioNode,
} from '@/types'

export const scenariosApi = {
  /**
   * POST /api/scenarios/attempts
   * Starts a new attempt OR resumes an in-progress one.
   */
  startAttempt: async (childId: number, lessonId: number): Promise<AttemptWithNode> => {
    const { data } = await apiClient.post<AttemptWithNode>('/api/scenarios/attempts', {
      child_id: childId,
      lesson_id: lessonId,
    })
    return data
  },

  /**
   * GET /api/scenarios/attempts/:id
   * Resume — returns current state + current node.
   */
  getAttempt: async (attemptId: number): Promise<AttemptWithNode> => {
    const { data } = await apiClient.get<AttemptWithNode>(
      `/api/scenarios/attempts/${attemptId}`,
    )
    return data
  },

  /**
   * POST /api/scenarios/attempts/:id/choose
   * Submit a choice. Returns next node (or null if complete).
   */
  submitChoice: async (attemptId: number, choiceId: number): Promise<ChoiceResult> => {
    const { data } = await apiClient.post<ChoiceResult>(
      `/api/scenarios/attempts/${attemptId}/choose`,
      { choice_id: choiceId },
    )
    return data
  },

  /**
   * GET /api/scenarios/attempts/:id/history
   * Full choice audit trail — for parent review.
   */
  getHistory: async (attemptId: number): Promise<AttemptHistory> => {
    const { data } = await apiClient.get<AttemptHistory>(
      `/api/scenarios/attempts/${attemptId}/history`,
    )
    return data
  },

  /** GET /api/scenarios/nodes/:id */
  getNode: async (nodeId: number): Promise<ScenarioNode> => {
    const { data } = await apiClient.get<ScenarioNode>(`/api/scenarios/nodes/${nodeId}`)
    return data
  },
}
