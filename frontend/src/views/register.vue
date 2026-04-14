<template>
  <div class="register-container">
    <div class="register-header">
      <div class="logo-section">
        <div class="logo">🔬</div>
        <div class="title">
          <h1>多智能体科研协作平台</h1>
          <p class="subtitle">AI驱动的智能科研助手</p>
        </div>
      </div>
    </div>

    <div class="register-content">
      <h2>用户注册</h2>
      <p class="form-description">创建账号，开启智能科研之旅</p>
      <form @submit.prevent="handleRegister">
      <div class="form-group">
        <input 
          v-model="username" 
          type="text" 
          placeholder="用户名" 
          required
        />
      </div>
      
      <div class="form-group">
        <input 
          v-model="email" 
          type="email" 
          placeholder="邮箱" 
          required
        />
      </div>
      
      <div class="form-group">
        <input 
          v-model="password" 
          type="password" 
          placeholder="密码" 
          required
        />
      </div>
      
      <div class="form-group">
        <input 
          v-model="password2" 
          type="password" 
          placeholder="确认密码" 
          required
        />
      </div>
      
      <div class="form-row">
        <div class="form-group half">
          <input 
            v-model="firstName" 
            type="text" 
            placeholder="姓（可选）"
          />
        </div>
        
        <div class="form-group half">
          <input 
            v-model="lastName" 
            type="text" 
            placeholder="名（可选）"
          />
        </div>
      </div>
      
      <button type="submit" :disabled="loading">
        {{ loading ? '注册中...' : '注册' }}
      </button>
    </form>
    
    <div v-if="error" class="error">
      <p v-for="(msg, index) in errorMessages" :key="index">{{ msg }}</p>
    </div>
    
    <div v-if="success" class="success">
      {{ success }}
    </div>
    
      <router-link to="/login" class="login-link">已有账号？去登录</router-link>

      <div class="register-features">
        <h3>注册后您将获得</h3>
        <div class="benefits-grid">
          <div class="benefit-item">
            <span class="benefit-icon">🚀</span>
            <div class="benefit-content">
              <h4>智能科研助手</h4>
              <p>AI驱动的文献调研、数据分析工具</p>
            </div>
          </div>
          <div class="benefit-item">
            <span class="benefit-icon">🔬</span>
            <div class="benefit-content">
              <h4>多智能体协作</h4>
              <p>文献助手、实验助手协同工作</p>
            </div>
          </div>
          <div class="benefit-item">
            <span class="benefit-icon">📈</span>
            <div class="benefit-content">
              <h4>数据可视化</h4>
              <p>专业的数据分析和图表生成</p>
            </div>
          </div>
          <div class="benefit-item">
            <span class="benefit-icon">✍️</span>
            <div class="benefit-content">
              <h4>论文写作支持</h4>
              <p>AI辅助的论文撰写和编辑</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../axios'

const router = useRouter()

// 表单数据
const username = ref('')
const email = ref('')
const password = ref('')
const password2 = ref('')
const firstName = ref('')
const lastName = ref('')

// UI状态
const loading = ref(false)
const error = ref(null)
const success = ref('')

// 格式化错误消息
const errorMessages = computed(() => {
  if (!error.value) return []
  if (typeof error.value === 'string') return [error.value]
  return Object.entries(error.value).map(([field, msg]) => `${field}: ${msg}`)
})

const handleRegister = async () => {
  // 前端验证
  if (password.value !== password2.value) {
    error.value = { password: '两次输入的密码不一致' }
    return
  }
  
  if (password.value.length < 6) {
    error.value = { password: '密码长度至少6位' }
    return
  }
  
  loading.value = true
  error.value = null
  success.value = ''
  
  try {
    await axios.post('/auth/register/', {
      username: username.value,
      email: email.value,
      password: password.value,
      password2: password2.value,
      first_name: firstName.value,
      last_name: lastName.value
    })

    success.value = '注册成功！2秒后跳转到登录页...'

    // 2秒后跳转
    setTimeout(() => {
      router.push('/login')
    }, 2000)

  } catch (err) {
    if (err.response && err.response.data) {
      error.value = err.response.data
    } else {
      error.value = { error: '注册失败，请稍后重试' }
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 24px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-primary);
}

.register-header {
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

.register-content {
  max-width: 520px;
  margin: 0 auto;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

.register-content h2 {
  text-align: center;
  margin-bottom: 16px;
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
}

.form-description {
  text-align: center;
  margin-bottom: 32px;
  color: var(--text-secondary);
  font-size: 15px;
}

.form-group {
  margin-bottom: 24px;
}

.form-row {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.form-group.half {
  flex: 1;
  margin-bottom: 0;
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
  padding: 16px;
  background-color: #ffebee;
  border-radius: 12px;
  font-size: 14px;
}

.error p {
  margin: 4px 0;
}

.success {
  color: #4caf50;
  margin-top: 20px;
  padding: 16px;
  background-color: #e8f5e9;
  border-radius: 12px;
  text-align: center;
  font-size: 15px;
  font-weight: 500;
}

.login-link {
  display: block;
  margin-top: 24px;
  text-align: center;
  color: var(--success-color);
  text-decoration: none;
  font-weight: 500;
  font-size: 15px;
  transition: color 0.3s ease;
}

.login-link:hover {
  text-decoration: underline;
  color: #36a1ff;
}

.register-features {
  margin-top: 40px;
  padding-top: 32px;
  border-top: 1px solid var(--border-color);
}

.register-features h3 {
  text-align: center;
  margin-bottom: 24px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-secondary);
}

.benefits-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.benefit-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.benefit-item:hover {
  background: var(--bg-tertiary);
  transform: translateY(-2px);
}

.benefit-icon {
  font-size: 24px;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--success-color) 0%, #36a1ff 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.benefit-content h4 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
  color: var(--text-primary);
}

.benefit-content p {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.4;
}

@media (max-width: 768px) {
  .register-container {
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

  .register-content {
    padding: 32px 24px;
  }

  .form-row {
    flex-direction: column;
    gap: 16px;
  }
}
</style>