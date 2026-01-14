<template>
  <div class="execution-detail">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="execution" class="execution-content">
      <!-- Header -->
      <header class="execution-header">
        <div>
          <h1>{{ execution.workflow_id }}</h1>
          <p class="execution-id">执行 ID: {{ execution.id }}</p>
        </div>
        <div class="header-actions">
          <div class="status-badge" :class="execution.status">
            {{ getStatusText(execution.status) }}
          </div>
          <button
            v-if="execution.status === 'running'"
            @click="cancelExecution"
            class="btn btn-danger"
          >
            取消执行
          </button>
          <button @click="goBack" class="btn btn-secondary">
            返回
          </button>
        </div>
      </header>

      <!-- Progress -->
      <section class="progress-section">
        <h2>执行进度</h2>
        <div class="progress-bar-large">
          <div class="progress-fill" :style="{ width: `${execution.progress}%` }"></div>
        </div>
        <div class="progress-info">
          <span class="progress-percentage">{{ execution.progress.toFixed(1) }}%</span>
          <span class="current-step">{{ execution.current_step }}</span>
        </div>
      </section>

      <!-- Output -->
      <section v-if="execution.status === 'completed' && execution.output" class="output-section">
        <h2>执行结果</h2>
        <div v-if="execution.output.final_report" class="report-content">
          <div v-html="renderMarkdown(execution.output.final_report)" class="markdown"></div>
        </div>
        <div v-else class="json-output">
          <pre>{{ JSON.stringify(execution.output, null, 2) }}</pre>
        </div>
      </section>

      <!-- Error -->
      <section v-if="execution.status === 'failed' && execution.error_message" class="error-section">
        <h2>错误信息</h2>
        <div class="error-message">
          {{ execution.error_message }}
        </div>
      </section>

      <!-- Details -->
      <section class="details-section">
        <h2>详细信息</h2>
        <div class="detail-grid">
          <div class="detail-item">
            <label>开始时间</label>
            <span>{{ formatDateTime(execution.started_at) }}</span>
          </div>
          <div class="detail-item">
            <label>完成时间</label>
            <span>{{ execution.completed_at ? formatDateTime(execution.completed_at) : '-' }}</span>
          </div>
          <div class="detail-item">
            <label>执行时长</label>
            <span>{{ execution.duration ? `${execution.duration.toFixed(2)}秒` : '-' }}</span>
          </div>
          <div class="detail-item">
            <label>重试次数</label>
            <span>{{ execution.retry_count }}</span>
          </div>
          <div class="detail-item">
            <label>线程 ID</label>
            <span>{{ execution.thread_id }}</span>
          </div>
        </div>
      </section>

      <!-- Input Params -->
      <section v-if="execution.input_params" class="params-section">
        <h2>输入参数</h2>
        <div class="params-content">
          <pre>{{ JSON.stringify(execution.input_params, null, 2) }}</pre>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useWorkflowStore } from '../stores/workflow'
import { wsClient } from '../api/websocket'

const route = useRoute()
const router = useRouter()
const workflowStore = useWorkflowStore()

const executionId = route.params.id as string
const execution = ref(workflowStore.currentExecution)
const loading = ref(false)
const error = ref<string | null>(null)

const { loading: storeLoading, error: storeError } = workflowStore

async function loadExecution() {
  loading.value = true
  error.value = null
  try {
    await workflowStore.fetchExecution(executionId)
    execution.value = workflowStore.currentExecution

    // Connect WebSocket for real-time updates if still running
    if (execution.value?.status === 'running') {
      wsClient.connect(executionId, (update) => {
        workflowStore.updateExecutionStatus(update)
      })
    }
  } catch (err: any) {
    error.value = 'Failed to load execution'
    console.error('Error loading execution:', err)
  } finally {
    loading.value = false
  }
}

async function cancelExecution() {
  try {
    await workflowStore.cancelExecution(executionId)
    await loadExecution()
  } catch (err: any) {
    error.value = 'Failed to cancel execution'
    console.error('Error cancelling execution:', err)
  }
}

function goBack() {
  router.push('/')
}

function getStatusText(status: string) {
  const statusMap: Record<string, string> = {
    idle: '等待中',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

function formatDateTime(timestamp: string) {
  return new Date(timestamp).toLocaleString('zh-CN')
}

function renderMarkdown(content: string) {
  // Simple markdown rendering - in production, use a library like marked
  return content
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*)\*/gim, '<em>$1</em>')
    .replace(/!\[(.*?)\]\((.*?)\)/gim, '<img src="$2" alt="$1" />')
    .replace(/\[(.*?)\]\((.*?)\)/gim, '<a href="$2" target="_blank">$1</a>')
    .replace(/\n$/gim, '<br />')
}

onMounted(() => {
  loadExecution()
  // Poll for updates every 2 seconds
  const pollInterval = setInterval(() => {
    if (execution.value?.status === 'running') {
      loadExecution()
    }
  }, 2000)

  onUnmounted(() => {
    clearInterval(pollInterval)
    wsClient.disconnect()
  })
})
</script>

<style scoped>
.execution-detail {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px;
}

.execution-header {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.execution-header h1 {
  margin: 0 0 8px 0;
  color: #1a1a1a;
}

.execution-id {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.status-badge.idle {
  background: #e0e0e0;
  color: #666;
}

.status-badge.running {
  background: #2196f3;
  color: white;
}

.status-badge.completed {
  background: #4caf50;
  color: white;
}

.status-badge.failed {
  background: #f44336;
  color: white;
}

.status-badge.cancelled {
  background: #9e9e9e;
  color: white;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background: #1976d2;
  color: white;
}

.btn-secondary {
  background: #e0e0e0;
  color: #1a1a1a;
}

.btn-danger {
  background: #f44336;
  color: white;
}

.progress-section,
.output-section,
.error-section,
.details-section,
.params-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.progress-section h2,
.output-section h2,
.error-section h2,
.details-section h2,
.params-section h2 {
  margin: 0 0 20px 0;
  color: #1a1a1a;
}

.progress-bar-large {
  width: 100%;
  height: 24px;
  background: #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 16px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #1976d2, #2196f3);
  transition: width 0.5s ease;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-percentage {
  font-size: 24px;
  font-weight: 700;
  color: #1976d2;
}

.current-step {
  color: #666;
  font-size: 14px;
}

.report-content {
  max-height: 600px;
  overflow-y: auto;
}

.markdown {
  line-height: 1.8;
  color: #333;
}

.markdown h1 {
  font-size: 2em;
  margin: 0.5em 0;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 0.3em;
}

.markdown h2 {
  font-size: 1.5em;
  margin: 0.5em 0;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 0.3em;
}

.markdown h3 {
  font-size: 1.2em;
  margin: 0.5em 0;
}

.markdown p {
  margin: 1em 0;
}

.markdown ul,
.markdown ol {
  margin: 1em 0;
  padding-left: 2em;
}

.markdown li {
  margin: 0.5em 0;
}

.markdown a {
  color: #1976d2;
  text-decoration: none;
}

.markdown a:hover {
  text-decoration: underline;
}

.json-output,
.params-content {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
}

.json-output pre,
.params-content pre {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: #333;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #f44336;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.detail-item span {
  font-size: 14px;
  color: #1a1a1a;
}

.loading,
.error {
  text-align: center;
  padding: 60px 20px;
  font-size: 18px;
}

.error {
  color: #f44336;
}
</style>
