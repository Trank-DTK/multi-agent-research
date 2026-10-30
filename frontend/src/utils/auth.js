export function accessRedirect(to, storage = window.localStorage) {
  const authenticated = Boolean(storage.getItem('access'))
  if (to.meta.requiresAuth && !authenticated) return '/login'
  if (to.meta.requiresGuest && authenticated) return '/dashboard'
  return true
}

export function saveSessionTokens(data, storage = window.localStorage) {
  if (
    typeof data?.access !== 'string' ||
    !data.access.trim() ||
    typeof data?.refresh !== 'string' ||
    !data.refresh.trim()
  )
    throw new Error('登录响应异常，请重试')
  storage.setItem('access', data.access)
  storage.setItem('refresh', data.refresh)
}
