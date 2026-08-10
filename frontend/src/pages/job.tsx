import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Clock, CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { useJob } from '@/hooks/use-jobs'
import { Button } from '@/components/ui/button'
import { ProgressBar } from '@/components/progress-bar'
import { StatusBadge } from '@/components/status-badge'
import { formatDate, formatDuration } from '@/utils/format'

export function JobPage() {
  const { jobId } = useParams<{ jobId: string }>()
  const { data: job, isLoading } = useJob(jobId!)

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  if (!job) {
    return (
      <div className="text-center">
        <h2 className="text-2xl font-bold">Job not found</h2>
        <Button asChild className="mt-4">
          <Link to="/dashboard">Go back</Link>
        </Button>
      </div>
    )
  }

  const isComplete = job.status === 'completed' || job.status === 'failed'
  const isRunning = job.status === 'running' || job.status === 'queued'

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Button asChild variant="ghost" size="sm">
          <Link to="/dashboard">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Job Details</h1>
          <p className="text-sm text-muted-foreground">ID: {job.id}</p>
        </div>
      </div>

      {/* Status */}
      <div className="rounded-lg border bg-card p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <StatusBadge status={job.status} />
            {isRunning && (
              <div className="flex items-center text-sm text-muted-foreground">
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </div>
            )}
            {isComplete && job.status === 'completed' && (
              <div className="flex items-center text-sm text-green-600">
                <CheckCircle className="mr-2 h-4 w-4" />
                Completed
              </div>
            )}
            {isComplete && job.status === 'failed' && (
              <div className="flex items-center text-sm text-destructive">
                <XCircle className="mr-2 h-4 w-4" />
                Failed
              </div>
            )}
          </div>
          <div className="text-right">
            <p className="text-sm text-muted-foreground">Started</p>
            <p className="text-sm">{formatDate(job.started_at)}</p>
          </div>
        </div>

        {isRunning && (
          <div className="mt-4">
            <ProgressBar value={job.progress || 0} />
            <p className="mt-2 text-sm text-muted-foreground">
              {job.progress || 0}% complete
            </p>
          </div>
        )}

        {job.error_message && (
          <div className="mt-4 rounded-lg bg-destructive/10 p-4 text-sm text-destructive">
            <p className="font-semibold">Error:</p>
            <p>{job.error_message}</p>
          </div>
        )}
      </div>

      {/* Details */}
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-lg border bg-card p-4">
          <h3 className="text-sm font-medium text-muted-foreground">Type</h3>
          <p className="mt-1 capitalize">{job.type}</p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <h3 className="text-sm font-medium text-muted-foreground">Progress</h3>
          <p className="mt-1">{job.progress || 0}%</p>
        </div>
        {job.started_at && (
          <div className="rounded-lg border bg-card p-4">
            <h3 className="text-sm font-medium text-muted-foreground">Started</h3>
            <p className="mt-1">{formatDate(job.started_at)}</p>
          </div>
        )}
        {job.completed_at && (
          <div className="rounded-lg border bg-card p-4">
            <h3 className="text-sm font-medium text-muted-foreground">Completed</h3>
            <p className="mt-1">{formatDate(job.completed_at)}</p>
          </div>
        )}
      </div>

      {job.results && (
        <div className="rounded-lg border bg-card p-4">
          <h3 className="mb-2 text-sm font-medium text-muted-foreground">Results</h3>
          <pre className="rounded bg-secondary p-4 text-sm">
            {JSON.stringify(job.results, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}