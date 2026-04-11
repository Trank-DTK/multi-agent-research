<template>
  <div class="dashboard">
    <ResponsiveNav />
    
    <main class="main-content">
      <div class="welcome-card">
        <h2>欢迎回来！</h2>
        <p>多智能体科研协作平台已就绪</p>
      </div>
      
      <div class="stats-grid" :class="{ 'mobile': isMobile }">
        <div class="stat-card" v-for="stat in stats" :key="stat.label">
          <h3>{{ stat.label }}</h3>
          <p>{{ stat.value }}</p>
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
import { ref } from 'vue'
import { useResponsive } from '@/composables/useResponsive'
import ResponsiveNav from '@/components/ResponsiveNav.vue'

const { isMobile } = useResponsive()

const stats = ref([
  { label: '对话次数', value: '156' },
  { label: '文献数量', value: '23' },
  { label: '论文数量', value: '5' },
  { label: '数据集', value: '8' }
])
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background-color: var(--bg-primary);
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

.welcome-card {
  background-color: var(--bg-secondary);
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  text-align: center;
}

.welcome-card h2 {
  margin-bottom: 10px;
  color: var(--text-primary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stats-grid.mobile {
  grid-template-columns: repeat(2, 1fr);
}

.stat-card {
  background-color: var(--bg-secondary);
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.stat-card h3 {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 10px;
}

.stat-card p {
  font-size: 28px;
  font-weight: bold;
  color: var(--success-color);
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
  background-color: var(--bg-secondary);
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  text-decoration: none;
  color: var(--text-primary);
  transition: transform 0.2s, box-shadow 0.2s;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--card-shadow);
}

.action-card .icon {
  font-size: 32px;
  display: block;
  margin-bottom: 10px;
}
</style>