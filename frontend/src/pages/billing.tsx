import { useState } from 'react'
import { useAuth } from '@/hooks/use-auth'
import { useBilling } from '@/hooks/use-billing'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Check, Zap, Crown, Building2, Loader2 } from 'lucide-react'

const plans = [
  {
    id: 'free',
    name: 'Free',
    icon: Zap,
    price: '$0',
    description: 'Perfect for trying out the platform',
    features: ['1 video per month', '1 minute max duration', '100MB storage'],
  },
  {
    id: 'pro',
    name: 'Pro',
    icon: Crown,
    price: '$49',
    description: 'For professionals and small teams',
    features: ['10 videos per month', '5 minute max duration', '5GB storage'],
  },
  {
    id: 'business',
    name: 'Business',
    icon: Building2,
    price: '$199',
    description: 'For growing businesses',
    features: ['50 videos per month', '10 minute max duration', '50GB storage'],
  },
]

export function BillingPage() {
  const { user } = useAuth()
  const { data: subscription, isLoading } = useBilling()
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null)

  const currentPlan = subscription?.plan || 'free'

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Billing</h1>
        <p className="text-muted-foreground">
          Manage your subscription and billing details
        </p>
      </div>

      {/* Current Plan */}
      <div className="rounded-lg border bg-card p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Current Plan</h2>
            <p className="text-3xl font-bold capitalize">{currentPlan}</p>
          </div>
          <Badge variant={subscription?.status === 'active' ? 'default' : 'secondary'}>
            {subscription?.status || 'Active'}
          </Badge>
        </div>
        {subscription?.current_period_end && (
          <p className="mt-2 text-sm text-muted-foreground">
            Renews on{' '}
            {new Date(subscription.current_period_end).toLocaleDateString()}
          </p>
        )}
      </div>

      {/* Plans */}
      <div>
        <h2 className="mb-4 text-xl font-semibold">Available Plans</h2>
        <div className="grid gap-4 md:grid-cols-3">
          {plans.map((plan) => {
            const isCurrent = plan.id === currentPlan
            const Icon = plan.icon

            return (
              <div
                key={plan.id}
                className={`rounded-lg border p-6 ${
                  isCurrent ? 'border-primary bg-primary/5' : 'bg-card'
                }`}
              >
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold">{plan.name}</h3>
                    <p className="text-3xl font-bold">{plan.price}</p>
                    <p className="text-sm text-muted-foreground">
                      per month
                    </p>
                  </div>
                  <Icon className="h-8 w-8 text-primary" />
                </div>

                <p className="mb-4 text-sm text-muted-foreground">
                  {plan.description}
                </p>

                <ul className="mb-6 space-y-2">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center text-sm">
                      <Check className="mr-2 h-4 w-4 text-primary" />
                      {feature}
                    </li>
                  ))}
                </ul>

                <Button
                  className="w-full"
                  variant={isCurrent ? 'outline' : 'default'}
                  disabled={isCurrent || isLoading}
                  onClick={() => setSelectedPlan(plan.id)}
                >
                  {isCurrent ? 'Current Plan' : 'Upgrade'}
                </Button>
              </div>
            )
          })}
        </div>
      </div>

      {/* Payment Methods */}
      <div className="rounded-lg border bg-card p-6">
        <h2 className="mb-4 text-xl font-semibold">Payment Methods</h2>
        {subscription?.payment_methods?.length > 0 ? (
          <div className="space-y-2">
            {subscription.payment_methods.map((method) => (
              <div
                key={method.id}
                className="flex items-center justify-between rounded border p-3"
              >
                <div>
                  <p className="font-medium">
                    {method.brand} •••• {method.last4}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Expires {method.exp_month}/{method.exp_year}
                  </p>
                </div>
                {method.is_default && (
                  <Badge variant="outline">Default</Badge>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground">No payment methods on file</p>
        )}
        <Button className="mt-4" variant="outline">
          Add Payment Method
        </Button>
      </div>

      {/* Invoices */}
      <div className="rounded-lg border bg-card p-6">
        <h2 className="mb-4 text-xl font-semibold">Invoice History</h2>
        {subscription?.invoices?.length > 0 ? (
          <div className="space-y-2">
            {subscription.invoices.map((invoice) => (
              <div
                key={invoice.id}
                className="flex items-center justify-between rounded border p-3"
              >
                <div>
                  <p className="font-medium">Invoice #{invoice.invoice_number}</p>
                  <p className="text-sm text-muted-foreground">
                    {new Date(invoice.invoice_date).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="font-medium">
                    ${invoice.amount} {invoice.currency}
                  </span>
                  <Badge variant={invoice.status === 'paid' ? 'default' : 'secondary'}>
                    {invoice.status}
                  </Badge>
                  {invoice.pdf_url && (
                    <Button asChild variant="ghost" size="sm">
                      <a href={invoice.pdf_url} target="_blank" rel="noopener noreferrer">
                        PDF
                      </a>
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground">No invoices found</p>
        )}
      </div>
    </div>
  )
}