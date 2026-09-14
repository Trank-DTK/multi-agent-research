<template>
  <main class="documents-page modern-page">
    <header class="section-title">
      <div>
        <p class="eyebrow">KNOWLEDGE LIBRARY</p>
        <h1>文献与问答</h1>
        <p>管理研究资料，让每个问题都有证据可循。</p>
      </div>
      <button class="primary-button" @click="openUpload">＋ 上传文献</button>
    </header>
    <div class="library-workspace">
      <section class="panel library-panel">
        <div class="panel-heading">
          <h2>
            我的文献 <span class="count-badge">{{ documents.length }}</span>
          </h2>
          <button class="text-button" :disabled="loading" @click="fetchDocuments">刷新</button>
        </div>
        <input
          v-model="search"
          type="search"
          class="full-search"
          aria-label="搜索文献"
          placeholder="搜索标题或文件名"
        />
        <p v-if="error" class="error-banner" role="alert">{{ error }}</p>
        <p v-if="notice" class="notice-banner" role="status">{{ notice }}</p>
        <p v-if="loading" class="empty-state">正在加载文献…</p>
        <div v-else-if="!documents.length" class="empty-state">
          <el-icon><FolderOpened /></el-icon>
          <h3>建立你的知识库</h3>
          <p>上传 PDF 后可直接提问，也可将资料用于协作研究。</p>
          <button class="secondary-button" @click="openUpload">上传第一篇文献</button>
        </div>
        <div v-else class="document-list">
          <article
            v-for="doc in filtered"
            :key="doc.id"
            class="library-document"
            :class="{ selected: selectedIds.includes(doc.id) }"
          >
            <label
              ><input
                v-model="selectedIds"
                type="checkbox"
                :value="doc.id"
                :aria-label="'选择 ' + doc.title"
              /><span class="pdf-icon">PDF</span
              ><span class="document-info"
                ><strong>{{ doc.title }}</strong
                ><small
                  >{{ doc.page_count }} 页 · {{ formatSize(doc.file_size) }} ·
                  {{ formatDate(doc.uploaded_at) }}</small
                ><small>{{ doc.file_name }}</small></span
              ></label
            ><button
              class="icon-button danger-text"
              :aria-label="'删除 ' + doc.title"
              @click="remove(doc)"
            >
              ×
            </button>
          </article>
          <p v-if="!filtered.length" class="empty-state">没有匹配的文献</p>
        </div>
        <div v-if="documents.length" class="library-selection">
          <span>已选 {{ selectedIds.length }} 篇作为问答资料</span
          ><button class="text-button" @click="selectedIds = []">清空选择</button>
        </div>
      </section>
      <ResearchConversation
        endpoint="/literature/chat/"
        title="文献问答"
        :subtitle="selectedIds.length ? '仅依据你选择的文献回答' : '先在左侧选择参考文献'"
        :context="{ document_ids: selectedIds }"
        :disabled="!selectedIds.length"
        empty-title="与文献展开对话"
        empty-description="选择文献后，可以提取关键结论、总结方法或查找论据。回答会附上文献 ID。"
        placeholder="例如：这些文献采用了哪些方法？有哪些研究局限？"
      />
    </div>
    <el-dialog
      v-model="showUpload"
      title="上传 PDF 文献"
      width="min(560px,94vw)"
      :close-on-click-modal="!uploading"
      :close-on-press-escape="!uploading"
      :show-close="!uploading"
      ><form class="settings-form" @submit.prevent="upload">
        <label class="upload-zone"
          ><el-icon><UploadFilled /></el-icon><strong>{{ file?.name || '选择 PDF 文献' }}</strong
          ><span>支持文本型 PDF，最大 30 MB</span
          ><input
            type="file"
            accept=".pdf,application/pdf"
            :disabled="uploading"
            @change="selectFile" /></label
        ><label
          >文献标题<input
            v-model.trim="title"
            placeholder="留空使用文件名"
            maxlength="500"
            :disabled="uploading"
        /></label>
        <p class="field-help">扫描件请先完成 OCR。上传和文本检索不要求本地模型正在运行。</p>
        <el-progress v-if="uploading" :percentage="progress" />
        <p v-if="uploadError" class="error-banner" role="alert">{{ uploadError }}</p>
        <div class="dialog-actions">
          <button
            type="button"
            class="secondary-button"
            :disabled="uploading"
            @click="showUpload = false"
          >
            取消</button
          ><button class="primary-button" :disabled="uploading || !file">
            {{ uploading ? '正在上传与解析…' : '上传文献' }}
          </button>
        </div>
      </form></el-dialog
    >
  </main>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import axios from '@/axios'
import ResearchConversation from '@/components/ResearchConversation.vue'
import { apiError } from '@/utils/apiError'
defineOptions({name:'DocumentLibrary'})
const documents = ref([]),
  selectedIds = ref([]),
  search = ref(''),
  loading = ref(false),
  error = ref(''),
  notice = ref(''),
  showUpload = ref(false),
  uploading = ref(false),
  file = ref(null),
  title = ref(''),
  uploadError = ref(''),
  progress = ref(0)
const filtered = computed(() =>
  documents.value.filter((doc) =>
    (doc.title + ' ' + doc.file_name).toLowerCase().includes(search.value.toLowerCase()),
  ),
)
const formatDate = (value) => new Date(value).toLocaleDateString('zh-CN')
const formatSize = (value) =>
  value < 1024 * 1024 ? `${(value / 1024).toFixed(0)} KB` : `${(value / 1024 / 1024).toFixed(1)} MB`
function openUpload() {
  file.value = null
  title.value = ''
  uploadError.value = ''
  progress.value = 0
  showUpload.value = true
}
function selectFile(event) {
  file.value = event.target.files[0] || null
  uploadError.value = ''
  if (
    file.value &&
    (!file.value.name.toLowerCase().endsWith('.pdf') || file.value.size > 30 * 1024 * 1024)
  ) {
    uploadError.value = '请选择 30 MB 以内的 PDF 文件'
    file.value = null
  }
}
async function fetchDocuments() {
  loading.value = true
  error.value = ''
  try {
    documents.value = (await axios.get('/documents/')).data
    selectedIds.value = selectedIds.value.filter((id) =>
      documents.value.some((doc) => doc.id === id),
    )
  } catch (e) {
    error.value = apiError(e, '文献列表加载失败')
  } finally {
    loading.value = false
  }
}
async function upload() {
  if (!file.value || uploading.value) return
  uploading.value = true
  uploadError.value = ''
  const body = new FormData()
  body.append('file', file.value)
  if (title.value) body.append('title', title.value)
  try {
    const { data } = await axios.post('/documents/upload/', body, {
      headers: { 'Content-Type': undefined },
      timeout: 180000,
      onUploadProgress: (event) => {
        progress.value = Math.min(99, Math.round((event.progress || 0) * 100))
      },
    })
    progress.value = 100
    showUpload.value = false
    notice.value = data.message
    await fetchDocuments()
    selectedIds.value = [data.document.id]
  } catch (e) {
    uploadError.value = apiError(e, '上传失败，请检查网络与后端服务')
  } finally {
    uploading.value = false
  }
}
async function remove(doc) {
  try {
    await ElMessageBox.confirm(`删除文献“${doc.title}”？`, '删除文献', { type: 'warning' })
  } catch {
    return
  }
  try {
    await axios.delete(`/documents/${doc.id}/delete/`)
    await fetchDocuments()
  } catch (e) {
    error.value = apiError(e)
  }
}
onMounted(fetchDocuments)
</script>
