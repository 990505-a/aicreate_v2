export interface WorkflowUpdate {
  type: string
  execution_id: string
  status: string
  current_step: string
  progress: number
  error_message: string | null
}

export class WebSocketClient {
  private ws: WebSocket | null = null
  private url: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

  constructor() {
    this.url = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws'
  }

  connect(executionId: string, onMessage: (update: WorkflowUpdate) => void): void {
    const wsUrl = `${this.url}/executions/${executionId}/updates`

    this.ws = new WebSocket(wsUrl)

    this.ws.onopen = () => {
      console.log(`WebSocket connected for execution ${executionId}`)
      this.reconnectAttempts = 0
    }

    this.ws.onmessage = (event) => {
      try {
        const update: WorkflowUpdate = JSON.parse(event.data)
        onMessage(update)
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    this.ws.onclose = () => {
      console.log(`WebSocket disconnected for execution ${executionId}`)
      this.attemptReconnect(executionId, onMessage)
    }
  }

  private attemptReconnect(executionId: string, onMessage: (update: WorkflowUpdate) => void): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

      setTimeout(() => {
        this.connect(executionId, onMessage)
      }, this.reconnectDelay * this.reconnectAttempts)
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

export const wsClient = new WebSocketClient()
