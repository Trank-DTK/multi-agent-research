<!-- 文献助手聊天页面 -->
<template>
  <div class="literature-chat">
    <div class="chat-header">
      <button class="back-btn" @click="$router.push('/dashboard')">
        <span class="btn-icon">←</span>
        <span class="btn-text">返回主页</span>
      </button>
      <div class="header-content">
        <h2>📖 文献助手</h2>
        <p>我可以帮你在已上传的文献中检索信息、总结内容</p>
      </div>
      <button @click="resetChat" class="reset-btn">重置对话</button>
    </div>
    
    <div class="messages" ref="messagesContainer">
      <div v-for="(msg, idx) in messages" :key="idx" 
           :class="['message', msg.role]">
        <div class="avatar">{{ msg.role === 'user' ? '👤' : '📚' }}</div>
        <div class="content">{{ msg.content }}</div>
      </div>
      <div v-if="loading" class="message assistant">
        <div class="avatar">📚</div>
        <div class="content typing">正在检索文献...</div>
      </div>
    </div>
    
    <div class="input-area">
      <textarea 
        v-model="inputMessage" 
        @keydown.enter.prevent="sendMessage"
        placeholder="输入你的问题，例如：帮我找一下关于深度学习的文献..."
        rows="2"
      ></textarea>
      <button @click="sendMessage" :disabled="!inputMessage || loading">
        发送
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from '../axios'

const messages = ref([
  { role: 'assistant', content: '你好！我是文献助手。请先在上方"文献库管理"上传PDF文献，然后我可以帮你：\n- 检索文献中的相关内容\n- 总结指定文献\n- 回答关于文献的问题' }
])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const conversationId = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return
  
  const userMessage = inputMessage.value
  messages.value.push({ role: 'user', content: userMessage })
  inputMessage.value = ''
  scrollToBottom()
  
  loading.value = true
  
  try {
    const response = await axios.post('/literature/chat/', {
      message: userMessage,
      conversation_id: conversationId.value
    })
    
    messages.value.push({ 
      role: 'assistant', 
      content: response.data.response 
    })
    
  } catch (error) {
    console.error('文献助手出错:', error)
    messages.value.push({ 
      role: 'assistant', 
      content: '抱歉，我遇到了一些问题。请检查：\n1. 是否已上传文献\n2. 后端服务是否正常' 
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

const resetChat = async () => {
  try {
    await axios.post('/literature/reset/')
    messages.value = [
      { role: 'assistant', content: '对话已重置！有什么可以帮你的？' }
    ]
    conversationId.value = null
  } catch (error) {
    console.error('重置失败', error)
  }
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.literature-chat {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 100px);
  max-width: 800px;
  margin: 0 auto;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f9f9f9;
}

.chat-header {
  padding: 15px;
  background-color: #1890ff;
  color: white;
  text-align: center;
  position: relative;
}

.back-btn {
  position: absolute;
  top: 15px;
  left: 15px;
  padding: 5px 12px;
  background-color: rgba(255,255,255,0.2);
  color: white;
  border: 1px solid white;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background-color: rgba(255,255,255,0.3);
  transform: translateX(-2px);
}

.btn-icon {
  font-size: 12px;
}

.header-content {
  padding: 0 100px; /* 为左右按钮留出空间 */
}

.chat-header h2 {
  margin: 0;
  font-size: 20px;
}

.chat-header p {
  margin: 5px 0 0;
  font-size: 12px;
  opacity: 0.9;
}

.reset-btn {
  position: absolute;
  right: 15px;
  top: 15px;
  padding: 5px 12px;
  background-color: rgba(255,255,255,0.2);
  color: white;
  border: 1px solid white;
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
  background-color: #1890ff;
  color: white;
}

.message.assistant .content {
  background-color: white;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e0e0e0;
  margin-right: 10px;
  margin-left: 10px;
}

.message.user .avatar {
  order: 2;
  margin-right: 0;
  margin-left: 10px;
}

.content {
  max-width: 70%;
  padding: 10px 15px;
  border-radius: 18px;
  line-height: 1.5;
  white-space: pre-wrap;
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
  background-color: #1890ff;
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
</style>