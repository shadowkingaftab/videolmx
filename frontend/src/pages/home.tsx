import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, Sparkles, Video, Globe, Zap } from 'lucide-react'
import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'

export function HomePage() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-secondary/20">
      <div className="container mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <div className="inline-flex items-center rounded-full border px-4 py-1.5 text-sm font-medium text-primary">
            <Sparkles className="mr-1 h-4 w-4" />
            AI-Powered Video Generation
          </div>

          <h1 className="mt-8 text-5xl font-bold tracking-tight sm:text-6xl md:text-7xl">
            Transform Any Website into a{' '}
            <span className="bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
              Professional Video
            </span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
            Paste a URL and get a narrated, animated explainer video in minutes.
            No editing skills required.
          </p>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            {user ? (
              <Button asChild size="lg">
                <Link to="/dashboard">
                  Go to Dashboard
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            ) : (
              <>
                <Button asChild size="lg">
                  <Link to="/signup">
                    Get Started Free
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild variant="outline" size="lg">
                  <Link to="/login">Sign In</Link>
                </Button>
              </>
            )}
          </div>
        </motion.div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-24 grid gap-8 md:grid-cols-3"
        >
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
              className="rounded-lg border bg-card p-6 text-card-foreground shadow-sm"
            >
              <div className="mb-4 inline-flex rounded-lg bg-primary/10 p-3 text-primary">
                <feature.icon className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold">{feature.title}</h3>
              <p className="mt-2 text-muted-foreground">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mt-24 border-t pt-16"
        >
          <div className="grid gap-8 md:grid-cols-4">
            <div className="text-center">
              <div className="text-3xl font-bold">10k+</div>
              <div className="text-sm text-muted-foreground">Videos Generated</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">5k+</div>
              <div className="text-sm text-muted-foreground">Websites Analyzed</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">99%</div>
              <div className="text-sm text-muted-foreground">Satisfaction Rate</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">50+</div>
              <div className="text-sm text-muted-foreground">Countries Served</div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

const features = [
  {
    icon: Globe,
    title: 'Website Understanding',
    description:
      'Our AI crawls and understands your website\'s structure, content, and purpose automatically.',
  },
  {
    icon: Video,
    title: 'Professional Videos',
    description:
      'Generate high-quality explainer videos with AI narration, animations, and transitions.',
  },
  {
    icon: Zap,
    title: 'Fast & Scalable',
    description:
      'Get your video in minutes. Scale to thousands of websites with our production-grade platform.',
  },
]