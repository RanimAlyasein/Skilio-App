import React from 'react'
import ReactDOM from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

import { router } from './router'
import './styles/globals.css'

// ── React Query client configuration ─────────────────────────────────────────
// Global defaults applied to every query and mutation in the app.
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Data stays fresh for 1 minute before being considered stale
      staleTime: 60_000,
      // Retry failed requests once (not 3x — reduces UX jank on real errors)
      retry: 1,
      // Don't refetch just because the window regained focus
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      {/* DevTools only included in development builds */}
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  </React.StrictMode>,
)
