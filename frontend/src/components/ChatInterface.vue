<template>
  <div class="chat-container">
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
</template>

<script setup>
import { ref, nextTick } from 'vue'
import axios from '@/utils/axios'

const messages = ref([
  { role: 'assistant', content: '你好！我是你的科研助手，有什么可以帮你的吗？' }
])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
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
    // 调用后端API
    const response = await axios.post('/chat/', {
      message: userMessage
    })
    
    messages.value.push({ 
      role: 'assistant', 
      content: response.data.response 
    })
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
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 500px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f9f9f9;
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