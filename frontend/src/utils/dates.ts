import { format, formatDistanceToNow, parseISO, differenceInDays } from 'date-fns'

export function parseDate(date: string | Date): Date {
  if (typeof date === 'string') {
    return parseISO(date)
  }
  return date
}

export function isExpired(date: string | Date): boolean {
  const d = parseDate(date)
  return d < new Date()
}

export function daysUntil(date: string | Date): number {
  const d = parseDate(date)
  return differenceInDays(d, new Date())
}

export function isToday(date: string | Date): boolean {
  const d = parseDate(date)
  const today = new Date()
  return (
    d.getFullYear() === today.getFullYear() &&
    d.getMonth() === today.getMonth() &&
    d.getDate() === today.getDate()
  )
}

export function isThisWeek(date: string | Date): boolean {
  const d = parseDate(date)
  const today = new Date()
  const weekAgo = new Date(today)
  weekAgo.setDate(weekAgo.getDate() - 7)
  return d >= weekAgo && d <= today
}

export function isThisMonth(date: string | Date): boolean {
  const d = parseDate(date)
  const today = new Date()
  return (
    d.getFullYear() === today.getFullYear() &&
    d.getMonth() === today.getMonth()
  )
}