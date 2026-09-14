<template>
  <main class="data-analysis-page modern-page">
    <header class="section-title">
      <div>
        <p class="eyebrow">DATA EXPLORER</p>
        <h1>数据分析</h1>
        <p>从原始数据到可解释的结果，探索每一个发现。</p>
      </div>
      <button
        class="primary-button"
        @click="openUpload"
      >
        ＋ 上传数据
      </button>
    </header>
    <p v-if="pageError" class="error-banner" role="alert">{{ pageError }}</p>
    <div class="analysis-workspace">
      <aside class="panel dataset-rail">
        <div class="panel-heading">
          <h2>
            数据集 <span class="count-badge">{{ datasets.length }}</span>
          </h2>
          <button class="text-button" :disabled="listLoading" @click="fetchDatasets">刷新</button>
        </div>
        <input
          v-model="search"
          class="full-search"
          type="search"
          aria-label="搜索数据集"
          placeholder="搜索数据集"
        />
        <p v-if="listLoading" class="empty-state">正在加载…</p>
        <button
          v-for="ds in filteredDatasets"
          :key="ds.id"
          class="dataset-choice"
          :class="{ active: selectedDataset?.id === ds.id }"
          :disabled="busy"
          @click="selectDataset(ds)"
        >
          <strong>{{ ds.name }}</strong
          ><small>{{ ds.row_count }} 行 × {{ ds.column_count }} 列</small
          ><small>{{ formatDate(ds.uploaded_at) }}</small>
        </button>
        <p v-if="!listLoading && !filteredDatasets.length" class="empty-state">
          {{ datasets.length ? '没有匹配的数据集' : '还没有数据集，上传文件开始分析。' }}
        </p>
      </aside>
      <div v-if="selectedDataset" class="analysis-canvas">
        <div class="analysis-stats">
          <div class="metric-card">
            <small>数据行数</small><strong>{{ selectedDataset.row_count }}</strong>
          </div>
          <div class="metric-card">
            <small>字段数量</small><strong>{{ selectedDataset.column_count }}</strong>
          </div>
          <div class="metric-card">
            <small>文件大小</small><strong>{{ formatFileSize(selectedDataset.file_size) }}</strong>
          </div>
        </div>
        <section class="panel">
          <div class="section-title">
            <div>
              <h2>{{ selectedDataset.name }}</h2>
              <p>数据预览 · 前 20 行</p>
            </div>
          </div>
          <p v-if="detailLoading" class="thinking">正在读取数据…</p>
          <div v-else class="preview-table">
            <table>
              <thead>
                <tr>
                  <th v-for="col in previewColumns" :key="col">{{ col }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in previewData" :key="index">
                  <td v-for="col in previewColumns" :key="col">{{ row[col] ?? '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
        <section class="panel">
          <div class="section-title">
            <div>
              <h2>统计分析</h2>
              <p>查看数据分布与变量关系</p>
            </div>
            <div class="row-actions">
              <button :disabled="busy" @click="runAnalysis('descriptive')">描述性统计</button
              ><button :disabled="busy" @click="runAnalysis('correlation')">相关性分析</button>
            </div>
          </div>
          <p v-if="analyzing" class="thinking">正在分析数据…</p>
          <template v-else-if="analysisResult"
            ><p class="report-text">{{ analysisResult.insight }}</p>
            <details>
              <summary>查看完整统计结果</summary>
              <pre class="result-json">{{ JSON.stringify(analysisResult.result, null, 2) }}</pre>
            </details></template
          >
          <p v-else class="field-help">选择一种分析方式，结果将显示在这里。</p>
        </section>
        <section class="panel">
          <h2>数据可视化</h2>
          <div class="chart-controls">
            <label
              >图表类型<select v-model="vizConfig.chartType">
                <option value="bar">柱状图</option>
                <option value="line">折线图</option>
                <option value="scatter">散点图</option>
                <option value="histogram">直方图</option>
              </select></label
            ><label
              >X 轴 / 分布字段<select v-model="vizConfig.xColumn">
                <option value="">选择字段</option>
                <option v-for="col in columns" :key="col" :value="col">{{ col }}</option>
              </select></label
            ><label
              >Y 轴<select
                v-model="vizConfig.yColumn"
                :disabled="vizConfig.chartType === 'histogram'"
              >
                <option value="">不指定</option>
                <option v-for="col in columns" :key="col" :value="col">{{ col }}</option>
              </select></label
            ><button
              class="primary-button"
              :disabled="busy || !vizConfig.xColumn"
              @click="generateChart"
            >
              {{ generatingChart ? '生成中…' : '生成图表' }}
            </button>
          </div>
          <div v-if="chartData" ref="chartContainer" class="chart-container" />
        </section>
        <ResearchConversation
          :key="selectedDataset.id"
          :endpoint="'/datasets/' + selectedDataset.id + '/agent/'"
          title="数据解读助手"
          empty-title="让数据回答问题"
          empty-description="基于当前数据集的统计信息，讨论结果、异常与后续分析方向。"
        />
      </div>
      <section v-else class="panel empty-state analysis-empty">
        <el-icon><DataAnalysis /></el-icon>
        <h3>从一份数据，开始探索</h3>
        <p>上传 CSV 或 Excel，预览字段、计算统计指标并生成可视化图表。</p>
        <button class="primary-button" @click="showUpload = true">上传第一份数据</button>
        <p class="field-help">也可以在左侧选择已有数据集。</p>
      </section>
    </div>
    <el-dialog
      v-model="showUpload"
      title="上传数据集"
      width="min(540px,94vw)"
      :close-on-click-modal="!uploading"
      :show-close="!uploading"
      :close-on-press-escape="!uploading"
      ><form class="settings-form" @submit.prevent="uploadFile">
        <label class="upload-zone"
          ><el-icon><UploadFilled /></el-icon><strong>选择数据文件</strong
          ><span>CSV / Excel（.xlsx、.xls）</span
          ><input
            ref="fileInput"
            type="file"
            accept=".csv,.xlsx,.xls"
            :disabled="uploading"
            @change="onFileSelected" /></label
        ><label>数据集名称<input v-model="uploadName" placeholder="留空使用文件名" /></label
        ><label
          >描述<textarea v-model="uploadDesc" rows="2" placeholder="说明数据来源、内容或用途" />
        </label>
        <p v-if="uploadError" class="error-banner" role="alert">{{ uploadError }}</p>
        <div class="dialog-actions">
          <button
            type="button"
            class="secondary-button"
            :disabled="uploading"
            @click="showUpload = false"
          >
            取消</button
          ><button class="primary-button" :disabled="uploading || !selectedFile">
            {{ uploading ? '正在上传…' : '上传数据' }}
          </button>
        </div>
      </form></el-dialog
    >
  </main>
</template>
<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import axios from '../axios'
import * as echarts from 'echarts/core'
import { BarChart, LineChart, ScatterChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import ResearchConversation from '@/components/ResearchConversation.vue'
import { apiError } from '@/utils/apiError'
echarts.use([
  BarChart,
  LineChart,
  ScatterChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  CanvasRenderer,
])

const openUpload=()=>{showUpload.value=true;uploadError.value='';selectedFile.value=null;uploadName.value='';uploadDesc.value=''}
const datasets = ref([])
const pageError = ref(''),
  listLoading = ref(false),
  detailLoading = ref(false),
  search = ref('')
const filteredDatasets = computed(() =>
  datasets.value.filter((ds) => ds.name.toLowerCase().includes(search.value.toLowerCase())),
)
const busy = computed(() => detailLoading.value || analyzing.value || generatingChart.value)
let resizeObserver
const disposeChart = () => {
  resizeObserver?.disconnect()
  chart?.dispose()
  chart = null
}
onUnmounted(disposeChart)
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
  listLoading.value = true
  pageError.value = ''
  try {
    const res = await axios.get('/datasets/')
    datasets.value = res.data
  } catch (error) {
    pageError.value = apiError(error, '数据集加载失败')
  } finally {
    listLoading.value = false
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
    await axios.post('/datasets/upload/', formData, {
      headers: { 'Content-Type': undefined },
      timeout: 180000,
    })

    showUpload.value = false
    uploadName.value = ''
    uploadDesc.value = ''
    selectedFile.value = null
    if (fileInput.value) fileInput.value.value = ''
    fetchDatasets()
  } catch (error) {
    uploadError.value = apiError(error, '上传失败')
  } finally {
    uploading.value = false
  }
}

const selectDataset = async (dataset) => {
  if (busy.value) return
  detailLoading.value = true
  pageError.value = ''
  selectedDataset.value = dataset
  analysisResult.value = null
  chartData.value = null
  disposeChart()
  previewData.value = []
  previewColumns.value = []
  columns.value = []
  vizConfig.value.xColumn = ''
  vizConfig.value.yColumn = ''

  try {
    const res = await axios.get(`/datasets/${dataset.id}/`)
    previewData.value = res.data.preview || []
    previewColumns.value = res.data.columns || []
    columns.value = res.data.columns || []
    vizConfig.value.xColumn = columns.value[0] || ''
  } catch (error) {
    pageError.value = apiError(error, '数据预览加载失败')
  } finally {
    detailLoading.value = false
  }
}

const runAnalysis = async (type) => {
  if (!selectedDataset.value || busy.value) return

  pageError.value = ''
  analyzing.value = true

  try {
    const res = await axios.post(`/datasets/${selectedDataset.value.id}/analyze/`, {
      analysis_type: type,
    })
    analysisResult.value = res.data
  } catch (error) {
    pageError.value = apiError(error, '分析失败')
  } finally {
    analyzing.value = false
  }
}

const generateChart = async () => {
  if (!selectedDataset.value || !vizConfig.value.xColumn || busy.value) return
  pageError.value = ''
  if (vizConfig.value.chartType === 'scatter' && !vizConfig.value.yColumn) {
    pageError.value = '散点图需要选择 X 和 Y 列'
    return
  }

  generatingChart.value = true

  try {
    const res = await axios.post(`/datasets/${selectedDataset.value.id}/visualize/`, {
      chart_type: vizConfig.value.chartType,
      x_column: vizConfig.value.xColumn,
      y_column: vizConfig.value.yColumn,
    })

    chartData.value = res.data

    await nextTick()
    if (chartContainer.value) {
      disposeChart()
      chart = echarts.init(chartContainer.value)

      let option = {}
      if (res.data.chart_type === 'bar') {
        option = {
          title: { text: res.data.title },
          tooltip: { trigger: 'axis' },
          xAxis: { type: 'category', data: res.data.chart_data.x },
          yAxis: { type: 'value' },
          series: [{ type: 'bar', data: res.data.chart_data.y }],
        }
      } else if (res.data.chart_type === 'line') {
        option = {
          title: { text: res.data.title },
          tooltip: { trigger: 'axis' },
          xAxis: { type: 'category', data: res.data.chart_data.x },
          yAxis: { type: 'value' },
          series: [{ type: 'line', data: res.data.chart_data.y }],
        }
      } else if (res.data.chart_type === 'scatter') {
        option = {
          title: { text: res.data.title },
          tooltip: { trigger: 'axis' },
          xAxis: { type: 'value' },
          yAxis: { type: 'value' },
          series: [
            {
              type: 'scatter',
              data: res.data.chart_data.x.map((x, i) => [x, res.data.chart_data.y[i]]),
            },
          ],
        }
      } else if (res.data.chart_type === 'histogram') {
        // 计算直方图
        const values = res.data.chart_data.values.filter(Number.isFinite)
        if (!values.length) throw new Error('没有有效数值')
        const bins = res.data.chart_data.bins || 20
        const min = values.reduce((a, b) => Math.min(a, b), Infinity)
        const max = values.reduce((a, b) => Math.max(a, b), -Infinity)
        const binWidth = (max - min || 1) / bins
        const histogram = new Array(bins).fill(0)
        values.forEach((v) => {
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
            axisLabel: { rotate: 45 },
          },
          yAxis: { type: 'value' },
          series: [
            {
              type: 'bar',
              data: histogram,
              name: '频数',
            },
          ],
        }
      }

      chart.setOption({
        ...option,
        color: ['#326bd6'],
        grid: { left: 48, right: 24, bottom: 70, containLabel: true },
      })
      resizeObserver = new ResizeObserver(() => chart?.resize())
      resizeObserver.observe(chartContainer.value)
    }
  } catch (error) {
    pageError.value = apiError(error, '生成图表失败')
  } finally {
    generatingChart.value = false
  }
}

const vizConfig = ref({
  chartType: 'bar',
  xColumn: '',
  yColumn: '',
})

onMounted(() => {
  fetchDatasets()
})
</script>
