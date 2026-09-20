<template>
  <!-- Both renderers sanitize before the sole HTML sink. -->
  <div class="markdown-body" v-html="rendered"></div>
</template>
<script setup>
import { computed } from 'vue'
import { renderMarkdown, renderStoredContent } from '@/utils/markdown'
const props = defineProps({ content: { type: String, default: '' }, richText: Boolean })
const rendered = computed(() =>
  props.richText ? renderStoredContent(props.content) : renderMarkdown(props.content),
)
</script>
<style>
.markdown-body {
  min-width: 0;
  max-width: 100%;
  overflow-wrap: anywhere;
  line-height: 1.8;
  white-space: normal !important;
}
.markdown-body > :first-child {
  margin-top: 0;
}
.markdown-body > :last-child {
  margin-bottom: 0;
}
.markdown-body p {
  margin: 0.65em 0;
}
.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  color: inherit;
  margin: 1.1em 0 0.5em;
  line-height: 1.4;
  font-weight: 650;
}
.markdown-body h1 {
  font-size: 1.6em;
}
.markdown-body h2 {
  font-size: 1.35em;
}
.markdown-body h3 {
  font-size: 1.15em;
}
.markdown-body ul,
.markdown-body ol {
  padding-left: 1.6em;
  margin: 0.6em 0;
}
.markdown-body ul {
  list-style: disc;
}
.markdown-body ol {
  list-style: decimal;
}
.markdown-body li + li {
  margin-top: 0.3em;
}
.markdown-body blockquote {
  border-left: 3px solid #528ef2;
  padding: 0.25em 1em;
  margin: 1em 0;
  background: var(--bg-primary);
  color: var(--text-secondary);
}
.markdown-body pre {
  overflow-x: auto;
  max-width: 100%;
  padding: 16px;
  border-radius: 10px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  white-space: pre;
  line-height: 1.6;
}
.markdown-body code {
  font-family: Consolas, 'Courier New', monospace;
  font-size: 0.9em;
  background: var(--bg-primary);
  border-radius: 4px;
  padding: 0.15em 0.35em;
}
.markdown-body pre code {
  padding: 0;
  background: transparent;
  white-space: pre;
}
.markdown-body table {
  display: block;
  width: max-content;
  max-width: 100%;
  overflow-x: auto;
  border-collapse: collapse;
  margin: 1em 0;
}
.markdown-body th,
.markdown-body td {
  border: 1px solid var(--border-color);
  padding: 8px 14px;
  text-align: left;
  min-width: 80px;
}
.markdown-body th {
  background: var(--bg-primary);
  font-weight: 650;
}
.markdown-body a {
  color: #528ef2;
  text-decoration: underline;
  text-underline-offset: 3px;
}
.markdown-body hr {
  border: 0;
  border-top: 1px solid var(--border-color);
  margin: 1.2em 0;
}
</style>
