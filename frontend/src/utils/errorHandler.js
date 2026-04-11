// 全局错误处理工具，统一处理API错误并显示友好的消息
import { ElMessage } from 'element-plus'

export const errorHandler = {
  // 处理API错误
  handleAPIError(error, context = '') {
    console.error(`API错误 [${context}]:`, error)

    let message = '操作失败，请稍后重试'

    if (error.response) {
      const status = error.response.status
      const data = error.response.data

      switch (status) {
        case 400:
          message = data.message || '请求参数错误'
          break
        case 401:
          message = '登录已过期，请重新登录'
          // 跳转到登录页
          localStorage.removeItem('access')
          localStorage.removeItem('refresh')
          window.location.href = '/login'
          break
        case 403:
          message = '没有权限执行此操作'
          break
        case 404:
          message = '资源不存在'
          break
        case 429:
          message = '请求过于频繁，请稍后再试'
          break
        case 500:
          message = '服务器错误，请稍后重试'
          break
        default:
          message = data.message || data.error || '未知错误'
      }
    } else if (error.request) {
      message = '网络连接失败，请检查网络'
    }

    ElMessage.error(message)
    return message
  },

  // 显示成功消息
  showSuccess(message) {
    ElMessage.success(message)
  },

  // 显示警告消息
  showWarning(message) {
    ElMessage.warning(message)
  },

  // 显示信息消息
  showInfo(message) {
    ElMessage.info(message)
  }
}