import { Link } from 'react-router-dom'
import { FolderOpen, Video, Globe, MoreVertical } from 'lucide-react'
import { Project } from '@/types/project'
import { cn } from '@/utils/cn'
import { formatDate } from '@/utils/format'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

interface ProjectCardProps {
  project: Project
  className?: string
}

export function ProjectCard({ project, className }: ProjectCardProps) {
  return (
    <div
      className={cn(
        'group rounded-lg border bg-card p-6 transition-all hover:shadow-md',
        className
      )}
    >
      <div className="flex items-start justify-between">
        <Link to={`/projects/${project.id}`} className="flex-1">
          <div className="flex items-center space-x-3">
            <div className="rounded-lg bg-primary/10 p-2 text-primary">
              <FolderOpen className="h-5 w-5" />
            </div>
            <div>
              <h3 className="font-semibold hover:text-primary">{project.name}</h3>
              {project.description && (
                <p className="line-clamp-2 text-sm text-muted-foreground">
                  {project.description}
                </p>
              )}
            </div>
          </div>
        </Link>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem asChild>
              <Link to={`/projects/${project.id}`}>View Project</Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <Link to={`/projects/${project.id}/settings`}>Settings</Link>
            </DropdownMenuItem>
            {project.status === 'active' && (
              <DropdownMenuItem className="text-yellow-600">
                Archive
              </DropdownMenuItem>
            )}
            {project.status === 'archived' && (
              <DropdownMenuItem className="text-green-600">
                Restore
              </DropdownMenuItem>
            )}
            <DropdownMenuItem className="text-destructive">
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <div className="mt-4 flex items-center space-x-4 text-sm text-muted-foreground">
        <div className="flex items-center space-x-1">
          <Globe className="h-4 w-4" />
          <span>{project.website_count || 0} websites</span>
        </div>
        <div className="flex items-center space-x-1">
          <Video className="h-4 w-4" />
          <span>{project.video_count || 0} videos</span>
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between border-t pt-4 text-xs text-muted-foreground">
        <span>Created {formatDate(project.created_at)}</span>
        <span className="capitalize">{project.status}</span>
      </div>
    </div>
  )
}