<template>
  <main class="collaboration-page modern-page">
    <header class="section-title">
      <div>
        <p class="eyebrow">COLLABORATIVE RESEARCH</p>
        <h1>协作研究</h1>
        <p>从文献证据到研究方案，在一个空间完成协作与评审。</p>
      </div>
      <span class="badge">多角色协作</span>
    </header>
    <div class="research-steps">
      <div v-for="(step, i) in steps" :key="step">
        <span>0{{ i + 1 }}</span
        ><strong>{{ step }}</strong>
      </div>
    </div>
    <section class="panel research-brief">
      <h2>这次想研究什么？</h2>
      <p>描述你的问题、预期目标与研究约束。</p>
      <textarea
        v-model="question"
        rows="5"
        aria-label="研究问题"
        placeholder="例如：如何提高小样本条件下图像分类模型的准确率？请比较可行方法，并设计对照实验。"
        :disabled="loading"
      />
      <div class="research-options">
        <el-select
          v-model="selectedIds"
          multiple
          collapse-tags
          collapse-tags-tooltip
          placeholder="从文献库添加参考资料"
          :disabled="loading || documentsLoading"
          style="min-width: 240px; flex: 1"
          ><el-option
            v-for="doc in documents"
            :key="doc.id"
            :value="doc.id"
            :label="doc.title" /></el-select
        ><label class="check-label"
          ><input
            v-model="withReview"
            type="checkbox"
            :disabled="loading"
          />完成后进行研究评审</label
        >
      </div>
      <p v-if="documentError" class="error-banner">
        {{ documentError }} <button class="text-button" @click="loadDocuments">重试</button>
      </p>
      <div class="brief-actions">
        <span>{{
          selectedIds.length
            ? '已添加 ' + selectedIds.length + ' 篇参考文献'
            : '可选：添加资料，让方案更贴近你的研究'
        }}</span
        ><button class="primary-button" :disabled="loading || !question.trim()" @click="start">
          {{ loading ? '正在协作研究…' : '开始研究 →' }}
        </button>
      </div>
    </section>
    <p v-if="error" class="error-banner" role="alert">{{ error }}</p>
    <section v-if="loading" class="panel thinking" role="status">
      <el-icon class="is-loading"><Loading /></el-icon> 正在依次完成文献分析、实验设计与报告整合{{
        withReview ? '，随后进行评审' : ''
      }}，请稍候。
    </section>
    <section v-if="result" class="panel research-result">
      <div class="section-title">
        <h2>研究成果</h2>
        <button class="secondary-button" @click="download">下载报告</button>
      </div>
      <div class="segmented">
        <button
          v-for="item in resultTabs"
          :key="item.id"
          :class="{ active: activeTab === item.id }"
          @click="activeTab = item.id"
        >
          {{ item.name }}
        </button>
      </div>
      <div class="report-text">{{ resultText }}</div>
    </section>
    <section v-else-if="!loading" class="research-guide">
      <div>
        <el-icon><Reading /></el-icon>
        <h3>文献分析</h3>
        <p>整理所选资料中的研究证据与空白。</p>
      </div>
      <div>
        <el-icon><Aim /></el-icon>
        <h3>实验设计</h3>
        <p>明确假设、变量、对照和评估指标。</p>
      </div>
      <div>
        <el-icon><CircleCheck /></el-icon>
        <h3>研究评审</h3>
        <p>按需检查方案并提出具体改进建议。</p>
      </div>
    </section>
  </main>
</template>
<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import axios from '@/axios'
import { apiError } from '@/utils/apiError'
defineOptions({ name: 'ResearchCollaboration' })
const route = useRoute(),
  question = ref(''),
  selectedIds = ref([]),
  documents = ref([]),
  documentsLoading = ref(false),
  documentError = ref(''),
  withReview = ref(route.query.review === '1'),
  loading = ref(false),
  error = ref(''),
  result = ref(null),
  activeTab = ref('report')
const steps = computed(() =>
  withReview.value
    ? ['文献分析', '实验设计', '报告整合', '研究评审']
    : ['文献分析', '实验设计', '报告整合'],
)
const resultTabs = computed(() => [
  { id: 'report', name: '研究报告' },
  { id: 'literature', name: '文献分析' },
  { id: 'experiment', name: '实验设计' },
  ...(result.value?.review ? [{ id: 'review', name: '评审意见' }] : []),
])
const resultText = computed(
  () =>
    ({
      report: result.value?.response,
      literature: result.value?.results?.literature_review,
      experiment: result.value?.results?.experiment_design,
      review: result.value?.review,
    })[activeTab.value],
)
async function loadDocuments() {
  documentsLoading.value = true
  documentError.value = ''
  try {
    documents.value = (await axios.get('/documents/')).data
  } catch (e) {
    documentError.value = apiError(e, '参考文献加载失败')
  } finally {
    documentsLoading.value = false
  }
}
async function start() {
  if (loading.value || !question.value.trim()) return
  loading.value = true
  error.value = ''
  result.value = null
  try {
    result.value = (
      await axios.post(
        '/collaboration/research/',
        {
          question: question.value,
          document_ids: selectedIds.value,
          with_review: withReview.value,
        },
        { timeout: 600000 },
      )
    ).data
    activeTab.value = 'report'
  } catch (e) {
    error.value = apiError(e)
  } finally {
    loading.value = false
  }
}
function download() {
  const text =
    result.value.response + (result.value.review ? '\n\n## 评审意见\n' + result.value.review : '')
  const url = URL.createObjectURL(new Blob([text], { type: 'text/markdown;charset=utf-8' }))
  const link = document.createElement('a')
  link.href = url
  link.download = '研究报告.md'
  link.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
onMounted(loadDocuments)
</script>
