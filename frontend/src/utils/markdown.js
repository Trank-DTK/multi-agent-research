import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

const parser = new MarkdownIt({ html: false, breaks: true, linkify: true })
// Render remote images as explicit links rather than requesting them automatically.
parser.renderer.rules.image = (tokens, index) => {
  const token = tokens[index]
  const label = parser.utils.escapeHtml(token.content || '图片')
  const source = token.attrGet('src') || ''
  return parser.validateLink(source)
    ? `<a href="${parser.utils.escapeHtml(source)}" target="_blank" rel="noopener noreferrer">${label}</a>`
    : label
}
const defaultLink =
  parser.renderer.rules.link_open ||
  ((tokens, idx, options, env, self) => self.renderToken(tokens, idx, options))
parser.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  tokens[idx].attrSet('target', '_blank')
  tokens[idx].attrSet('rel', 'noopener noreferrer')
  return defaultLink(tokens, idx, options, env, self)
}
export function renderMarkdown(content = '') {
  return DOMPurify.sanitize(parser.render(String(content || '')), {
    ADD_ATTR: ['target', 'rel'],
    FORBID_TAGS: ['img', 'style', 'iframe', 'form', 'input'],
  })
}
export function renderStoredContent(content = '') {
  const text = String(content || '')
  if (!/^\s*<(?:p|div|h[1-6]|ul|ol|blockquote|pre)\b/i.test(text)) return renderMarkdown(text)
  return DOMPurify.sanitize(text, {
    FORBID_TAGS: ['img', 'style', 'iframe', 'form', 'input'],
    FORBID_ATTR: ['style'],
  })
}
