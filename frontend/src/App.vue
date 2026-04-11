<template>
  <div :class="{ dark: isDark }">
    <router-view />
    <GlobalNotification />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useThemeStore } from './stores/theme'
import GlobalNotification from './components/GlobalNotification.vue'

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDark)
</script>