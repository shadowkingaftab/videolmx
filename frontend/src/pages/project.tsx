import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Plus, Video, Globe, Settings, Trash2 } from 'lucide-react'
import { useProject, useDeleteProject } from '@/hooks/use-projects'
import { useWebsites } from '@/hooks/use-website'
import { Button } from '@/components/ui/button'
import { WebsiteCard } from '@/components/website-card'
import { EmptyState } from '@/components/empty-state'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { toast } from 'react-hot-toast'

export function ProjectPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

  const { data: project, isLoading: projectLoading } = useProject(projectId!)
  const { data: websites, isLoading: websitesLoading } = useWebsites(projectId!)
  const deleteProject = useDeleteProject()

  const handleDelete = async () => {
    try {
      await deleteProject.mutateAsync(projectId!)
      toast.success('Project deleted successfully')
      navigate('/dashboard')
    } catch (err) {
      toast.error('Failed to delete project')
    }
  }

  if (projectLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  if (!project) {
    return (
      <div className="text-center">
        <h2 className="text-2xl font-bold">Project not found</h2>
        <Button asChild className="mt-4">
          <Link to="/dashboard">Go back</Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button asChild variant="ghost" size="sm">
            <Link to="/dashboard">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{project.name}</h1>
            {project.description && (
              <p className="text-muted-foreground">{project.description}</p>
            )}
          </div>
        </div>
        <div className="flex space-x-2">
          <Button asChild variant="outline">
            <Link to={`/projects/${projectId}/settings`}>
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </Link>
          </Button>
          <Button
            variant="destructive"
            onClick={() => setShowDeleteDialog(true)}
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Delete
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border bg-card p-4">
          <p className="text-sm text-muted-foreground">Websites</p>
          <p className="text-2xl font-bold">{websites?.length || 0}</p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <p className="text-sm text-muted-foreground">Videos</p>
          <p className="text-2xl font-bold">{project.video_count || 0}</p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <p className="text-sm text-muted-foreground">Status</p>
          <p className="text-2xl font-bold capitalize">{project.status}</p>
        </div>
      </div>

      {/* Websites */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold">Websites</h2>
          <Button asChild size="sm">
            <Link to={`/projects/${projectId}/websites/new`}>
              <Plus className="mr-2 h-4 w-4" />
              Add Website
            </Link>
          </Button>
        </div>

        {websites && websites.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {websites.map((website) => (
              <WebsiteCard key={website.id} website={website} />
            ))}
          </div>
        ) : (
          <EmptyState
            title="No websites added"
            description="Add a website to start generating videos"
            action={
              <Button asChild>
                <Link to={`/projects/${projectId}/websites/new`}>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Website
                </Link>
              </Button>
            }
          />
        )}
      </div>

      {/* Delete Confirmation */}
      <ConfirmDialog
        open={showDeleteDialog}
        onOpenChange={setShowDeleteDialog}
        title="Delete Project"
        description="Are you sure you want to delete this project? This action cannot be undone."
        confirmLabel="Delete"
        onConfirm={handleDelete}
        variant="destructive"
      />
    </div>
  )
}