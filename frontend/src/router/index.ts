import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/login.vue'
import Register from '../views/register.vue'
import Dashboard from '../views/dashboard.vue'
import Chat from '../views/chat.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { requiresGuest: true }  // 游客才能访问
    },
    {
      path: '/register',
      name: 'register',
      component: Register,
      meta: { requiresGuest: true }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: Dashboard,
      meta: { requiresAuth: true }  // 需要登录
    },
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/chat',
      name: 'chat',
      component: Chat,
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access')

  // 需要登录但未登录 → 跳转到登录页
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  }
  // 已登录用户不能访问登录/注册页
  else if (to.meta.requiresGuest && isAuthenticated) {
    next('/dashboard')
  }
  else {
    next()
  }
})

export default router