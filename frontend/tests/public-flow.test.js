import { test } from 'node:test'
import assert from 'node:assert/strict'
import { accessRedirect, saveSessionTokens } from '../src/utils/auth.js'
const storage = (initial = {}) => {
  const values = new Map(Object.entries(initial))
  return {
    getItem: (key) => values.get(key) || null,
    setItem: (key, value) => values.set(key, String(value)),
  }
}
test('public homepage is accessible, workspace stays protected and logged in guests return to workspace', () => {
  assert.equal(accessRedirect({ meta: {} }, storage()), true)
  assert.equal(accessRedirect({ meta: { requiresAuth: true } }, storage()), '/login')
  assert.equal(
    accessRedirect({ meta: { requiresGuest: true } }, storage({ access: 'test' })),
    '/dashboard',
  )
  assert.equal(accessRedirect({ meta: { requiresAuth: true } }, storage({ access: 'test' })), true)
})
test('only a valid token pair is persisted, malformed replies preserve the previous session', () => {
  const existing = storage({ access: 'old-access', refresh: 'old-refresh' })
  assert.throws(() => saveSessionTokens({ access: 'new-access' }, existing))
  assert.equal(existing.getItem('access'), 'old-access')
  assert.equal(existing.getItem('refresh'), 'old-refresh')
  saveSessionTokens({ access: 'new-access', refresh: 'new-refresh' }, existing)
  assert.equal(existing.getItem('access'), 'new-access')
  assert.equal(existing.getItem('refresh'), 'new-refresh')
})
