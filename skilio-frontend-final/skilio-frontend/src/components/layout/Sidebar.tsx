import { NavLink, useNavigate } from 'react-router-dom'
import { clsx } from 'clsx'
import { useAuthStore } from '@/store/authStore'
import { Avatar } from '@/components/ui/Avatar'
import { useQueryClient } from '@tanstack/react-query'

interface NavItem {
  to: string
  label: string
  icon: string
  end?: boolean
}

const NAV_ITEMS: NavItem[] = [
  { to: '/dashboard',  label: 'Dashboard',  icon: '⬡', end: true },
  { to: '/children',   label: 'My Children', icon: '◎' },
  { to: '/learn',      label: 'Modules',     icon: '◈' },
]

export function Sidebar() {
  const user      = useAuthStore((s) => s.user)
  const clearAuth = useAuthStore((s) => s.clearAuth)
  const navigate  = useNavigate()
  const qc        = useQueryClient()

  function handleLogout() {
    clearAuth()
    qc.clear()
    navigate('/login', { replace: true })
  }

  return (
    <aside
      className={clsx(
        'fixed left-0 top-0 h-full z-30',
        'w-[var(--sidebar-width)] flex flex-col',
        'bg-surface-900 text-surface-100',
        'border-r border-surface-800',
        'hidden md:flex',   // hide on mobile — MobileNav takes over
      )}
    >
      {/* ── Logo ── */}
      <div className="px-6 pt-7 pb-6 border-b border-surface-800">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-primary-500 flex items-center justify-center shadow-glow-primary">
            <span className="text-white font-display font-bold text-sm">S</span>
          </div>
          <span className="font-display text-xl font-semibold text-white tracking-tight">
            Skilio
          </span>
        </div>
        <p className="text-surface-500 text-[11px] mt-1.5 font-medium tracking-wider uppercase">
          Parent Portal
        </p>
      </div>

      {/* ── Nav ── */}
      <nav className="flex-1 px-3 py-5 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold',
                'transition-all duration-150',
                isActive
                  ? 'bg-primary-600 text-white shadow-sm'
                  : 'text-surface-400 hover:bg-surface-800 hover:text-surface-100',
              )
            }
          >
            <span className="text-base w-5 text-center opacity-80">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* ── User footer ── */}
      {user && (
        <div className="px-3 py-4 border-t border-surface-800">
          <div className="flex items-center gap-3 px-3 py-2 rounded-xl">
            <Avatar name={user.full_name} size="sm" className="shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-surface-200 truncate">
                {user.full_name}
              </p>
              <p className="text-xs text-surface-500 truncate">{user.email}</p>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className={clsx(
              'mt-2 w-full flex items-center gap-2.5 px-3 py-2 rounded-xl',
              'text-sm text-surface-500 hover:bg-surface-800 hover:text-surface-200',
              'transition-all duration-150 font-medium',
            )}
          >
            <span className="text-base">↪</span>
            Sign out
          </button>
        </div>
      )}
    </aside>
  )
}
