import axios from 'axios'
import router from './router'

// 创建 axios 实例，设置 baseURL
const instance = axios.create({
  baseURL: '/api'  // 所有请求都会自动加上 /api 前缀
})

// 请求拦截器
instance.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
instance.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const refresh = localStorage.getItem('refresh')
        // 注意：刷新 token 的请求也要用 instance
        const res = await instance.post('/auth/refresh/', { refresh })
        localStorage.setItem('access', res.data.access)
        originalRequest.headers.Authorization = `Bearer ${res.data.access}`
        return instance(originalRequest)
      } catch (refreshError) {
        router.push('/login')
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  }
)

export default instance