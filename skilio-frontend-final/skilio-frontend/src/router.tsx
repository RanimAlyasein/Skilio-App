import { createBrowserRouter, Navigate } from 'react-router-dom'

import { ProtectedRoute } from '@/components/ProtectedRoute'
import { PublicRoute } from '@/components/PublicRoute'
import { AppShell } from '@/components/layout/AppShell'

// Auth pages
import { LoginPage }    from '@/pages/auth/Login'
import { RegisterPage } from '@/pages/auth/Register'

// Parent portal pages
import { DashboardPage }       from '@/pages/parent/Dashboard'
import { ManageChildrenPage }  from '@/pages/parent/ManageChildren'
import { ChildDetailPage }     from '@/pages/parent/ChildDetail'

// Learning space pages
import { ModuleBrowserPage }  from '@/pages/learn/ModuleBrowser'
import { LessonListPage }     from '@/pages/learn/LessonList'
import { ScenarioPlayerPage } from '@/pages/learn/ScenarioPlayer'

export const router = createBrowserRouter([
  // ── Public routes (redirect to /dashboard if already logged in) ────────────
  {
    element: <PublicRoute />,
    children: [
      { path: '/login',    element: <LoginPage /> },
      { path: '/register', element: <RegisterPage /> },
    ],
  },

  // ── Protected routes (redirect to /login if not authenticated) ─────────────
  {
    element: <ProtectedRoute />,
    children: [
      {
        // AppShell wraps all protected pages with sidebar + top nav
        element: <AppShell />,
        children: [
          // Default redirect
          { path: '/', element: <Navigate to="/dashboard" replace /> },

          // Parent portal
          { path: '/dashboard',          element: <DashboardPage /> },
          { path: '/children',           element: <ManageChildrenPage /> },
          { path: '/children/:childId',  element: <ChildDetailPage /> },

          // Learning space
          { path: '/learn',                              element: <ModuleBrowserPage /> },
          { path: '/learn/:moduleId',                    element: <LessonListPage /> },
          { path: '/learn/:moduleId/:lessonId/play',     element: <ScenarioPlayerPage /> },
        ],
      },
    ],
  },

  // ── Fallback ───────────────────────────────────────────────────────────────
  { path: '*', element: <Navigate to="/dashboard" replace /> },
])
