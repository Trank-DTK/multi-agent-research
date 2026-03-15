<template>
  <div class="chat-container">
    <!-- 侧边栏：历史会话列表 -->
    <div class="sidebar" v-if="showSidebar">
      <div class="sidebar-header">
        <h3>历史对话</h3>
        <button @click="newConversation" class="new-chat-btn">+ 新对话</button>
      </div>
      <div class="conversation-list">
        <div 
          v-for="conv in conversations" 
          :key="conv.id"
          :class="['conversation-item', { active: currentConversationId === conv.id }]"
          @click="loadConversation(conv.id)"
        >
          <div class="conv-title">{{ conv.title }}</div>
          <div class="conv-time">{{ formatTime(conv.updated_at) }}</div>
          <button @click.stop="deleteConversation(conv.id)" class="delete-btn">🗑️</button>
        </div>
        <div v-if="conversations.length === 0" class="empty-list">
          暂无历史对话
        </div>
      </div>
    </div>
    
    <!-- 主聊天区域 -->
    <div class="chat-main">
      <!-- 切换侧边栏按钮（移动端） -->
      <button @click="showSidebar = !showSidebar" class="toggle-sidebar">
        ☰
      </button>
      
      <div class="messages" ref="messagesContainer">
        <div v-for="(msg, index) in messages" :key="index" 
             :class="['message', msg.role]">
          <div class="avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
          <div class="content">{{ msg.content }}</div>
        </div>
        <div v-if="loading" class="message assistant">
          <div class="avatar">🤖</div>
          <div class="content typing">正在输入...</div>
        </div>
      </div>
      
      <div class="input-area">
        <textarea 
          v-model="inputMessage" 
          @keydown.enter.prevent="sendMessage"
          placeholder="输入你的问题..."
          rows="2"
        ></textarea>
        <button @click="sendMessage" :disabled="!inputMessage || loading">
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from '@/axios'

// 状态变量
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const conversations = ref([])
const currentConversationId = ref(null)
const showSidebar = ref(true)

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
  } catch (error) {
    console.error('获取对话列表失败:', error)
  }
}

// 加载指定对话
const loadConversation = async (convId) => {
  try {
    const response = await axios.get(`/chat/conversations/${convId}/`)
    messages.value = response.data
    currentConversationId.value = convId
    await scrollToBottom()
  } catch (error) {
    console.error('加载对话失败:', error)
  }
}

// 新建对话
const newConversation = () => {
  messages.value = []
  currentConversationId.value = null
  inputMessage.value = ''
}

// 删除对话
const deleteConversation = async (convId) => {
  if (!confirm('确定要删除这个对话吗？')) return

  try {
    // 先清空当前显示的消息
    if (currentConversationId.value === convId) {
      messages.value = []
    }

    // 删除后端数据
    await axios.delete(`/chat/conversations/${convId}/delete/`)

    // 等待一小段时间确保后端删除完成
    await new Promise(resolve => setTimeout(resolve, 100))

    // 刷新对话列表
    await fetchConversations()

    // 如果删除的是当前对话，清空当前状态
    if (currentConversationId.value === convId) {
      currentConversationId.value = null
      inputMessage.value = ''
    }
  } catch (error) {
    console.error('删除对话失败:', error)
    // 删除失败时刷新列表以显示最新状态
    await fetchConversations()
  }
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return

  const userMessage = inputMessage.value
  messages.value.push({ role: 'user', content: userMessage })
  inputMessage.value = ''
  scrollToBottom()

  loading.value = true

  try {
    const response = await axios.post('/chat/', {
      sender: 'user',
      message: userMessage,
      conversation_id: currentConversationId.value
    })

    messages.value.push({
      role: 'assistant',
      content: response.data.response
    })

    // 更新当前会话ID（如果是新会话）
    if (!currentConversationId.value) {
      currentConversationId.value = response.data.conversation_id
      await fetchConversations()
    }

  } catch (error) {
    console.error('聊天出错:', error)
    messages.value.push({
      role: 'assistant',
      content: '抱歉，我遇到了一些问题，请稍后再试。'
    })
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
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.sidebar {
  width: 260px;
  background-color: #f5f5f5;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
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
  background-color: #42b983;
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
  background-color: white;
  border-radius: 4px;
  cursor: pointer;
  position: relative;
  display: flex;
  flex-direction: column;
  border: 1px solid transparent;
}

.conversation-item:hover {
  background-color: #e8f5e9;
}

.conversation-item.active {
  background-color: #e8f5e9;
  border-color: #42b983;
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
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #f9f9f9;
  position: relative;
}

.toggle-sidebar {
  display: none;
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 10;
  padding: 5px 10px;
  background-color: #42b983;
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
  background-color: #42b983;
  color: white;
  margin-left: 10px;
}

.message.assistant .content {
  background-color: white;
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
  max-width: 70%;
  padding: 10px 15px;
  border-radius: 18px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
  line-height: 1.5;
  word-wrap: break-word;
}

.input-area {
  display: flex;
  padding: 15px;
  background-color: white;
  border-top: 1px solid #e0e0e0;
}

textarea {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: none;
  margin-right: 10px;
  font-family: inherit;
}

button {
  padding: 0 20px;
  background-color: #42b983;
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
</style>