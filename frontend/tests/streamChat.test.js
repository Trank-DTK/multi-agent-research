import { test } from 'node:test'
import assert from 'node:assert/strict'
import { streamChat } from '../src/utils/streamChat.js'

globalThis.localStorage = { getItem: () => 'test-token' }
const encoder = new TextEncoder()

test('renders before completion, decodes split UTF-8, authenticates POST', async () => {
  let controller
  let sent
  globalThis.fetch = async (url, options) => {
    sent = { url, options }
    return new Response(new ReadableStream({ start(c) { controller = c } }), { headers: { 'content-type': 'text/event-stream' } })
  }
  let firstResolve
  const first = new Promise(resolve => { firstResolve = resolve })
  const events = []
  const request = streamChat('/chat/stream/', { message: 'hello' }, event => {
    events.push(event)
    if (event.token) firstResolve()
  })
  await new Promise(resolve => setImmediate(resolve))
  const bytes = encoder.encode('data: {"token":"你好"}\r\n\r\n')
  for (const byte of bytes) controller.enqueue(new Uint8Array([byte]))
  await first
  assert.deepEqual(events, [{ token: '你好' }])
  assert.equal(sent.options.headers.Authorization, 'Bearer test-token')
  assert.equal(sent.options.headers.Accept, 'text/event-stream, application/json')
  assert.equal(JSON.parse(sent.options.body).stream, true)
  controller.enqueue(encoder.encode('data: {"token":"!"}\n\ndata: [DONE]\n\n'))
  controller.close()
  await request
  assert.equal(events.map(e => e.token).join(''), '你好!')
})

test('truncation and server errors are reported instead of silent success', async () => {
  for (const body of ['data: {"token":"partial"}\n\n', 'data: {"error":"service failed"}\n\n']) {
    globalThis.fetch = async () => new Response(body, { headers: { 'content-type': 'text/event-stream' } })
    await assert.rejects(streamChat('/test/', {}, () => {}), /中断|service failed/)
  }
})

test('HTTP authentication failure remains distinguishable', async () => {
  globalThis.fetch = async () => new Response(JSON.stringify({ detail: '登录已过期' }), { status: 401 })
  await assert.rejects(streamChat('/test/', {}, () => {}), /登录已过期/)
})
