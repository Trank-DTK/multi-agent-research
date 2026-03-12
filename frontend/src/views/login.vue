<template>
  <div>
    <h2>登录</h2>
    <form @submit.prevent="handleLogin">
      <input v-model="username" placeholder="用户名" />
      <input v-model="password" type="password" placeholder="密码" />
      <button type="submit">登录</button>
    </form>
    <p v-if="error">{{ error }}</p>
    <router-link to="/register">去注册</router-link>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const username = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()

const handleLogin = async () => {
  try {
    //发送post请求到后端登录接口，获取access和refresh token
    const res = await axios.post('/api/auth/login/', {
      username: username.value,
      password: password.value
    })
    //存储JWT token到localStorage
    localStorage.setItem('access', res.data.access)   //访问令牌
    localStorage.setItem('refresh', res.data.refresh)  //刷新令牌
    //登录成功后跳转到仪表盘界面
    router.push('/dashboard')
  } catch (err) {
    error.value = '登录失败，请检查用户名密码'
  }
}
</script>