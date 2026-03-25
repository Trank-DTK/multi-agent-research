<template>
  <div class="collaboration-page">
    <div class="header">
      <h2>🤝 多智能体协作研究</h2>
      <p>文献助手 + 实验助手 协同工作，完成完整的研究流程</p>
    </div>
    
    <div class="input-section">
      <textarea 
        v-model="researchQuestion" 
        placeholder="输入你的研究问题，例如：如何提高深度学习模型在图像分类任务中的准确率？"
        rows="3"
      ></textarea>
      <button @click="startResearch" :disabled="loading || !researchQuestion">
        {{ loading ? '研究中...' : '开始研究' }}
      </button>
    </div>
    
    <!-- 结果显示区域 -->
    <div v-if="result" class="result-section">
      <div class="result-tabs">
        <button :class="{ active: activeTab === 'report' }" @click="activeTab = 'report'">
          📄 研究报告
        </button>
        <button :class="{ active: activeTab === 'literature' }" @click="activeTab = 'literature'">
          📚 文献调研
        </button>
        <button :class="{ active: activeTab === 'experiment' }" @click="activeTab = 'experiment'">
          🔬 实验设计
        </button>
      </div>
      
      <div class="result-content">
        <div v-if="activeTab === 'report'" class="report">
          <h3>研究方案报告</h3>
          <div class="markdown-content">{{ formatContent(result.response) }}</div>
        </div>
        
        <div v-if="activeTab === 'literature'" class="literature">
          <h3>文献调研结果</h3>
          <div class="markdown-content">{{ formatContent(result.results?.literature_review || '无') }}</div>
        </div>
        
        <div v-if="activeTab === 'experiment'" class="experiment">
          <h3>实验设计方案</h3>
          <div class="markdown-content">{{ formatContent(result.results?.experiment_design || '无') }}</div>
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
const activeTab = ref('report')
const literatureStatus = ref('等待中')
const experimentStatus = ref('等待中')

const formatContent = (content) => {
  if (!content) return ''
  // 简单处理换行和列表
  return content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
}

const startResearch = async () => {
  if (!researchQuestion.value.trim()) return
  
  loading.value = true
  result.value = null
  literatureStatus.value = '调研中...'
  experimentStatus.value = '等待中'
  
  try {
    const response = await axios.post('/api/collaboration/research/', {
      question: researchQuestion.value
    })
    
    result.value = response.data
    
    // 更新状态
    if (response.data.results?.literature_review) {
      literatureStatus.value = '完成 ✓'
    }
    if (response.data.results?.experiment_design) {
      experimentStatus.value = '完成 ✓'
    }
    
  } catch (error) {
    console.error('协作研究失败:', error)
    alert(error.response?.data?.error || '研究失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.collaboration-page {
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
</style>