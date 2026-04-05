<template>
  <div class="collaboration-review-page">
    <div class="header">
      <h2>🔍 智能评审协作研究</h2>
      <p>文献助手 + 实验助手 + Critic评审官 协同工作，自动评估质量并优化</p>
    </div>
    
    <div class="input-section">
      <textarea 
        v-model="researchQuestion" 
        placeholder="输入你的研究问题，例如：如何提高深度学习模型在图像分类任务中的准确率？"
        rows="3"
      ></textarea>
      <button @click="startResearch" :disabled="loading || !researchQuestion">
        {{ loading ? '研究中...' : '开始研究（带评审）' }}
      </button>
    </div>

    <!-- 工作流可视化 -->
    <WorkflowVisualizer 
      v-if="showWorkflow" 
      :steps="workflowSteps" 
      :show-dag="showDAG"
      :dag-data="dagData"
    />
    
    <!-- 评审结果卡片 -->
    <div v-if="evaluation" class="evaluation-card" :class="{ passed: evaluation.passed, failed: !evaluation.passed }">
      <div class="evaluation-header">
        <div class="score">
          <span class="score-number">{{ evaluation.overall_score }}</span>
          <span class="score-max">/10</span>
          <span class="status-badge" :class="evaluation.passed ? 'passed' : 'failed'">
            {{ evaluation.passed ? '✅ 通过' : '❌ 需改进' }}
          </span>
        </div>
      </div>
      
      <div class="dimensions">
        <h4>各维度评分</h4>
        <div class="dimension-bars">
          <div class="dimension-item">
            <span>文献质量</span>
            <div class="bar"><div class="fill" :style="{ width: (evaluation.dimensions.literature_review * 10) + '%' }"></div></div>
            <span>{{ evaluation.dimensions.literature_review }}/10</span>
          </div>
          <div class="dimension-item">
            <span>实验设计</span>
            <div class="bar"><div class="fill" :style="{ width: (evaluation.dimensions.experiment_design * 10) + '%' }"></div></div>
            <span>{{ evaluation.dimensions.experiment_design }}/10</span>
          </div>
          <div class="dimension-item">
            <span>一致性</span>
            <div class="bar"><div class="fill" :style="{ width: (evaluation.dimensions.consistency * 10) + '%' }"></div></div>
            <span>{{ evaluation.dimensions.consistency }}/10</span>
          </div>
          <div class="dimension-item">
            <span>可行性</span>
            <div class="bar"><div class="fill" :style="{ width: (evaluation.dimensions.feasibility * 10) + '%' }"></div></div>
            <span>{{ evaluation.dimensions.feasibility }}/10</span>
          </div>
        </div>
      </div>
      
      <div v-if="evaluation.suggestions && evaluation.suggestions.length" class="suggestions">
        <h4>💡 改进建议</h4>
        <ul>
          <li v-for="(s, idx) in evaluation.suggestions" :key="idx">{{ s }}</li>
        </ul>
      </div>
      
      <div v-if="improved" class="improved-badge">
        ✨ 已根据建议自动优化
      </div>
    </div>
    
    <!-- 研究结果 -->
    <div v-if="result" class="result-section">
      <div class="result-tabs">
        <button :class="{ active: activeTab === 'report' }" @click="activeTab = 'report'">
          📄 研究报告
        </button>
        <button :class="{ active: activeTab === 'review' }" @click="activeTab = 'review'">
          🔍 评审详情
        </button>
      </div>
      
      <div class="result-content">
        <div v-if="activeTab === 'report'" class="report">
          <div class="markdown-content" v-html="formatContent(result.response)"></div>
        </div>
        
        <div v-if="activeTab === 'review'" class="review-detail">
          <h3>评审报告</h3>
          <pre>{{ JSON.stringify(evaluation, null, 2) }}</pre>
        </div>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>智能体正在协同工作...</p>
      <div class="agent-status">
        <div class="status-item">
          <span class="dot literature"></span>
          <span>文献助手：{{ literatureStatus }}</span>
        </div>
        <div class="status-item">
          <span class="dot experiment"></span>
          <span>实验助手：{{ experimentStatus }}</span>
        </div>
        <div class="status-item">
          <span class="dot critic"></span>
          <span>Critic评审官：{{ criticStatus }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from '../axios'

const researchQuestion = ref('')
const loading = ref(false)
const result = ref(null)
const evaluation = ref(null)
const improved = ref(false)
const activeTab = ref('report')
const literatureStatus = ref('等待中')
const experimentStatus = ref('等待中')
const criticStatus = ref('等待中')

const escapeHtml = (text) => {
  if (!text) return ''
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

const formatContent = (content) => {
  if (!content) return ''

  // 先转义HTML特殊字符
  let formatted = escapeHtml(content)

  // 处理标题
  formatted = formatted.replace(/^### (.*?)$/gm, '<h3>$1</h3>')
  formatted = formatted.replace(/^## (.*?)$/gm, '<h2>$1</h2>')
  formatted = formatted.replace(/^# (.*?)$/gm, '<h1>$1</h1>')

  // 处理无序列表
  formatted = formatted.replace(/^\s*[-*+] (.*?)$/gm, '<li>$1</li>')

  // 处理有序列表
  formatted = formatted.replace(/^\s*\d+\. (.*?)$/gm, '<li>$1</li>')

  // 如果有列表项，包裹在ul或ol中（简化处理）
  if (formatted.includes('<li>')) {
    formatted = formatted.replace(/<li>(.*?)<\/li>/g, '<ul><li>$1</li></ul>')
    // 合并相邻的ul标签
    formatted = formatted.replace(/<\/ul>\s*<ul>/g, '')
  }

  // 处理粗体
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')

  // 处理斜体
  formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>')

  // 处理换行：两个以上换行符作为段落分隔，单个换行作为<br>
  formatted = formatted.replace(/\n\s*\n/g, '</p><p>')
  formatted = formatted.replace(/\n/g, '<br>')

  // 包裹在段落中
  if (!formatted.startsWith('<h') && !formatted.startsWith('<ul') && !formatted.startsWith('<li')) {
    formatted = '<p>' + formatted + '</p>'
  }

  return formatted
}

const startResearch = async () => {
  if (!researchQuestion.value.trim()) return
  
  loading.value = true
  result.value = null
  evaluation.value = null
  improved.value = false
  literatureStatus.value = '调研中...'
  experimentStatus.value = '等待中'
  criticStatus.value = '等待中'
  
  try {
    const response = await axios.post('/collaboration/review/', {
      question: researchQuestion.value
    })
    
    result.value = response.data
    evaluation.value = response.data.evaluation
    improved.value = response.data.improved || false
    
    literatureStatus.value = '完成 ✓'
    experimentStatus.value = '完成 ✓'
    criticStatus.value = evaluation.value?.passed ? '评审通过 ✓' : '建议改进'
    
  } catch (error) {
    console.error('协作研究失败:', error)
    alert(error.response?.data?.error || '研究失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.collaboration-review-page {
  max-width: 1000px;
  margin: 30px auto;
  padding: 0 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h2 {
  color: #42b983;
  margin-bottom: 10px;
}

.input-section {
  margin-bottom: 30px;
}

textarea {
  width: 100%;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  resize: vertical;
  font-family: inherit;
  margin-bottom: 15px;
}

button {
  padding: 12px 30px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.evaluation-card {
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  background-color: #f9f9f9;
  border-left: 4px solid #ccc;
}

.evaluation-card.passed {
  border-left-color: #42b983;
  background-color: #e8f5e9;
}

.evaluation-card.failed {
  border-left-color: #f44336;
  background-color: #ffebee;
}

.evaluation-header {
  margin-bottom: 15px;
}

.score {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.score-number {
  font-size: 32px;
  font-weight: bold;
  color: #333;
}

.score-max {
  font-size: 16px;
  color: #999;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: bold;
}

.status-badge.passed {
  background-color: #42b983;
  color: white;
}

.status-badge.failed {
  background-color: #f44336;
  color: white;
}

.dimensions {
  margin-bottom: 20px;
}

.dimensions h4 {
  margin-bottom: 10px;
  font-size: 14px;
  color: #666;
}

.dimension-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.dimension-item span:first-child {
  width: 70px;
  font-size: 13px;
}

.bar {
  flex: 1;
  height: 8px;
  background-color: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.fill {
  height: 100%;
  background-color: #42b983;
  border-radius: 4px;
}

.suggestions {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}

.suggestions h4 {
  margin-bottom: 10px;
  font-size: 14px;
  color: #666;
}

.suggestions ul {
  margin: 0;
  padding-left: 20px;
}

.suggestions li {
  margin-bottom: 5px;
  font-size: 13px;
  color: #666;
}

.improved-badge {
  margin-top: 15px;
  padding: 8px 12px;
  background-color: #fff3e0;
  border-radius: 4px;
  font-size: 13px;
  color: #ff9800;
  text-align: center;
}

.result-section {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  background-color: white;
}

.result-tabs {
  display: flex;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f5f5f5;
}

.result-tabs button {
  flex: 1;
  background: none;
  color: #666;
  padding: 12px;
  border-radius: 0;
  background-color: transparent;
}

.result-tabs button.active {
  color: #42b983;
  border-bottom: 2px solid #42b983;
  background-color: white;
}

.result-content {
  padding: 20px;
  max-height: 500px;
  overflow-y: auto;
}

.markdown-content {
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.review-detail pre {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
}

.loading {
  text-align: center;
  padding: 40px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-top: 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #42b983;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.agent-status {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 20px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.dot.literature {
  background-color: #42b983;
}

.dot.experiment {
  background-color: #ff9800;
}

.dot.critic {
  background-color: #9c27b0;
}
</style>