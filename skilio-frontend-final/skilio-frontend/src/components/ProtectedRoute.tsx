import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { Spinner } from '@/components/ui/Spinner'

/**
 * ProtectedRoute
 *
 * Wraps routes that require authentication.
 * - If loading: shows a full-screen spinner (avoids flash of /login redirect)
 * - If no token: redirects to /login, preserving the intended destination
 *   so after login the user lands where they were trying to go.
 * - If authenticated: renders <Outlet /> (child routes)
 */
export function ProtectedRoute() {
  const { token, isLoading } = useAuthStore()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface-50">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <Outlet />
}
