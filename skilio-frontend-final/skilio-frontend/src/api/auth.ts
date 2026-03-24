// src/api/auth.ts
import apiClient from './client'
import type { LoginCredentials, RegisterPayload, Token, User } from '@/types'

export const authApi = {
  /**
   * POST /api/auth/login
   * FastAPI uses OAuth2PasswordRequestForm — credentials must be form-encoded,
   * not JSON. The 'username' field maps to email on the backend.
   */
  login: async (credentials: LoginCredentials): Promise<Token> => {
    const form = new URLSearchParams()
    form.append('username', credentials.username)
    form.append('password', credentials.password)

    const { data } = await apiClient.post<Token>('/api/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return data
  },

  /** POST /api/auth/register */
  register: async (payload: RegisterPayload): Promise<User> => {
    const { data } = await apiClient.post<User>('/api/auth/register', payload)
    return data
  },

  /** GET /api/auth/me */
  getMe: async (): Promise<User> => {
    const { data } = await apiClient.get<User>('/api/auth/me')
    return data
  },
}
