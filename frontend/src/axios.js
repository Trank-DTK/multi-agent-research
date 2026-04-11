import axios from 'axios'
import router from '@/router'
import { errorHandler } from './utils/errorHandler'
import { performanceMonitor } from './utils/performance'

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
    const duration = Date.now() - response.config.metadata?.startTime
    performanceMonitor.measureAPI(response.config.url, duration, true)
    return response
  },
  error => {
    const duration = Date.now() - error.config?.metadata?.startTime
    performanceMonitor.measureAPI(error.config?.url, duration, false)
    return Promise.reject(error)
  }
)

export default instance