import { Link } from 'react-router-dom'
import { Loader2, CheckCircle, XCircle, Clock } from 'lucide-react'
import { Job } from '@/types/job'
import { StatusBadge } from './status-badge'
import { ProgressBar } from './progress-bar'
import { cn } from '@/utils/cn'

interface JobStatusProps {
  job: Job
  showDetails?: boolean
  className?: string
}

export function JobStatus({ job, showDetails = false, className }: JobStatusProps) {
  const isRunning = job.status === 'running' || job.status === 'queued'
  const isComplete = job.status === 'completed'
  const isFailed = job.status === 'failed'
  const isCancelled = job.status === 'cancelled'

  return (
    <div className={cn('space-y-2', className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <StatusBadge status={job.status} />
          {isRunning && (
            <div className="flex items-center text-sm text-muted-foreground">
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Processing...
            </div>
          )}
          {isComplete && (
            <div className="flex items-center text-sm text-green-600">
              <CheckCircle className="mr-2 h-4 w-4" />
              Completed
            </div>
          )}
          {isFailed && (
            <div className="flex items-center text-sm text-destructive">
              <XCircle className="mr-2 h-4 w-4" />
              Failed
            </div>
          )}
          {isCancelled && (
            <div className="flex items-center text-sm text-muted-foreground">
              <Clock className="mr-2 h-4 w-4" />
              Cancelled
            </div>
          )}
        </div>

        {showDetails && (
          <Link
            to={`/jobs/${job.id}`}
            className="text-sm text-primary hover:underline"
          >
            View Details
          </Link>
        )}
      </div>

      {isRunning && (
        <div className="space-y-1">
          <ProgressBar value={job.progress || 0} />
          <p className="text-xs text-muted-foreground">
            {job.progress || 0}% complete
          </p>
        </div>
      )}

      {isFailed && job.error_message && (
        <div className="rounded bg-destructive/10 p-2 text-sm text-destructive">
          <p className="font-semibold">Error:</p>
          <p>{job.error_message}</p>
        </div>
      )}

      {showDetails && job.results && isComplete && (
        <div className="rounded bg-secondary/50 p-2 text-sm">
          <p className="font-semibold">Results:</p>
          <pre className="mt-1 overflow-auto text-xs">
            {JSON.stringify(job.results, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}