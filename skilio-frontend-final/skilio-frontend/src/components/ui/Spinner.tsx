import { clsx } from 'clsx'

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const sizes = {
  sm: 'w-4 h-4 border-2',
  md: 'w-6 h-6 border-2',
  lg: 'w-10 h-10 border-[3px]',
}

export function Spinner({ size = 'md', className }: SpinnerProps) {
  return (
    <div
      role="status"
      aria-label="Loading"
      className={clsx(
        'rounded-full border-surface-300 border-t-primary-500 animate-spin',
        sizes[size],
        className,
      )}
    />
  )
}
