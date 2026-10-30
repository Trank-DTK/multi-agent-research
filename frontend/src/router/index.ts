// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { accessRedirect } from '@/utils/auth'

// 路由懒加载 - 所有页面组件按需加载
const Login = () => import('@/views/login.vue')
const Register = () => import('@/views/register.vue')
const Dashboard = () => import('@/views/dashboard.vue')
const Chat = () => import('@/views/Chat.vue')
const AgentChat = () => import('@/views/AgentChat.vue')
const Documents = () => import('@/views/Documents.vue')

const Collaboration = () => import('@/views/Collaboration.vue')

const DataAnalysis = () => import('@/views/DataAnalysis.vue')
const PaperWriting = () => import('@/views/PaperWriting.vue')

const routes = [
  { path: '/', name: 'home', component: () => import('@/views/Landing.vue') },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/Settings.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: { requiresGuest: true },
  },
  {
    path: '/register',
    name: 'register',
    component: Register,
    meta: { requiresGuest: true },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard,
    meta: { requiresAuth: true },
  },
  {
    path: '/chat',
    name: 'chat',
    component: Chat,
    meta: { requiresAuth: true },
  },
  {
    path: '/agent',
    name: 'agent',
    component: AgentChat,
    meta: { requiresAuth: true },
  },
  {
    path: '/documents',
    name: 'documents',
    component: Documents,
    meta: { requiresAuth: true },
  },
  {
    path: '/literature',
    name: 'literature',
    redirect: '/documents',
    meta: { requiresAuth: true },
  },
  {
    path: '/collaboration',
    name: 'collaboration',
    component: Collaboration,
    meta: { requiresAuth: true },
  },
  {
    path: '/collaboration-review',
    name: 'collaboration-review',
    redirect: { path: '/collaboration', query: { review: '1' } },
    meta: { requiresAuth: true },
  },
  {
    path: '/analysis',
    name: 'analysis',
    component: DataAnalysis,
    meta: { requiresAuth: true },
  },
  {
    path: '/writing',
    name: 'writing',
    component: PaperWriting,
    meta: { requiresAuth: true },
  },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash)
      return {
        el: to.hash,
        top: 100,
        behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches
          ? 'instant'
          : 'smooth',
      }
    return { top: 0 }
  },
})

// 路由守卫
router.beforeEach((to) => accessRedirect(to, localStorage))

export default router
