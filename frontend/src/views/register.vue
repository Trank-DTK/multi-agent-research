<template>
  <div class="register-container">
    <h2>用户注册</h2>
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
    
    <router-link to="/login">已有账号？去登录</router-link>
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
    const response = await axios.post('/auth/register/', {
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
  max-width: 500px;
  margin: 50px auto;
  padding: 30px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.form-group.half {
  flex: 1;
  margin-bottom: 0;
}

input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #42b983;
}

button {
  width: 100%;
  padding: 12px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #3aa876;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error {
  color: #f44336;
  margin-top: 15px;
  padding: 10px;
  background-color: #ffebee;
  border-radius: 4px;
}

.success {
  color: #4caf50;
  margin-top: 15px;
  padding: 10px;
  background-color: #e8f5e9;
  border-radius: 4px;
  text-align: center;
}

a {
  display: block;
  margin-top: 20px;
  text-align: center;
  color: #42b983;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>