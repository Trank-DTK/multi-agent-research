<!-- 骨架屏组件 -->
<template>
  <div class="skeleton-loader" :class="{ 'animated': animated }">
    <div v-for="i in lines" :key="i" class="skeleton-line" :style="{ width: getRandomWidth() }"></div>
    <div v-if="hasAvatar" class="skeleton-avatar"></div>
    <div v-if="hasImage" class="skeleton-image"></div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  lines: {
    type: Number,
    default: 3
  },
  animated: {
    type: Boolean,
    default: true
  },
  hasAvatar: {
    type: Boolean,
    default: false
  },
  hasImage: {
    type: Boolean,
    default: false
  }
})

const getRandomWidth = () => {
  const widths = ['60%', '80%', '90%', '70%', '85%']
  return widths[Math.floor(Math.random() * widths.length)]
}
</script>

<style scoped>
.skeleton-loader {
  width: 100%;
}

.skeleton-loader.animated .skeleton-line,
.skeleton-loader.animated .skeleton-avatar,
.skeleton-loader.animated .skeleton-image {
  background: linear-gradient(90deg, var(--bg-secondary) 25%, var(--bg-tertiary) 50%, var(--bg-secondary) 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

.skeleton-line {
  height: 16px;
  background-color: var(--bg-secondary);
  border-radius: 4px;
  margin-bottom: 12px;
}

.skeleton-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: var(--bg-secondary);
  margin-bottom: 12px;
}

.skeleton-image {
  width: 100%;
  height: 200px;
  background-color: var(--bg-secondary);
  border-radius: 8px;
  margin-bottom: 12px;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>