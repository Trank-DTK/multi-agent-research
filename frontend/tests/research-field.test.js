import { test } from 'node:test'
import assert from 'node:assert/strict'
import { JSDOM } from 'jsdom'
import { mountResearchField } from '../src/utils/researchField.js'

function scene({ reduced = false, contextMissing = false } = {}) {
  const dom = new JSDOM(
    '<div class="public-shell" data-theme="dark" data-motion="full"><canvas></canvas></div>',
    { pretendToBeVisual: true },
  )
  const { window } = dom
  const canvas = window.document.querySelector('canvas')
  const root = canvas.parentElement
  const frames = new Map(),
    observers = []
  let frameId = 0,
    arcs = 0
  window.requestAnimationFrame = (callback) => {
    frames.set(++frameId, callback)
    return frameId
  }
  window.cancelAnimationFrame = (id) => frames.delete(id)
  const media = new window.EventTarget()
  media.matches = reduced
  window.matchMedia = () => media
  window.ResizeObserver = class {
    constructor(callback) {
      this.callback = callback
      this.disconnected = false
      observers.push(this)
    }
    observe() {}
    disconnect() {
      this.disconnected = true
    }
  }
  window.IntersectionObserver = class extends window.ResizeObserver {}
  canvas.getBoundingClientRect = () => ({ width: 1000, height: 800 })
  canvas.getContext = () =>
    contextMissing
      ? null
      : {
          setTransform() {},
          clearRect() {},
          fillRect() {},
          beginPath() {},
          stroke() {},
          fill() {},
          moveTo(x, y) {
            assert.ok(Number.isFinite(x) && Number.isFinite(y))
          },
          lineTo(x, y) {
            assert.ok(Number.isFinite(x) && Number.isFinite(y))
          },
          arc(x, y, radius) {
            assert.ok(Number.isFinite(x) && Number.isFinite(y) && radius > 0)
            arcs++
          },
          createRadialGradient() {
            return { addColorStop() {} }
          },
        }
  return {
    dom,
    window,
    canvas,
    root,
    frames,
    observers,
    media,
    get arcs() {
      return arcs
    },
  }
}

test('field draws finite particles, pauses offscreen and on hidden tabs, releases resources on disposal', async () => {
  const s = scene()
  const dispose = mountResearchField(s.canvas)
  assert.ok(s.arcs >= 1700)
  assert.equal(s.frames.size, 1)
  s.observers[1].callback([{ isIntersecting: false }])
  assert.equal(s.frames.size, 0)
  s.observers[1].callback([{ isIntersecting: true }])
  assert.equal(s.frames.size, 1)
  Object.defineProperty(s.window.document, 'hidden', { configurable: true, value: true })
  s.window.document.dispatchEvent(new s.window.Event('visibilitychange'))
  assert.equal(s.frames.size, 0)
  Object.defineProperty(s.window.document, 'hidden', { configurable: true, value: false })
  s.window.document.dispatchEvent(new s.window.Event('visibilitychange'))
  assert.equal(s.frames.size, 1)
  s.root.dataset.motion = 'static'
  await new Promise((resolve) => s.window.queueMicrotask(resolve))
  assert.equal(s.frames.size, 0)
  s.root.dataset.motion = 'full'
  await new Promise((resolve) => s.window.queueMicrotask(resolve))
  assert.equal(s.frames.size, 1)
  dispose()
  assert.equal(s.frames.size, 0)
  assert.ok(s.observers.every((observer) => observer.disconnected))
  const before = s.arcs
  s.window.document.dispatchEvent(new s.window.Event('visibilitychange'))
  s.window.dispatchEvent(new s.window.Event('resize'))
  s.media.dispatchEvent(new s.window.Event('change'))
  s.root.dataset.theme = 'light'
  await new Promise((resolve) => s.window.queueMicrotask(resolve))
  assert.equal(s.arcs, before)
  assert.equal(s.frames.size, 0)
  s.dom.window.close()
})

test('reduced motion renders a static field and handles later system preference changes', () => {
  const s = scene({ reduced: true })
  const dispose = mountResearchField(s.canvas)
  assert.ok(s.arcs >= 1700)
  assert.equal(s.frames.size, 0)
  s.media.matches = false
  s.media.dispatchEvent(new s.window.Event('change'))
  assert.equal(s.frames.size, 1)
  s.media.matches = true
  s.media.dispatchEvent(new s.window.Event('change'))
  assert.equal(s.frames.size, 0)
  dispose()
  s.dom.window.close()
})

test('canvas unavailable degrades without observers, listeners or animation frames', () => {
  const s = scene({ contextMissing: true })
  assert.doesNotThrow(() => mountResearchField(s.canvas)())
  assert.equal(s.frames.size, 0)
  assert.equal(s.observers.length, 0)
  s.dom.window.close()
})
