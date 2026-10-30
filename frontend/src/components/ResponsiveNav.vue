<template>
  <button
    class="mobile-nav-toggle"
    :aria-expanded="menuOpen"
    aria-controls="workspace-nav"
    @click="menuOpen = !menuOpen"
  >
    <el-icon class="mobile-menu-icon"><Menu /></el-icon>
    <img src="/favicon.ico" alt="" class="mobile-brand-mark" />
    <span>研知协作</span>
    <small>科研工作台</small>
  </button>
  <button v-if="menuOpen" class="nav-backdrop" aria-label="关闭导航" @click="menuOpen = false" />
  <aside
    id="workspace-nav"
    class="workspace-nav"
    :class="{ open: menuOpen }"
    @keydown.esc="menuOpen = false"
  >
    <router-link to="/dashboard" class="brand" @click="menuOpen = false">
      <span class="brand-emblem"><img class="brand-mark" src="/favicon.ico" alt="" /></span>
      <span class="brand-name">研知协作<small>RESEARCH WORKSPACE</small></span>
    </router-link>
    <p class="nav-caption"><span>科研空间</span><span class="caption-line" aria-hidden="true" /></p>
    <nav aria-label="主要导航">
      <router-link
        v-for="item in navigation"
        :key="item.path"
        :to="item.path"
        @click="menuOpen = false"
      >
        <span class="nav-icon"
          ><el-icon><component :is="item.icon" /></el-icon
        ></span>
        <span>{{ item.label }}</span>
        <span class="nav-active-marker" aria-hidden="true" />
      </router-link>
    </nav>
    <div class="nav-footer">
      <div class="workspace-note">
        <span class="note-icon"
          ><el-icon><Connection /></el-icon
        ></span>
        <div>连接知识与灵感<small>让研究有序推进</small></div>
      </div>
      <div class="account-menu" @keydown.esc="accountOpen = false">
        <div v-if="accountOpen" id="account-popup" class="account-popup">
          <span class="account-label">个人账户</span>
          <p>{{ user?.email || '个人科研空间' }}</p>
          <button @click="theme.toggleTheme()">
            <el-icon><component :is="theme.isDark ? 'Sunny' : 'Moon'" /></el-icon>
            {{ theme.isDark ? '切换亮色背景' : '切换暗色背景' }}
          </button>
          <router-link to="/settings" @click="closeMenus">
            <el-icon><Setting /></el-icon>设置与模型供应商
          </router-link>
          <router-link to="/" @click="closeMenus"
            ><el-icon><House /></el-icon>产品首页</router-link
          >
          <button class="danger-text" @click="logout">
            <el-icon><SwitchButton /></el-icon>退出登录
          </button>
        </div>
        <button
          class="account-trigger"
          :class="{ active: accountOpen }"
          :aria-expanded="accountOpen"
          aria-controls="account-popup"
          @click="accountOpen = !accountOpen"
        >
          <span class="user-avatar">{{ (user?.username || 'U').slice(0, 1).toUpperCase() }}</span
          ><span class="account-identity"
            ><strong>{{ user?.username || '个人账户' }}</strong
            ><small>个人科研空间</small></span
          ><el-icon class="account-chevron"><ArrowUp /></el-icon>
        </button>
      </div>
    </div>
  </aside>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { navigation } from '@/navigation'
import axios from '@/axios'
import { useThemeStore } from '@/stores/theme'
const router = useRouter()
const menuOpen = ref(false)
const accountOpen = ref(false),
  user = ref(null)
const theme = useThemeStore()
onMounted(async () => {
  try {
    user.value = (await axios.get('/auth/user/')).data
  } catch {
    user.value = null
  }
})
const closeMenus = () => {
  accountOpen.value = false
  menuOpen.value = false
}
const logout = () => {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  router.replace('/login')
}
</script>
<style scoped>
.workspace-nav {
  position: fixed;
  inset: 0 auto 0 0;
  width: var(--nav-width, 232px);
  overflow-y: auto;
  overscroll-behavior: contain;
  background: var(--nav-surface, var(--bg-secondary));
  border-right: 1px solid var(--border-color);
  padding: 30px 16px 18px;
  display: flex;
  flex-direction: column;
  z-index: 100;
}
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-primary);
  text-decoration: none;
  padding: 0 8px 30px;
}
.brand-emblem {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 45px;
  height: 45px;
  padding: 3px;
  border: 1px solid var(--accent-line, var(--border-color));
  border-radius: 14px;
  background: var(--bg-secondary);
  box-shadow: 0 5px 14px #173c7610;
}
.brand-mark {
  width: 37px;
  height: 37px;
  object-fit: contain;
  border-radius: 10px;
}
.brand-name {
  font-size: 19px;
  font-weight: 750;
  letter-spacing: 0.2px;
}
.brand small {
  display: block;
  font-size: 7px;
  font-weight: 650;
  letter-spacing: 1.7px;
  color: var(--text-tertiary);
  margin-top: 7px;
  white-space: nowrap;
}
.nav-caption {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 10px;
  font-weight: 600;
  color: var(--text-tertiary);
  letter-spacing: 2px;
  padding: 4px 12px;
  margin: 4px 0 14px;
}
.caption-line {
  height: 1px;
  flex: 1;
  background: var(--border-color);
}
nav {
  display: grid;
  gap: 6px;
}
nav a {
  position: relative;
  display: flex;
  align-items: center;
  gap: 11px;
  min-height: 49px;
  padding: 8px 12px;
  border: 1px solid transparent;
  border-radius: 12px;
  text-decoration: none;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  transition:
    background 180ms ease,
    color 180ms ease,
    border-color 180ms ease;
}
nav a::before {
  content: '';
  position: absolute;
  left: -1px;
  top: 14px;
  bottom: 14px;
  width: 3px;
  border-radius: 0 4px 4px 0;
  background: var(--accent-gradient, var(--success-color));
  opacity: 0;
  transition: opacity 180ms ease;
}
nav a:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}
nav a.router-link-exact-active {
  background: var(--accent-soft);
  border-color: var(--accent-line, var(--border-color));
  color: var(--success-color);
  font-weight: 650;
}
nav a.router-link-exact-active::before {
  opacity: 1;
}
.nav-icon {
  display: grid;
  place-items: center;
  width: 31px;
  height: 31px;
  flex-shrink: 0;
  border-radius: 9px;
  transition:
    background 180ms ease,
    transform 180ms ease;
}
nav a:hover .nav-icon {
  transform: translateX(2px);
}
nav a.router-link-exact-active .nav-icon {
  background: var(--bg-secondary);
  box-shadow: 0 2px 7px #173c760b;
}
nav .el-icon {
  font-size: 18px;
}
.nav-active-marker {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  margin-left: auto;
  background: currentColor;
  opacity: 0;
}
.router-link-exact-active .nav-active-marker {
  opacity: 0.75;
}
.nav-footer {
  margin-top: auto;
  padding-top: 28px;
}
.workspace-note {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 12px;
  border-top: 1px solid var(--border-color);
  font-size: 11px;
  color: var(--text-secondary);
}
.note-icon {
  display: grid;
  place-items: center;
  width: 29px;
  height: 29px;
  flex-shrink: 0;
  border: 1px solid var(--accent-line, var(--border-color));
  border-radius: 9px;
  background: var(--accent-soft);
  color: var(--success-color);
  font-size: 15px;
}
.workspace-note small {
  display: block;
  color: var(--text-tertiary);
  font-size: 10px;
  margin-top: 5px;
}
.account-menu {
  position: relative;
  margin-top: 6px;
}
.account-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: 14px;
  width: 100%;
  padding: 11px;
  text-align: left;
  font-size: 13px;
  cursor: pointer;
  transition:
    border-color 180ms ease,
    background 180ms ease;
}
.account-trigger:hover,
.account-trigger.active {
  border-color: var(--accent-line, var(--success-color));
  background: var(--accent-soft);
}
.account-identity {
  min-width: 0;
  flex: 1;
}
.account-identity strong {
  display: block;
  font-size: 12px;
  font-weight: 650;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.account-trigger small {
  display: block;
  font-size: 10px;
  color: var(--text-tertiary);
  margin-top: 5px;
}
.user-avatar {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  background: var(--accent-gradient, #326bd6);
  color: #fff;
  width: 34px;
  height: 36px;
  border-radius: 11px;
  font-size: 13px;
  font-weight: 700;
}
.account-chevron {
  margin-left: auto;
  font-size: 11px;
  color: var(--text-tertiary);
  transition: transform 180ms ease;
}
.account-trigger.active .account-chevron {
  transform: rotate(180deg);
}
.account-popup {
  background: var(--bg-secondary);
  border: 1px solid var(--accent-line, var(--border-color));
  border-radius: 16px;
  padding: 9px;
  margin-bottom: 10px;
  box-shadow: var(--surface-shadow, var(--card-shadow));
}
.account-label {
  display: block;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1px;
  color: var(--text-tertiary);
  padding: 7px 9px 0;
}
.account-popup p {
  font-size: 11px;
  color: var(--text-secondary);
  padding: 0 9px 12px;
  margin: 7px 0;
  border-bottom: 1px solid var(--border-color);
  overflow-wrap: anywhere;
  line-height: 1.6;
}
.account-popup button,
.account-popup a {
  display: flex;
  align-items: center;
  gap: 9px;
  width: 100%;
  padding: 11px 9px;
  border: 0;
  background: transparent;
  text-align: left;
  color: var(--text-primary);
  text-decoration: none;
  font-size: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 180ms ease;
}
.account-popup .el-icon {
  font-size: 16px;
  color: var(--text-secondary);
}
.account-popup button:hover,
.account-popup a:hover {
  background: var(--accent-soft);
}
.account-popup .danger-text,
.account-popup .danger-text .el-icon {
  color: var(--error-color);
}
.brand:focus-visible,
nav a:focus-visible,
.account-trigger:focus-visible,
.account-popup button:focus-visible,
.account-popup a:focus-visible,
.mobile-nav-toggle:focus-visible {
  outline: 2px solid var(--success-color);
  outline-offset: 3px;
}
.mobile-nav-toggle,
.nav-backdrop {
  display: none;
}
@media (max-width: 1000px) {
  .workspace-nav {
    transform: translateX(-100%);
    visibility: hidden;
    transition: transform 200ms ease;
    box-shadow: var(--surface-shadow, var(--card-shadow));
  }
  .workspace-nav.open {
    transform: translateX(0);
    visibility: visible;
  }
  .mobile-nav-toggle {
    display: flex;
    gap: 11px;
    align-items: center;
    position: sticky;
    top: 0;
    width: 100%;
    height: 56px;
    padding: 0 18px;
    background: var(--nav-surface, var(--bg-secondary));
    border: 0;
    border-bottom: 1px solid var(--accent-line, var(--border-color));
    color: var(--text-primary);
    font-size: 14px;
    font-weight: 650;
    z-index: 90;
    cursor: pointer;
  }
  .mobile-menu-icon {
    font-size: 19px;
    color: var(--text-secondary);
    margin-right: 3px;
  }
  .mobile-brand-mark {
    width: 27px;
    height: 27px;
    border-radius: 8px;
  }
  .mobile-nav-toggle small {
    margin-left: auto;
    font-size: 10px;
    font-weight: 400;
    letter-spacing: 1px;
    color: var(--text-tertiary);
  }
  .nav-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    border: 0;
    background: #07142680;
    backdrop-filter: blur(4px);
    z-index: 99;
  }
}
@media (max-height: 800px) {
  .workspace-nav {
    padding-top: 20px;
    padding-bottom: 14px;
  }
  .brand {
    padding-bottom: 20px;
  }
  .nav-caption {
    margin-bottom: 10px;
  }
  nav {
    gap: 4px;
  }
  nav a {
    min-height: 44px;
    padding-top: 5px;
    padding-bottom: 5px;
  }
  .nav-footer {
    padding-top: 18px;
  }
  .workspace-note {
    padding-top: 12px;
    padding-bottom: 12px;
  }
}
@media (prefers-reduced-motion: reduce) {
  *,
  *::before {
    transition: none !important;
  }
}
</style>
