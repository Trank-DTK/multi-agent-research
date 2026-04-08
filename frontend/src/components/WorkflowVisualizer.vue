<template>
  <div class="workflow-visualizer">
    <h3>工作流执行状态</h3>
    
    <div class="workflow-steps">
      <div 
        v-for="(step, index) in steps" 
        :key="step.id"
        :class="['step', step.status]"
      >
        <div class="step-indicator">
          <div class="step-number">{{ index + 1 }}</div>
          <div v-if="index < steps.length - 1" class="step-line"></div>
        </div>
        <div class="step-content">
          <div class="step-title">{{ step.name }}</div>
          <div class="step-description">{{ step.description }}</div>
          <div v-if="step.status === 'running'" class="step-loader"></div>
          <div v-if="step.status === 'completed'" class="step-check">✓</div>
          <div v-if="step.status === 'failed'" class="step-error">✗</div>
          <div v-if="step.duration" class="step-duration">{{ step.duration }}ms</div>
        </div>
      </div>
    </div>
    
    <!-- DAG可视化 -->
    <div v-if="showDAG" class="dag-view">
      <h4>依赖关系图</h4>
      <div class="dag-graph" ref="dagContainer"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const props = defineProps({
  steps: {
    type: Array,
    default: () => []
  },
  showDAG: {
    type: Boolean,
    default: false
  },
  dagData: {
    type: Object,
    default: () => ({})
  }
})

const dagContainer = ref(null)

// 简单的DAG可视化（使用Canvas）
const drawDAG = () => {
  if (!dagContainer.value || !props.dagData.nodes) return
  
  const canvas = document.createElement('canvas')
  canvas.width = 600
  canvas.height = 400
  const ctx = canvas.getContext('2d')
  
  ctx.fillStyle = '#f9f9f9'
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  
  // 绘制节点
  const nodes = props.dagData.nodes || []
  const positions = {}
  
  nodes.forEach((node, idx) => {
    const x = 100 + (idx % 3) * 150
    const y = 50 + Math.floor(idx / 3) * 80
    positions[node.id] = { x, y }
    
    ctx.fillStyle = node.status === 'completed' ? '#42b983' : 
                    node.status === 'running' ? '#ff9800' : 
                    node.status === 'failed' ? '#f44336' : '#e0e0e0'
    ctx.beginPath()
    ctx.arc(x, y, 25, 0, 2 * Math.PI)
    ctx.fill()
    ctx.fillStyle = '#333'
    ctx.font = '12px Arial'
    ctx.fillText(node.name, x - 20, y + 5)
  })
  
  // 绘制连线
  nodes.forEach(node => {
    node.depends_on?.forEach(depId => {
      const from = positions[depId]
      const to = positions[node.id]
      if (from && to) {
        ctx.beginPath()
        ctx.moveTo(from.x + 20, from.y)
        ctx.lineTo(to.x - 25, to.y)
        ctx.strokeStyle = '#999'
        ctx.stroke()
      }
    })
  })
  
  dagContainer.value.innerHTML = ''
  dagContainer.value.appendChild(canvas)
}

watch(() => props.dagData, () => {
  if (props.showDAG) drawDAG()
}, { deep: true })

onMounted(() => {
  if (props.showDAG) drawDAG()
})
</script>

<style scoped>
.workflow-visualizer {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #e0e0e0;
}

h3, h4 {
  margin-bottom: 20px;
  color: #333;
}

.workflow-steps {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
}

.step {
  flex: 1;
  display: flex;
  min-width: 150px;
  position: relative;
}

.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 15px;
  position: relative;
}

.step-number {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  z-index: 1;
}

.step.completed .step-number {
  background-color: #42b983;
  color: white;
}

.step.running .step-number {
  background-color: #ff9800;
  color: white;
  animation: pulse 1s infinite;
}

.step.failed .step-number {
  background-color: #f44336;
  color: white;
}

.step-line {
  position: absolute;
  top: 30px;
  width: 2px;
  height: 40px;
  background-color: #e0e0e0;
}

.step-content {
  flex: 1;
  padding-bottom: 20px;
}

.step-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.step-description {
  font-size: 12px;
  color: #666;
}

.step-loader {
  width: 20px;
  height: 20px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #ff9800;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-top: 8px;
}

.step-check, .step-error {
  margin-top: 8px;
  font-size: 16px;
}

.step-check {
  color: #42b983;
}

.step-error {
  color: #f44336;
}

.step-duration {
  font-size: 10px;
  color: #999;
  margin-top: 4px;
}

.dag-view {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.dag-graph {
  min-height: 300px;
  background-color: #f9f9f9;
  border-radius: 8px;
  overflow: auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.7; }
  100% { transform: scale(1); opacity: 1; }
}
</style>