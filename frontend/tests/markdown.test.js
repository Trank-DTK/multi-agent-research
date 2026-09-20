import { test } from 'node:test'
import assert from 'node:assert/strict'
import { JSDOM } from 'jsdom'
globalThis.window = new JSDOM('').window
const { renderMarkdown, renderStoredContent } = await import('../src/utils/markdown.js')
const doc = html => new JSDOM(html).window.document

test('renders headings, nested lists, tables, quotes and fenced code', () => {
  const output = doc(renderMarkdown('# 结论\n\n**证据**\n\n1. 方法\n   - 变量\n\n> 引用\n\n| 指标 | 数值 |\n| --- | --- |\n| 准确率 | 0.9 |\n\n```python\nprint("hello")\n```'))
  for (const selector of ['h1', 'strong', 'ol li ul li', 'blockquote', 'table tbody td', 'pre code.language-python']) assert.ok(output.querySelector(selector), selector)
})
test('handles incomplete streaming Markdown and later completes it', () => {
  assert.equal(doc(renderMarkdown('```python\nprint(')).querySelector('pre code').textContent.trimEnd(), 'print(')
  assert.ok(doc(renderMarkdown('**结果**')).querySelector('strong'))
})
test('blocks active HTML, unsafe URLs and automatic remote images', () => {
  const output = doc(renderMarkdown('<script>alert(1)</script>\n<img src=x onerror=alert(1)>\n[bad](javascript:alert(1))\n![远程图片](https://example.com/image.png)'))
  assert.equal(output.querySelector('script,img,iframe,[onerror],a[href^="javascript:"]'), null)
  assert.equal(output.querySelector('a').getAttribute('rel'), 'noopener noreferrer')
})
test('preserves existing editor HTML but removes injected handlers', () => {
  const output = doc(renderStoredContent('<p onclick="alert(1)"><strong>论文</strong></p><script>alert(1)</script>'))
  assert.equal(output.querySelector('strong').textContent, '论文')
  assert.equal(output.querySelector('script,[onclick]'), null)
  assert.ok(doc(renderStoredContent('## Markdown 章节')).querySelector('h2'))
})
