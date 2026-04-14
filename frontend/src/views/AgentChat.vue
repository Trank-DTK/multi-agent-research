<!-- frontend/src/views/AgentChat.vue -->
<template>
  <div class="agent-chat-page">
    <div class="page-header">
      <button class="back-btn" @click="$router.push('/dashboard')">
        <span class="btn-icon">←</span>
        <span class="btn-text">返回主页</span>
      </button>
      <div class="header-content">
        <h1>🤖 智能体助手</h1>
        <p class="subtitle">支持时间查询、数学计算、随机数生成等实用功能</p>
      </div>
    </div>

    <div class="chat-container">
      <div class="chat-info">
        <div class="info-card">
          <div class="info-icon">⏰</div>
          <div class="info-content">
            <h3>时间查询</h3>
            <p>获取当前日期和时间信息</p>
          </div>
        </div>
        <div class="info-card">
          <div class="info-icon">🧮</div>
          <div class="info-content">
            <h3>数学计算</h3>
            <p>支持复杂的数学表达式计算</p>
          </div>
        </div>
        <div class="info-card">
          <div class="info-icon">🎲</div>
          <div class="info-content">
            <h3>随机数生成</h3>
            <p>生成指定范围内的随机数</p>
          </div>
        </div>
      </div>

      <div class="chat-wrapper">
        <div class="messages" ref="messagesContainer">
          <div v-for="(msg, idx) in messages" :key="idx"
               :class="['message', msg.role]">
            <div class="message-avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
            <div class="message-bubble">
              <div class="message-content">{{ msg.content }}</div>
              <div class="message-time">{{ formatTime() }}</div>
            </div>
          </div>
          <div v-if="loading" class="message assistant">
            <div class="message-avatar">🤖</div>
            <div class="message-bubble">
              <div class="typing-indicator">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="input-area">
          <div class="input-wrapper">
            <textarea
              v-model="inputMessage"
              @keydown.enter.prevent="sendMessage"
              placeholder="输入你的问题，例如：123*456、当前时间、1-100之间的随机数..."
              rows="2"
            ></textarea>
            <div class="input-actions">
              <button class="send-btn" @click="sendMessage" :disabled="!inputMessage || loading">
                <span class="btn-text">发送</span>
                <span class="btn-icon">↑</span>
              </button>
            </div>
          </div>
        </div>
      </div>
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

const formatTime = () => {
  const now = new Date()
  return now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return

  const userMessage = inputMessage.value
  messages.value.push({ role: 'user', content: userMessage })
  inputMessage.value = ''
  scrollToBottom()

  loading.value = true

  try {
    const response = await axios.post('/agent/chat/', {
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
.agent-chat-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px;
}

.page-header {
  position: relative;
  margin-bottom: 40px;
}

.back-btn {
  position: absolute;
  top: 0;
  left: 0;
  padding: 10px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  z-index: 10;
}

.back-btn:hover {
  background: var(--bg-tertiary);
  border-color: var(--success-color);
  transform: translateX(-4px);
}

.btn-icon {
  font-size: 16px;
}

.header-content {
  text-align: center;
}

.page-header h1 {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 12px;
  color: var(--text-primary);
  background: linear-gradient(135deg, var(--success-color) 0%, #36a1ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 16px;
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

.chat-container {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 32px;
}

.chat-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.info-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: var(--success-color);
}

.info-icon {
  font-size: 32px;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, var(--success-color) 0%, #36a1ff 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.info-content h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
  color: var(--text-primary);
}

.info-content p {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.chat-wrapper {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 600px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background-color: var(--bg-secondary);
}

.message {
  display: flex;
  margin-bottom: 20px;
}

.message.user {
  justify-content: flex-end;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--success-color) 0%, #36a1ff 100%);
  color: white;
  font-size: 18px;
  margin-right: 12px;
  flex-shrink: 0;
}

.message.user .message-avatar {
  order: 2;
  margin-right: 0;
  margin-left: 12px;
  background: linear-gradient(135deg, #36a1ff 0%, var(--success-color) 100%);
}

.message-bubble {
  max-width: 70%;
  background: white;
  border-radius: 20px;
  padding: 16px 20px;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.message.user .message-bubble {
  background: linear-gradient(135deg, var(--success-color) 0%, #36a1ff 100%);
  color: white;
}

.message-content {
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 14px;
}

.message-time {
  font-size: 11px;
  color: var(--text-tertiary);
  margin-top: 8px;
  text-align: right;
}

.message.user .message-time {
  color: rgba(255, 255, 255, 0.8);
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--text-tertiary);
  animation: typing 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0.7); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

.input-area {
  border-top: 1px solid var(--border-color);
  background: white;
  padding: 20px;
}

.input-wrapper {
  display: flex;
  gap: 16px;
  align-items: flex-end;
}

textarea {
  flex: 1;
  padding: 16px;
  border: 1px solid var(--border-color);
  border-radius: 16px;
  resize: none;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
  transition: all 0.3s ease;
  background: var(--bg-tertiary);
}

textarea:focus {
  outline: none;
  border-color: var(--success-color);
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
  background: white;
}

.input-actions {
  display: flex;
  gap: 12px;
}

.send-btn {
  padding: 14px 24px;
  background: linear-gradient(135deg, var(--success-color) 0%, #36a1ff 100%);
  color: white;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  min-width: 100px;
  justify-content: center;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(24, 144, 255, 0.3);
}

.send-btn:disabled {
  background: var(--border-color);
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-text {
  font-size: 14px;
}

.btn-icon {
  font-size: 18px;
}

@media (max-width: 768px) {
  .chat-container {
    grid-template-columns: 1fr;
  }

  .chat-info {
    display: none;
  }

  .message-bubble {
    max-width: 85%;
  }
}
</style>