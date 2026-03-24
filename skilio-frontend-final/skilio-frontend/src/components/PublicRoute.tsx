import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'

/**
 * PublicRoute
 *
 * Wraps public pages (login, register).
 * If the user is already authenticated, send them straight to /dashboard
 * so they don't see the login form again.
 */
export function PublicRoute() {
  const token = useAuthStore((s) => s.token)

  if (token) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}
