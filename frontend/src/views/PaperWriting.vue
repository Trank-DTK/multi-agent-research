<!-- 论文写作页面 -->
<template>
  <div class="paper-writing-page">
    <div class="header">
      <h2>✍️ 论文写作</h2>
      <button @click="showNewPaper = true" class="new-btn">+ 新建论文</button>
    </div>
    
    <!-- 新建论文弹窗 -->
    <div v-if="showNewPaper" class="modal">
      <div class="modal-content">
        <h3>新建论文</h3>
        <input v-model="newPaperTitle" placeholder="论文标题" />
        <textarea v-model="newPaperTopic" placeholder="研究主题（可选，用于生成大纲）" rows="3"></textarea>
        <div class="modal-buttons">
          <button @click="createPaper" :disabled="creating">创建</button>
          <button @click="showNewPaper = false">取消</button>
        </div>
      </div>
    </div>
    
    <div class="main-layout">
      <!-- 左侧：论文列表 -->
      <div class="paper-list">
        <h3>我的论文</h3>
        <div v-for="paper in papers" :key="paper.id" 
             :class="['paper-item', { active: selectedPaper?.id === paper.id }]"
             @click="selectPaper(paper.id)">
          <div class="paper-title">{{ paper.title }}</div>
          <div class="paper-status">{{ getStatusText(paper.status) }}</div>
          <div class="paper-time">{{ formatDate(paper.updated_at) }}</div>
          <button @click.stop="deletePaper(paper.id)" class="delete-paper">🗑️</button>
        </div>
        <div v-if="papers.length === 0" class="empty">
          暂无论文，点击上方按钮创建
        </div>
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
          <label>摘要</label>
          <textarea v-model="selectedPaper.abstract" rows="4" @blur="savePaper"></textarea>
        </div>
        
        <!-- 章节列表 -->
        <div class="sections">
          <div v-for="(section, idx) in sections" :key="section.id" class="section-card">
            <div class="section-header">
              <input v-model="section.title" class="section-title" @blur="saveSection(section)" />
              <button @click="polishSection(section)" class="polish-btn" :disabled="polishing">润色</button>
              <button @click="deleteSection(section.id)" class="delete-section">×</button>
            </div>
            <div class="section-content">
              <QuillEditor v-model:content="section.content" contentType="html" @blur="saveSection(section)" />
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
              {{ msg.content }}
            </div>
          </div>
          <div class="chat-input">
            <input v-model="chatInput" @keydown.enter="sendChat" placeholder="问关于写作的问题..." />
            <button @click="sendChat" :disabled="chatLoading">发送</button>
          </div>
        </div>
      </div>
      
      <!-- 未选择论文时的占位 -->
      <div v-else class="empty-editor">
        <p>请选择或创建一篇论文</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '../axios'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'

const papers = ref([])
const selectedPaper = ref(null)
const sections = ref([])
const showNewPaper = ref(false)
const newPaperTitle = ref('')
const newPaperTopic = ref('')
const creating = ref(false)
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
    const res = await axios.get('/writing/papers/')
    papers.value = res.data
  } catch (error) {
    console.error('获取论文列表失败', error)
  }
}

const createPaper = async () => {
  if (!newPaperTitle.value) return
  
  creating.value = true
  try {
    const res = await axios.post('/writing/papers/create/', {
      title: newPaperTitle.value,
      topic: newPaperTopic.value
    })
    showNewPaper.value = false
    newPaperTitle.value = ''
    newPaperTopic.value = ''
    await fetchPapers()
    await selectPaper(res.data.id)
  } catch (error) {
    console.error('创建论文失败', error)
  } finally {
    creating.value = false
  }
}

const selectPaper = async (paperId) => {
  try {
    const res = await axios.get(`/writing/papers/${paperId}/`)
    selectedPaper.value = res.data
    sections.value = res.data.sections || []
  } catch (error) {
    console.error('加载论文失败', error)
  }
}

const savePaper = async () => {
  if (!selectedPaper.value) return
  
  saving.value = true
  try {
    await axios.put(`/writing/papers/${selectedPaper.value.id}/`, {
      title: selectedPaper.value.title,
      abstract: selectedPaper.value.abstract,
      keywords: selectedPaper.value.keywords,
      content: selectedPaper.value.content,
      status: selectedPaper.value.status
    })
  } catch (error) {
    console.error('保存失败', error)
  } finally {
    saving.value = false
  }
}

const saveSection = async (section) => {
  // 章节保存逻辑
  await savePaper()
}

const addSection = async () => {
  if (!newSectionTitle.value || !selectedPaper.value) return
  
  try {
    const res = await axios.post(`/writing/papers/${selectedPaper.value.id}/section/`, {
      title: newSectionTitle.value,
      context: selectedPaper.value.abstract || ''
    })
    sections.value.push({
      id: res.data.section_id,
      title: newSectionTitle.value,
      content: res.data.content
    })
    newSectionTitle.value = ''
  } catch (error) {
    console.error('添加章节失败', error)
  }
}

const generateSection = async () => {
  if (!newSectionTitle.value || !selectedPaper.value) return
  
  try {
    const res = await axios.post(`/writing/papers/${selectedPaper.value.id}/section/`, {
      title: newSectionTitle.value,
      context: `研究主题：${selectedPaper.value.title}\n摘要：${selectedPaper.value.abstract || ''}`,
      word_count: 500
    })
    sections.value.push({
      id: res.data.section_id,
      title: newSectionTitle.value,
      content: res.data.content
    })
    newSectionTitle.value = ''
  } catch (error) {
    console.error('AI生成章节失败', error)
  }
}

const deleteSection = async (sectionId) => {
  sections.value = sections.value.filter(s => s.id !== sectionId)
  await savePaper()
}

const generateAbstract = async () => {
  if (!selectedPaper.value) return
  
  generatingAbstract.value = true
  try {
    const res = await axios.post(`/writing/papers/${selectedPaper.value.id}/abstract/`, {
      content: sections.value.map(s => s.content).join('\n')
    })
    selectedPaper.value.abstract = res.data.abstract
    await savePaper()
  } catch (error) {
    console.error('生成摘要失败', error)
  } finally {
    generatingAbstract.value = false
  }
}

const polishSection = async (section) => {
  polishing.value = true
  try {
    const res = await axios.post('/writing/polish/', {
      text: section.content,
      style: 'academic'
    })
    section.content = res.data.polished
    await saveSection(section)
  } catch (error) {
    console.error('润色失败', error)
  } finally {
    polishing.value = false
  }
}

const exportDocx = async () => {
  if (!selectedPaper.value) return
  
  exporting.value = true
  try {
    window.open(`/api/writing/papers/${selectedPaper.value.id}/export/`, '_blank')
  } catch (error) {
    console.error('导出失败', error)
  } finally {
    exporting.value = false
  }
}

const deletePaper = async (paperId) => {
  if (!confirm('确定删除这篇论文吗？')) return
  
  try {
    await axios.delete(`/writing/papers/${paperId}/delete/`)
    await fetchPapers()
    if (selectedPaper.value?.id === paperId) {
      selectedPaper.value = null
      sections.value = []
    }
  } catch (error) {
    console.error('删除失败', error)
  }
}

const sendChat = async () => {
  if (!chatInput.value.trim()) return
  
  const userMsg = chatInput.value
  chatMessages.value.push({ role: 'user', content: userMsg })
  chatInput.value = ''
  chatLoading.value = true
  
  try {
    const res = await axios.post('/writing/agent/', { message: userMsg })
    chatMessages.value.push({ role: 'assistant', content: res.data.response })
  } catch (error) {
    chatMessages.value.push({ role: 'assistant', content: '抱歉，处理失败' })
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
  max-width: 1400px;
  margin: 20px auto;
  padding: 0 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.new-btn {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.main-layout {
  display: flex;
  gap: 20px;
  min-height: 70vh;
}

.paper-list {
  width: 260px;
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 15px;
}

.paper-list h3 {
  margin-bottom: 15px;
}

.paper-item {
  padding: 10px;
  margin-bottom: 8px;
  background-color: white;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  border: 1px solid transparent;
}

.paper-item:hover {
  border-color: #42b983;
}

.paper-item.active {
  border-color: #42b983;
  background-color: #e8f5e9;
}

.paper-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.paper-status {
  font-size: 11px;
  color: #999;
}

.paper-time {
  font-size: 10px;
  color: #ccc;
}

.delete-paper {
  position: absolute;
  top: 8px;
  right: 8px;
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0;
}

.paper-item:hover .delete-paper {
  opacity: 1;
}

.editor-area {
  flex: 1;
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e0e0e0;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.title-input {
  font-size: 24px;
  font-weight: bold;
  border: none;
  width: 60%;
  padding: 8px;
}

.title-input:focus {
  outline: none;
  border-bottom: 1px solid #42b983;
}

.actions button {
  padding: 6px 12px;
  margin-left: 10px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.abstract-area {
  margin-bottom: 20px;
}

.abstract-area label {
  font-weight: bold;
  display: block;
  margin-bottom: 8px;
}

.abstract-area textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
}

.sections {
  margin-bottom: 20px;
}

.section-card {
  margin-bottom: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  background-color: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.section-title {
  flex: 1;
  font-size: 18px;
  font-weight: bold;
  border: none;
  background: transparent;
  padding: 5px;
}

.section-title:focus {
  outline: none;
}

.polish-btn, .delete-section {
  margin-left: 10px;
  padding: 4px 10px;
  background-color: #ff9800;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.delete-section {
  background-color: #f44336;
}

.section-content {
  padding: 15px;
  min-height: 200px;
}

.add-section {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.add-section input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.add-section button {
  padding: 8px 16px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.ai-assistant {
  margin-top: 30px;
  border-top: 1px solid #e0e0e0;
  padding-top: 20px;
}

.ai-assistant h4 {
  margin-bottom: 15px;
}

.chat-messages {
  height: 200px;
  overflow-y: auto;
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 10px;
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
  gap: 10px;
}

.chat-input input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.chat-input button {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.empty-editor {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f9f9f9;
  border-radius: 8px;
  color: #999;
}

.empty {
  text-align: center;
  color: #999;
  padding: 20px;
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
</style>