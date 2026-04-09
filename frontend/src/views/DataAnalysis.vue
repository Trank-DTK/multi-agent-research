<!-- 数据集管理页面 -->
<template>
  <div class="data-analysis-page">
    <div class="header">
      <h2>数据分析</h2>
      <button @click="showUpload = true" class="upload-btn">+ 上传数据</button>
    </div>
    
    <!-- 上传弹窗 -->
    <div v-if="showUpload" class="modal">
      <div class="modal-content">
        <h3>上传数据文件</h3>
        <p class="hint">支持 CSV、Excel (.xlsx, .xls)</p>
        <input type="file" accept=".csv,.xlsx,.xls" @change="onFileSelected" ref="fileInput" />
        <input v-model="uploadName" placeholder="数据集名称（可选）" />
        <textarea v-model="uploadDesc" placeholder="描述（可选）" rows="2"></textarea>
        <div class="modal-buttons">
          <button @click="uploadFile" :disabled="uploading">{{ uploading ? '上传中...' : '确认上传' }}</button>
          <button @click="showUpload = false">取消</button>
        </div>
        <p v-if="uploadError" class="error">{{ uploadError }}</p>
      </div>
    </div>
    
    <!-- 数据集列表 -->
    <div class="dataset-list">
      <div v-for="ds in datasets" :key="ds.id" class="dataset-card" @click="selectDataset(ds)">
        <h3>{{ ds.name }}</h3>
        <p>{{ ds.row_count }} 行 × {{ ds.column_count }} 列</p>
        <p class="time">{{ formatDate(ds.uploaded_at) }}</p>
      </div>
      <div v-if="datasets.length === 0" class="empty">
        暂无数据集，点击上方按钮上传
      </div>
    </div>
    
    <!-- 数据分析详情 -->
    <div v-if="selectedDataset" class="analysis-detail">
      <div class="detail-header">
        <h3>{{ selectedDataset.name }}</h3>
        <button @click="selectedDataset = null" class="close-btn">×</button>
      </div>
      
      <!-- 数据预览 -->
      <div class="data-preview">
        <h4>数据预览</h4>
        <div class="preview-table">
          <table>
            <thead>
              <tr>
                <th v-for="col in previewColumns" :key="col">{{ col }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in previewData" :key="idx">
                <td v-for="col in previewColumns" :key="col">{{ row[col] }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- 统计摘要 -->
      <div class="statistics">
        <h4>统计摘要</h4>
        <div class="stats-grid">
          <div class="stat-card">
            <span class="stat-label">行数</span>
            <span class="stat-value">{{ selectedDataset.row_count }}</span>
          </div>
          <div class="stat-card">
            <span class="stat-label">列数</span>
            <span class="stat-value">{{ selectedDataset.column_count }}</span>
          </div>
          <div class="stat-card">
            <span class="stat-label">内存</span>
            <span class="stat-value">{{ formatFileSize(selectedDataset.file_size) }}</span>
          </div>
        </div>
      </div>
      
      <!-- 分析操作 -->
      <div class="analysis-actions">
        <button @click="runAnalysis('descriptive')" :disabled="analyzing">描述性统计</button>
        <button @click="runAnalysis('correlation')" :disabled="analyzing">相关性分析</button>
      </div>
      
      <!-- 分析结果 -->
      <div v-if="analysisResult" class="analysis-result">
        <h4>分析结果</h4>
        <div class="insight">{{ analysisResult.insight }}</div>
        <pre class="result-data">{{ JSON.stringify(analysisResult.result, null, 2) }}</pre>
      </div>
      
      <!-- 可视化 -->
      <div class="visualization">
        <h4>数据可视化</h4>
        <div class="viz-controls">
          <select v-model="vizConfig.chartType">
            <option value="bar">柱状图</option>
            <option value="line">折线图</option>
            <option value="scatter">散点图</option>
            <option value="histogram">直方图</option>
          </select>
          <select v-model="vizConfig.xColumn">
            <option v-for="col in columns" :key="col" :value="col">{{ col }}</option>
          </select>
          <select v-model="vizConfig.yColumn">
            <option value="">无</option>
            <option v-for="col in columns" :key="col" :value="col">{{ col }}</option>
          </select>
          <button @click="generateChart" :disabled="generatingChart">生成图表</button>
        </div>
        <div v-if="chartData" class="chart-container" ref="chartContainer"></div>
      </div>
      
      <!-- AI 对话 -->
      <div class="ai-chat">
        <h4>数据分析助手</h4>
        <div class="chat-messages">
          <div v-for="(msg, idx) in chatMessages" :key="idx" :class="['message', msg.role]">
            {{ msg.content }}
          </div>
        </div>
        <div class="chat-input">
          <input v-model="chatInput" @keydown.enter="sendChat" placeholder="问关于数据的问题..." />
          <button @click="sendChat" :disabled="chatLoading">发送</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import axios from '../axios'
import * as echarts from 'echarts'

const datasets = ref([])
const selectedDataset = ref(null)
const showUpload = ref(false)
const uploading = ref(false)
const uploadName = ref('')
const uploadDesc = ref('')
const uploadError = ref('')
const fileInput = ref(null)
const selectedFile = ref(null)
const previewData = ref([])
const previewColumns = ref([])
const columns = ref([])
const analyzing = ref(false)
const analysisResult = ref(null)
const generatingChart = ref(false)
const chartData = ref(null)
const chartContainer = ref(null)
let chart = null
const chatMessages = ref([])
const chatInput = ref('')
const chatLoading = ref(false)

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const fetchDatasets = async () => {
  try {
    const res = await axios.get('/datasets/')
    datasets.value = res.data
  } catch (error) {
    console.error('获取数据集失败', error)
  }
}

const onFileSelected = (e) => {
  selectedFile.value = e.target.files[0]
}

const uploadFile = async () => {
  if (!selectedFile.value) {
    uploadError.value = '请选择文件'
    return
  }
  
  uploading.value = true
  uploadError.value = ''
  
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  if (uploadName.value) formData.append('name', uploadName.value)
  if (uploadDesc.value) formData.append('description', uploadDesc.value)
  
  try {
    const res = await axios.post('/datasets/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    showUpload.value = false
    uploadName.value = ''
    uploadDesc.value = ''
    selectedFile.value = null
    if (fileInput.value) fileInput.value.value = ''
    fetchDatasets()
    
  } catch (error) {
    uploadError.value = error.response?.data?.error || '上传失败'
  } finally {
    uploading.value = false
  }
}

const selectDataset = async (dataset) => {
  selectedDataset.value = dataset
  analysisResult.value = null
  chartData.value = null
  chatMessages.value = []
  
  try {
    const res = await axios.get(`/datasets/${dataset.id}/`)
    previewData.value = res.data.preview || []
    previewColumns.value = res.data.columns || []
    columns.value = res.data.columns || []
  } catch (error) {
    console.error('加载数据集详情失败', error)
  }
}

const runAnalysis = async (type) => {
  if (!selectedDataset.value) return
  
  analyzing.value = true
  
  try {
    const res = await axios.post(`/datasets/${selectedDataset.value.id}/analyze/`, {
      analysis_type: type
    })
    analysisResult.value = res.data
  } catch (error) {
    console.error('分析失败', error)
  } finally {
    analyzing.value = false
  }
}

const generateChart = async () => {
  if (!selectedDataset.value || !vizConfig.value.xColumn) return
  
  generatingChart.value = true
  
  try {
    const res = await axios.post(`/datasets/${selectedDataset.value.id}/visualize/`, {
      chart_type: vizConfig.value.chartType,
      x_column: vizConfig.value.xColumn,
      y_column: vizConfig.value.yColumn
    })
    
    chartData.value = res.data
    
    await nextTick()
    if (chartContainer.value) {
      if (chart) chart.dispose()
      chart = echarts.init(chartContainer.value)
      
      let option = {}
      if (res.data.chart_type === 'bar') {
        option = {
          title: { text: res.data.title },
          tooltip: { trigger: 'axis' },
          xAxis: { type: 'category', data: res.data.chart_data.x },
          yAxis: { type: 'value' },
          series: [{ type: 'bar', data: res.data.chart_data.y }]
        }
      } else if (res.data.chart_type === 'line') {
        option = {
          title: { text: res.data.title },
          tooltip: { trigger: 'axis' },
          xAxis: { type: 'category', data: res.data.chart_data.x },
          yAxis: { type: 'value' },
          series: [{ type: 'line', data: res.data.chart_data.y }]
        }
      } else if (res.data.chart_type === 'scatter') {
        option = {
          title: { text: res.data.title },
          tooltip: { trigger: 'axis' },
          xAxis: { type: 'value' },
          yAxis: { type: 'value' },
          series: [{
            type: 'scatter',
            data: res.data.chart_data.x.map((x, i) => [x, res.data.chart_data.y[i]])
          }]
        }
      } else if (res.data.chart_type === 'histogram') {
        // 计算直方图
        const values = res.data.chart_data.values
        const bins = res.data.chart_data.bins || 20
        const min = Math.min(...values)
        const max = Math.max(...values)
        const binWidth = (max - min) / bins
        const histogram = new Array(bins).fill(0)
        values.forEach(v => {
          let binIndex = Math.floor((v - min) / binWidth)
          if (binIndex === bins) binIndex = bins - 1 // 处理最大值
          histogram[binIndex]++
        })
        // 生成x轴标签（区间中点）
        const xAxisData = []
        for (let i = 0; i < bins; i++) {
          const left = min + i * binWidth
          const right = left + binWidth
          xAxisData.push(`${left.toFixed(2)}-${right.toFixed(2)}`)
        }
        option = {
          title: { text: res.data.title || '直方图' },
          tooltip: { trigger: 'axis' },
          xAxis: {
            type: 'category',
            data: xAxisData,
            axisLabel: { rotate: 45 }
          },
          yAxis: { type: 'value' },
          series: [{
            type: 'bar',
            data: histogram,
            name: '频数'
          }]
        }
      }
      
      chart.setOption(option)
    }
    
  } catch (error) {
    console.error('生成图表失败', error)
  } finally {
    generatingChart.value = false
  }
}

const sendChat = async () => {
  if (!chatInput.value.trim() || !selectedDataset.value) return
  
  const userMsg = chatInput.value
  chatMessages.value.push({ role: 'user', content: userMsg })
  chatInput.value = ''
  chatLoading.value = true
  
  try {
    const res = await axios.post(`/datasets/${selectedDataset.value.id}/agent/`, {
      message: userMsg
    })
    chatMessages.value.push({ role: 'assistant', content: res.data.response })
  } catch (error) {
    chatMessages.value.push({ role: 'assistant', content: '抱歉，分析失败' })
  } finally {
    chatLoading.value = false
  }
}

const vizConfig = ref({
  chartType: 'bar',
  xColumn: '',
  yColumn: ''
})

onMounted(() => {
  fetchDatasets()
})
</script>

<style scoped>
.data-analysis-page {
  max-width: 1200px;
  margin: 30px auto;
  padding: 0 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.upload-btn {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.dataset-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.dataset-card {
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.dataset-card:hover {
  border-color: #42b983;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.dataset-card h3 {
  margin: 0 0 10px;
  font-size: 16px;
}

.dataset-card p {
  margin: 5px 0;
  color: #666;
  font-size: 12px;
}

.analysis-detail {
  border-top: 1px solid #e0e0e0;
  padding-top: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.preview-table {
  overflow-x: auto;
  margin-bottom: 20px;
}

.preview-table table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.preview-table th, .preview-table td {
  border: 1px solid #e0e0e0;
  padding: 8px;
  text-align: left;
}

.stats-grid {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #42b983;
}

.analysis-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.analysis-actions button {
  padding: 8px 16px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.insight {
  padding: 15px;
  background-color: #e8f5e9;
  border-radius: 8px;
  margin-bottom: 15px;
  line-height: 1.6;
}

.result-data {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 12px;
  max-height: 300px;
}

.viz-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.viz-controls select, .viz-controls button {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.viz-controls button {
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
}

.chart-container {
  height: 400px;
  margin-bottom: 20px;
}

.ai-chat {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.chat-messages {
  height: 200px;
  overflow-y: auto;
  padding: 15px;
  background-color: #f9f9f9;
}

.message {
  margin-bottom: 10px;
  padding: 8px 12px;
  border-radius: 8px;
}

.message.user {
  background-color: #42b983;
  color: white;
  text-align: right;
}

.message.assistant {
  background-color: white;
  border: 1px solid #e0e0e0;
}

.chat-input {
  display: flex;
  padding: 10px;
  border-top: 1px solid #e0e0e0;
}

.chat-input input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-right: 10px;
}

.chat-input button {
  padding: 8px 16px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  width: 450px;
}

.modal-content input, .modal-content textarea {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.modal-buttons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.error {
  color: #f44336;
  margin-top: 10px;
}

.empty {
  text-align: center;
  color: #999;
  padding: 40px;
}

.hint {
  font-size: 12px;
  color: #999;
  margin-bottom: 10px;
}
</style>