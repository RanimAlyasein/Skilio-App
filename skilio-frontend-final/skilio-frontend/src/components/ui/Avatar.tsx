import { clsx } from 'clsx'

interface AvatarProps {
  name: string
  imageUrl?: string | null
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
}

// Deterministic colour based on the first character of the name
const COLOURS = [
  'bg-primary-100 text-primary-700',
  'bg-accent-100  text-accent-700',
  'bg-purple-100  text-purple-700',
  'bg-blue-100    text-blue-700',
  'bg-rose-100    text-rose-700',
  'bg-teal-100    text-teal-700',
]

function colourFor(name: string): string {
  const idx = name.charCodeAt(0) % COLOURS.length
  return COLOURS[idx]
}

const sizes = {
  sm: 'w-8 h-8 text-xs',
  md: 'w-10 h-10 text-sm',
  lg: 'w-14 h-14 text-lg',
  xl: 'w-20 h-20 text-2xl',
}

export function Avatar({ name, imageUrl, size = 'md', className }: AvatarProps) {
  const initials = name
    .split(' ')
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? '')
    .join('')

  if (imageUrl) {
    return (
      <img
        src={imageUrl}
        alt={name}
        className={clsx('rounded-full object-cover flex-shrink-0', sizes[size], className)}
      />
    )
  }

  return (
    <div
      aria-label={name}
      className={clsx(
        'rounded-full flex items-center justify-center font-bold flex-shrink-0 select-none',
        sizes[size],
        colourFor(name),
        className,
      )}
    >
      {initials}
    </div>
  )
}
