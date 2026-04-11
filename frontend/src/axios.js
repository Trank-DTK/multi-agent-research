import axios from 'axios'
import router from '/router'
import { errorHandler } from './utils/errorHandler'

// 创建axios实例
const instance = axios.create({
  baseURL: '/api',
  timeout: 30000,  // 30秒超时
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
instance.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 添加请求开始时间（用于性能监控）
    config.metadata = { startTime: Date.now() }

    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  response => {
    // 记录请求耗时
    const duration = Date.now() - response.config.metadata?.startTime
    if (duration > 3000) {
      console.warn(`慢请求: ${response.config.url} - ${duration}ms`)
    }

    return response
  },
  async error => {
    const originalRequest = error.config

    // 处理401 token过期
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refresh = localStorage.getItem('refresh')
        const res = await axios.post('/api/auth/refresh/', { refresh })
        localStorage.setItem('access', res.data.access)

        originalRequest.headers.Authorization = `Bearer ${res.data.access}`
        return instance(originalRequest)
      } catch (refreshError) {
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        router.push('/login')
        return Promise.reject(refreshError)
      }
    }

    // 统一错误处理
    errorHandler.handleAPIError(error, originalRequest?.url)

    return Promise.reject(error)
  }
)

export default instance