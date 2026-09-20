export function apiError(error, fallback = '请求失败，请稍后重试') {
  const data = error.response?.data
  if (error.response?.status === 429) {
    const seconds = data?.retry_after || error.response?.headers?.['retry-after']
    return seconds ? `操作较频繁，请在 ${seconds} 秒后重试。` : '操作较频繁，请稍后重试。'
  }
  if (typeof data === 'string')
    return `服务返回异常（HTTP ${error.response.status}），请检查后端服务`
  if (!data && error.message && !error.isAxiosError) return error.message
  const message = data?.error?.message || data?.error || data?.detail || data?.message
  if (typeof message === 'string') return message
  if (data && typeof data === 'object')
    return Object.entries(data)
      .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join('；') : value}`)
      .join('；')
  return error.code === 'ECONNABORTED' ? '请求超时，请检查服务后重试' : fallback
}
export function submitOnEnter(event, submit) {
  if (event.isComposing || event.keyCode === 229 || event.shiftKey) return
  event.preventDefault()
  submit()
}
