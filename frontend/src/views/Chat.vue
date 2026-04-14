<template>
  <div class="chat-page">
    <div class="page-header">
      <button class="back-btn" @click="$router.push('/dashboard')">
        <span class="btn-icon">←</span>
        <span class="btn-text">返回主页</span>
      </button>
      <div class="header-content">
        <h1>AI对话助手</h1>
        <p class="subtitle">与智能助手进行自然对话，获取科研支持</p>
      </div>
    </div>
    <ChatInterface />
  </div>
</template>

<script setup>
import ChatInterface from '@/components/ChatInterface.vue'
import { useKeyboardShortcuts } from '@/composables/useKeyboardShortcuts'

// 添加快捷键 - 这些快捷键会在ChatInterface组件中处理
useKeyboardShortcuts([
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
</style>