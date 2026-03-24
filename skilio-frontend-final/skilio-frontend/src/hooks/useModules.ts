import { useQuery } from '@tanstack/react-query'
import { modulesApi, lessonsApi } from '@/api/modules'

export function useModules(age?: number) {
  return useQuery({
    queryKey: ['modules', age ?? 'all'],
    queryFn:  () => modulesApi.list(age),
    staleTime: 5 * 60_000,
  })
}

export function useModule(id: number) {
  return useQuery({
    queryKey: ['modules', id],
    queryFn:  () => modulesApi.get(id),
    enabled:  id > 0,
    staleTime: 5 * 60_000,
  })
}

export function useLesson(id: number) {
  return useQuery({
    queryKey: ['lessons', id],
    queryFn:  () => lessonsApi.get(id),
    enabled:  id > 0,
  })
}
