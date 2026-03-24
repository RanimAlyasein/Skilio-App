// src/store/scenarioStore.ts
// Manages the active scenario play-through state for the scenario player UI.
// This lives in Zustand (client state) rather than React Query (server state)
// because it changes on every choice click and needs instant local updates.

import { create } from 'zustand'
import type { AttemptWithNode, ScenarioNode, ChoiceResult } from '@/types'

interface ScenarioState {
  // The current active attempt (null when not in a scenario)
  attempt: AttemptWithNode | null

  // The node currently being displayed to the child
  currentNode: ScenarioNode | null

  // Feedback text shown after a choice (before advancing to next node)
  pendingFeedback: string | null

  // Badge IDs just awarded — drives the celebration screen
  newlyAwardedBadgeIds: number[]

  // True while a choice submission is in-flight
  isAdvancing: boolean

  // ── Actions ────────────────────────────────────────────────────────────

  /** Called when a new attempt is started or resumed */
  startScenario: (attempt: AttemptWithNode) => void

  /** Called after a choice is submitted successfully */
  applyChoiceResult: (result: ChoiceResult) => void

  /** Clear feedback after it has been displayed */
  clearFeedback: () => void

  /** Reset everything when leaving the scenario player */
  resetScenario: () => void

  setIsAdvancing: (v: boolean) => void
}

export const useScenarioStore = create<ScenarioState>((set) => ({
  attempt: null,
  currentNode: null,
  pendingFeedback: null,
  newlyAwardedBadgeIds: [],
  isAdvancing: false,

  startScenario: (attempt) =>
    set({
      attempt,
      currentNode: attempt.current_node,
      pendingFeedback: null,
      newlyAwardedBadgeIds: [],
    }),

  applyChoiceResult: (result) =>
    set({
      attempt: { ...result.attempt, current_node: result.next_node },
      currentNode: result.next_node,
      pendingFeedback: result.feedback,
      newlyAwardedBadgeIds: result.newly_awarded_badge_ids,
      isAdvancing: false,
    }),

  clearFeedback: () => set({ pendingFeedback: null }),

  resetScenario: () =>
    set({
      attempt: null,
      currentNode: null,
      pendingFeedback: null,
      newlyAwardedBadgeIds: [],
      isAdvancing: false,
    }),

  setIsAdvancing: (isAdvancing) => set({ isAdvancing }),
}))
