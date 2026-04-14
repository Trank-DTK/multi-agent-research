<template>
  <div class="login-container">
    <div class="login-header">
      <div class="logo-section">
        <div class="logo">🔬</div>
        <div class="title">
          <h1>多智能体科研协作平台</h1>
          <p class="subtitle">AI驱动的智能科研助手</p>
        </div>
      </div>
    </div>

    <div class="login-content">
      <h2>用户登录</h2>
      <form @submit.prevent="handleLogin">
      <div class="form-group">
        <input 
          v-model="username" 
          type="text" 
          placeholder="用户名" 
          required
          autocomplete="username"
        />
      </div>
      
      <div class="form-group">
        <input 
          v-model="password" 
          type="password" 
          placeholder="密码" 
          required
          autocomplete="current-password"
        />
      </div>
      
      <button type="submit" :disabled="loading">
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </form>
    
    <p v-if="error" class="error">{{ error }}</p>
    
      <p v-if="error" class="error">{{ error }}</p>

      <router-link to="/register" class="register-link">还没有账号？立即注册</router-link>

      <div class="login-features">
        <h3>平台特色功能</h3>
        <div class="features-grid">
          <div class="feature-item">
            <span class="feature-icon">🤖</span>
            <span class="feature-text">多智能体协作研究</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">📚</span>
            <span class="feature-text">文献智能管理</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">📊</span>
            <span class="feature-text">数据分析可视化</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">✍️</span>
            <span class="feature-text">AI辅助论文写作</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../axios'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const response = await axios.post('/auth/login/', {
      username: username.value,
      password: password.value
    })
    
    // 保存token
    localStorage.setItem('access', response.data.access)
    localStorage.setItem('refresh', response.data.refresh)
    
    // 跳转到仪表盘
    router.push('/dashboard')
  } catch (err) {
    if (err.response?.status === 401) {
      error.value = '用户名或密码错误'
    } else {
      error.value = '登录失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 60px 24px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-primary);
}

.login-header {
  text-align: center;
  margin-bottom: 60px;
}

.logo-section {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.logo {
  font-size: 64px;
  background: linear-gradient(135deg, var(--success-color) 0%, #36a1ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title h1 {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text-primary);
  background: linear-gradient(135deg, var(--success-color) 0%, #36a1ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.login-content {
  max-width: 480px;
  margin: 0 auto;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

.login-content h2 {
  text-align: center;
  margin-bottom: 32px;
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
}

.form-group {
  margin-bottom: 24px;
}

input {
  width: 100%;
  padding: 16px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  font-size: 16px;
  box-sizing: border-box;
  transition: all 0.3s ease;
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

input:focus {
  outline: none;
  border-color: var(--success-color);
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
  background: white;
}

input::placeholder {
  color: var(--text-tertiary);
}

button {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, var(--success-color) 0%, #36a1ff 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 8px;
}

button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(24, 144, 255, 0.3);
}

button:disabled {
  background: var(--border-color);
  cursor: not-allowed;
  opacity: 0.6;
}

.error {
  color: #f44336;
  margin-top: 20px;
  padding: 12px;
  background-color: #ffebee;
  border-radius: 8px;
  text-align: center;
  font-size: 14px;
}

.register-link {
  display: block;
  margin-top: 24px;
  text-align: center;
  color: var(--success-color);
  text-decoration: none;
  font-weight: 500;
  font-size: 15px;
  transition: color 0.3s ease;
}

.register-link:hover {
  text-decoration: underline;
  color: #36a1ff;
}

.login-features {
  margin-top: 40px;
  padding-top: 32px;
  border-top: 1px solid var(--border-color);
}

.login-features h3 {
  text-align: center;
  margin-bottom: 24px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-secondary);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.feature-item:hover {
  background: var(--bg-tertiary);
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 20px;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--success-color) 0%, #36a1ff 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.feature-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

@media (max-width: 768px) {
  .login-container {
    padding: 40px 20px;
  }

  .logo-section {
    gap: 16px;
  }

  .logo {
    font-size: 48px;
  }

  .title h1 {
    font-size: 28px;
  }

  .login-content {
    padding: 32px 24px;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>