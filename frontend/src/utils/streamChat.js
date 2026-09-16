// POST SSE supports authentication and incremental UTF-8 decoding.
export async function streamChat(endpoint, payload, onEvent, signal) {
  const headers = { 'Content-Type': 'application/json', Accept: 'text/event-stream' }
  const token = localStorage.getItem('access')
  if (token) headers.Authorization = `Bearer ${token}`
  const response = await fetch('/api' + endpoint, {
    method: 'POST',
    headers,
    body: JSON.stringify({ ...payload, stream: true }),
    signal,
  })
  if (!response.ok) {
    const data = await response.json().catch(() => null)
    const error = new Error(
      data?.error?.message || data?.error || data?.detail || `请求失败（HTTP ${response.status}）`,
    )
    error.response = { status: response.status, data }
    throw error
  }
  if (!response.headers.get('content-type')?.includes('text/event-stream') || !response.body)
    throw new Error('服务未返回流式响应，请更新并重启后端')
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = '',
    completed = false
  const parse = (frame) => {
    const data = frame
      .split(/\r?\n/)
      .filter((line) => line.startsWith('data:'))
      .map((line) => line.slice(5).trimStart())
      .join('\n')
    if (!data) return
    if (data === '[DONE]') {
      completed = true
      return
    }
    const event = JSON.parse(data)
    if (event.error) throw new Error(event.error)
    onEvent(event)
  }
  try {
    while (!completed) {
      const { value, done } = await reader.read()
      buffer += done ? decoder.decode() : decoder.decode(value, { stream: true })
      let match
      while ((match = /\r?\n\r?\n/.exec(buffer))) {
        parse(buffer.slice(0, match.index))
        buffer = buffer.slice(match.index + match[0].length)
        if (completed) break
      }
      if (done) {
        if (buffer.trim() && !completed) parse(buffer)
        break
      }
    }
    if (!completed) throw new Error('连接中断，回复尚未完成，请重试')
  } finally {
    await reader.cancel().catch(() => {})
    reader.releaseLock()
  }
}
