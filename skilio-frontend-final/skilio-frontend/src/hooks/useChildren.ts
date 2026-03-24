// src/hooks/useChildren.ts
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { childrenApi } from '@/api/children'
import type { ChildCreate, ChildUpdate } from '@/types'

export const CHILDREN_KEY = ['children'] as const

export function useChildren() {
  return useQuery({
    queryKey: CHILDREN_KEY,
    queryFn: childrenApi.list,
    staleTime: 60_000,
  })
}

export function useChild(id: number) {
  return useQuery({
    queryKey: ['children', id],
    queryFn: () => childrenApi.get(id),
    enabled: id > 0,
  })
}

export function useChildSummary(id: number) {
  return useQuery({
    queryKey: ['children', id, 'summary'],
    queryFn: () => childrenApi.getSummary(id),
    enabled: id > 0,
  })
}

export function useCreateChild() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: ChildCreate) => childrenApi.create(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHILDREN_KEY }),
  })
}

export function useUpdateChild(id: number) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: ChildUpdate) => childrenApi.update(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: CHILDREN_KEY })
      qc.invalidateQueries({ queryKey: ['children', id] })
    },
  })
}

export function useDeleteChild() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => childrenApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHILDREN_KEY }),
  })
}
