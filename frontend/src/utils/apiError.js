export function apiError(error, fallback = '请求失败，请稍后重试') {
  const data = error.response?.data
  if (typeof data === 'string') return fallback
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
