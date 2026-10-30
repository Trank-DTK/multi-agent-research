import { readFile } from 'node:fs/promises'
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { parse, compileScript } from '@vue/compiler-sfc'
import { JSDOM } from 'jsdom'

test('actual auth forms preserve requests, loading, sessions and cancellation', async () => {
  const dom = new JSDOM('<div id="app"></div>', { url: 'http://localhost/' })
  for (const name of [
    'window',
    'document',
    'Element',
    'HTMLElement',
    'SVGElement',
    'Node',
    'Event',
    'localStorage',
  ])
    globalThis[name] = dom.window[name]
  const vue = await import('vue')
  const calls = [],
    routes = []
  let response
  globalThis.__authHarness = {
    axios: {
      post: (...args) => {
        calls.push(args)
        return new Promise((resolve) => {
          response = resolve
        })
      },
    },
    router: { replace: (path) => routes.push(path) },
    AuthShell: {
      setup(_, { slots }) {
        return () => vue.h('main', [slots.default?.(), slots.footer?.()])
      },
    },
  }
  const flush = async () => {
    await new Promise((resolve) => setImmediate(resolve))
    await vue.nextTick()
  }
  async function mount(name) {
    const file = new URL(`../src/views/${name}.vue`, import.meta.url)
    const { descriptor } = parse(await readFile(file, 'utf8'))
    let code = compileScript(descriptor, { id: `check-${name}`, inlineTemplate: true }).content
    code = code
      .replace(
        /from ['"]vue['"]/g,
        `from '${new URL('../node_modules/vue/index.mjs', import.meta.url).href}'`,
      )
      .replace(
        /import \{ useRouter \} from ['"]vue-router['"]/,
        'const useRouter = () => globalThis.__authHarness.router',
      )
      .replace(/import axios from ['"]@\/axios['"]/, 'const axios = globalThis.__authHarness.axios')
      .replace(
        /import AuthShell from ['"]@\/components\/AuthShell.vue['"]/,
        'const AuthShell = globalThis.__authHarness.AuthShell',
      )
      .replace(
        /from ['"]@\/utils\/auth['"]/,
        `from '${new URL('../src/utils/auth.js', import.meta.url).href}'`,
      )
    const module = await import(
      `data:text/javascript;base64,${Buffer.from(code).toString('base64')}`
    )
    const app = vue.createApp(module.default)
    app.component('RouterLink', {
      props: ['to'],
      setup(props, { slots }) {
        return () => vue.h('a', { href: props.to }, slots.default?.())
      },
    })
    app.mount(document.getElementById('app'))
    return app
  }
  const input = (selector, value) => {
    const field = document.querySelector(selector)
    field.value = value
    field.dispatchEvent(new Event('input', { bubbles: true }))
  }
  const submit = () =>
    document
      .querySelector('form')
      .dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))

  let app = await mount('login')
  input('input[autocomplete="username"]', ' researcher ')
  input('input[autocomplete="current-password"]', 'a-private-password')
  submit()
  submit()
  await flush()
  assert.equal(calls.length, 1)
  assert.equal(calls[0][0], '/auth/login/')
  assert.deepEqual(calls[0][1], { username: 'researcher', password: 'a-private-password' })
  assert.equal(document.querySelector('[type="submit"]').disabled, true)
  response({ data: { access: 'test-access', refresh: 'test-refresh' } })
  await flush()
  assert.equal(localStorage.getItem('access'), 'test-access')
  assert.deepEqual(routes, ['/dashboard'])
  app.unmount()

  app = await mount('login')
  input('input[autocomplete="username"]', 'researcher')
  input('input[autocomplete="current-password"]', 'password')
  submit()
  await flush()
  app.unmount()
  assert.equal(calls[1][2].signal.aborted, true)
  response({ data: { access: 'must-not-save', refresh: 'must-not-save' } })
  await flush()
  assert.equal(localStorage.getItem('access'), 'test-access')
  assert.deepEqual(routes, ['/dashboard'])

  app = await mount('register')
  input('input[autocomplete="username"]', 'new-researcher')
  input('input[autocomplete="email"]', 'researcher@example.org')
  const passwords = document.querySelectorAll('input[autocomplete="new-password"]')
  passwords[0].value = 'secure-password'
  passwords[0].dispatchEvent(new Event('input'))
  passwords[1].value = 'secure-password'
  passwords[1].dispatchEvent(new Event('input'))
  submit()
  submit()
  await flush()
  assert.equal(calls.length, 3)
  assert.equal(calls[2][0], '/auth/register/')
  assert.deepEqual(calls[2][1], {
    username: 'new-researcher',
    email: 'researcher@example.org',
    password: 'secure-password',
    password2: 'secure-password',
    first_name: '',
    last_name: '',
  })
  response({ data: {} })
  await flush()
  assert.match(document.querySelector('[role="status"]').textContent, /注册成功/)
  assert.equal(document.querySelector('[type="submit"]').disabled, true)
  app.unmount()
  dom.window.close()
  delete globalThis.__authHarness
})
