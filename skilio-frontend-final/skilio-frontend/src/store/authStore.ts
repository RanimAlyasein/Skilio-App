// ─────────────────────────────────────────────────────────────────────────────
// src/store/authStore.ts
// Zustand auth store — manages the authenticated user and JWT access token.
//
// SECURITY NOTE:
//   The access token is stored in memory only (Zustand state).
//   It is NEVER written to localStorage or sessionStorage.
//   On page refresh the token is lost and the user must log in again.
//
//   Why? localStorage is accessible to any JS on the page (XSS risk).
//   Memory storage means a stolen XSS payload cannot exfiltrate the token
//   between page loads.
//
//   Trade-off: users will need to log in again after a hard refresh.
//   This is the accepted trade-off for this security model. For production,
//   pair with an httpOnly refresh-token cookie for seamless re-auth.
// ─────────────────────────────────────────────────────────────────────────────

import { create } from 'zustand'
import type { User } from '@/types'

interface AuthState {
  // The authenticated parent user (null = not logged in)
  user: User | null

  // JWT access token in memory — null when not authenticated
  token: string | null

  // True during the initial "am I logged in?" check on app mount
  isLoading: boolean

  // ── Actions ──────────────────────────────────────────────────────────────

  /** Called after a successful login or token refresh */
  setAuth: (user: User, token: string) => void

  /** Called on logout or when a 401 is received */
  clearAuth: () => void

  /** Called during the initial auth check */
  setLoading: (loading: boolean) => void

  /** Update the stored user (e.g. after profile update) */
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isLoading: true,

  setAuth: (user, token) =>
    set({ user, token, isLoading: false }),

  clearAuth: () =>
    set({ user: null, token: null, isLoading: false }),

  setLoading: (isLoading) =>
    set({ isLoading }),

  setUser: (user) =>
    set({ user }),
}))

// ── Selector helpers (use these in components for stable references) ──────────

export const selectUser  = (s: AuthState) => s.user
export const selectToken = (s: AuthState) => s.token
export const selectIsAuthenticated = (s: AuthState) => s.token !== null
export const selectIsLoading = (s: AuthState) => s.isLoading
