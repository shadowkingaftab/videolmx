import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Video, FolderOpen, TrendingUp } from 'lucide-react'
import { useProjects } from '@/hooks/use-projects'
import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { ProjectCard } from '@/components/project-card'
import { EmptyState } from '@/components/empty-state'

export function DashboardPage() {
  const { user } = useAuth()
  const { data: projects, isLoading, refetch } = useProjects()

  useEffect(() => {
    refetch()
  }, [])

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  const stats = [
    {
      label: 'Total Projects',
      value: projects?.length || 0,
      icon: FolderOpen,
    },
    {
      label: 'Total Videos',
      value: projects?.reduce((acc, p) => acc + (p.video_count || 0), 0) || 0,
      icon: Video,
    },
    {
      label: 'Plan',
      value: user?.plan || 'Free',
      icon: TrendingUp,
    },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back, {user?.full_name || 'User'}!
          </p>
        </div>
        <Button asChild>
          <Link to="/projects/new">
            <Plus className="mr-2 h-4 w-4" />
            New Project
          </Link>
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        {stats.map((stat) => (
          <div key={stat.label} className="rounded-lg border bg-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  {stat.label}
                </p>
                <p className="mt-2 text-3xl font-bold">{stat.value}</p>
              </div>
              <div className="rounded-lg bg-primary/10 p-3 text-primary">
                <stat.icon className="h-5 w-5" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Projects */}
      <div>
        <h2 className="mb-4 text-xl font-semibold">Your Projects</h2>
        {projects && projects.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {projects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        ) : (
          <EmptyState
            title="No projects yet"
            description="Create your first project to start generating videos from websites."
            action={
              <Button asChild>
                <Link to="/projects/new">Create Project</Link>
              </Button>
            }
          />
        )}
      </div>
    </div>
  )
}