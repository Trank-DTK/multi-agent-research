<template>
  <PublicFrame auth>
    <main class="auth-page">
      <div class="auth-scene" aria-hidden="true">
        <ResearchField kind="auth" />
        <div class="auth-scene-fade" />
      </div>
      <div class="auth-layout">
        <section class="auth-story">
          <RouterLink class="back-link" to="/">← 返回首页</RouterLink>
          <span class="auth-kicker">属于你的科研空间</span>
          <h1>让好奇心，<br /><span>有处安放。</span></h1>
          <p>文献中的线索，数据中的证据，<br />想法与想法之间，尚未发现的连接。</p>
          <div class="auth-story-bottom">
            <span class="auth-line" /><span>从这里，走向下一个发现。</span>
          </div>
        </section>
        <section class="auth-card" aria-labelledby="auth-heading">
          <div class="auth-card-top">
            <span class="auth-icon"
              ><svg aria-hidden="true"><use href="#public-spark" /></svg
            ></span>
            <RouterLink to="/" class="preview-link">了解平台 ↗</RouterLink>
          </div>
          <div class="auth-heading">
            <h2 id="auth-heading">{{ title }}</h2>
            <p>{{ description }}</p>
          </div>
          <slot />
          <div class="auth-divider"><span /><small>开启你的研究旅程</small><span /></div>
          <p class="auth-switch"><slot name="footer" /></p>
        </section>
      </div>
      <div class="auth-footer">研知协作 · 连接知识，让探索更进一步</div>
    </main>
  </PublicFrame>
</template>
<script setup>
import PublicFrame from './PublicFrame.vue'
import ResearchField from './ResearchField.vue'
defineProps({
  title: { type: String, required: true },
  description: { type: String, required: true },
})
</script>
