<!-- 响应式导航栏 -->
<template>
  <nav class="responsive-nav" :class="{ 'mobile': isMobile }">
    <div class="nav-brand">
      <router-link to="/dashboard">
        <span class="logo">🔬</span>
        <span class="title" v-show="!isMobile">科研协作平台</span>
      </router-link>
    </div>
    
    <button class="menu-toggle" @click="toggleMenu" v-if="isMobile">
      ☰
    </button>
    
    <div class="nav-links" :class="{ 'show': menuOpen }">
      <router-link to="/dashboard" @click="closeMenu">仪表盘</router-link>
      <router-link to="/chat" @click="closeMenu">AI对话</router-link>
      <router-link to="/agent" @click="closeMenu">智能体</router-link>
      <router-link to="/documents" @click="closeMenu">文献库</router-link>
      <router-link to="/literature" @click="closeMenu">文献助手</router-link>
      <router-link to="/collaboration" @click="closeMenu">协作研究</router-link>
      <router-link to="/analysis" @click="closeMenu">数据分析</router-link>
      <router-link to="/writing" @click="closeMenu">论文写作</router-link>
      
      <div class="nav-actions">
        <ThemeToggle />
        <button @click="logout" class="logout-btn">退出</button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useResponsive } from '@/composables/useResponsive'
import ThemeToggle from './ThemeToggle.vue'

const router = useRouter()
const { isMobile } = useResponsive()
const menuOpen = ref(false)

const toggleMenu = () => {
  menuOpen.value = !menuOpen.value
}

const closeMenu = () => {
  menuOpen.value = false
}

const logout = () => {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  router.push('/login')
}
</script>

<style scoped>
.responsive-nav {
  background-color: var(--header-bg);
  color: var(--header-text);
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-brand a {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: inherit;
  font-size: 18px;
  font-weight: bold;
}

.logo {
  font-size: 24px;
}

.menu-toggle {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: inherit;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-links a {
  text-decoration: none;
  color: inherit;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-links a:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-links a.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-left: 20px;
}

.logout-btn {
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: inherit;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.logout-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

/* 移动端样式 */
.responsive-nav.mobile .nav-links {
  position: fixed;
  top: 60px;
  left: -100%;
  width: 80%;
  height: calc(100vh - 60px);
  background-color: var(--bg-primary);
  flex-direction: column;
  align-items: stretch;
  transition: left 0.3s ease;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
}

.responsive-nav.mobile .nav-links.show {
  left: 0;
}

.responsive-nav.mobile .nav-links a {
  padding: 15px 20px;
  border-bottom: 1px solid var(--border-color);
}

.responsive-nav.mobile .nav-actions {
  margin: 20px;
  flex-direction: column;
  gap: 10px;
}

.responsive-nav.mobile .nav-actions button {
  width: 100%;
}
</style>