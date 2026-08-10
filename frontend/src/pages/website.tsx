import { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Play, RefreshCw, Trash2, ExternalLink } from 'lucide-react'
import { useWebsite, useAnalyzeWebsite, useDeleteWebsite } from '@/hooks/use-website'
import { useJobs } from '@/hooks/use-jobs'
import { Button } from '@/components/ui/button'
import { JobStatus } from '@/components/job-status'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { toast } from 'react-hot-toast'

export function WebsitePage() {
  const { websiteId } = useParams<{ websiteId: string }>()
  const navigate = useNavigate()
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

  const { data: website, isLoading } = useWebsite(websiteId!)
  const { data: jobs } = useJobs(websiteId)
  const analyzeWebsite = useAnalyzeWebsite()
  const deleteWebsite = useDeleteWebsite()

  const handleAnalyze = async () => {
    try {
      await analyzeWebsite.mutateAsync({ websiteId: websiteId!, maxPages: 50 })
      toast.success('Analysis started')
    } catch (err) {
      toast.error('Failed to start analysis')
    }
  }

  const handleDelete = async () => {
    try {
      await deleteWebsite.mutateAsync(websiteId!)
      toast.success('Website deleted')
      navigate(`/projects/${website?.project_id}`)
    } catch (err) {
      toast.error('Failed to delete website')
    }
  }

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  if (!website) {
    return (
      <div className="text-center">
        <h2 className="text-2xl font-bold">Website not found</h2>
        <Button asChild className="mt-4">
          <Link to="/dashboard">Go back</Link>
        </Button>
      </div>
    )
  }

  const latestJob = jobs?.[0]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button asChild variant="ghost" size="sm">
            <Link to={`/projects/${website.project_id}`}>
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{website.title || website.url}</h1>
            <a
              href={website.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center text-sm text-muted-foreground hover:text-foreground"
            >
              {website.url}
              <ExternalLink className="ml-1 h-3 w-3" />
            </a>
          </div>
        </div>
        <div className="flex space-x-2">
          <Button onClick={handleAnalyze} disabled={analyzeWebsite.isPending}>
            <Play className="mr-2 h-4 w-4" />
            {analyzeWebsite.isPending ? 'Analyzing...' : 'Analyze'}
          </Button>
          <Button variant="destructive" onClick={() => setShowDeleteDialog(true)}>
            <Trash2 className="mr-2 h-4 w-4" />
            Delete
          </Button>
        </div>
      </div>

      {/* Status */}
      <div className="rounded-lg border bg-card p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Status</p>
            <p className="text-lg font-semibold capitalize">{website.status}</p>
          </div>
          {website.crawled_at && (
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Last Crawled</p>
              <p className="text-sm">
                {new Date(website.crawled_at).toLocaleDateString()}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Latest Job */}
      {latestJob && (
        <div className="rounded-lg border bg-card p-4">
          <h3 className="mb-2 text-sm font-medium text-muted-foreground">
            Latest Analysis
          </h3>
          <JobStatus job={latestJob} />
        </div>
      )}

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2">
        <Button asChild variant="outline" className="h-24 flex-col space-y-2">
          <Link to={`/editor/new?website=${websiteId}`}>
            <Video className="h-6 w-6" />
            <span>Generate Video</span>
          </Link>
        </Button>
        <Button
          variant="outline"
          className="h-24 flex-col space-y-2"
          onClick={handleAnalyze}
          disabled={analyzeWebsite.isPending}
        >
          <RefreshCw className="h-6 w-6" />
          <span>Re-analyze</span>
        </Button>
      </div>

      {/* Delete Confirmation */}
      <ConfirmDialog
        open={showDeleteDialog}
        onOpenChange={setShowDeleteDialog}
        title="Delete Website"
        description="Are you sure you want to delete this website? This will also remove all associated data."
        confirmLabel="Delete"
        onConfirm={handleDelete}
        variant="destructive"
      />
    </div>
  )
}