<!-- 性能监控 -->
<template>
  <div v-if="visible" class="performance-dashboard">
    <div class="dashboard-header">
      <h4>性能监控</h4>
      <button @click="visible = false">×</button>
    </div>
    
    <div class="metrics">
      <div class="metric" v-for="metric in recentMetrics" :key="metric.timestamp">
        <span class="metric-name">{{ metric.name }}</span>
        <span class="metric-value">{{ metric.value }}ms</span>
      </div>
    </div>
    
    <button @click="exportReport" class="export-btn">导出报告</button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { performanceMonitor } from '@/utils/performance'

const visible = ref(false)
const metrics = ref([])

const recentMetrics = computed(() => {
  return metrics.value.slice(-10).reverse()
})

const updateMetrics = () => {
  metrics.value = performanceMonitor.getMetrics()
}

const exportReport = () => {
  const report = performanceMonitor.exportReport()
  const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `perf-report-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
}

// 快捷键 Ctrl+Shift+P 打开性能面板
const handleKeydown = (e) => {
  if (e.ctrlKey && e.shiftKey && e.key === 'P') {
    visible.value = !visible.value
    if (visible.value) updateMetrics()
  }
}

// 定时更新
let interval
onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  interval = setInterval(() => {
    if (visible.value) updateMetrics()
  }, 5000)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  clearInterval(interval)
})
</script>

<style scoped>
.performance-dashboard {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 300px;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: var(--card-shadow);
  z-index: 1000;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid var(--border-color);
}

.dashboard-header button {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: var(--text-secondary);
}

.metrics {
  max-height: 300px;
  overflow-y: auto;
  padding: 10px;
}

.metric {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid var(--border-color);
  font-size: 12px;
}

.metric-name {
  color: var(--text-secondary);
}

.metric-value {
  font-family: monospace;
  color: var(--success-color);
}

.export-btn {
  width: 100%;
  padding: 8px;
  background-color: var(--success-color);
  color: white;
  border: none;
  cursor: pointer;
}
</style>