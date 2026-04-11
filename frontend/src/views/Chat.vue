<template>
  <div class="chat-page">
    <h2>AI对话助手</h2>
    <ChatInterface />
  </div>
</template>

<script setup>
import ChatInterface from '@/components/ChatInterface.vue'
import { useKeyboardShortcuts } from '@/composables/useKeyboardShortcuts'

// 添加快捷键
useKeyboardShortcuts([
  {
    key: 'enter',
    ctrl: true,
    handler: () => {
      sendMessage()
    }
  },
  {
    key: 'escape',
    handler: () => {
      inputMessage.value = ''
    }
  },
  {
    key: '/',
    handler: () => {
      document.querySelector('textarea')?.focus()
    }
  }
])
</script>

<style scoped>
.chat-page {
  max-width: 800px;
  margin: 30px auto;
  padding: 0 20px;
}

h2 {
  margin-bottom: 20px;
  color: #333;
}
</style>