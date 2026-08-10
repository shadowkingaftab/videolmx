// This file would typically contain image imports or URLs
// For now, we export placeholder paths that can be replaced with actual assets

export const Images = {
  logo: {
    light: '/logo-light.svg',
    dark: '/logo-dark.svg',
  },
  icon: '/icon.svg',
  favicon: '/favicon.ico',
  placeholder: '/placeholder.png',
  hero: {
    light: '/hero-light.svg',
    dark: '/hero-dark.svg',
  },
  empty: {
    projects: '/empty-projects.svg',
    videos: '/empty-videos.svg',
    websites: '/empty-websites.svg',
    search: '/empty-search.svg',
  },
  avatars: {
    default: '/avatar-default.svg',
    user: '/avatar-user.svg',
    team: '/avatar-team.svg',
  },
  illustrations: {
    dashboard: '/dashboard-illustration.svg',
    editor: '/editor-illustration.svg',
    analytics: '/analytics-illustration.svg',
    setup: '/setup-illustration.svg',
  },
  social: {
    github: '/social/github.svg',
    twitter: '/social/twitter.svg',
    linkedin: '/social/linkedin.svg',
    youtube: '/social/youtube.svg',
  },
}

// Helper to get image URL with fallback
export function getImageUrl(path: string): string {
  if (path.startsWith('http') || path.startsWith('/')) {
    return path
  }
  return `/${path}`
}

// Helper to get placeholder image
export function getPlaceholderImage(width: number, height: number, text?: string): string {
  return `https://via.placeholder.com/${width}x${height}?text=${text || 'Image'}`
}