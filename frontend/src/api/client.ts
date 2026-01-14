import axios, { type AxiosInstance, type AxiosResponse } from 'axios'

export interface Workflow {
  id: string
  name: string
  description: string
  version: string
  plugin_name: string
  is_active: boolean
  plugin_version?: string
  created_at: string
  updated_at: string
}

export interface WorkflowExecution {
  id: string
  workflow_id: string
  status: string
  current_step: string
  progress: number
  started_at: string
  completed_at: string | null
  duration: number | null
  error_message: string | null
  created_at: string
}

export interface WorkflowExecutionDetail extends WorkflowExecution {
  thread_id: string
  input_params: Record<string, any> | null
  config: Record<string, any> | null
  output: Record<string, any> | null
  total_steps: number
  retry_count: number
  updated_at: string
}

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  // Workflows
  async listWorkflows(): Promise<Workflow[]> {
    const response: AxiosResponse<Workflow[]> = await this.client.get('/workflows/')
    return response.data
  }

  async getWorkflow(workflowId: string): Promise<any> {
    const response = await this.client.get(`/workflows/${workflowId}`)
    return response.data
  }

  async startWorkflow(workflowId: string, inputParams: Record<string, any> = {}): Promise<{ message: string; execution_id: string; workflow_id: string; status: string }> {
    const response = await this.client.post(`/workflows/${workflowId}/start`, {
      input_params: inputParams
    })
    return response.data
  }

  // Executions
  async listExecutions(filters: {
    workflow_id?: string
    status?: string
    limit?: number
    offset?: number
  } = {}): Promise<WorkflowExecution[]> {
    const response: AxiosResponse<WorkflowExecution[]> = await this.client.get('/executions/', { params: filters })
    return response.data
  }

  async getExecution(executionId: string): Promise<WorkflowExecutionDetail> {
    const response: AxiosResponse<WorkflowExecutionDetail> = await this.client.get(`/executions/${executionId}`)
    return response.data
  }

  async cancelExecution(executionId: string): Promise<{ message: string }> {
    const response = await this.client.post(`/executions/${executionId}/cancel`)
    return response.data
  }
}

export const apiClient = new ApiClient()
