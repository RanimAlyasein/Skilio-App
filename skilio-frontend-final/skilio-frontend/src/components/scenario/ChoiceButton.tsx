import { clsx } from 'clsx'
import type { ScenarioChoice } from '@/types'

interface ChoiceButtonProps {
  choice: ScenarioChoice
  disabled: boolean
  onClick: (choice: ScenarioChoice) => void
  /** If we just submitted this choice (shows a loading indicator) */
  isSubmitting: boolean
}

/**
 * ChoiceButton
 *
 * A large, tappable card for a single scenario choice.
 * Designed to be finger-friendly — generous padding, clear hover state.
 * Safe choices are NOT visually distinguished before selection
 * (that would defeat the learning purpose).
 */
export function ChoiceButton({
  choice,
  disabled,
  onClick,
  isSubmitting,
}: ChoiceButtonProps) {
  return (
    <button
      onClick={() => onClick(choice)}
      disabled={disabled}
      className={clsx(
        // Base layout
        'w-full text-left px-5 py-4 rounded-2xl',
        'flex items-center gap-4',
        // Border + background
        'bg-white border-2 border-surface-200',
        'transition-all duration-150',
        // Enabled state
        !disabled && [
          'hover:border-primary-400 hover:bg-primary-50',
          'hover:shadow-card-hover hover:-translate-y-0.5',
          'active:scale-[0.99] active:translate-y-0',
          'cursor-pointer',
        ],
        // Disabled / loading state
        disabled && 'opacity-50 cursor-not-allowed',
      )}
    >
      {/* Choice marker */}
      <div
        className={clsx(
          'w-9 h-9 rounded-xl border-2 flex items-center justify-center shrink-0',
          'transition-all duration-150',
          isSubmitting
            ? 'border-primary-400 bg-primary-50'
            : 'border-surface-300 bg-surface-50',
        )}
      >
        {isSubmitting ? (
          <div className="w-4 h-4 rounded-full border-2 border-primary-300 border-t-primary-600 animate-spin" />
        ) : (
          <span className="text-surface-400 font-mono text-xs font-bold">
            {String.fromCharCode(65 + choice.order_index)}
          </span>
        )}
      </div>

      {/* Choice text */}
      <span
        className={clsx(
          'text-sm font-semibold leading-snug',
          isSubmitting ? 'text-primary-700' : 'text-surface-800',
        )}
      >
        {choice.choice_text}
      </span>

      {/* Arrow indicator */}
      <span className="ml-auto text-surface-300 shrink-0">›</span>
    </button>
  )
}
