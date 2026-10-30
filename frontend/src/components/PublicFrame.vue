<template>
  <div
    ref="shell"
    class="public-shell"
    :class="{ 'auth-mode': auth, 'motion-ready': motionReady }"
    :data-theme="theme.isDark ? 'dark' : 'light'"
    :data-motion="motionPaused || reduced ? 'static' : 'full'"
  >
    <!-- Public symbols are namespaced so workplace icons cannot collide with them. -->
    <svg class="sprite" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
      <symbol id="public-arrow" viewBox="0 0 24 24">
        <path d="M4 12h15M13 5l7 7-7 7" />
      </symbol>
      <symbol id="public-file" viewBox="0 0 24 24">
        <path d="M14 3H5v18h14V8zM14 3v5h5M8 12h8m-8 4h6" />
      </symbol>
      <symbol id="public-network" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="3" />
        <circle cx="4" cy="4" r="2" />
        <circle cx="20" cy="5" r="2" />
        <circle cx="5" cy="20" r="2" />
        <circle cx="20" cy="20" r="2" />
        <path d="m6 6 4 4m4 0 4-4M10 14l-4 4m8-4 4 4" />
      </symbol>
      <symbol id="public-chart" viewBox="0 0 24 24">
        <path d="M4 3v17h17M8 15v-4m5 4V6m5 9v6" />
      </symbol>
      <symbol id="public-pen" viewBox="0 0 24 24">
        <path d="m4 16 12-12 4 4L8 20l-5 1zM13 7l4 4" />
      </symbol>
      <symbol id="public-spark" viewBox="0 0 24 24">
        <path d="m12 2 3 7 7 3-7 3-3 7-3-7-7-3 7-3z" />
      </symbol>
      <symbol id="public-sun" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1 1m12 12 1 1M5 19l1-1M18 6l1-1" />
      </symbol>
      <symbol id="public-menu" viewBox="0 0 24 24">
        <path d="M4 7h16M4 12h16M4 17h16" />
      </symbol>
      <symbol id="public-tune" viewBox="0 0 24 24">
        <path d="M3 6h18M3 12h18M3 18h18" />
        <circle cx="8" cy="6" r="2" />
        <circle cx="16" cy="12" r="2" />
        <circle cx="9" cy="18" r="2" />
      </symbol>
      <symbol id="public-eye" viewBox="0 0 24 24">
        <path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z" />
        <circle cx="12" cy="12" r="3" />
      </symbol>
    </svg>
    <div class="progress-line" :style="{ transform: `scaleX(${progress})` }" aria-hidden="true" />
    <header class="site-header" :class="{ scrolled }">
      <RouterLink class="brand" to="/" aria-label="研知协作首页">
        <span class="brand-emblem"><img src="/favicon.ico" alt="研知协作 Logo" /></span>
        <strong>研知协作<span>RESEARCH WORKSPACE</span></strong>
      </RouterLink>
      <nav class="header-nav" aria-label="网站导航">
        <RouterLink to="/#capabilities">探索能力</RouterLink>
        <RouterLink to="/#workspace">工作空间</RouterLink>
        <RouterLink to="/#workflow">研究流程</RouterLink>
      </nav>
      <div class="header-actions">
        <button
          type="button"
          class="icon-button motion-button"
          :disabled="reduced"
          :aria-label="
            reduced ? '系统已启用减少动态效果' : motionPaused ? '播放动态效果' : '暂停动态效果'
          "
          :aria-pressed="motionPaused || reduced"
          @click="motionPaused = !motionPaused"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path v-if="motionPaused || reduced" d="m9 5 10 7-10 7z" />
            <path v-else d="M8 5v14M16 5v14" />
          </svg>
        </button>
        <button
          type="button"
          class="icon-button"
          :aria-label="theme.isDark ? '切换亮色主题' : '切换暗色主题'"
          @click="theme.toggleTheme()"
        >
          <svg aria-hidden="true"><use href="#public-sun" /></svg>
        </button>
        <RouterLink v-if="!authenticated" to="/login" class="login-link">登录</RouterLink>
        <RouterLink
          :to="authenticated ? '/dashboard' : '/register'"
          class="button button-small button-white"
        >
          {{ authenticated ? '进入工作台' : '开始探索' }}
          <svg aria-hidden="true"><use href="#public-arrow" /></svg>
        </RouterLink>
        <button
          ref="menuButton"
          type="button"
          class="icon-button mobile-menu-button"
          aria-label="打开菜单"
          :aria-expanded="menuOpen"
          aria-controls="public-mobile-menu"
          @click="menuOpen = !menuOpen"
        >
          <svg aria-hidden="true"><use href="#public-menu" /></svg>
        </button>
      </div>
    </header>
    <nav
      id="public-mobile-menu"
      ref="mobileMenu"
      class="mobile-menu"
      aria-label="手机导航"
      :hidden="!menuOpen"
    >
      <RouterLink to="/#capabilities" @click="closeMenu">探索能力</RouterLink>
      <RouterLink to="/#workspace" @click="closeMenu">工作空间</RouterLink>
      <RouterLink to="/#workflow" @click="closeMenu">研究流程</RouterLink>
      <RouterLink :to="authenticated ? '/dashboard' : '/login'" @click="closeMenu">{{
        authenticated ? '进入工作台' : '登录'
      }}</RouterLink>
      <RouterLink v-if="!authenticated" to="/register" @click="closeMenu">创建账户</RouterLink>
    </nav>
    <slot />
  </div>
</template>
<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import '@/styles/public.css'
defineProps({ auth: Boolean })
const theme = useThemeStore()
const route = useRoute()
const authenticated = Boolean(localStorage.getItem('access'))
const shell = ref(null),
  menuButton = ref(null),
  mobileMenu = ref(null)
const menuOpen = ref(false),
  motionPaused = ref(false),
  reduced = ref(false)
const motionReady = ref(false),
  scrolled = ref(false),
  progress = ref(0)
let scrollFrame = null,
  media
const closeMenu = () => {
  const returnFocus = mobileMenu.value?.contains(document.activeElement)
  menuOpen.value = false
  if (returnFocus) menuButton.value?.focus()
}
const onKey = (event) => {
  if (event.key === 'Escape') closeMenu()
}
const onOutside = (event) => {
  if (!mobileMenu.value?.contains(event.target) && !menuButton.value?.contains(event.target))
    closeMenu()
}
const updateScroll = () => {
  scrollFrame = null
  scrolled.value = window.scrollY > 24
  const distance = document.documentElement.scrollHeight - window.innerHeight
  progress.value = distance > 0 ? Math.max(0, Math.min(1, window.scrollY / distance)) : 0
}
const onScroll = () => {
  if (scrollFrame === null) scrollFrame = requestAnimationFrame(updateScroll)
}
const onMotion = () => {
  reduced.value = media.matches
}
watch(() => route.fullPath, closeMenu)
onMounted(() => {
  motionReady.value = Boolean(window.IntersectionObserver)
  media = window.matchMedia('(prefers-reduced-motion: reduce)')
  onMotion()
  media.addEventListener('change', onMotion)
  window.addEventListener('scroll', onScroll, { passive: true })
  document.addEventListener('keydown', onKey)
  document.addEventListener('pointerdown', onOutside)
  updateScroll()
})
onBeforeUnmount(() => {
  if (scrollFrame !== null) cancelAnimationFrame(scrollFrame)
  window.removeEventListener('scroll', onScroll)
  document.removeEventListener('keydown', onKey)
  document.removeEventListener('pointerdown', onOutside)
  media?.removeEventListener('change', onMotion)
})
</script>
