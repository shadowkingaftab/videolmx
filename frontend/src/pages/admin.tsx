import { useState } from 'react'
import { useAdmin } from '@/hooks/use-admin'
import { Button } from '@/components/ui/button'
import { StatusBadge } from '@/components/status-badge'
import { formatDate } from '@/utils/format'

export function AdminPage() {
  const { data: stats, isLoading } = useAdmin()
  const [activeTab, setActiveTab] = useState('overview')

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Admin Panel</h1>
        <p className="text-muted-foreground">
          System administration and monitoring
        </p>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-4">
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm text-muted-foreground">Total Users</p>
            <p className="text-2xl font-bold">{stats.total_users}</p>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm text-muted-foreground">Active Users</p>
            <p className="text-2xl font-bold">{stats.active_users}</p>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm text-muted-foreground">Total Videos</p>
            <p className="text-2xl font-bold">{stats.total_videos}</p>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm text-muted-foreground">Storage Used</p>
            <p className="text-2xl font-bold">{stats.storage_used_gb}GB</p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b">
        <nav className="flex space-x-4">
          {['overview', 'users', 'jobs', 'system'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`border-b-2 px-4 py-2 text-sm font-medium ${
                activeTab === tab
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="rounded-lg border bg-card p-6">
        {activeTab === 'overview' && (
          <div>
            <h3 className="mb-4 text-lg font-semibold">System Health</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span>Database</span>
                <StatusBadge status="healthy" />
              </div>
              <div className="flex items-center justify-between">
                <span>Cache</span>
                <StatusBadge status="healthy" />
              </div>
              <div className="flex items-center justify-between">
                <span>Storage</span>
                <StatusBadge status="healthy" />
              </div>
              <div className="flex items-center justify-between">
                <span>AI Services</span>
                <StatusBadge status="healthy" />
              </div>
              <div className="flex items-center justify-between">
                <span>Workers</span>
                <StatusBadge status="healthy" />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div>
            <h3 className="mb-4 text-lg font-semibold">Recent Users</h3>
            <p className="text-muted-foreground">User management coming soon</p>
          </div>
        )}

        {activeTab === 'jobs' && (
          <div>
            <h3 className="mb-4 text-lg font-semibold">Active Jobs</h3>
            <p className="text-muted-foreground">Job monitoring coming soon</p>
          </div>
        )}

        {activeTab === 'system' && (
          <div>
            <h3 className="mb-4 text-lg font-semibold">System Settings</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Maintenance Mode</span>
                <Button variant="outline" size="sm">
                  Disable
                </Button>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Allow Registration</span>
                <Button variant="outline" size="sm">
                  Enable
                </Button>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Max File Size</span>
                <span className="text-sm">100 MB</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">AI Provider</span>
                <span className="text-sm">OpenAI</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}