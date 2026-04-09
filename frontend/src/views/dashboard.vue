<template>
  <div class="dashboard">
    <header>
      <h1>科研协作平台</h1>
      <div class="user-info">
        <span>欢迎，{{ user?.username || '用户' }}</span>
        <button @click="logout" class="logout-btn">退出</button>
      </div>
    </header>
    
    <main>
      <div class="welcome-card">
        <h2>第8周功能可用！ 🎉</h2>
        <p>数据分析Agent已上线，支持CSV/Excel上传、统计分析、数据可视化</p>
      </div>
      
      <div class="feature-grid">
        <!-- 已有功能 -->
        <router-link to="/chat" class="feature-card">
          <div class="feature-icon">💬</div>
          <h3>智能对话</h3>
          <p>与AI助手自由对话</p>
        </router-link>
        
        <router-link to="/documents" class="feature-card">
          <div class="feature-icon">📚</div>
          <h3>文献管理</h3>
          <p>上传和管理PDF文献</p>
        </router-link>
        
        <router-link to="/literature" class="feature-card">
          <div class="feature-icon">📖</div>
          <h3>文献助手</h3>
          <p>基于文献的智能问答</p>
        </router-link>
        
        <router-link to="/collaboration" class="feature-card">
          <div class="feature-icon">🤝</div>
          <h3>协作研究</h3>
          <p>文献+实验双智能体协作</p>
        </router-link>
        
        <router-link to="/collaboration-review" class="feature-card">
          <div class="feature-icon">🔍</div>
          <h3>智能评审协作</h3>
          <p>Critic评审官自动评估质量</p>
        </router-link>
        
        <!-- 新增：数据分析入口 -->
        <router-link to="/analysis" class="feature-card highlight">
          <div class="feature-icon">📊</div>
          <h3>数据分析</h3>
          <p>上传CSV/Excel，统计分析、可视化</p>
          <span class="new-badge">NEW</span>
        </router-link>
      </div>
      
      <div class="stats">
        <div class="stat-card">
          <h3>项目状态</h3>
          <p>基础框架 ✓</p>
          <p>用户认证 ✓</p>
          <p>Docker编排 ✓</p>
          <p>Ollama集成 ✓</p>
          <p>Agent开发 ✓</p>
          <p>RAG系统 ✓</p>
          <p>多智能体协作 ✓</p>
          <p>Critic评审 ✓</p>
          <p>任务调度优化 ✓</p>
          <p>数据分析 ✓</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../axios'

const router = useRouter()
const user = ref(null)

const fetchUserInfo = async () => {
  try {
    const response = await axios.get('/auth/user/')
    user.value = response.data
  } catch (err) {
    console.error('获取用户信息失败', err)
  }
}

const logout = () => {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  router.push('/login')
}

onMounted(() => {
  fetchUserInfo()
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background-color: #f5f5f5;
}

header {
  background-color: #42b983;
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

header h1 {
  margin: 0;
  font-size: 24px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logout-btn {
  padding: 8px 16px;
  background-color: rgba(255,255,255,0.2);
  color: white;
  border: 1px solid white;
  border-radius: 4px;
  cursor: pointer;
}

.logout-btn:hover {
  background-color: rgba(255,255,255,0.3);
}

main {
  padding: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  background-color: white;
  border-radius: 8px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.feature-card {
  background-color: white;
  border-radius: 12px;
  padding: 20px;
  text-decoration: none;
  color: #333;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  position: relative;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}

.feature-card.highlight {
  border: 2px solid #9c27b0;
  background: linear-gradient(135deg, #fff 0%, #f3e5f5 100%);
}

.feature-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.feature-card h3 {
  margin: 0 0 8px;
  font-size: 18px;
}

.feature-card p {
  margin: 0;
  font-size: 13px;
  color: #666;
}

.new-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background-color: #9c27b0;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.stat-card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.stat-card h3 {
  margin-top: 0;
  color: #42b983;
}
</style>