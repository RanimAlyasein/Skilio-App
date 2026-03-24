import { Link } from 'react-router-dom'
import { clsx } from 'clsx'

import { useAuthStore }  from '@/store/authStore'
import { useChildren }   from '@/hooks/useChildren'
import { Avatar }        from '@/components/ui/Avatar'
import { XPBar }         from '@/components/ui/XPBar'
import { Spinner }       from '@/components/ui/Spinner'
import { EmptyState }    from '@/components/ui/EmptyState'
import { ErrorMessage }  from '@/components/ui/ErrorMessage'
import { getApiErrorMessage } from '@/api/client'
import type { ChildSummary } from '@/types'

export function DashboardPage() {
  const user             = useAuthStore((s) => s.user)
  const { data, isLoading, error } = useChildren()

  const firstName = user?.full_name.split(' ')[0] ?? 'there'

  return (
    <div className="page-container">

      {/* ── Header ── */}
      <div className="flex items-end justify-between mb-8 animate-fade-up">
        <div>
          <p className="text-surface-400 text-sm font-medium mb-1">
            {greeting()}, {firstName}
          </p>
          <h1 className="page-title">Your children</h1>
        </div>

        <Link to="/children" className="btn-outline btn-sm">
          Manage profiles
        </Link>
      </div>

      {/* ── Loading ── */}
      {isLoading && (
        <div className="flex justify-center py-20">
          <Spinner size="lg" />
        </div>
      )}

      {/* ── Error ── */}
      {error && (
        <ErrorMessage message={getApiErrorMessage(error)} className="mb-6" />
      )}

      {/* ── Empty state ── */}
      {!isLoading && !error && data?.length === 0 && (
        <EmptyState
          icon="👶"
          title="No children yet"
          description="Add your first child profile to start tracking their learning journey."
          action={
            <Link to="/children" className="btn-primary">
              Add first child
            </Link>
          }
        />
      )}

      {/* ── Child cards grid ── */}
      {data && data.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {data.map((child, i) => (
            <ChildCard key={child.id} child={child} delay={i * 80} />
          ))}

          {/* Add child CTA card */}
          <Link
            to="/children"
            className={clsx(
              'card border-dashed border-surface-300 bg-transparent',
              'flex flex-col items-center justify-center gap-2',
              'p-8 text-center cursor-pointer',
              'hover:border-primary-400 hover:bg-primary-50 transition-all duration-200',
              'group animate-fade-up',
            )}
            style={{ animationDelay: `${data.length * 80}ms` }}
          >
            <div className="w-12 h-12 rounded-2xl border-2 border-dashed border-surface-300 group-hover:border-primary-400 flex items-center justify-center transition-colors">
              <span className="text-2xl text-surface-300 group-hover:text-primary-400 transition-colors">+</span>
            </div>
            <span className="text-sm font-semibold text-surface-400 group-hover:text-primary-600 transition-colors">
              Add another child
            </span>
          </Link>
        </div>
      )}

      {/* ── Quick actions ── */}
      {data && data.length > 0 && (
        <div className="mt-10">
          <h2 className="section-heading">Quick actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <QuickAction
              icon="◈"
              title="Browse modules"
              description="Explore all available skill modules"
              to="/learn"
              colour="green"
            />
            <QuickAction
              icon="◎"
              title="Manage children"
              description="Add, edit, or view child profiles"
              to="/children"
              colour="amber"
            />
          </div>
        </div>
      )}
    </div>
  )
}

// ── Child card ─────────────────────────────────────────────────────────────────

function ChildCard({ child, delay }: { child: ChildSummary; delay: number }) {
  return (
    <Link
      to={`/children/${child.id}`}
      className="card-hover p-5 flex flex-col gap-4 animate-fade-up opacity-0"
      style={{ animationDelay: `${delay}ms`, animationFillMode: 'forwards' }}
    >
      {/* Avatar + name */}
      <div className="flex items-center gap-3">
        <Avatar name={child.display_name} imageUrl={child.avatar_url} size="lg" />
        <div>
          <p className="font-semibold text-surface-900 text-base leading-tight">
            {child.display_name}
          </p>
          <p className="text-surface-400 text-sm">Age {child.age}</p>
        </div>
      </div>

      {/* XP bar */}
      <XPBar current={child.total_xp} showLabel />

      {/* CTA */}
      <div className="flex items-center justify-between pt-1">
        <span className="badge-green">View progress</span>
        <span className="text-surface-300 text-sm">→</span>
      </div>
    </Link>
  )
}

// ── Quick action card ──────────────────────────────────────────────────────────

function QuickAction({
  icon, title, description, to, colour,
}: {
  icon: string
  title: string
  description: string
  to: string
  colour: 'green' | 'amber'
}) {
  const colours = {
    green: 'bg-primary-50 border-primary-200 hover:border-primary-400',
    amber: 'bg-accent-50 border-accent-200 hover:border-accent-400',
  }
  const iconColours = {
    green: 'text-primary-500',
    amber: 'text-accent-500',
  }

  return (
    <Link
      to={to}
      className={clsx(
        'flex items-center gap-4 p-4 rounded-2xl border transition-all duration-200',
        'hover:-translate-y-0.5 hover:shadow-card',
        colours[colour],
      )}
    >
      <span className={clsx('text-2xl', iconColours[colour])}>{icon}</span>
      <div>
        <p className="font-semibold text-surface-800 text-sm">{title}</p>
        <p className="text-surface-400 text-xs">{description}</p>
      </div>
      <span className="ml-auto text-surface-300">→</span>
    </Link>
  )
}

// ── Greeting based on time ─────────────────────────────────────────────────────
function greeting(): string {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good afternoon'
  return 'Good evening'
}
