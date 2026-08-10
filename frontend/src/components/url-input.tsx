import { useState } from 'react'
import { Globe, Loader2 } from 'lucide-react'
import { cn } from '@/utils/cn'
import { isValidUrl } from '@/utils/validators'

interface UrlInputProps {
  onSubmit: (url: string) => void
  isLoading?: boolean
  placeholder?: string
  className?: string
}

export function UrlInput({
  onSubmit,
  isLoading = false,
  placeholder = 'Enter website URL...',
  className,
}: UrlInputProps) {
  const [url, setUrl] = useState('')
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    const trimmedUrl = url.trim()
    if (!trimmedUrl) {
      setError('Please enter a URL')
      return
    }

    // Add https:// if no protocol
    let finalUrl = trimmedUrl
    if (!finalUrl.startsWith('http://') && !finalUrl.startsWith('https://')) {
      finalUrl = `https://${finalUrl}`
    }

    if (!isValidUrl(finalUrl)) {
      setError('Please enter a valid URL')
      return
    }

    onSubmit(finalUrl)
  }

  return (
    <div className={cn('w-full', className)}>
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative flex items-center">
          <Globe className="absolute left-3 h-5 w-5 text-muted-foreground" />
          <input
            type="text"
            value={url}
            onChange={(e) => {
              setUrl(e.target.value)
              setError(null)
            }}
            placeholder={placeholder}
            className={cn(
              'h-12 w-full rounded-lg border bg-background pl-10 pr-28 text-sm outline-none transition-colors',
              error
                ? 'border-destructive focus:border-destructive'
                : 'border-input focus:border-primary'
            )}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !url.trim()}
            className={cn(
              'absolute right-1 h-10 rounded-md px-4 text-sm font-medium transition-colors',
              'bg-primary text-primary-foreground hover:bg-primary/90',
              'disabled:cursor-not-allowed disabled:opacity-50'
            )}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              'Analyze'
            )}
          </button>
        </div>
        {error && <p className="mt-2 text-sm text-destructive">{error}</p>}
      </form>
    </div>
  )
}