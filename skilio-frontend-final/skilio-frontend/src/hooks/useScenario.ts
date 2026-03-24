// src/hooks/useScenario.ts
import { useMutation } from '@tanstack/react-query'
import { scenariosApi } from '@/api/scenarios'
import { useScenarioStore } from '@/store/scenarioStore'
import { getApiErrorMessage } from '@/api/client'

/**
 * useSubmitChoice
 *
 * Wraps the POST /scenarios/attempts/:id/choose endpoint.
 * On success, pushes the ChoiceResult into the scenario store
 * so the ScenarioPlayer re-renders with the next node.
 */
export function useSubmitChoice() {
  const applyChoiceResult = useScenarioStore((s) => s.applyChoiceResult)
  const setIsAdvancing    = useScenarioStore((s) => s.setIsAdvancing)

  return useMutation({
    mutationFn: ({
      attemptId,
      choiceId,
    }: {
      attemptId: number
      choiceId: number
    }) => scenariosApi.submitChoice(attemptId, choiceId),

    onMutate: () => {
      setIsAdvancing(true)
    },

    onSuccess: (result) => {
      applyChoiceResult(result)
    },

    onError: () => {
      setIsAdvancing(false)
    },
  })
}
