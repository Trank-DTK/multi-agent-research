<!-- 论文写作页面 -->
<template>
  <div class="paper-writing-page modern-page">
    <div class="page-header">
      <div class="header-content">
        <div class="header-title">
          <h1>论文写作</h1>
          <p class="subtitle">AI辅助的论文撰写、编辑和导出工具</p>
        </div>
        <button @click="showNewPaper = true" class="new-btn">
          <span class="btn-icon">+</span>
          <span class="btn-text">新建论文</span>
        </button>
      </div>
    </div>

    <!-- 新建论文弹窗 -->
    <div v-if="showNewPaper" class="modal">
      <div class="modal-content" :aria-busy="creating">
        <h3>新建论文</h3>
        <input v-model="newPaperTitle" :disabled="creating" placeholder="论文标题" />
        <textarea
          v-model="newPaperTopic"
          :disabled="creating"
          placeholder="研究主题（可选，用于生成大纲）"
          rows="3"
        ></textarea>
        <p v-if="createError" class="error-banner" role="alert">{{ createError }}</p>
        <div v-if="creating" class="creation-status" role="status" aria-live="polite">
          <span class="creation-spinner" aria-hidden="true"></span
          >{{ newPaperTopic.trim() ? '正在创建论文并生成大纲，请稍候…' : '正在创建论文，请稍候…' }}
        </div>
        <div class="modal-buttons">
          <button @click="createPaper" :disabled="creating || !newPaperTitle.trim()">
            {{ creating ? '创建中…' : '创建' }}
          </button>
          <button @click="showNewPaper = false" :disabled="creating">取消</button>
        </div>
      </div>
    </div>

    <p v-if="pageError" class="error-banner" role="alert">{{ pageError }}</p>
    <div class="main-layout">
      <!-- 左侧：论文列表 -->
      <div class="paper-list">
        <h3>
          我的论文 <span class="count-badge">{{ papers.length }}</span>
        </h3>
        <div
          v-for="paper in papers"
          :key="paper.id"
          :class="['paper-item', { active: selectedPaper?.id === paper.id }]"
          @click="selectPaper(paper.id)"
        >
          <div class="paper-title">{{ paper.title }}</div>
          <div class="paper-status">{{ getStatusText(paper.status) }}</div>
          <div class="paper-time">{{ formatDate(paper.updated_at) }}</div>
          <button @click.stop="deletePaper(paper.id)" class="delete-paper">🗑️</button>
        </div>
        <div v-if="papers.length === 0" class="empty">暂无论文，点击上方按钮创建</div>
      </div>

      <!-- 右侧：编辑器 -->
      <div v-if="selectedPaper" class="editor-area">
        <div class="editor-header">
          <input v-model="selectedPaper.title" class="title-input" @blur="savePaper" />
          <div class="actions">
            <button @click="generateAbstract" :disabled="generatingAbstract">生成摘要</button>
            <button @click="exportDocx" :disabled="exporting">导出Word</button>
            <button @click="savePaper" :disabled="saving">保存</button>
          </div>
        </div>

        <!-- 摘要区域 -->
        <div class="abstract-area">
          <label>摘要</label
          ><button class="text-button" @click="editingAbstract = !editingAbstract">
            {{ editingAbstract ? '预览' : '编辑' }}
          </button>
          <textarea
            v-if="editingAbstract || !selectedPaper.abstract"
            v-model="selectedPaper.abstract"
            rows="4"
            @blur="savePaper"
          ></textarea
          ><MarkdownContent v-else :content="selectedPaper.abstract" />
        </div>

        <!-- 章节列表 -->
        <div class="sections">
          <div v-for="section in sections" :key="section.id" class="section-card">
            <div class="section-header">
              <input v-model="section.title" class="section-title" @blur="saveSection(section)" />
              <button @click="polishSection(section)" class="polish-btn" :disabled="polishing">
                润色
              </button>
              <button @click="deleteSection(section.id)" class="delete-section">×</button>
            </div>
            <button class="text-button" @click="toggleSection(section)">
              {{ editingSections.includes(section.id) ? '预览' : '编辑' }}
            </button>
            <div class="section-content">
              <MarkdownContent
                v-if="!editingSections.includes(section.id)"
                :content="section.content"
                rich-text
              />
              <QuillEditor
                v-else
                v-model:content="section.content"
                contentType="html"
                @blur="saveSection(section)"
              />
            </div>
          </div>

          <div class="add-section">
            <input v-model="newSectionTitle" placeholder="新章节标题" />
            <button @click="addSection" :disabled="!newSectionTitle">+ 添加章节</button>
            <button @click="generateSection" :disabled="!newSectionTitle">🤖 AI生成</button>
          </div>
        </div>

        <!-- AI助手聊天 -->
        <div class="ai-assistant">
          <h4>🤖 写作助手</h4>
          <div class="chat-messages">
            <div v-for="(msg, idx) in chatMessages" :key="idx" :class="['message', msg.role]">
              <MarkdownContent v-if="msg.role === 'assistant'" :content="msg.content" /><span
                v-else
                >{{ msg.content }}</span
              >
            </div>
          </div>
          <div class="chat-input">
            <input
              v-model="chatInput"
              @keydown.enter="sendChat"
              placeholder="问关于写作的问题..."
            />
            <button @click="sendChat" :disabled="chatLoading">发送</button>
          </div>
        </div>
      </div>

      <!-- 未选择论文时的占位 -->
      <div v-else class="empty-editor">
        <el-icon><EditPen /></el-icon>
        <h2>把研究写成作品</h2>
        <p>选择已有论文继续编辑，或从一个新标题开始。</p>
        <button class="primary-button" @click="showNewPaper = true">＋ 创建论文</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import MarkdownContent from '@/components/MarkdownContent.vue'
import { renderStoredContent } from '@/utils/markdown'
import { ref, onMounted } from 'vue'
import axios from '../axios'
import { apiError } from '@/utils/apiError'
const pageError = ref('')
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'

const papers = ref([])
const selectedPaper = ref(null)
const sections = ref([])
const editingAbstract = ref(false)
const editingSections = ref([])
const toggleSection = (section) => {
  if (editingSections.value.includes(section.id)) {
    editingSections.value = editingSections.value.filter((id) => id !== section.id)
    saveSection(section)
  } else {
    section.content = renderStoredContent(section.content)
    editingSections.value.push(section.id)
  }
}
const showNewPaper = ref(false)
const newPaperTitle = ref('')
const newPaperTopic = ref('')
const creating = ref(false)
const createError = ref('')
const saving = ref(false)
const generatingAbstract = ref(false)
const exporting = ref(false)
const polishing = ref(false)
const newSectionTitle = ref('')
const chatMessages = ref([])
const chatInput = ref('')
const chatLoading = ref(false)

const getStatusText = (status) => {
  const map = { draft: '草稿', writing: '写作中', review: '评审中', completed: '已完成' }
  return map[status] || status
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const fetchPapers = async () => {
  try {
    const res = await axios.get('/papers/')
    papers.value = res.data
  } catch (error) {
    pageError.value = apiError(error, '获取论文列表失败')
  }
}

const createPaper = async () => {
  if (creating.value || !newPaperTitle.value.trim()) return
  createError.value = ''
  pageError.value = ''

  creating.value = true
  try {
    const res = await axios.post('/papers/create/', {
      title: newPaperTitle.value,
      topic: newPaperTopic.value,
    })
    showNewPaper.value = false
    newPaperTitle.value = ''
    newPaperTopic.value = ''
    await fetchPapers()
    await selectPaper(res.data.id)
  } catch (error) {
    createError.value = apiError(error, '创建论文失败')
  } finally {
    creating.value = false
  }
}

const selectPaper = async (paperId) => {
  try {
    const res = await axios.get(`/papers/${paperId}/`)
    selectedPaper.value = res.data
    editingSections.value = []
    editingAbstract.value = false
    sections.value = res.data.sections || []
  } catch (error) {
    pageError.value = apiError(error, '加载论文失败')
  }
}

const savePaper = async () => {
  if (!selectedPaper.value) return

  saving.value = true
  pageError.value = ''
  try {
    await axios.put(`/papers/${selectedPaper.value.id}/`, {
      title: selectedPaper.value.title,
      abstract: selectedPaper.value.abstract,
      keywords: selectedPaper.value.keywords,
      content: selectedPaper.value.content,
      status: selectedPaper.value.status,
    })
    const item = papers.value.find((paper) => paper.id === selectedPaper.value.id)
    if (item)
      Object.assign(item, { title: selectedPaper.value.title, status: selectedPaper.value.status })
  } catch (error) {
    pageError.value = apiError(error, '保存失败')
  } finally {
    saving.value = false
  }
}

const saveSection = async (section) => {
  try {
    await axios.patch(`/papers/${selectedPaper.value.id}/sections/${section.id}/`, {
      title: section.title,
      content: section.content,
    })
  } catch (error) {
    pageError.value = apiError(error, '章节保存失败，请重试')
  }
}

const addSection = async () => {
  if (!newSectionTitle.value || !selectedPaper.value) return

  try {
    const res = await axios.post(`/papers/${selectedPaper.value.id}/section/`, {
      title: newSectionTitle.value,
      context: selectedPaper.value.abstract || '',
      generate: false,
    })
    sections.value.push({
      id: res.data.section_id,
      title: newSectionTitle.value,
      content: res.data.content,
    })
    newSectionTitle.value = ''
  } catch (error) {
    pageError.value = apiError(error, '添加章节失败')
  }
}

const generateSection = async () => {
  if (!newSectionTitle.value || !selectedPaper.value) return

  try {
    const res = await axios.post(`/papers/${selectedPaper.value.id}/section/`, {
      title: newSectionTitle.value,
      context: `研究主题：${selectedPaper.value.title}\n摘要：${selectedPaper.value.abstract || ''}`,
      word_count: 500,
    })
    sections.value.push({
      id: res.data.section_id,
      title: newSectionTitle.value,
      content: res.data.content,
    })
    newSectionTitle.value = ''
  } catch (error) {
    pageError.value = apiError(error, 'AI生成章节失败')
  }
}

const deleteSection = async (sectionId) => {
  try {
    await axios.delete(`/papers/${selectedPaper.value.id}/sections/${sectionId}/`)
    sections.value = sections.value.filter((s) => s.id !== sectionId)
  } catch (error) {
    pageError.value = apiError(error, '删除章节失败')
  }
}

const generateAbstract = async () => {
  if (!selectedPaper.value) return

  generatingAbstract.value = true
  try {
    const res = await axios.post(`/papers/${selectedPaper.value.id}/abstract/`, {
      content: sections.value.map((s) => s.content).join('\n'),
    })
    selectedPaper.value.abstract = res.data.abstract
    editingAbstract.value = false
    await savePaper()
  } catch (error) {
    pageError.value = apiError(error, '生成摘要失败')
  } finally {
    generatingAbstract.value = false
  }
}

const polishSection = async (section) => {
  polishing.value = true
  try {
    const res = await axios.post('/polish/', {
      text: section.content,
      style: 'academic',
    })
    section.content = res.data.polished
    await saveSection(section)
  } catch (error) {
    pageError.value = apiError(error, '润色失败')
  } finally {
    polishing.value = false
  }
}

const exportDocx = async () => {
  if (!selectedPaper.value) return

  exporting.value = true
  try {
    // 使用axios下载文件，以便处理错误
    const response = await axios.get(`/papers/${selectedPaper.value.id}/export/`, {
      responseType: 'blob',
    })

    // 检查响应状态
    if (response.status === 200) {
      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url

      // 从Content-Disposition头获取文件名，或使用默认文件名
      let filename = `${selectedPaper.value.title}.docx`
      const contentDisposition = response.headers['content-disposition']
      if (contentDisposition) {
        const matches = /filename="?(.+?)"?$/i.exec(contentDisposition)
        if (matches && matches[1]) {
          filename = matches[1]
        }
      }

      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } else {
      // 尝试解析错误消息
      const text = await response.data.text()
      let errorMsg = '导出失败'
      try {
        const errorJson = JSON.parse(text)
        errorMsg = errorJson.error || errorMsg
      } catch {
        errorMsg = text || errorMsg
      }
      alert(`导出失败: ${errorMsg}`)
    }
  } catch (error) {
    pageError.value = apiError(error, '导出失败')
    if (error.response) {
      // 服务器返回了错误状态码
      let errorMsg = '导出失败'
      try {
        const errorData = error.response.data
        if (typeof errorData === 'object' && errorData.error) {
          errorMsg = errorData.error
        } else if (typeof errorData === 'string') {
          errorMsg = errorData
        }
      } catch {
        // 忽略解析错误
      }
      alert(`导出失败: ${errorMsg}`)
    } else {
      alert('导出失败：网络错误或服务器无响应')
    }
  } finally {
    exporting.value = false
  }
}

const deletePaper = async (paperId) => {
  if (!confirm('确定删除这篇论文吗？')) return

  try {
    await axios.delete(`/papers/${paperId}/delete/`)
    await fetchPapers()
    if (selectedPaper.value?.id === paperId) {
      selectedPaper.value = null
      sections.value = []
    }
  } catch (error) {
    pageError.value = apiError(error, '删除失败')
  }
}

const sendChat = async () => {
  if (!chatInput.value.trim() || chatLoading.value) return

  const userMsg = chatInput.value
  chatMessages.value.push({ role: 'user', content: userMsg })
  chatInput.value = ''
  chatLoading.value = true

  try {
    const res = await axios.post('/agent/', { message: userMsg })
    chatMessages.value.push({ role: 'assistant', content: res.data.response })
  } catch (error) {
    chatMessages.value.push({ role: 'assistant', content: apiError(error, '处理失败') })
  } finally {
    chatLoading.value = false
  }
}

onMounted(() => {
  fetchPapers()
})
</script>

<style scoped>
.paper-writing-page {
  max-width: 1600px;
}
.page-header {
  margin-bottom: 24px;
}
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}
.header-title h1 {
  font-size: 28px;
  margin: 0 0 10px;
}
.subtitle {
  color: var(--text-secondary);
  font-size: 13px;
}
.main-layout {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  gap: 22px;
  min-height: calc(100dvh - 170px);
}
.paper-list,
.editor-area,
.empty-editor {
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 22px;
  min-width: 0;
}
.paper-list h3 {
  font-size: 16px;
  margin-top: 0;
}
.paper-item {
  position: relative;
  padding: 15px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 11px;
  margin-bottom: 12px;
  cursor: pointer;
}
.paper-item.active {
  border-color: var(--success-color);
  background: var(--accent-soft);
}
.paper-title {
  font-size: 13px;
  line-height: 1.8;
  padding-right: 18px;
  overflow-wrap: anywhere;
}
.paper-status {
  font-size: 11px;
  color: var(--success-color);
  margin-top: 8px;
}
.paper-time {
  font-size: 10px;
  color: var(--text-tertiary);
  margin-top: 5px;
}
.delete-paper {
  position: absolute;
  right: 5px;
  top: 10px;
  background: none !important;
  border: 0 !important;
  padding: 5px !important;
}
.empty-editor {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  text-align: center;
}
.empty-editor > .el-icon {
  font-size: 48px;
  color: var(--success-color);
}
.empty-editor h2 {
  font-size: 22px;
}
.empty-editor p,
.empty {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.8;
}
.empty-editor button {
  margin-top: 15px;
}
.editor-header {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.title-input {
  flex: 1;
  font-size: 20px !important;
  font-weight: 600;
}
.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
button {
  border: 1px solid var(--border-color);
  background: var(--accent-soft);
  color: var(--success-color);
  border-radius: 9px;
  padding: 10px 14px;
  font-size: 12px;
}
.new-btn {
  background: #326bd6;
  color: white;
  padding: 12px 20px;
}
.abstract-area {
  display: grid;
  gap: 12px;
  margin-top: 24px;
  font-size: 13px;
}
.section-card {
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  margin-top: 22px;
}
.section-header {
  display: flex;
  gap: 10px;
  padding: 12px;
  background: var(--bg-primary);
}
input,
textarea {
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 9px;
  min-width: 0;
  color: var(--text-primary);
  background: var(--bg-secondary);
  font-size: 13px;
}
.section-title {
  flex: 1;
}
.add-section {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 22px;
}
.ai-assistant {
  margin-top: 25px;
  border-top: 1px solid var(--border-color);
  padding-top: 20px;
}
.chat-messages {
  max-height: 280px;
  overflow: auto;
}
.message {
  white-space: pre-wrap;
  line-height: 1.8;
  font-size: 13px;
  background: var(--bg-primary);
  padding: 13px;
  border-radius: 10px;
  margin-bottom: 10px;
}
.message.user {
  background: var(--accent-soft);
}
.chat-input {
  display: flex;
  gap: 10px;
}
.chat-input input {
  flex: 1;
}
.modal {
  position: fixed;
  inset: 0;
  background: #14264088;
  z-index: 200;
  display: grid;
  place-items: center;
  padding: 20px;
}
.modal-content {
  width: min(500px, 100%);
  background: var(--bg-secondary);
  border-radius: 18px;
  padding: 28px;
  display: grid;
  gap: 18px;
}
.modal-content h3 {
  margin: 0;
}
.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
:deep(.ql-toolbar),
:deep(.ql-container) {
  border-color: var(--border-color);
}
:deep(.ql-editor) {
  min-height: 180px;
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.9;
}
@media (max-width: 760px) {
  .main-layout {
    grid-template-columns: 1fr;
  }
  .paper-list {
    max-height: 280px;
    overflow: auto;
  }
  .empty-editor {
    min-height: 380px;
  }
  .editor-area {
    padding: 16px;
  }
  .section-header {
    flex-wrap: wrap;
  }
  .section-title {
    width: 100%;
  }
  .header-content {
    gap: 12px;
  }
  .title-input {
    width: 100%;
  }
}
</style>
