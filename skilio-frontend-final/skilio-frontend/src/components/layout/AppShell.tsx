import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { MobileNav } from './MobileNav'

/**
 * AppShell
 *
 * The persistent layout for all authenticated pages.
 * - Desktop (md+): sidebar on the left, content offset right
 * - Mobile (<640px): sidebar hidden, MobileNav fixed at bottom
 */
export function AppShell() {
  return (
    <div className="min-h-screen bg-surface-50">
      {/* Sidebar — hidden on mobile via CSS */}
      <Sidebar />

      {/* Main content — offset by sidebar width on desktop */}
      <main className="md:ml-[var(--sidebar-width)] min-h-screen">
        <Outlet />
      </main>

      {/* Mobile bottom tab bar — visible only on small screens */}
      <MobileNav />
    </div>
  )
}
