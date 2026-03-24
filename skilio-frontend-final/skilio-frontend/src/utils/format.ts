// src/utils/format.ts
// Shared formatting utilities used across the app.

/** Format a date string as a human-readable relative time */
export function timeAgo(dateString: string): string {
  const now  = Date.now()
  const then = new Date(dateString).getTime()
  const diff = now - then

  const minute = 60_000
  const hour   = 60 * minute
  const day    = 24 * hour
  const week   = 7 * day

  if (diff < minute)   return 'just now'
  if (diff < hour)     return `${Math.floor(diff / minute)}m ago`
  if (diff < day)      return `${Math.floor(diff / hour)}h ago`
  if (diff < week)     return `${Math.floor(diff / day)}d ago`
  return new Date(dateString).toLocaleDateString()
}

/** Capitalise the first letter of a string */
export function capitalise(s: string): string {
  if (!s) return ''
  return s.charAt(0).toUpperCase() + s.slice(1)
}

/** Format XP with a thousands separator */
export function formatXP(xp: number): string {
  return xp.toLocaleString()
}
