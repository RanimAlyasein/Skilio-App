import { clsx } from 'clsx'

interface XPBarProps {
  current: number
  /** The XP threshold for the next level. Defaults to next round 100 */
  max?: number
  showLabel?: boolean
  className?: string
  animate?: boolean
}

export function XPBar({
  current,
  max,
  showLabel = true,
  className,
  animate = true,
}: XPBarProps) {
  // Compute a meaningful max: next multiple of 100 above current
  const effectiveMax = max ?? Math.max(100, Math.ceil(current / 100) * 100)
  const pct = Math.min(100, Math.round((current / effectiveMax) * 100))

  return (
    <div className={clsx('w-full', className)}>
      {showLabel && (
        <div className="flex justify-between text-xs text-surface-500 mb-1 font-semibold">
          <span className="text-accent-600">⭐ {current} XP</span>
          <span>{effectiveMax} XP</span>
        </div>
      )}
      <div className="h-2.5 w-full rounded-full bg-surface-200 overflow-hidden">
        <div
          className={clsx(
            'h-full rounded-full bg-gradient-to-r from-accent-400 to-accent-500',
            animate && 'transition-all duration-700 ease-out',
          )}
          style={{ width: `${pct}%` }}
          role="progressbar"
          aria-valuenow={current}
          aria-valuemax={effectiveMax}
          aria-label={`${current} XP`}
        />
      </div>
    </div>
  )
}
