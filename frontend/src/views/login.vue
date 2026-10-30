<template>
  <AuthShell title="欢迎回来" description="继续你的探索，让研究向前一步。">
    <form :aria-busy="loading" @submit.prevent="handleLogin">
      <label class="auth-field"
        ><span>用户名</span
        ><input
          v-model="username"
          type="text"
          placeholder="输入用户名"
          required
          autocomplete="username"
          :disabled="loading"
      /></label>
      <div class="auth-field">
        <label for="login-password">密码</label>
        <span class="password-wrap">
          <input
            id="login-password"
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="输入密码"
            required
            autocomplete="current-password"
            :disabled="loading"
          />
          <button
            type="button"
            :aria-label="showPassword ? '隐藏密码' : '显示密码'"
            :aria-pressed="showPassword"
            @click="showPassword = !showPassword"
          >
            <svg aria-hidden="true"><use href="#public-eye" /></svg>
          </button>
        </span>
      </div>
      <p v-if="error" class="auth-error" role="alert">{{ error }}</p>
      <button
        type="submit"
        class="button button-blue auth-submit"
        :class="{ busy: loading }"
        :disabled="loading"
      >
        <span>{{ loading ? '正在登录…' : '登录并进入工作台' }}</span
        ><svg aria-hidden="true"><use href="#public-arrow" /></svg>
      </button>
    </form>
    <template #footer>还没有账户？<RouterLink to="/register">创建新账户 ↗</RouterLink></template>
  </AuthShell>
</template>
<script setup>
import { ref, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/axios'
import AuthShell from '@/components/AuthShell.vue'
import { saveSessionTokens } from '@/utils/auth'
defineOptions({ name: 'LoginPage' })
const router = useRouter()
const username = ref(''),
  password = ref(''),
  showPassword = ref(false)
const loading = ref(false),
  error = ref('')
let controller
onBeforeUnmount(() => controller?.abort())
const handleLogin = async () => {
  if (loading.value) return
  if (!username.value.trim() || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  error.value = ''
  controller = new AbortController()
  try {
    const response = await axios.post(
      '/auth/login/',
      { username: username.value.trim(), password: password.value },
      { signal: controller.signal },
    )
    if (controller.signal.aborted) return
    saveSessionTokens(response.data)
    await router.replace('/dashboard')
  } catch (err) {
    if (controller.signal.aborted) return
    error.value = err.response?.status === 401 ? '用户名或密码错误' : '登录失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>
