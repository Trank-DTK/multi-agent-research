<!-- 全局通知组件 -->
<template>
  <TransitionGroup name="notification" tag="div" class="notification-container">
    <div v-for="notif in notifications" :key="notif.id" :class="['notification', notif.type]">
      <span class="notification-icon">{{ getIcon(notif.type) }}</span>
      <span class="notification-message">{{ notif.message }}</span>
      <button class="notification-close" @click="removeNotification(notif.id)">×</button>
    </div>
  </TransitionGroup>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const notifications = ref([])
let nextId = 0

const getIcon = (type) => {
  const icons = {
    success: '✓',
    error: '✗',
    warning: '⚠',
    info: 'ℹ'
  }
  return icons[type] || 'ℹ'
}

const addNotification = (message, type = 'info', duration = 3000) => {
  const id = nextId++
  notifications.value.push({ id, message, type })
  
  if (duration > 0) {
    setTimeout(() => {
      removeNotification(id)
    }, duration)
  }
}

const removeNotification = (id) => {
  const index = notifications.value.findIndex(n => n.id === id)
  if (index !== -1) {
    notifications.value.splice(index, 1)
  }
}

// 挂载到window
onMounted(() => {
  window.notify = addNotification
})

onUnmounted(() => {
  delete window.notify
})
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notification {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background-color: var(--bg-primary);
  border-radius: 8px;
  box-shadow: var(--card-shadow);
  border-left: 4px solid;
  min-width: 280px;
}

.notification.success {
  border-left-color: var(--success-color);
}
.notification.error {
  border-left-color: var(--error-color);
}
.notification.warning {
  border-left-color: var(--warning-color);
}
.notification.info {
  border-left-color: var(--info-color);
}

.notification-icon {
  font-size: 18px;
}

.notification-message {
  flex: 1;
  color: var(--text-primary);
}

.notification-close {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: var(--text-tertiary);
}

.notification-close:hover {
  color: var(--text-primary);
}

/* 动画 */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.notification-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>