import { useEffect, useRef, useCallback } from 'react'
import { useWebSocket as useWebSocketClient } from '@/api/websocket'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'

export function useWebSocket() {
  const client = useWebSocketClient(WS_URL)

  return {
    subscribe: client.subscribe,
    subscribeToJob: client.subscribeToJob,
    unsubscribeFromJob: client.unsubscribeFromJob,
    send: client.send,
    isConnected: client.isConnected,
  }
}

export function useJobWebSocket(jobId: string | null) {
  const { subscribeToJob, unsubscribeFromJob, subscribe } = useWebSocket()
  const handlersRef = useRef<Map<string, (data: any) => void>>(new Map())

  useEffect(() => {
    if (jobId) {
      subscribeToJob(jobId)
      return () => {
        unsubscribeFromJob(jobId)
      }
    }
  }, [jobId])

  const onJobProgress = useCallback((handler: (data: any) => void) => {
    const unsub = subscribe('job_progress', (message) => {
      if (message.job_id === jobId) {
        handler(message)
      }
    })
    return unsub
  }, [jobId, subscribe])

  const onJobCompleted = useCallback((handler: (data: any) => void) => {
    const unsub = subscribe('job_completed', (message) => {
      if (message.job_id === jobId) {
        handler(message)
      }
    })
    return unsub
  }, [jobId, subscribe])

  const onJobFailed = useCallback((handler: (data: any) => void) => {
    const unsub = subscribe('job_failed', (message) => {
      if (message.job_id === jobId) {
        handler(message)
      }
    })
    return unsub
  }, [jobId, subscribe])

  return {
    onJobProgress,
    onJobCompleted,
    onJobFailed,
  }
}