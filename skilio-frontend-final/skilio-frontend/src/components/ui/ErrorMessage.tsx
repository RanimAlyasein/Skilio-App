import { clsx } from 'clsx'

interface ErrorMessageProps {
  message: string
  className?: string
}

export function ErrorMessage({ message, className }: ErrorMessageProps) {
  return (
    <div
      role="alert"
      className={clsx(
        'flex items-start gap-2.5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700',
        className,
      )}
    >
      <span className="mt-0.5 shrink-0 text-base">⚠</span>
      <span>{message}</span>
    </div>
  )
}
