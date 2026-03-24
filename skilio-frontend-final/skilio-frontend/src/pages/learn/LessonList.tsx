import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { clsx } from 'clsx'

import { useModule }   from '@/hooks/useModules'
import { useChildren } from '@/hooks/useChildren'
import { Spinner }     from '@/components/ui/Spinner'
import { ErrorMessage }from '@/components/ui/ErrorMessage'
import { Avatar }      from '@/components/ui/Avatar'
import { getApiErrorMessage } from '@/api/client'
import { scenariosApi } from '@/api/scenarios'
import { useScenarioStore } from '@/store/scenarioStore'
import type { Lesson, ChildSummary } from '@/types'

export function LessonListPage() {
  const { moduleId } = useParams<{ moduleId: string }>()
  const id = Number(moduleId)

  const { data: module, isLoading, error } = useModule(id)
  const { data: children } = useChildren()

  // Which child is playing — defaults to first child
  const [selectedChildId, setSelectedChildId] = useState<number | null>(null)
  const [startingLessonId, setStartingLessonId] = useState<number | null>(null)
  const [startError, setStartError] = useState<string | null>(null)

  const startScenario = useScenarioStore((s) => s.startScenario)
  const navigate = useNavigate()

  // Resolved child: explicit selection or first child
  const activeChildId =
    selectedChildId ??
    (children && children.length > 0 ? children[0].id : null)

  async function handleStart(lesson: Lesson) {
    if (!activeChildId) return
    if (!lesson.entry_node_id) {
      setStartError('This lesson has no content yet.')
      return
    }

    setStartingLessonId(lesson.id)
    setStartError(null)

    try {
      const attempt = await scenariosApi.startAttempt(activeChildId, lesson.id)
      startScenario(attempt)
      navigate(`/learn/${moduleId}/${lesson.id}/play`)
    } catch (err) {
      setStartError(getApiErrorMessage(err))
    } finally {
      setStartingLessonId(null)
    }
  }

  // ── Loading ────────────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="page-container flex justify-center py-20">
        <Spinner size="lg" />
      </div>
    )
  }

  if (error || !module) {
    return (
      <div className="page-container">
        <ErrorMessage message={error ? getApiErrorMessage(error) : 'Module not found'} />
      </div>
    )
  }

  const COLOURS = [
    'from-primary-400 to-primary-600',
    'from-accent-400 to-accent-600',
    'from-blue-400 to-blue-600',
    'from-purple-400 to-purple-600',
    'from-teal-400 to-teal-600',
  ]
  const bannerColour = COLOURS[module.id % COLOURS.length]

  return (
    <div className="page-container">

      {/* ── Back link ── */}
      <Link
        to="/learn"
        className="inline-flex items-center gap-1.5 text-sm text-surface-400 hover:text-surface-700 mb-6 transition-colors animate-fade-up"
      >
        ← All modules
      </Link>

      {/* ── Module header banner ── */}
      <div
        className={clsx(
          'rounded-3xl bg-gradient-to-br p-8 mb-8 animate-fade-up animation-delay-100',
          bannerColour,
        )}
      >
        <span className="text-white/70 text-xs font-semibold uppercase tracking-widest">
          Ages {module.age_min}–{module.age_max}
        </span>
        <h1 className="font-display text-3xl font-semibold text-white mt-1 mb-2">
          {module.title}
        </h1>
        <p className="text-white/80 text-sm max-w-xl leading-relaxed">
          {module.description}
        </p>
        <div className="mt-4 flex items-center gap-2">
          <span className="bg-white/20 text-white text-xs font-semibold px-3 py-1 rounded-full">
            {module.lessons.length} {module.lessons.length === 1 ? 'lesson' : 'lessons'}
          </span>
        </div>
      </div>

      {/* ── Child selector ── */}
      {children && children.length > 1 && (
        <div className="card p-4 mb-6 animate-fade-up animation-delay-200">
          <p className="text-sm font-semibold text-surface-600 mb-3">Playing as:</p>
          <div className="flex gap-2 flex-wrap">
            {children.map((child) => (
              <ChildSelectChip
                key={child.id}
                child={child}
                active={(selectedChildId ?? children[0].id) === child.id}
                onClick={() => setSelectedChildId(child.id)}
              />
            ))}
          </div>
        </div>
      )}

      {/* ── No child warning ── */}
      {(!children || children.length === 0) && (
        <div className="card p-5 mb-6 border-amber-200 bg-amber-50 animate-fade-up">
          <p className="text-sm text-amber-700 font-medium">
            You need to add a child profile before playing lessons.{' '}
            <Link to="/children" className="underline font-semibold">
              Add a child →
            </Link>
          </p>
        </div>
      )}

      {/* ── Start error ── */}
      {startError && (
        <ErrorMessage message={startError} className="mb-5 animate-scale-in" />
      )}

      {/* ── Lesson list ── */}
      <h2 className="section-heading animate-fade-up animation-delay-200">
        Lessons
      </h2>

      {module.lessons.length === 0 ? (
        <p className="text-surface-400 text-sm py-6">
          No lessons available yet — check back soon.
        </p>
      ) : (
        <div className="space-y-3">
          {module.lessons
            .sort((a, b) => a.order_index - b.order_index)
            .map((lesson, i) => (
              <LessonCard
                key={lesson.id}
                lesson={lesson}
                index={i + 1}
                isStarting={startingLessonId === lesson.id}
                canPlay={!!activeChildId}
                onPlay={() => handleStart(lesson)}
                delay={i * 60}
              />
            ))}
        </div>
      )}
    </div>
  )
}

// ── Lesson card ────────────────────────────────────────────────────────────────

function LessonCard({
  lesson, index, isStarting, canPlay, onPlay, delay,
}: {
  lesson: Lesson
  index: number
  isStarting: boolean
  canPlay: boolean
  onPlay: () => void
  delay: number
}) {
  return (
    <div
      className="card p-5 flex items-center gap-5 animate-fade-up opacity-0"
      style={{ animationDelay: `${delay}ms`, animationFillMode: 'forwards' }}
    >
      {/* Lesson number badge */}
      <div className="w-10 h-10 rounded-2xl bg-surface-100 border border-surface-200 flex items-center justify-center shrink-0">
        <span className="text-sm font-bold text-surface-600 font-mono">{index}</span>
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-surface-900 text-base">{lesson.title}</h3>
        {lesson.description && (
          <p className="text-surface-400 text-sm mt-0.5 line-clamp-1">
            {lesson.description}
          </p>
        )}
        <div className="flex items-center gap-2 mt-2">
          <span className="badge-amber">⭐ {lesson.xp_reward} XP</span>
          {!lesson.entry_node_id && (
            <span className="badge-gray">Coming soon</span>
          )}
        </div>
      </div>

      {/* Play button */}
      <button
        onClick={onPlay}
        disabled={!canPlay || isStarting || !lesson.entry_node_id}
        className={clsx(
          'shrink-0 btn',
          lesson.entry_node_id
            ? 'btn-primary'
            : 'btn-outline opacity-50 cursor-not-allowed',
        )}
      >
        {isStarting ? (
          <>
            <Spinner size="sm" className="border-white/30 border-t-white" />
            Starting…
          </>
        ) : (
          '▶ Play'
        )}
      </button>
    </div>
  )
}

// ── Child selector chip ────────────────────────────────────────────────────────

function ChildSelectChip({
  child, active, onClick,
}: { child: ChildSummary; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={clsx(
        'flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-semibold',
        'transition-all duration-150 border',
        active
          ? 'bg-primary-500 text-white border-primary-500 shadow-sm'
          : 'bg-white text-surface-600 border-surface-200 hover:border-surface-300',
      )}
    >
      <Avatar name={child.display_name} size="sm" />
      {child.display_name}
    </button>
  )
}
