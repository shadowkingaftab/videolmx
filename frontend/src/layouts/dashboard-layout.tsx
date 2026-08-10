import { Outlet } from 'react-router-dom'
import { Sidebar } from '@/components/sidebar'

export function DashboardLayout() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 overflow-hidden">
        <main className="h-full overflow-y-auto p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}