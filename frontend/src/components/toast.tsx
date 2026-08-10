import toast from 'react-hot-toast'
import { CheckCircle, XCircle, AlertCircle, Info } from 'lucide-react'

export function showToast(
  message: string,
  type: 'success' | 'error' | 'warning' | 'info' = 'info'
) {
  const icons = {
    success: CheckCircle,
    error: XCircle,
    warning: AlertCircle,
    info: Info,
  }

  const Icon = icons[type]

  toast.custom(
    (t) => (
      <div
        className={`${
          t.visible ? 'animate-enter' : 'animate-leave'
        } pointer-events-auto flex w-full max-w-md rounded-lg bg-background shadow-lg ring-1 ring-black ring-opacity-5`}
      >
        <div className="flex w-0 flex-1 items-center p-4">
          <Icon
            className={`h-5 w-5 ${
              type === 'success'
                ? 'text-green-500'
                : type === 'error'
                ? 'text-red-500'
                : type === 'warning'
                ? 'text-yellow-500'
                : 'text-blue-500'
            }`}
          />
          <div className="ml-3 flex-1">
            <p className="text-sm font-medium text-foreground">{message}</p>
          </div>
        </div>
        <div className="flex border-l border-border">
          <button
            onClick={() => toast.dismiss(t.id)}
            className="flex w-full items-center justify-center rounded-none rounded-r-lg border border-transparent p-4 text-sm font-medium text-muted-foreground hover:text-foreground focus:outline-none"
          >
            Dismiss
          </button>
        </div>
      </div>
    ),
    { duration: 4000 }
  )
}

export const toastSuccess = (message: string) => showToast(message, 'success')
export const toastError = (message: string) => showToast(message, 'error')
export const toastWarning = (message: string) => showToast(message, 'warning')
export const toastInfo = (message: string) => showToast(message, 'info')