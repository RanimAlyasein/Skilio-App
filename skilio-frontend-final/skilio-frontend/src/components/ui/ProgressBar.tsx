import { clsx } from 'clsx'

interface ProgressBarProps {
  value: number      // 0-100
  label?: string
  size?: 'sm' | 'md'
  colour?: 'primary' | 'accent' | 'blue'
  className?: string
}

const trackColours = {
  primary: 'bg-primary-500',
  accent:  'bg-accent-500',
  blue:    'bg-blue-500',
}

const heights = {
  sm: 'h-1.5',
  md: 'h-2.5',
}

export function ProgressBar({
  value,
  label,
  size = 'md',
  colour = 'primary',
  className,
}: ProgressBarProps) {
  const clamped = Math.max(0, Math.min(100, Math.round(value)))

  return (
    <div className={clsx('w-full', className)}>
      {label && (
        <div className="flex justify-between items-center mb-1">
          <span className="text-xs text-surface-600 font-medium">{label}</span>
          <span className="text-xs text-surface-400 font-semibold">{clamped}%</span>
        </div>
      )}
      <div className={clsx('w-full rounded-full bg-surface-200 overflow-hidden', heights[size])}>
        <div
          className={clsx(
            'h-full rounded-full transition-all duration-700 ease-out',
            trackColours[colour],
          )}
          style={{ width: `${clamped}%` }}
          role="progressbar"
          aria-valuenow={clamped}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  )
}
