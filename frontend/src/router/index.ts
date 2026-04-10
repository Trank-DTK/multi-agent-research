import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/login.vue'
import Register from '../views/register.vue'
import Dashboard from '../views/dashboard.vue'
import Chat from '../views/chat.vue'
import AgentChat from '@/views/AgentChat.vue'
import Documents from '@/views/Documents.vue'
import LiteratureChat from '@/views/LiteratureChat.vue'
import Collaboration from '@/views/Collaboration.vue'
import CollaborationWithReview from '@/views/CollaborationWithReview.vue'
import DataAnalysis from '@/views/DataAnalysis.vue'
import PaperWriting from '@/views/PaperWriting.vue'

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
    },
    {
      path: '/agent',
      name: 'agent',
      component: AgentChat,
      meta: { requiresAuth: true }
    },
    {
      path: '/documents',
      name: 'documents',
      component: Documents,
      meta: { requiresAuth: true }
    },
    {
      path: '/literature',
      name: 'literature',
      component: LiteratureChat,
      meta: { requiresAuth: true }
    },
    {
      path: '/collaboration',
      name: 'collaboration',
      component: Collaboration,
      meta: { requiresAuth: true }
    },
    {
      path: '/collaboration-review',
      name: 'collaboration-review',
      component: CollaborationWithReview,
      meta: { requiresAuth: true }
    },
    {
      path: '/analysis',
      name: 'analysis',
      component: DataAnalysis,
      meta: { requiresAuth: true }
    },
    {
      path: '/writing',
      name: 'writing',
      component: PaperWriting,
      meta: { requiresAuth: true }
    },

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