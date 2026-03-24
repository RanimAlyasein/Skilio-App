import { useState } from 'react'
import { Link } from 'react-router-dom'
import { clsx } from 'clsx'

import { useModules }    from '@/hooks/useModules'
import { useChildren }   from '@/hooks/useChildren'
import { Spinner }       from '@/components/ui/Spinner'
import { EmptyState }    from '@/components/ui/EmptyState'
import { ErrorMessage }  from '@/components/ui/ErrorMessage'
import { getApiErrorMessage } from '@/api/client'
import type { SkillModule } from '@/types'

export function ModuleBrowserPage() {
  const { data: children } = useChildren()

  // Age filter: "all" or a specific child's age
  const [selectedAge, setSelectedAge] = useState<number | undefined>(undefined)

  const { data: modules, isLoading, error } = useModules(selectedAge)

  return (
    <div className="page-container">

      <div className="animate-fade-up">
        <h1 className="page-title">Skill modules</h1>
        <p className="page-subtitle">Choose a module to start learning</p>
      </div>

      {/* ── Age filter ── */}
      {children && children.length > 0 && (
        <div className="flex gap-2 flex-wrap mb-8 animate-fade-up animation-delay-100">
          <FilterChip
            label="All ages"
            active={selectedAge === undefined}
            onClick={() => setSelectedAge(undefined)}
          />
          {children.map((c) => (
            <FilterChip
              key={c.id}
              label={`${c.display_name} (age ${c.age})`}
              active={selectedAge === c.age}
              onClick={() => setSelectedAge(c.age)}
            />
          ))}
        </div>
      )}

      {isLoading && (
        <div className="flex justify-center py-20"><Spinner size="lg" /></div>
      )}

      {error && <ErrorMessage message={getApiErrorMessage(error)} />}

      {!isLoading && modules?.length === 0 && (
        <EmptyState
          icon="📚"
          title="No modules found"
          description="No modules match the selected age filter."
        />
      )}

      {modules && modules.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {modules.map((module, i) => (
            <ModuleCard
              key={module.id}
              module={module}
              delay={i * 60}
            />
          ))}
        </div>
      )}
    </div>
  )
}

// ── Module card ────────────────────────────────────────────────────────────────

function ModuleCard({ module: m, delay }: { module: SkillModule; delay: number }) {
  const COLOURS = [
    'from-primary-400 to-primary-600',
    'from-accent-400 to-accent-600',
    'from-blue-400 to-blue-600',
    'from-purple-400 to-purple-600',
    'from-teal-400 to-teal-600',
  ]
  const colour = COLOURS[m.id % COLOURS.length]

  return (
    <Link
      to={`/learn/${m.id}`}
      className="card-hover flex flex-col overflow-hidden animate-fade-up opacity-0"
      style={{ animationDelay: `${delay}ms`, animationFillMode: 'forwards' }}
    >
      {/* Colour banner */}
      <div className={clsx('h-28 bg-gradient-to-br flex items-end p-4', colour)}>
        <div>
          <span className="text-white/70 text-xs font-semibold uppercase tracking-wider">
            Ages {m.age_min}–{m.age_max}
          </span>
          <h3 className="font-display text-xl font-semibold text-white leading-tight mt-0.5">
            {m.title}
          </h3>
        </div>
      </div>

      {/* Body */}
      <div className="p-5 flex flex-col gap-3 flex-1">
        <p className="text-surface-500 text-sm leading-relaxed line-clamp-2">
          {m.description}
        </p>
        <div className="mt-auto flex items-center justify-between">
          <span className="badge-green">Explore →</span>
        </div>
      </div>
    </Link>
  )
}

// ── Filter chip ────────────────────────────────────────────────────────────────

function FilterChip({
  label, active, onClick,
}: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={clsx(
        'px-3.5 py-1.5 rounded-full text-sm font-semibold transition-all duration-150',
        active
          ? 'bg-primary-500 text-white shadow-sm'
          : 'bg-surface-100 text-surface-500 hover:bg-surface-200',
      )}
    >
      {label}
    </button>
  )
}
