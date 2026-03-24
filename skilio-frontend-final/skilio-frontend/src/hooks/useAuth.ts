// src/hooks/useAuth.ts
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/store/authStore'
import { getApiErrorMessage } from '@/api/client'
import type { LoginCredentials, RegisterPayload } from '@/types'

// ── useLogin ──────────────────────────────────────────────────────────────────

export function useLogin() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)

  return useMutation({
    mutationFn: async (credentials: LoginCredentials) => {
      const token = await authApi.login(credentials)
      // Immediately fetch the user with the new token
      // We need to temporarily set it so the interceptor can use it
      useAuthStore.setState({ token: token.access_token })
      const user = await authApi.getMe()
      return { token, user }
    },
    onSuccess: ({ token, user }) => {
      setAuth(user, token.access_token)
      navigate('/dashboard', { replace: true })
    },
  })
}

// ── useRegister ───────────────────────────────────────────────────────────────

export function useRegister() {
  const navigate = useNavigate()

  return useMutation({
    mutationFn: (payload: RegisterPayload) => authApi.register(payload),
    onSuccess: () => {
      navigate('/login', {
        replace: true,
        state: { registered: true },
      })
    },
  })
}

// ── useLogout ─────────────────────────────────────────────────────────────────

export function useLogout() {
  const navigate = useNavigate()
  const clearAuth = useAuthStore((s) => s.clearAuth)
  const queryClient = useQueryClient()

  return () => {
    clearAuth()
    queryClient.clear()
    navigate('/login', { replace: true })
  }
}

// ── useMe ─────────────────────────────────────────────────────────────────────

export function useMe() {
  const token = useAuthStore((s) => s.token)

  return useQuery({
    queryKey: ['me'],
    queryFn: authApi.getMe,
    enabled: !!token,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: false,
  })
}
