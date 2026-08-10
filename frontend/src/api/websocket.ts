import { useEffect, useRef, useCallback } from 'react'

type WebSocketMessage = {
  type: string
  [key: string]: any
}

type MessageHandler = (message: WebSocketMessage) => void

export class WebSocketClient {
  private ws: WebSocket | null = null
  private url: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private handlers: Map<string, Set<MessageHandler>> = new Map()
  private pingInterval: NodeJS.Timeout | null = null

  constructor(url: string) {
    this.url = url
  }

  connect(token: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) return

    const wsUrl = new URL(this.url)
    wsUrl.searchParams.set('token', token)

    this.ws = new WebSocket(wsUrl.toString())
    this.ws.onopen = this.handleOpen.bind(this)
    this.ws.onmessage = this.handleMessage.bind(this)
    this.ws.onclose = this.handleClose.bind(this)
    this.ws.onerror = this.handleError.bind(this)
  }

  disconnect(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval)
      this.pingInterval = null
    }

    if (this.ws) {
      this.ws.close(1000, 'Normal closure')
      this.ws = null
    }
  }

  send(message: WebSocketMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected')
    }
  }

  subscribe(eventType: string, handler: MessageHandler): () => void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set())
    }
    this.handlers.get(eventType)!.add(handler)

    return () => {
      this.handlers.get(eventType)?.delete(handler)
    }
  }

  subscribeToJob(jobId: string): void {
    this.send({
      type: 'subscribe_job',
      job_id: jobId,
    })
  }

  unsubscribeFromJob(jobId: string): void {
    this.send({
      type: 'unsubscribe_job',
      job_id: jobId,
    })
  }

  private handleOpen(): void {
    console.log('WebSocket connected')
    this.reconnectAttempts = 0

    // Send ping every 30 seconds
    this.pingInterval = setInterval(() => {
      this.send({ type: 'ping', timestamp: Date.now() })
    }, 30000)
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message = JSON.parse(event.data)
      const { type } = message

      // Handle specific message types
      if (type === 'pong') {
        return
      }

      // Broadcast to handlers
      const handlers = this.handlers.get(type) || new Set()
      handlers.forEach((handler) => {
        try {
          handler(message)
        } catch (error) {
          console.error('Error in message handler:', error)
        }
      })

      // Also broadcast to wildcard handlers
      const wildcardHandlers = this.handlers.get('*') || new Set()
      wildcardHandlers.forEach((handler) => {
        try {
          handler(message)
        } catch (error) {
          console.error('Error in wildcard handler:', error)
        }
      })
    } catch (error) {
      console.error('Error parsing WebSocket message:', error)
    }
  }

  private handleClose(event: CloseEvent): void {
    console.log(`WebSocket closed: ${event.code} - ${event.reason}`)

    if (this.pingInterval) {
      clearInterval(this.pingInterval)
      this.pingInterval = null
    }

    // Attempt to reconnect if not closed intentionally
    if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1)
      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`)
      setTimeout(() => {
        const token = localStorage.getItem('access_token')
        if (token) {
          this.connect(token)
        }
      }, delay)
    }
  }

  private handleError(error: Event): void {
    console.error('WebSocket error:', error)
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  getReadyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED
  }
}

// Hook for using WebSocket in React components
export function useWebSocket(url: string) {
  const clientRef = useRef<WebSocketClient | null>(null)

  useEffect(() => {
    if (!clientRef.current) {
      clientRef.current = new WebSocketClient(url)
    }

    const token = localStorage.getItem('access_token')
    if (token && !clientRef.current.isConnected()) {
      clientRef.current.connect(token)
    }

    return () => {
      if (clientRef.current) {
        clientRef.current.disconnect()
      }
    }
  }, [url])

  const subscribe = useCallback((eventType: string, handler: MessageHandler) => {
    if (clientRef.current) {
      return clientRef.current.subscribe(eventType, handler)
    }
    return () => {}
  }, [])

  const subscribeToJob = useCallback((jobId: string) => {
    if (clientRef.current) {
      clientRef.current.subscribeToJob(jobId)
    }
  }, [])

  const unsubscribeFromJob = useCallback((jobId: string) => {
    if (clientRef.current) {
      clientRef.current.unsubscribeFromJob(jobId)
    }
  }, [])

  const send = useCallback((message: WebSocketMessage) => {
    if (clientRef.current) {
      clientRef.current.send(message)
    }
  }, [])

  const isConnected = useCallback(() => {
    return clientRef.current?.isConnected() ?? false
  }, [])

  return {
    subscribe,
    subscribeToJob,
    unsubscribeFromJob,
    send,
    isConnected,
  }
}