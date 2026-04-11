<template>
  <button class="theme-toggle" @click="toggleTheme" :title="isDark ? '切换到亮色模式' : '切换到暗色模式'">
    <span v-if="isDark">🌙</span>
    <span v-else>☀️</span>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDark)

const toggleTheme = () => {
  themeStore.toggleTheme()
}
</script>

<style scoped>
.theme-toggle {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.theme-toggle:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.dark .theme-toggle:hover {
  background-color: rgba(255, 255, 255, 0.1);
}
</style>