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
        <h2>第1周开发完成！ 🎉</h2>
        <p>用户认证系统已就绪，下周将开始集成Ollama和LangChain</p>
      </div>
      
      <div class="stats">
        <div class="stat-card">
          <h3>项目状态</h3>
          <p>基础框架 ✓</p>
          <p>用户认证 ✓</p>
          <p>Docker编排 ✓</p>
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

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const response = await axios.get('/auth/user/')
    user.value = response.data
  } catch (err) {
    console.error('获取用户信息失败', err)
  }
}

// 退出登录
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