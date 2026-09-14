<template>
  <button
    class="mobile-nav-toggle"
    :aria-expanded="menuOpen"
    aria-controls="workspace-nav"
    @click="menuOpen = !menuOpen"
  >
    ☰ <span>科研工作台</span>
  </button>
  <button v-if="menuOpen" class="nav-backdrop" aria-label="关闭导航" @click="menuOpen = false" />
  <aside
    id="workspace-nav"
    class="workspace-nav"
    :class="{ open: menuOpen }"
    @keydown.esc="menuOpen = false"
  >
    <router-link to="/dashboard" class="brand" @click="menuOpen = false"
      ><img class="brand-mark" src="/favicon.ico" alt="研知协作 logo" /><span
        >研知协作<small>RESEARCH WORKSPACE</small></span
      ></router-link
    >
    <p class="nav-caption">科研空间</p>
    <nav aria-label="主要导航">
      <router-link
        v-for="item in navigation"
        :key="item.path"
        :to="item.path"
        @click="menuOpen = false"
        ><el-icon><component :is="item.icon" /></el-icon>{{ item.label }}</router-link
      >
    </nav>
    <div class="nav-footer">
      <div class="workspace-note">
        <el-icon><Connection /></el-icon>
        <div>连接知识与灵感<small>让研究有序推进</small></div>
      </div>
      <div class="account-menu" @keydown.esc="accountOpen = false">
        <div v-if="accountOpen" class="account-popup">
          <p>{{ user?.email || '个人科研空间' }}</p>
          <button @click="theme.toggleTheme()">
            {{ theme.isDark ? '切换亮色背景' : '切换暗色背景' }}</button
          ><router-link
            to="/settings"
            @click="closeMenus"
            >设置与模型供应商</router-link
          ><button class="danger-text" @click="logout">退出登录</button>
        </div>
        <button
          class="account-trigger"
          :aria-expanded="accountOpen"
          @click="accountOpen = !accountOpen"
        >
          <span class="user-avatar">{{ (user?.username || 'U').slice(0, 1).toUpperCase() }}</span
          ><span>{{ user?.username || '个人账户' }}<small>个人科研空间</small></span
          ><span class="account-chevron">⌃</span>
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
const closeMenus=()=>{accountOpen.value=false;menuOpen.value=false}
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
  width: 232px;
  overflow-y: auto;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  padding: 30px 18px;
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
  font-size: 19px;
  font-weight: 750;
  padding: 0 10px 30px;
}
.brand-mark {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  object-fit: contain;
  background: transparent;
  color: white;
  border-radius: 12px;
  font-size: 25px;
}
.brand small {
  display: block;
  font-size: 8px;
  letter-spacing: 1.7px;
  color: var(--text-secondary);
  margin-top: 7px;
}
.nav-caption {
  font-size: 11px;
  color: var(--text-tertiary);
  letter-spacing: 2px;
  padding: 8px 15px;
}
nav {
  display: grid;
  gap: 5px;
}
nav a {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 9px;
  text-decoration: none;
  color: var(--text-secondary);
  font-size: 14px;
}
nav a:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}
nav a.router-link-exact-active {
  background: var(--accent-soft);
  color: var(--success-color);
  font-weight: 650;
}
nav .el-icon {
  font-size: 19px;
}
.nav-footer {
  margin-top: auto;
  padding-top: 30px;
}
.workspace-note {
  display: flex;
  gap: 12px;
  padding: 17px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  font-size: 12px;
}
.workspace-note small {
  display: block;
  color: var(--text-tertiary);
  margin-top: 5px;
}
.account-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 18px;
}
.account-actions button {
  background: none;
  border: 0;
  color: var(--text-secondary);
  cursor: pointer;
}
.mobile-nav-toggle,
.nav-backdrop {
  display: none;
}
@media (max-width: 1000px) {
  .workspace-nav {
    transform: translateX(-100%);
    visibility: hidden;
    transition: transform 0.2s;
  }
  .workspace-nav.open {
    transform: translateX(0);
    visibility: visible;
  }
  .mobile-nav-toggle {
    display: flex;
    gap: 12px;
    align-items: center;
    position: sticky;
    top: 0;
    width: 100%;
    height: 56px;
    padding: 0 20px;
    background: var(--bg-secondary);
    border: 0;
    border-bottom: 1px solid var(--border-color);
    color: var(--text-primary);
    z-index: 90;
  }
  .nav-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    border: 0;
    background: #0b182766;
    z-index: 99;
  }
}
@media (max-height: 800px) {
  .workspace-nav {
    padding-top: 20px;
    padding-bottom: 16px;
  }
  .brand {
    padding-bottom: 16px;
  }
  nav a {
    padding-top: 10px;
    padding-bottom: 10px;
  }
  .nav-footer {
    padding-top: 16px;
  }
}
.account-menu {
  position: relative;
  margin-top: 18px;
}
.account-trigger {
  display: flex;
  align-items: center;
  gap: 11px;
  border: 0;
  background: var(--bg-primary);
  color: var(--text-primary);
  border-radius: 12px;
  width: 100%;
  padding: 12px;
  text-align: left;
  font-size: 13px;
}
.account-trigger small {
  display: block;
  font-size: 10px;
  color: var(--text-secondary);
  margin-top: 5px;
}
.user-avatar {
  display: grid;
  place-items: center;
  background: var(--accent-soft);
  color: var(--success-color);
  width: 34px;
  height: 34px;
  border-radius: 50%;
  font-weight: 700;
}
.account-chevron {
  margin-left: auto;
}
.account-popup {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 8px;
  margin-bottom: 8px;
  box-shadow: var(--card-shadow);
}
.account-popup p {
  font-size: 11px;
  color: var(--text-secondary);
  padding: 0 8px;
  overflow-wrap: anywhere;
}
.account-popup button,
.account-popup a {
  display: block;
  width: 100%;
  padding: 10px;
  border: 0;
  background: transparent;
  text-align: left;
  color: var(--text-primary);
  text-decoration: none;
  font-size: 12px;
  border-radius: 6px;
}
.account-popup button:hover,
.account-popup a:hover {
  background: var(--accent-soft);
}
</style>
