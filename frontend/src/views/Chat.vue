<template>
  <div class="chat-page">
    <h2>AI对话助手</h2>
    <ChatInterface />
  </div>
</template>

<script setup>
import ChatInterface from '@/components/ChatInterface.vue'
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