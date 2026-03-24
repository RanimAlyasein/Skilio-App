import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { clsx } from 'clsx'
import { useScenarioStore } from '@/store/scenarioStore'
import type { ScenarioAttempt } from '@/types'

interface CompletionScreenProps {
  attempt: ScenarioAttempt
  moduleId: string
  lessonTitle: string
  onPlayAgain: () => void
}

/**
 * CompletionScreen
 *
 * Shown when a child reaches an END node.
 * Celebrates the achievement with XP display, safe-path feedback,
 * and any newly awarded badges.
 */
export function CompletionScreen({
  attempt,
  moduleId,
  lessonTitle,
  onPlayAgain,
}: CompletionScreenProps) {
  const newBadgeIds     = useScenarioStore((s) => s.newlyAwardedBadgeIds)
  const resetScenario   = useScenarioStore((s) => s.resetScenario)

  // Staggered reveal: XP counter animates up
  const [displayXP, setDisplayXP] = useState(0)

  useEffect(() => {
    let frame: number
    let current = 0
    const target = attempt.xp_earned
    const step   = Math.max(1, Math.ceil(target / 40))

    function tick() {
      current = Math.min(current + step, target)
      setDisplayXP(current)
      if (current < target) frame = requestAnimationFrame(tick)
    }

    // Small delay so the animation starts after the screen fades in
    const delay = setTimeout(() => { frame = requestAnimationFrame(tick) }, 400)

    return () => {
      clearTimeout(delay)
      cancelAnimationFrame(frame)
    }
  }, [attempt.xp_earned])

  const isCorrectPath = attempt.xp_earned >= 40   // heuristic: full XP = correct path
  const xpColour      = isCorrectPath ? 'text-accent-500' : 'text-surface-500'

  return (
    <div className="flex flex-col items-center justify-center min-h-full py-16 px-6 animate-fade-in">

      {/* ── Trophy / result icon ── */}
      <div
        className={clsx(
          'w-24 h-24 rounded-3xl flex items-center justify-center mb-6',
          'shadow-lg animate-scale-in',
          isCorrectPath
            ? 'bg-gradient-to-br from-accent-300 to-accent-500'
            : 'bg-gradient-to-br from-surface-200 to-surface-400',
        )}
      >
        <span className="text-5xl">{isCorrectPath ? '🏆' : '📖'}</span>
      </div>

      {/* ── Heading ── */}
      <h1
        className={clsx(
          'font-display text-3xl font-semibold text-center mb-2 animate-fade-up animation-delay-100',
          isCorrectPath ? 'text-surface-900' : 'text-surface-700',
        )}
      >
        {isCorrectPath ? 'Lesson complete!' : 'Nice try!'}
      </h1>

      <p className="text-surface-400 text-sm text-center max-w-xs mb-8 animate-fade-up animation-delay-200">
        {isCorrectPath
          ? `You made great choices in "${lessonTitle}".`
          : `Keep practising — every attempt builds your skills.`}
      </p>

      {/* ── XP earned card ── */}
      <div className="card px-10 py-6 mb-6 text-center animate-scale-in animation-delay-300">
        <p className="text-xs font-semibold text-surface-400 uppercase tracking-widest mb-1">
          XP earned
        </p>
        <p className={clsx('font-display text-5xl font-semibold', xpColour)}>
          +{displayXP}
        </p>
      </div>

      {/* ── New badges ── */}
      {newBadgeIds.length > 0 && (
        <div className="mb-8 text-center animate-fade-up animation-delay-400">
          <p className="text-sm font-semibold text-accent-600 mb-3">
            🎖 New badge{newBadgeIds.length > 1 ? 's' : ''} earned!
          </p>
          <div className="flex gap-3 justify-center">
            {newBadgeIds.map((id) => (
              <div
                key={id}
                className="w-14 h-14 rounded-2xl bg-accent-50 border-2 border-accent-200 flex items-center justify-center text-2xl animate-bounce-soft"
              >
                ⭐
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Actions ── */}
      <div className="flex flex-col sm:flex-row gap-3 w-full max-w-xs animate-fade-up animation-delay-400">
        <Link
          to={`/learn/${moduleId}`}
          onClick={() => resetScenario()}
          className="btn-primary btn-lg flex-1 justify-center"
        >
          Back to lessons
        </Link>
        <button
          onClick={onPlayAgain}
          className="btn-outline btn-lg flex-1 justify-center"
        >
          Play again
        </button>
      </div>

      {/* ── Tip for incorrect path ── */}
      {!isCorrectPath && (
        <p className="mt-6 text-xs text-surface-400 text-center max-w-xs animate-fade-up animation-delay-500">
          Tip: Look for choices that keep you safe and near trusted adults.
        </p>
      )}
    </div>
  )
}
