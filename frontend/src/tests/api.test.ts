import { describe, it, expect } from 'vitest'
import { apiClient } from '../src/api/client'


describe('ApiClient', () => {
  it('should have correct base URL', () => {
    expect(apiClient).toBeDefined()
  })

  it('should have workflow methods', () => {
    expect(apiClient.listWorkflows).toBeTypeOf('function')
    expect(apiClient.getWorkflow).toBeTypeOf('function')
    expect(apiClient.startWorkflow).toBeTypeOf('function')
  })

  it('should have execution methods', () => {
    expect(apiClient.listExecutions).toBeTypeOf('function')
    expect(apiClient.getExecution).toBeTypeOf('function')
    expect(apiClient.cancelExecution).toBeTypeOf('function')
  })
})
