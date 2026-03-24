import { clsx } from 'clsx'

interface EmptyStateProps {
  icon?: string
  title: string
  description?: string
  action?: React.ReactNode
  className?: string
}

export function EmptyState({ icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div
      className={clsx(
        'flex flex-col items-center justify-center text-center py-16 px-6',
        className,
      )}
    >
      {icon && (
        <div className="text-5xl mb-4 animate-bounce-soft">{icon}</div>
      )}
      <h3 className="font-display text-xl font-semibold text-surface-700 mb-2">{title}</h3>
      {description && (
        <p className="text-surface-400 text-sm max-w-xs mb-6">{description}</p>
      )}
      {action}
    </div>
  )
}
