import { createBrowserRouter } from 'react-router-dom'
import { RootLayout } from './layouts/root-layout'
import { DashboardLayout } from './layouts/dashboard-layout'
import { AuthLayout } from './layouts/auth-layout'
import { AuthGuard } from './app/auth-guard'

// Pages
import { HomePage } from './pages/home'
import { LoginPage } from './pages/login'
import { SignupPage } from './pages/signup'
import { DashboardPage } from './pages/dashboard'
import { ProjectPage } from './pages/project'
import { WebsitePage } from './pages/website'
import { JobPage } from './pages/job'
import { EditorPage } from './pages/editor'
import { VideoPage } from './pages/video'
import { BillingPage } from './pages/billing'
import { SettingsPage } from './pages/settings'
import { AdminPage } from './pages/admin'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <HomePage /> },
      {
        element: <AuthLayout />,
        children: [
          { path: 'login', element: <LoginPage /> },
          { path: 'signup', element: <SignupPage /> },
        ],
      },
      {
        element: <AuthGuard />,
        children: [
          {
            element: <DashboardLayout />,
            children: [
              { path: 'dashboard', element: <DashboardPage /> },
              { path: 'projects/:projectId', element: <ProjectPage /> },
              { path: 'websites/:websiteId', element: <WebsitePage /> },
              { path: 'jobs/:jobId', element: <JobPage /> },
              { path: 'editor/:videoId', element: <EditorPage /> },
              { path: 'videos/:videoId', element: <VideoPage /> },
              { path: 'billing', element: <BillingPage /> },
              { path: 'settings', element: <SettingsPage /> },
              { path: 'admin', element: <AdminPage /> },
            ],
          },
        ],
      },
    ],
  },
])