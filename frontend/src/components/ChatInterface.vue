<template>
  <div class="chat-container">
    <!-- 侧边栏：历史会话列表 -->
    <div class="sidebar" :class="{ show: showSidebar }" v-if="showSidebar">
      <div class="sidebar-header">
        <h3>历史对话</h3>
        <button class="close-history" aria-label="关闭历史对话" @click="showSidebar = false">
          ×
        </button>
        <button
          @click="newConversation"
          class="new-chat-btn"
          :disabled="loading || conversationLoading"
        >
          + 新对话
        </button>
      </div>
      <div class="conversation-list">
        <div
          v-for="conv in conversations"
          :key="conv.id"
          :class="['conversation-item', { active: currentConversationId === conv.id }]"
          tabindex="0"
          role="button"
          :aria-disabled="loading || conversationLoading"
          @keydown.enter.self="loadConversation(conv.id)"
          @keydown.space.self.prevent="loadConversation(conv.id)"
          @click="loadConversation(conv.id)"
        >
          <div class="conv-title">{{ conv.title }}</div>
          <div class="conv-time">{{ formatTime(conv.updated_at) }}</div>
          <button
            @click.stop="deleteConversation(conv.id)"
            class="delete-btn"
            :disabled="loading || conversationLoading"
            aria-label="删除对话"
          >
            🗑️
          </button>
        </div>
        <div v-if="conversations.length === 0" class="empty-list">暂无历史对话</div>
      </div>
    </div>

    <!-- 主聊天区域 -->
    <div class="chat-main">
      <!-- 切换侧边栏按钮（移动端） -->
      <button
        @click="showSidebar = !showSidebar"
        class="toggle-sidebar"
        aria-label="切换历史对话"
        :aria-expanded="showSidebar"
      >
        ☰
      </button>

      <div class="messages" ref="messagesContainer">
        <div v-if="!messages.length && !loading" class="chat-empty">
          <el-icon><ChatDotRound /></el-icon>
          <h2>一起探索你的研究问题</h2>
          <p>讨论一个想法、梳理实验思路，或请助手解释一个概念。</p>
        </div>
        <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.role]">
          <div class="avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
          <div class="content">{{ msg.content }}</div>
        </div>
        <div v-if="loading && !messages.at(-1)?.content" class="message assistant">
          <div class="avatar">🤖</div>
          <div class="content typing">正在输入...</div>
        </div>
      </div>

      <p v-if="requestError" role="alert" class="request-error">{{ requestError }}</p>
      <div class="input-area">
        <textarea
          v-model="inputMessage"
          @keydown.enter="handleEnter"
          aria-label="输入研究问题"
          placeholder="输入研究问题，Enter 发送，Shift+Enter 换行"
          rows="2"
        ></textarea>
        <button
          @click="sendMessage"
          :disabled="!inputMessage.trim() || loading || conversationLoading"
        >
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import axios from '@/axios'
import { streamChat } from '@/utils/streamChat'
import { apiError } from '@/utils/apiError'
let streamController
onBeforeUnmount(() => streamController?.abort())

// 状态变量
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const conversations = ref([])
const currentConversationId = ref(null)
const showSidebar = ref(window.innerWidth > 768)
const requestError = ref('')
const conversationLoading = ref(false)
const handleEnter = (event) => {
  if (event.isComposing || event.keyCode === 229 || event.shiftKey) return
  event.preventDefault()
  sendMessage()
}

// 格式化时间
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date

  // 今天
  if (diff < 24 * 60 * 60 * 1000 && date.getDate() === now.getDate()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  // 昨天
  if (diff < 48 * 60 * 60 * 1000 && date.getDate() === now.getDate() - 1) {
    return '昨天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  // 更早
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

// 获取对话列表
const fetchConversations = async () => {
  try {
    const response = await axios.get('/chat/conversations/')
    conversations.value = response.data
  } catch {
    requestError.value = '历史对话加载失败，请刷新后重试。'
  }
}

// 加载指定对话
const loadConversation = async (convId) => {
  if (loading.value || conversationLoading.value) return
  conversationLoading.value = true
  requestError.value = ''
  try {
    const response = await axios.get(`/chat/conversations/${convId}/`)
    messages.value = response.data
    if (window.innerWidth <= 768) showSidebar.value = false
    currentConversationId.value = convId
    await scrollToBottom()
  } catch {
    requestError.value = '加载对话失败，请重试。'
  } finally {
    conversationLoading.value = false
  }
}

// 新建对话
const newConversation = () => {
  if (loading.value || conversationLoading.value) return
  requestError.value = ''
  if (window.innerWidth <= 768) showSidebar.value = false
  messages.value = []
  currentConversationId.value = null
  inputMessage.value = ''
}

// 删除对话
const deleteConversation = async (convId) => {
  if (loading.value || conversationLoading.value) return
  if (!confirm('确定要删除这个对话吗？')) return

  conversationLoading.value = true
  try {
    // 删除后端数据
    await axios.delete(`/chat/conversations/${convId}/delete/`)

    // 刷新对话列表
    await fetchConversations()

    // 如果删除的是当前对话，清空当前状态
    if (currentConversationId.value === convId) {
      messages.value = []
      currentConversationId.value = null
      inputMessage.value = ''
    }
  } catch {
    requestError.value = '删除失败，对话已保留，请重试。'
    // 删除失败时刷新列表以显示最新状态
    await fetchConversations()
  } finally {
    conversationLoading.value = false
  }
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value || conversationLoading.value) return
  requestError.value = ''

  const userMessage = inputMessage.value
  messages.value.push({ role: 'user', content: userMessage })
  inputMessage.value = ''
  scrollToBottom()

  loading.value = true

  try {
    streamController = new AbortController()
    messages.value.push({ role: 'assistant', content: '' })
    const answer = messages.value.at(-1)
    await streamChat(
      '/chat/stream/',
      {
        sender: 'user',
        message: userMessage,
        conversation_id: currentConversationId.value,
      },
      (event) => {
        if (event.conversation_id) currentConversationId.value = event.conversation_id
        if (event.token) {
          answer.content += event.token
          scrollToBottom()
        }
        if (event.message_id) answer.id = event.message_id
      },
      streamController.signal,
    )
    await fetchConversations()
  } catch (error) {
    if (error.name !== 'AbortError') {
      requestError.value = apiError(error)
      if (!inputMessage.value) inputMessage.value = userMessage
    }
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 组件挂载时获取对话列表
onMounted(() => {
  fetchConversations()
})
</script>

<style scoped>
.chat-container {
  display: flex;
  height: 600px;
  border: 1px solid var(--chat-border-color);
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.sidebar {
  width: 260px;
  background-color: var(--bg-primary);
  border-right: 1px solid var(--chat-border-color);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 15px;
  border-bottom: 1px solid var(--chat-border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
}

.new-chat-btn {
  padding: 5px 10px;
  background-color: #326bd6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.conversation-item {
  padding: 10px;
  margin-bottom: 5px;
  background-color: var(--bg-secondary);
  border-radius: 4px;
  cursor: pointer;
  position: relative;
  display: flex;
  flex-direction: column;
  border: 1px solid transparent;
}

.conversation-item:hover {
  background-color: var(--accent-soft);
}

.conversation-item.active {
  background-color: var(--accent-soft);
  border-color: #1890ff;
}

.conv-title {
  font-weight: 500;
  font-size: 14px;
  margin-bottom: 5px;
  padding-right: 25px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conv-time {
  font-size: 12px;
  color: #999;
}

.delete-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
}

.conversation-item:hover .delete-btn {
  opacity: 1;
}

.empty-list {
  text-align: center;
  color: #999;
  padding: 20px;
}

.chat-main {
  min-width: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-secondary);
  position: relative;
}

.toggle-sidebar {
  display: none;
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 10;
  padding: 5px 10px;
  background-color: #326bd6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.message {
  display: flex;
  margin-bottom: 15px;
}

.message.user {
  justify-content: flex-end;
}

.message.user .content {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  background-color: #326bd6;
  color: white;
  margin-left: 10px;
}

.message.assistant .content {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  background-color: var(--bg-secondary);
  margin-right: 10px;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  background-color: #f0f0f0;
}

.content {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  max-width: 70%;
  padding: 10px 15px;
  border-radius: 18px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  word-wrap: break-word;
}

.input-area {
  display: flex;
  padding: 15px;
  background-color: var(--bg-secondary);
  border-top: 1px solid var(--chat-border-color);
}

textarea {
  flex: 1;
  padding: 10px;
  border: 1px solid var(--chat-border-color);
  border-radius: 4px;
  resize: none;
  margin-right: 10px;
  font-family: inherit;
}

button {
  padding: 0 20px;
  background-color: #326bd6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.typing {
  color: #999;
  font-style: italic;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .sidebar {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    z-index: 20;
    display: none;
  }

  .sidebar.show {
    display: flex;
  }

  .toggle-sidebar {
    display: block;
  }
}
.chat-empty {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: var(--text-secondary);
  padding: 30px;
}
.chat-empty .el-icon {
  font-size: 38px;
  color: var(--success-color);
}
.chat-empty h2 {
  font-size: 20px;
  color: var(--text-primary);
}
.chat-empty p {
  font-size: 13px;
  line-height: 1.8;
}
.request-error {
  padding: 10px 16px;
  color: var(--error-color);
  font-size: 13px;
}
.close-history {
  display: none;
}
.sidebar {
  flex-shrink: 0;
}
.messages {
  min-height: 0;
}
.input-area textarea {
  min-width: 0;
}
.chat-container {
  height: clamp(380px, calc(100dvh - 290px), 680px);
  min-height: 380px;
}
.conversation-item:focus-within .delete-btn {
  opacity: 1;
}
@media (max-width: 768px) {
  .close-history {
    display: block;
  }
  .messages {
    padding-top: 50px;
  }
  .delete-btn {
    opacity: 1;
  }
  .sidebar {
    width: min(280px, 100%);
  }
  .content {
    max-width: 85%;
  }
}
</style>
