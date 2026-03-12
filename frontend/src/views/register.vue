<template>
  <div class="register-container">
    <h2>用户注册</h2>
    <form @submit.prevent="handleRegister">
      <div class="form-group">
        <input 
          v-model="username" 
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
      
      <div class="form-group">
        <input 
          v-model="firstName" 
          placeholder="姓（可选）"
        />
      </div>
      
      <div class="form-group">
        <input 
          v-model="lastName" 
          placeholder="名（可选）"
        />
      </div>
      
      <button type="submit" :disabled="loading">
        {{ loading ? '注册中...' : '注册' }}
      </button>
    </form>
    
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="success" class="success">{{ success }}</p>
    
    <router-link to="/login">已有账号？去登录</router-link>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

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
const error = ref('')
const success = ref('')

const handleRegister = async () => {
  // 简单前端验证
  if (password.value !== password2.value) {
    error.value = '两次输入的密码不一致'
    return
  }
  
  loading.value = true
  error.value = ''
  success.value = ''
  
  try {
    const response = await axios.post('/api/auth/register/', {
      username: username.value,
      email: email.value,
      password: password.value,
      password2: password2.value,
      first_name: firstName.value,
      last_name: lastName.value
    })
    
    // 注册成功
    success.value = '注册成功！正在跳转到登录页...'
    
    // 2秒后跳转到登录页
    setTimeout(() => {
      router.push('/login')
    }, 2000)
    
  } catch (err) {
    // 处理后端返回的错误
    if (err.response && err.response.data) {
      // 提取所有错误信息
      const errorData = err.response.data
      const errorMessages = []
      
      for (const field in errorData) {
        if (Array.isArray(errorData[field])) {
          errorMessages.push(`${field}: ${errorData[field].join(' ')}`)
        } else {
          errorMessages.push(`${field}: ${errorData[field]}`)
        }
      }
      
      error.value = errorMessages.join('； ')
    } else {
      error.value = '注册失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
}

.form-group {
  margin-bottom: 15px;
}

input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error {
  color: red;
  margin-top: 10px;
}

.success {
  color: green;
  margin-top: 10px;
}

a {
  display: block;
  margin-top: 15px;
  text-align: center;
  color: #42b983;
  text-decoration: none;
}
</style>