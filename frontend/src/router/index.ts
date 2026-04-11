// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

// 路由懒加载 - 所有页面组件按需加载
const Login = () => import('@/views/login.vue')
const Register = () => import('@/views/register.vue')
const Dashboard = () => import('@/views/dashboard.vue')
const Chat = () => import('@/views/Chat.vue')
const AgentChat = () => import('@/views/AgentChat.vue')
const Documents = () => import('@/views/Documents.vue')
const LiteratureChat = () => import('@/views/LiteratureChat.vue')
const Collaboration = () => import('@/views/Collaboration.vue')
const CollaborationWithReview = () => import('@/views/CollaborationWithReview.vue')
const DataAnalysis = () => import('@/views/DataAnalysis.vue')
const PaperWriting = () => import('@/views/PaperWriting.vue')

const routes = [
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: { requiresGuest: true }
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
    meta: { requiresAuth: true }
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
  {
    path: '/',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
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