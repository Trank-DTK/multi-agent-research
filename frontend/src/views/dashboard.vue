<template>
  <div class="dashboard">
    <ResponsiveNav />
    
    <main class="main-content">
      <div class="welcome-card">
        <div class="welcome-icon">🚀</div>
        <div class="welcome-content">
          <h2>欢迎回来！</h2>
          <p class="subtitle">多智能体科研协作平台已就绪</p>
          <p class="description">AI驱动的科研助手，助您高效完成文献调研、数据分析、论文写作与协作研究</p>
        </div>
        <div class="welcome-stats">
          <div class="stat-item">
            <span class="stat-value">6</span>
            <span class="stat-label">个核心功能</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">24/7</span>
            <span class="stat-label">全天候服务</span>
          </div>
        </div>
      </div>
      
      <div class="quick-tools">
        <h3>快速工具</h3>
        <div class="tools-grid" :class="{ 'mobile': isMobile }">
          <button class="tool-btn" @click="quickAction('new_chat')">
            <span class="tool-icon">💬</span>
            <span class="tool-label">新建对话</span>
          </button>
          <button class="tool-btn" @click="quickAction('upload_doc')">
            <span class="tool-icon">📄</span>
            <span class="tool-label">上传文献</span>
          </button>
          <button class="tool-btn" @click="quickAction('new_analysis')">
            <span class="tool-icon">📊</span>
            <span class="tool-label">新建分析</span>
          </button>
          <button class="tool-btn" @click="quickAction('start_collab')">
            <span class="tool-icon">🤝</span>
            <span class="tool-label">开始协作</span>
          </button>
        </div>
      </div>
      
      <div class="action-grid" :class="{ 'mobile': isMobile }">
        <router-link to="/chat" class="action-card">
          <span class="icon">💬</span>
          <span>AI对话</span>
        </router-link>
        <router-link to="/agent" class="action-card">
          <span class="icon">🤖</span>
          <span>智能体</span>
        </router-link>
        <router-link to="/documents" class="action-card">
          <span class="icon">📚</span>
          <span>文献库</span>
        </router-link>
        <router-link to="/analysis" class="action-card">
          <span class="icon">📊</span>
          <span>数据分析</span>
        </router-link>
        <router-link to="/writing" class="action-card">
          <span class="icon">✍️</span>
          <span>论文写作</span>
        </router-link>
        <router-link to="/collaboration" class="action-card">
          <span class="icon">🤝</span>
          <span>协作研究</span>
        </router-link>
      </div>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useResponsive } from '@/composables/useResponsive.js'
import ResponsiveNav from '@/components/ResponsiveNav.vue'

const router = useRouter()
const { isMobile } = useResponsive()

const quickAction = (action) => {
  switch (action) {
    case 'new_chat':
      router.push('/chat')
      break
    case 'upload_doc':
      router.push('/documents')
      break
    case 'new_analysis':
      router.push('/analysis')
      break
    case 'start_collab':
      router.push('/collaboration')
      break
  }
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background-color: var(--bg-primary);
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 24px;
}

.welcome-card {
  background: linear-gradient(135deg, var(--header-bg) 0%, #36a1ff 100%);
  border-radius: 20px;
  padding: 40px;
  margin-bottom: 40px;
  display: flex;
  align-items: center;
  gap: 40px;
  color: white;
  box-shadow: 0 8px 32px rgba(24, 144, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.welcome-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  z-index: 0;
}

.welcome-icon {
  font-size: 64px;
  z-index: 1;
}

.welcome-content {
  flex: 1;
  z-index: 1;
}

.welcome-content h2 {
  margin-bottom: 8px;
  font-size: 32px;
  font-weight: 700;
}

.subtitle {
  font-size: 18px;
  opacity: 0.9;
  margin-bottom: 16px;
}

.description {
  font-size: 14px;
  opacity: 0.8;
  max-width: 600px;
  line-height: 1.6;
}

.quick-tools {
  margin-bottom: 40px;
}

.quick-tools h3 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.tools-grid.mobile {
  grid-template-columns: repeat(2, 1fr);
}

.tool-btn {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-primary);
}

.tool-btn:hover {
  transform: translateY(-4px);
  box-shadow: var(--card-shadow);
  border-color: var(--success-color);
  background-color: var(--bg-tertiary);
}

.tool-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.tool-label {
  font-size: 14px;
  font-weight: 500;
}

.welcome-stats {
  display: flex;
  gap: 30px;
  z-index: 1;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}


.action-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.action-grid.mobile {
  grid-template-columns: repeat(2, 1fr);
}

.action-card {
  background-color: white;
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
  text-decoration: none;
  color: var(--text-primary);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.action-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--success-color) 0%, #36a1ff 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.action-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
  border-color: var(--success-color);
}

.action-card:hover::before {
  opacity: 1;
}

.action-card .icon {
  font-size: 40px;
  display: block;
  margin-bottom: 16px;
  transition: transform 0.3s ease;
}

.action-card:hover .icon {
  transform: scale(1.1);
}
</style>