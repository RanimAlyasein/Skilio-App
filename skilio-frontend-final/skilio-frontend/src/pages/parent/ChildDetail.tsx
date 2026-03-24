import { Link, useParams } from 'react-router-dom'
import { useChildSummary } from '@/hooks/useChildren'
import { Avatar }       from '@/components/ui/Avatar'
import { XPBar }        from '@/components/ui/XPBar'
import { ProgressBar }  from '@/components/ui/ProgressBar'
import { Spinner }      from '@/components/ui/Spinner'
import { ErrorMessage } from '@/components/ui/ErrorMessage'
import { getApiErrorMessage } from '@/api/client'
import type { BadgeAward, ModuleProgress } from '@/types'

export function ChildDetailPage() {
  const { childId } = useParams<{ childId: string }>()
  const id = Number(childId)

  const { data, isLoading, error } = useChildSummary(id)

  if (isLoading) {
    return (
      <div className="page-container flex justify-center py-20">
        <Spinner size="lg" />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="page-container">
        <ErrorMessage message={error ? getApiErrorMessage(error) : 'Child not found'} />
      </div>
    )
  }

  return (
    <div className="page-container">

      {/* ── Back link ── */}
      <Link to="/dashboard" className="inline-flex items-center gap-1.5 text-sm text-surface-400 hover:text-surface-700 mb-6 transition-colors">
        ← Back to dashboard
      </Link>

      {/* ── Profile header ── */}
      <div className="card p-6 mb-6 flex items-center gap-5 animate-fade-up">
        <Avatar name={data.display_name} size="xl" />
        <div className="flex-1 min-w-0">
          <h1 className="font-display text-2xl font-semibold text-surface-900 mb-0.5">
            {data.display_name}
          </h1>
          <p className="text-surface-400 text-sm mb-3">Age {data.age}</p>
          <XPBar current={data.total_xp} className="max-w-sm" />
        </div>
        <div className="text-right shrink-0">
          <p className="font-display text-3xl font-semibold text-surface-900">
            {data.recent_attempt_count}
          </p>
          <p className="text-xs text-surface-400 font-medium">lessons played</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* ── Module progress ── */}
        <div className="card p-6 animate-fade-up animation-delay-100">
          <h2 className="section-heading">Module progress</h2>
          {data.module_progress.length === 0 ? (
            <p className="text-surface-400 text-sm py-4">
              No modules started yet.{' '}
              <Link to="/learn" className="text-primary-600 font-semibold hover:underline">
                Browse modules →
              </Link>
            </p>
          ) : (
            <div className="space-y-4">
              {data.module_progress.map((m) => (
                <ModuleProgressRow key={m.module_id} module={m} />
              ))}
            </div>
          )}
        </div>

        {/* ── Badges ── */}
        <div className="card p-6 animate-fade-up animation-delay-200">
          <h2 className="section-heading">Badges earned</h2>
          {data.badges_earned.length === 0 ? (
            <p className="text-surface-400 text-sm py-4">
              No badges yet — complete lessons to earn them!
            </p>
          ) : (
            <div className="grid grid-cols-2 gap-3">
              {data.badges_earned.map((award) => (
                <BadgeCard key={award.id} award={award} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function ModuleProgressRow({ module: m }: { module: ModuleProgress }) {
  return (
    <div>
      <div className="flex justify-between items-center mb-1.5">
        <span className="text-sm font-semibold text-surface-800">{m.module_title}</span>
        <span className="text-xs text-surface-400">
          {m.lessons_completed}/{m.total_lessons} lessons
        </span>
      </div>
      <ProgressBar value={m.completion_percentage} size="md" colour="primary" />
    </div>
  )
}

function BadgeCard({ award }: { award: BadgeAward }) {
  return (
    <div className="flex flex-col items-center gap-2 p-3 rounded-xl bg-accent-50 border border-accent-200 text-center">
      <div className="w-10 h-10 rounded-full bg-accent-100 flex items-center justify-center text-lg">
        ⭐
      </div>
      <p className="text-xs font-semibold text-accent-800 leading-tight">
        {award.badge.name}
      </p>
    </div>
  )
}
