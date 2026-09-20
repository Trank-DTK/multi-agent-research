<template>
  <section class="research-conversation panel">
    <header class="conversation-toolbar">
      <div>
        <h2>{{ title }}</h2>
        <small>{{ subtitle }}</small>
      </div>
      <button class="secondary-button" :disabled="loading" @click="reset">新对话</button>
    </header>
    <div ref="messageArea" class="conversation-messages" aria-live="polite">
      <div v-if="!messages.length" class="empty-state">
        <el-icon><ChatDotRound /></el-icon>
        <h3>{{ emptyTitle }}</h3>
        <p>{{ emptyDescription }}</p>
      </div>
      <article
        v-for="(message, index) in messages"
        :key="index"
        class="research-message"
        :class="message.role"
      >
        <span class="message-role">{{ message.role === 'user' ? '你' : '研究助手' }}</span>
        <MarkdownContent v-if="message.role === 'assistant'" :content="message.content" />
        <div v-else>{{ message.content }}</div>
      </article>
      <p v-if="loading && (!streaming || !messages.at(-1)?.content)" class="thinking" role="status">
        正在分析你的问题…
      </p>
    </div>
    <p v-if="error" class="error-banner" role="alert">{{ error }}</p>
    <form class="conversation-composer" @submit.prevent="send">
      <textarea
        v-model="input"
        rows="3"
        aria-label="输入研究问题"
        :placeholder="placeholder"
        @keydown.enter="submitOnEnter($event, send)"
      />
      <div class="composer-bottom">
        <small>Enter 发送 · Shift+Enter 换行</small
        ><button class="primary-button" :disabled="loading || !input.trim() || disabled">
          发送 ↑
        </button>
      </div>
    </form>
  </section>
</template>
<script setup>
import MarkdownContent from '@/components/MarkdownContent.vue'
import { ref, nextTick, watch, onBeforeUnmount } from 'vue'
import axios from '@/axios'
import { streamChat } from '@/utils/streamChat'
let streamController
onBeforeUnmount(() => streamController?.abort())
import { apiError, submitOnEnter } from '@/utils/apiError'
const props = defineProps({
  endpoint: { type: String, required: true },
  title: { type: String, default: '科研助手' },
  subtitle: { type: String, default: '使用设置中的默认模型' },
  emptyTitle: { type: String, default: '从一个研究问题开始' },
  emptyDescription: { type: String, default: '说明你的目标与背景，获取具体的研究建议。' },
  placeholder: { type: String, default: '输入研究问题…' },
  context: { type: Object, default: () => ({}) },
  disabled: Boolean,
  streaming: Boolean,
  prompt: { type: String, default: '' },
})
const input = ref(''),
  messages = ref([]),
  loading = ref(false),
  error = ref(''),
  conversationId = ref(null),
  messageArea = ref(null)
watch(
  () => props.prompt,
  (value) => {
    input.value = value
  },
)
function reset() {
  if (loading.value) return
  messages.value = []
  conversationId.value = null
  error.value = ''
}
async function scroll() {
  await nextTick()
  if (messageArea.value) messageArea.value.scrollTop = messageArea.value.scrollHeight
}
async function send() {
  if (loading.value || !input.value.trim() || props.disabled) return
  const message = input.value.trim()
  messages.value.push({ role: 'user', content: message })
  input.value = ''
  loading.value = true
  error.value = ''
  scroll()
  try {
    if (props.streaming) {
      streamController = new AbortController()
      messages.value.push({ role: 'assistant', content: '' })
      const answer = messages.value.at(-1)
      await streamChat(
        props.endpoint,
        { message, ...props.context },
        (event) => {
          if (event.token) {
            answer.content += event.token
            scroll()
          }
        },
        streamController.signal,
      )
    } else {
      const { data } = await axios.post(
        props.endpoint,
        { message, conversation_id: conversationId.value, ...props.context },
        { timeout: 180000 },
      )
      messages.value.push({ role: 'assistant', content: data.response })
      conversationId.value = data.conversation_id || null
    }
  } catch (e) {
    if (e.name === 'AbortError') return
    error.value = apiError(e)
    if (e.response?.data?.conversation_id) conversationId.value = e.response.data.conversation_id
    if (!input.value) input.value = message
  } finally {
    loading.value = false
    scroll()
  }
}
</script>
