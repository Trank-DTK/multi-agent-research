import axios from 'axios'
import router from './router'

// 请求拦截器，在发送请求前自动添加token
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access')
    if (token) {
      // 把access token添加到请求头中，Bearer Token是JWT的标准格式
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  //请求错误处理
  error => Promise.reject(error)
)

//响应拦截器：在收到响应后处理 token 过期
axios.interceptors.response.use(
  //请求成功则直接返回响应
  response => response,
  //失败处理
  async error => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      //标记已经重试过，避免无限循环
      originalRequest._retry = true
      try {
        const refresh = localStorage.getItem('refresh')
        //发送刷新 token 请求
        const res = await axios.post('/api/auth/refresh/', { refresh })
        //保存新的access token
        localStorage.setItem('access', res.data.access)
        originalRequest.headers.Authorization = `Bearer ${res.data.access}`
        //重新发送原始请求
        return axios(originalRequest)
      } catch (refreshError) {
        //刷新token失败，重定向到登录页
        router.push('/login')
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  }
)