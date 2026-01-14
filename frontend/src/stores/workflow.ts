import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient, type Workflow, type WorkflowExecution, type WorkflowExecutionDetail } from '../api/client'

export const useWorkflowStore = defineStore('workflow', () => {
  // State
  const workflows = ref<Workflow[]>([])
  const executions = ref<WorkflowExecution[]>([])
  const currentExecution = ref<WorkflowExecutionDetail | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const runningWorkflows = computed(() =>
    executions.value.filter(e => e.status === 'running')
  )

  const completedWorkflows = computed(() =>
    executions.value.filter(e => e.status === 'completed')
  )

  const failedWorkflows = computed(() =>
    executions.value.filter(e => e.status === 'failed')
  )

  // Actions
  async function fetchWorkflows() {
    loading.value = true
    error.value = null
    try {
      workflows.value = await apiClient.listWorkflows()
    } catch (err: any) {
      error.value = 'Failed to fetch workflows'
      console.error('Error fetching workflows:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchExecutions(filters: Record<string, any> = {}) {
    loading.value = true
    error.value = null
    try {
      executions.value = await apiClient.listExecutions(filters)
    } catch (err: any) {
      error.value = 'Failed to fetch executions'
      console.error('Error fetching executions:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchExecution(executionId: string) {
    loading.value = true
    error.value = null
    try {
      currentExecution.value = await apiClient.getExecution(executionId)
    } catch (err: any) {
      error.value = 'Failed to fetch execution details'
      console.error('Error fetching execution:', err)
    } finally {
      loading.value = false
    }
  }

  async function startWorkflow(workflowId: string, params: Record<string, any> = {}) {
    loading.value = true
    error.value = null
    try {
      const result = await apiClient.startWorkflow(workflowId, params)
      return result.execution_id
    } catch (err: any) {
      error.value = 'Failed to start workflow'
      console.error('Error starting workflow:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function cancelExecution(executionId: string) {
    loading.value = true
    error.value = null
    try {
      await apiClient.cancelExecution(executionId)
      await fetchExecution(executionId)
    } catch (err: any) {
      error.value = 'Failed to cancel execution'
      console.error('Error cancelling execution:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  function updateExecutionStatus(update: {
    execution_id: string
    status: string
    current_step: string
    progress: number
    error_message: string | null
  }) {
    // Update in executions list
    const idx = executions.value.findIndex(e => e.id === update.execution_id)
    if (idx !== -1) {
      executions.value[idx] = {
        ...executions.value[idx],
        status: update.status,
        current_step: update.current_step,
        progress: update.progress,
        error_message: update.error_message,
      }
    }

    // Update current execution if it matches
    if (currentExecution.value?.id === update.execution_id) {
      currentExecution.value = {
        ...currentExecution.value,
        status: update.status as any,
        current_step: update.current_step,
        progress: update.progress,
        error_message: update.error_message,
      }
    }
  }

  function resetError() {
    error.value = null
  }

  return {
    // State
    workflows,
    executions,
    currentExecution,
    loading,
    error,

    // Computed
    runningWorkflows,
    completedWorkflows,
    failedWorkflows,

    // Actions
    fetchWorkflows,
    fetchExecutions,
    fetchExecution,
    startWorkflow,
    cancelExecution,
    updateExecutionStatus,
    resetError,
  }
})
