import { useEffect, useState, useCallback } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { clsx } from 'clsx'

import { useScenarioStore }  from '@/store/scenarioStore'
import { useSubmitChoice }   from '@/hooks/useScenario'
import { ChoiceButton }      from '@/components/scenario/ChoiceButton'
import { CompletionScreen }  from '@/components/scenario/CompletionScreen'
import { FeedbackToast }     from '@/components/scenario/FeedbackToast'
import { Spinner }           from '@/components/ui/Spinner'
import { ErrorMessage }      from '@/components/ui/ErrorMessage'
import { getApiErrorMessage } from '@/api/client'
import { scenariosApi }      from '@/api/scenarios'
import type { ScenarioChoice } from '@/types'

/**
 * ScenarioPlayer
 *
 * Full-screen immersive scenario experience.
 *
 * Layout: light background, centred content card, choice buttons stacked below.
 * Node transitions: fade-out current content → fade-in new content.
 * Feedback: FeedbackToast appears for 2.2s after each choice.
 *
 * State source: useScenarioStore (populated by LessonList before navigation).
 * If the store is empty (direct URL access / page refresh), fetches the
 * attempt from the URL params and resumes.
 */
export function ScenarioPlayerPage() {
  const { moduleId, lessonId } = useParams<{
    moduleId: string
    lessonId: string
  }>()

  const attempt      = useScenarioStore((s) => s.attempt)
  const currentNode  = useScenarioStore((s) => s.currentNode)
  const pendingFeedback = useScenarioStore((s) => s.pendingFeedback)
  const isAdvancing  = useScenarioStore((s) => s.isAdvancing)
  const clearFeedback = useScenarioStore((s) => s.clearFeedback)
  const startScenario = useScenarioStore((s) => s.startScenario)
  const resetScenario = useScenarioStore((s) => s.resetScenario)

  const submitChoice = useSubmitChoice()
  const navigate     = useNavigate()

  // Track which choice the user just clicked (for per-button loading state)
  const [submittingChoiceId, setSubmittingChoiceId] = useState<number | null>(null)

  // Track which choice was last submitted (for feedback toast context)
  const [lastChoiceWasSafe, setLastChoiceWasSafe] = useState<boolean | null>(null)

  // Node transition animation flag
  const [nodeVisible, setNodeVisible] = useState(true)

  // Resume from URL if store is empty (page refresh scenario)
  const [isResuming, setIsResuming] = useState(false)
  const [resumeError, setResumeError] = useState<string | null>(null)

  useEffect(() => {
    // Store already has data — the user navigated here from LessonList
    if (attempt) return

    // Store is empty — try to resume the most recent in-progress attempt
    // by fetching from the backend using lessonId
    async function resume() {
      setIsResuming(true)
      try {
        const lessonIdNum = Number(lessonId)
        // We don't have the attemptId here, so we can't resume directly.
        // Redirect back to the lesson list — the user can start again.
        navigate(`/learn/${moduleId}`, { replace: true })
      } catch (err) {
        setResumeError(getApiErrorMessage(err))
      } finally {
        setIsResuming(false)
      }
    }

    resume()
  }, [attempt, lessonId, moduleId, navigate])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Don't reset if scenario is completed — we still want to show the
      // result if the user presses back then forward
    }
  }, [])

  // ── Handle choice submission ───────────────────────────────────────────────

  const handleChoiceClick = useCallback(
    (choice: ScenarioChoice) => {
      if (!attempt || isAdvancing || submittingChoiceId !== null) return

      setSubmittingChoiceId(choice.id)
      setLastChoiceWasSafe(choice.is_safe_choice)

      // Trigger node fade-out just before the network request resolves
      submitChoice.mutate(
        { attemptId: attempt.id, choiceId: choice.id },
        {
          onSuccess: () => {
            // Animate out current node
            setNodeVisible(false)
            // After fade-out, the store update will trigger a re-render
            // with the new node, then we fade it back in
            setTimeout(() => {
              setNodeVisible(true)
              setSubmittingChoiceId(null)
            }, 260)
          },
          onError: (err) => {
            setSubmittingChoiceId(null)
            setResumeError(getApiErrorMessage(err))
          },
        },
      )
    },
    [attempt, isAdvancing, submittingChoiceId, submitChoice],
  )

  // ── Handle "play again" ────────────────────────────────────────────────────

  async function handlePlayAgain() {
    if (!attempt) return
    resetScenario()

    try {
      const fresh = await scenariosApi.startAttempt(attempt.child_id, attempt.lesson_id)
      startScenario(fresh)
      setNodeVisible(true)
      setSubmittingChoiceId(null)
      setResumeError(null)
    } catch (err) {
      setResumeError(getApiErrorMessage(err))
    }
  }

  // ── Loading / error states ─────────────────────────────────────────────────

  if (isResuming) {
    return (
      <PlayerShell moduleId={moduleId!}>
        <div className="flex-1 flex items-center justify-center">
          <Spinner size="lg" />
        </div>
      </PlayerShell>
    )
  }

  if (resumeError) {
    return (
      <PlayerShell moduleId={moduleId!}>
        <div className="flex-1 flex flex-col items-center justify-center gap-4 px-6">
          <ErrorMessage message={resumeError} className="max-w-md" />
          <Link to={`/learn/${moduleId}`} className="btn-outline">
            Back to lessons
          </Link>
        </div>
      </PlayerShell>
    )
  }

  if (!attempt || !currentNode) {
    return (
      <PlayerShell moduleId={moduleId!}>
        <div className="flex-1 flex items-center justify-center">
          <Spinner size="lg" />
        </div>
      </PlayerShell>
    )
  }

  // ── Scenario complete ──────────────────────────────────────────────────────

  const isComplete = attempt.status === 'completed'

  if (isComplete) {
    return (
      <PlayerShell moduleId={moduleId!}>
        <CompletionScreen
          attempt={attempt}
          moduleId={moduleId!}
          lessonTitle={`Lesson ${lessonId}`}
          onPlayAgain={handlePlayAgain}
        />
      </PlayerShell>
    )
  }

  // ── Active play ────────────────────────────────────────────────────────────

  const choices = [...(currentNode.choices ?? [])].sort(
    (a, b) => a.order_index - b.order_index,
  )

  return (
    <PlayerShell moduleId={moduleId!}>
      {/* ── Node content ── */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-8">
        <div
          className={clsx(
            'w-full max-w-2xl transition-all duration-250',
            nodeVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2',
          )}
        >
          {/* Progress indicator (node type) */}
          <div className="flex items-center justify-center mb-6">
            <span
              className={clsx(
                'text-xs font-semibold uppercase tracking-widest px-3 py-1 rounded-full',
                currentNode.node_type === 'start'
                  ? 'bg-primary-100 text-primary-700'
                  : 'bg-surface-200 text-surface-500',
              )}
            >
              {currentNode.node_type === 'start' ? 'Scene' : 'What happens next…'}
            </span>
          </div>

          {/* Optional image */}
          {currentNode.image_url && (
            <div className="w-full rounded-2xl overflow-hidden mb-6 aspect-video bg-surface-100">
              <img
                src={currentNode.image_url}
                alt="Scene illustration"
                className="w-full h-full object-cover"
              />
            </div>
          )}

          {/* Story content card */}
          <div className="card p-7 mb-8 shadow-panel">
            <p className="font-sans text-lg text-surface-800 leading-relaxed text-center">
              {currentNode.content_text}
            </p>
          </div>

          {/* Choices */}
          <div className="space-y-3">
            {choices.length > 0 ? (
              <>
                <p className="text-xs text-surface-400 text-center font-semibold uppercase tracking-widest mb-4">
                  What do you do?
                </p>
                {choices.map((choice) => (
                  <ChoiceButton
                    key={choice.id}
                    choice={choice}
                    disabled={isAdvancing || submittingChoiceId !== null}
                    isSubmitting={submittingChoiceId === choice.id}
                    onClick={handleChoiceClick}
                  />
                ))}
              </>
            ) : (
              /* END node with no choices — shouldn't normally appear,
                 but handle gracefully */
              <div className="text-center">
                <p className="text-surface-400 text-sm mb-4">End of scenario</p>
                <Link to={`/learn/${moduleId}`} className="btn-primary">
                  Back to lessons
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Feedback toast */}
      {pendingFeedback && (
        <FeedbackToast
          message={pendingFeedback}
          isSafe={lastChoiceWasSafe}
          onDismiss={clearFeedback}
        />
      )}
    </PlayerShell>
  )
}

// ── Player shell ───────────────────────────────────────────────────────────────
// Provides the top bar and the full-height container for all player states.

function PlayerShell({
  moduleId,
  children,
}: {
  moduleId: string
  children: React.ReactNode
}) {
  const attempt = useScenarioStore((s) => s.attempt)
  const reset   = useScenarioStore((s) => s.resetScenario)

  return (
    <div className="min-h-screen bg-surface-50 flex flex-col">
      {/* ── Top bar ── */}
      <header className="bg-white border-b border-surface-200 px-6 py-3 flex items-center gap-4 sticky top-0 z-20">
        <Link
          to={`/learn/${moduleId}`}
          onClick={reset}
          className="flex items-center gap-2 text-sm text-surface-400 hover:text-surface-700 transition-colors font-medium"
        >
          ← Exit lesson
        </Link>

        <div className="flex-1" />

        {attempt && (
          <div className="flex items-center gap-2 text-sm text-surface-400">
            <span className="text-surface-300">⭐</span>
            <span className="font-semibold text-surface-600">
              {attempt.xp_earned} XP
            </span>
          </div>
        )}
      </header>

      {/* ── Content ── */}
      <div className="flex-1 flex flex-col">
        {children}
      </div>
    </div>
  )
}
