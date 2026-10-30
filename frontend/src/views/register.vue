<template>
  <AuthShell title="开启新的探索" description="创建账户，把下一个好问题带进来。">
    <form :aria-busy="loading" @submit.prevent="handleRegister">
      <fieldset class="auth-fields" :disabled="loading || Boolean(success)">
        <label class="auth-field"
          ><span>用户名</span
          ><input
            v-model="username"
            type="text"
            placeholder="你的用户名"
            required
            autocomplete="username"
        /></label>
        <label class="auth-field"
          ><span>邮箱</span
          ><input
            v-model="email"
            type="email"
            placeholder="用于你的科研账户"
            required
            autocomplete="email"
        /></label>
        <div class="auth-field">
          <label for="register-password">密码</label>
          <span class="password-wrap">
            <input
              id="register-password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="设置密码（至少 8 位）"
              required
              minlength="8"
              autocomplete="new-password"
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
        <label class="auth-field"
          ><span>确认密码</span
          ><input
            v-model="password2"
            type="password"
            placeholder="再次输入密码"
            required
            autocomplete="new-password"
        /></label>
        <div class="auth-optional">
          <label class="auth-field"
            ><span>姓（可选）</span
            ><input v-model="firstName" placeholder="姓" autocomplete="family-name"
          /></label>
          <label class="auth-field"
            ><span>名（可选）</span
            ><input v-model="lastName" placeholder="名" autocomplete="given-name"
          /></label>
        </div>
      </fieldset>
      <div v-if="errorMessages.length" class="auth-error" role="alert">
        <p v-for="(message, index) in errorMessages" :key="index">{{ message }}</p>
      </div>
      <p v-if="success" class="auth-success" role="status">{{ success }}</p>
      <button
        type="submit"
        class="button button-blue auth-submit"
        :class="{ busy: loading }"
        :disabled="loading || Boolean(success)"
      >
        <span>{{ loading ? '正在创建账户…' : success ? '账户已创建' : '创建我的研究空间' }}</span
        ><svg aria-hidden="true"><use href="#public-arrow" /></svg>
      </button>
    </form>
    <template #footer>已有账户？<RouterLink to="/login">去登录 ↗</RouterLink></template>
  </AuthShell>
</template>
<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/axios'
import AuthShell from '@/components/AuthShell.vue'
defineOptions({ name: 'RegisterPage' })
const router = useRouter()
const username = ref(''),
  email = ref(''),
  password = ref(''),
  password2 = ref('')
const firstName = ref(''),
  lastName = ref(''),
  showPassword = ref(false)
const loading = ref(false),
  error = ref(null),
  success = ref('')
let controller, redirectTimer
const errorMessages = computed(() => {
  if (!error.value) return []
  if (typeof error.value === 'string') return [error.value]
  const labels = {
    username: '用户名',
    email: '邮箱',
    password: '密码',
    password2: '确认密码',
    non_field_errors: '注册失败',
    detail: '提示',
  }
  return Object.entries(error.value).map(
    ([field, message]) =>
      `${labels[field] || field}：${Array.isArray(message) ? message.join('；') : message}`,
  )
})
onBeforeUnmount(() => {
  controller?.abort()
  clearTimeout(redirectTimer)
})
const handleRegister = async () => {
  if (loading.value || success.value) return
  if (password.value !== password2.value) {
    error.value = '两次输入的密码不一致'
    return
  }
  if (password.value.length < 8) {
    error.value = '密码长度至少 8 位'
    return
  }
  loading.value = true
  error.value = null
  controller = new AbortController()
  try {
    await axios.post(
      '/auth/register/',
      {
        username: username.value.trim(),
        email: email.value.trim(),
        password: password.value,
        password2: password2.value,
        first_name: firstName.value,
        last_name: lastName.value,
      },
      { signal: controller.signal },
    )
    if (controller.signal.aborted) return
    success.value = '注册成功！即将前往登录页…'
    redirectTimer = setTimeout(() => router.replace('/login'), 2000)
  } catch (err) {
    if (!controller.signal.aborted) error.value = err.response?.data || '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>
