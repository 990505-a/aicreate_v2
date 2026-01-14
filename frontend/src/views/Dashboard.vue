<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>AICreate 工作流平台</h1>
      <div class="status-badge" :class="{ running: runningWorkflows.length > 0 }">
        {{ runningWorkflows.length }} 运行中
      </div>
    </header>

    <div class="dashboard-content">
      <!-- Workflows Section -->
      <section class="workflows-section">
        <div class="section-header">
          <h2>可用工作流</h2>
          <button @click="refreshWorkflows" :disabled="loading" class="btn btn-secondary">
            {{ loading ? '刷新中...' : '刷新' }}
          </button>
        </div>

        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="error" class="error">{{ error }}</div>
        <div v-else class="workflow-list">
          <div
            v-for="workflow in workflows"
            :key="workflow.id"
            class="workflow-card"
            :class="{ active: workflow.is_active }"
          >
            <div class="workflow-info">
              <h3>{{ workflow.name }}</h3>
              <p>{{ workflow.description }}</p>
              <div class="workflow-meta">
                <span class="version">v{{ workflow.version }}</span>
                <span class="plugin">插件: {{ workflow.plugin_name }}</span>
              </div>
            </div>
            <button
              @click="startWorkflow(workflow.id)"
              :disabled="!workflow.is_active"
              class="btn btn-primary"
            >
              启动
            </button>
          </div>
        </div>
      </section>

      <!-- Executions Section -->
      <section class="executions-section">
        <div class="section-header">
          <h2>最近执行</h2>
          <div class="tabs">
            <button
              @click="filterExecutions(null)"
              :class="{ active: currentFilter === null }"
              class="tab"
            >
              全部
            </button>
            <button
              @click="filterExecutions('running')"
              :class="{ active: currentFilter === 'running' }"
              class="tab"
            >
              运行中
            </button>
            <button
              @click="filterExecutions('completed')"
              :class="{ active: currentFilter === 'completed' }"
              class="tab"
            >
              已完成
            </button>
            <button
              @click="filterExecutions('failed')"
              :class="{ active: currentFilter === 'failed' }"
              class="tab"
            >
              失败
            </button>
          </div>
        </div>

        <div class="execution-list">
          <div
            v-for="execution in filteredExecutions"
            :key="execution.id"
            class="execution-item"
            :class="execution.status"
            @click="viewExecution(execution.id)"
          >
            <div class="execution-status">
              <div class="status-indicator" :class="execution.status"></div>
            </div>
            <div class="execution-info">
              <h4>{{ execution.workflow_id }}</h4>
              <p>{{ execution.current_step }}</p>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: `${execution.progress}%` }"></div>
              </div>
              <span class="progress-text">{{ execution.progress.toFixed(1) }}%</span>
            </div>
            <div class="execution-actions">
              <span class="timestamp">{{ formatTime(execution.created_at) }}</span>
              <button
                v-if="execution.status === 'running'"
                @click.stop="cancelExecution(execution.id)"
                class="btn btn-danger btn-sm"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useWorkflowStore } from '../stores/workflow'
import { useRouter } from 'vue-router'

const router = useRouter()
const workflowStore = useWorkflowStore()

const currentFilter = ref<string | null>(null)

// Use storeToRefs to preserve reactivity
const { workflows, executions, loading, error, runningWorkflows } = storeToRefs(workflowStore)

const filteredExecutions = computed(() => {
  if (!currentFilter.value) {
    return executions.value.slice(0, 20)
  }
  return executions.value.filter(e => e.status === currentFilter.value).slice(0, 20)
})

async function refreshWorkflows() {
  await workflowStore.fetchWorkflows()
  await workflowStore.fetchExecutions()
}

async function startWorkflow(workflowId: string) {
  try {
    const executionId = await workflowStore.startWorkflow(workflowId)
    await workflowStore.fetchExecutions()
    router.push(`/executions/${executionId}`)
  } catch (error) {
    console.error('Failed to start workflow:', error)
  }
}

async function cancelExecution(executionId: string) {
  try {
    await workflowStore.cancelExecution(executionId)
    await workflowStore.fetchExecutions()
  } catch (error) {
    console.error('Failed to cancel execution:', error)
  }
}

function viewExecution(executionId: string) {
  router.push(`/executions/${executionId}`)
}

function filterExecutions(status: string | null) {
  currentFilter.value = status
}

function formatTime(timestamp: string) {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${Math.floor(diff / 86400000)}天前`
}

onMounted(() => {
  refreshWorkflows()
  // Auto-refresh executions every 5 seconds
  setInterval(() => {
    workflowStore.fetchExecutions()
  }, 5000)
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.dashboard-header h1 {
  margin: 0;
  color: #1a1a1a;
}

.status-badge {
  padding: 8px 16px;
  border-radius: 20px;
  background: #e0e0e0;
  color: #666;
}

.status-badge.running {
  background: #4caf50;
  color: white;
}

.dashboard-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

@media (max-width: 1024px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  color: #1a1a1a;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #1976d2;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1565c0;
}

.btn-secondary {
  background: #e0e0e0;
  color: #1a1a1a;
}

.btn-secondary:hover:not(:disabled) {
  background: #d0d0d0;
}

.btn-danger {
  background: #f44336;
  color: white;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 12px;
}

.tabs {
  display: flex;
  gap: 8px;
}

.tab {
  padding: 8px 16px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 6px;
  color: #666;
  transition: all 0.2s;
}

.tab:hover {
  background: #e0e0e0;
}

.tab.active {
  background: #1976d2;
  color: white;
}

.workflow-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.workflow-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.2s;
}

.workflow-card.active {
  border-left: 4px solid #4caf50;
}

.workflow-card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.workflow-info {
  flex: 1;
}

.workflow-info h3 {
  margin: 0 0 8px 0;
  color: #1a1a1a;
}

.workflow-info p {
  margin: 0 0 12px 0;
  color: #666;
  font-size: 14px;
}

.workflow-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #999;
}

.version {
  background: #e3f2fd;
  color: #1976d2;
  padding: 2px 8px;
  border-radius: 4px;
}

.plugin {
  background: #f5f5f5;
  padding: 2px 8px;
  border-radius: 4px;
}

.execution-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.execution-item {
  background: white;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.execution-item:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

.execution-item.running {
  border-left: 4px solid #2196f3;
}

.execution-item.completed {
  border-left: 4px solid #4caf50;
}

.execution-item.failed {
  border-left: 4px solid #f44336;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ccc;
}

.status-indicator.running {
  background: #2196f3;
  animation: pulse 1s infinite;
}

.status-indicator.completed {
  background: #4caf50;
}

.status-indicator.failed {
  background: #f44336;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.execution-info {
  flex: 1;
}

.execution-info h4 {
  margin: 0 0 4px 0;
  color: #1a1a1a;
  font-size: 14px;
}

.execution-info p {
  margin: 0 0 8px 0;
  color: #666;
  font-size: 12px;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: #e0e0e0;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 4px;
}

.progress-fill {
  height: 100%;
  background: #1976d2;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 11px;
  color: #999;
}

.execution-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.timestamp {
  font-size: 12px;
  color: #999;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error {
  color: #f44336;
}
</style>
