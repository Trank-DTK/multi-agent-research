<!-- frontend/src/views/AgentChat.vue -->
<template>
  <div class="agent-chat">
    <div class="chat-header">
      <h2>🤖 智能体助手</h2>
      <p>支持：时间查询、随机数、计算器</p>
    </div>
    
    <div class="messages" ref="messagesContainer">
      <div v-for="(msg, idx) in messages" :key="idx" 
           :class="['message', msg.role]">
        <div class="avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
        <div class="content">{{ msg.content }}</div>
      </div>
      <div v-if="loading" class="message assistant">
        <div class="avatar">🤖</div>
        <div class="content typing">思考中...</div>
      </div>
    </div>
    
    <div class="input-area">
      <textarea 
        v-model="inputMessage" 
        @keydown.enter.prevent="sendMessage"
        placeholder="输入你的问题，我可以：计算、查时间、生成随机数..."
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
  { role: 'assistant', content: '你好！我是智能体助手，我可以：\n- 查询当前时间\n- 计算数学表达式（如 123*456）\n- 生成随机数（如 1到100之间的随机数）\n- 记住我们的对话上下文\n请问有什么可以帮你的？' }
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
    const response = await axios.post('/api/agent/chat/', {
      message: userMessage,
      conversation_id: conversationId.value
    })
    
    messages.value.push({ 
      role: 'assistant', 
      content: response.data.response 
    })
    
    // 保存会话ID
    if (!conversationId.value) {
      conversationId.value = response.data.conversation_id
    }
    
  } catch (error) {
    console.error('Agent出错:', error)
    messages.value.push({ 
      role: 'assistant', 
      content: '抱歉，我遇到了一些问题。请检查：\n1. Ollama是否在运行\n2. 后端服务是否正常' 
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.agent-chat {
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
  background-color: #42b983;
  color: white;
  text-align: center;
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
</style>