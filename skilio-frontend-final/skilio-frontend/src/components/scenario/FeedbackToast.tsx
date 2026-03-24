import { useEffect } from 'react'
import { clsx } from 'clsx'

interface FeedbackToastProps {
  message: string
  isSafe: boolean | null
  onDismiss: () => void
}

/**
 * FeedbackToast
 *
 * Briefly shown after a choice is submitted, before transitioning to
 * the next node. Auto-dismisses after 2.2 seconds so gameplay feels fluid.
 */
export function FeedbackToast({ message, isSafe, onDismiss }: FeedbackToastProps) {
  useEffect(() => {
    const timer = setTimeout(onDismiss, 2200)
    return () => clearTimeout(timer)
  }, [message, onDismiss])

  return (
    <div
      className={clsx(
        'fixed bottom-8 left-1/2 -translate-x-1/2 z-50',
        'max-w-md w-[calc(100%-2rem)] px-5 py-3.5 rounded-2xl',
        'flex items-start gap-3 shadow-panel',
        'animate-fade-up',
        isSafe === true
          ? 'bg-primary-600 text-white'
          : isSafe === false
          ? 'bg-surface-800 text-surface-100'
          : 'bg-surface-800 text-surface-100',
      )}
    >
      <span className="text-xl shrink-0 mt-0.5">
        {isSafe === true ? '✓' : isSafe === false ? '→' : '→'}
      </span>
      <p className="text-sm font-medium leading-snug">{message}</p>
      <button
        onClick={onDismiss}
        className="ml-auto shrink-0 opacity-60 hover:opacity-100 transition-opacity text-lg leading-none"
        aria-label="Dismiss"
      >
        ×
      </button>
    </div>
  )
}
