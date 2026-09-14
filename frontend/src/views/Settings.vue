<template>
  <main class="settings-page modern-page">
    <header class="section-title">
      <div>
        <p class="eyebrow">PERSONAL SETTINGS</p>
        <h1>设置</h1>
        <p>连接你习惯的模型，打造自己的科研空间。</p>
      </div>
    </header>
    <section class="panel appearance-row">
      <div>
        <h2>外观</h2>
        <p>为工作空间选择舒适的背景</p>
      </div>
      <div class="segmented">
        <button :class="{ active: !theme.isDark }" @click="theme.setTheme(false)">亮色</button
        ><button :class="{ active: theme.isDark }" @click="theme.setTheme(true)">暗色</button>
      </div>
    </section>
    <section class="panel">
      <div class="section-title">
        <div>
          <h2>模型供应商</h2>
          <p>默认模型用于对话、文献问答、协作研究、数据解读和论文写作。</p>
        </div>
        <button class="primary-button" @click="openEditor()">＋ 添加模型</button>
      </div>
      <p v-if="error" class="error-banner" role="alert">{{ error }}</p>
      <p v-if="notice" class="notice-banner" role="status">{{ notice }}</p>
      <p v-if="loading" class="empty-state">正在加载配置…</p>
      <div v-else-if="!providers.length" class="empty-state">
        <el-icon><Cpu /></el-icon>
        <h3>连接第一个模型</h3>
        <p>尚未配置时使用服务器默认的 Ollama 模型。</p>
        <button class="secondary-button" @click="openEditor()">添加供应商</button>
      </div>
      <div v-else class="provider-list">
        <article v-for="provider in providers" :key="provider.id" class="provider-row">
          <span class="provider-icon"
            ><el-icon><Cpu /></el-icon
          ></span>
          <div class="provider-info">
            <h3>{{ provider.name }} <span v-if="provider.is_default" class="badge">默认</span></h3>
            <p>{{ provider.model }}</p>
            <small
              >{{ provider.base_url }} · {{ provider.has_api_key ? '密钥已保存' : '无密钥' }}</small
            >
          </div>
          <div class="row-actions">
            <button v-if="!provider.is_default" :disabled="!!busy" @click="setDefault(provider)">
              设为默认</button
            ><button :disabled="!!busy" @click="testProvider(provider)">
              {{ busy === provider.id ? '检测中…' : '测试连接' }}</button
            ><button @click="openEditor(provider)">编辑</button
            ><button class="danger-text" :disabled="!!busy" @click="remove(provider)">删除</button>
          </div>
        </article>
      </div>
      <p class="field-help">
        同一供应商可添加多个模型。API Key
        加密保存在服务器，编辑时留空保留原值；更换地址时需重新填写。
      </p>
    </section>
    <el-dialog
      v-model="editing"
      :title="form.id ? '编辑模型' : '添加模型供应商'"
      width="min(580px, 94vw)"
      :close-on-click-modal="false"
    >
      <form class="settings-form" @submit.prevent="save">
        <label
          >供应商模板<select v-model="preset" @change="applyPreset">
            <option v-for="item in presets" :key="item.name" :value="item.name">
              {{ item.name }}
            </option>
          </select></label
        >
        <div class="form-columns">
          <label
            >显示名称<input
              v-model.trim="form.name"
              required
              maxlength="100"
              placeholder="例如：我的 DeepSeek" /></label
          ><label
            >接口协议<select v-model="form.protocol">
              <option value="openai">OpenAI 兼容接口</option>
              <option value="ollama">Ollama 原生接口</option>
            </select></label
          >
        </div>
        <label
          >Base URL<input
            v-model.trim="form.base_url"
            type="url"
            required
            placeholder="https://api.example.com/v1" /></label
        ><label
          >模型 ID<input
            v-model.trim="form.model"
            required
            maxlength="200"
            placeholder="填写供应商提供的模型 ID" /></label
        ><label
          >API Key<input
            v-model="form.api_key"
            type="password"
            autocomplete="new-password"
            :placeholder="
              form.has_api_key ? '已保存，留空保留原密钥' : '本地模型未启用鉴权时可留空'
            " /></label
        ><label v-if="form.has_api_key" class="check-label"
          ><input v-model="clearKey" type="checkbox" />清除已保存的密钥</label
        ><label class="check-label"
          ><input v-model="form.is_default" type="checkbox" />设为默认模型</label
        >
        <p class="field-help">
          本地地址是相对于后端服务器的。Docker 访问宿主机可使用 host.docker.internal；Ollama
          原生地址不包含 /v1，LM Studio 使用 /v1。自定义接口需兼容所选协议。
        </p>
        <p v-if="formError" class="error-banner" role="alert">{{ formError }}</p>
        <div class="dialog-actions">
          <button type="button" class="secondary-button" @click="editing = false">取消</button
          ><button type="submit" class="primary-button" :disabled="saving">
            {{ saving ? '保存中…' : '保存配置' }}
          </button>
        </div>
      </form>
    </el-dialog>
  </main>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import axios from '@/axios'
import { apiError } from '@/utils/apiError'
import { useThemeStore } from '@/stores/theme'
defineOptions({ name: 'ModelSettings' })
const theme = useThemeStore()
const providers = ref([]),
  loading = ref(false),
  error = ref(''),
  notice = ref(''),
  editing = ref(false),
  saving = ref(false),
  busy = ref(null),
  formError = ref(''),
  clearKey = ref(false)
const presets = [
  {
    name: 'DeepSeek',
    protocol: 'openai',
    base_url: 'https://api.deepseek.com/v1',
    model: 'deepseek-chat',
  },
  { name: 'OpenRouter', protocol: 'openai', base_url: 'https://openrouter.ai/api/v1', model: '' },
  {
    name: 'Qwen',
    protocol: 'openai',
    base_url: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    model: 'qwen-plus',
  },
  { name: 'OpenAI', protocol: 'openai', base_url: 'https://api.openai.com/v1', model: '' },
  { name: 'Ollama', protocol: 'ollama', base_url: 'http://localhost:11434', model: 'qwen2.5:7b' },
  { name: 'LM Studio', protocol: 'openai', base_url: 'http://localhost:1234/v1', model: '' },
  { name: '自定义', protocol: 'openai', base_url: '', model: '' },
]
const preset = ref('DeepSeek'),
  form = ref({})
function applyPreset() {
  const item = presets.find((p) => p.name === preset.value)
  Object.assign(form.value, item, { api_key: '', has_api_key: false })
  clearKey.value = true
}
function openEditor(provider) {
  formError.value = ''
  clearKey.value = false
  form.value = provider
    ? { ...provider, api_key: '' }
    : { ...presets[0], is_default: !providers.value.length, api_key: '' }
  preset.value = provider ? '自定义' : 'DeepSeek'
  editing.value = true
}
async function load() {
  loading.value = true
  error.value = ''
  try {
    providers.value = (await axios.get('/settings/providers/')).data
  } catch (e) {
    error.value = apiError(e)
  } finally {
    loading.value = false
  }
}
async function save() {
  saving.value = true
  formError.value = ''
  try {
    const payload = {
      name: form.value.name,
      protocol: form.value.protocol,
      base_url: form.value.base_url,
      model: form.value.model,
      is_default: form.value.is_default,
    }
    if (form.value.api_key || clearKey.value || !form.value.id)
      payload.api_key = clearKey.value && !form.value.api_key ? '' : form.value.api_key
    if (form.value.id) await axios.patch(`/settings/providers/${form.value.id}/`, payload)
    else await axios.post('/settings/providers/', payload)
    editing.value = false
    form.value.api_key = ''
    notice.value = '配置已保存，下次请求使用最新默认模型。'
    await load()
  } catch (e) {
    formError.value = apiError(e)
  } finally {
    saving.value = false
  }
}
async function setDefault(p) {
  busy.value = 'saving'
  try {
    await axios.patch(`/settings/providers/${p.id}/`, { is_default: true })
    await load()
  } catch (e) {
    error.value = apiError(e)
  } finally {
    busy.value = null
  }
}
async function testProvider(p) {
  busy.value = p.id
  error.value = ''
  notice.value = ''
  try {
    notice.value = (
      await axios.post(`/settings/providers/${p.id}/test/`, {}, { timeout: 45000 })
    ).data.message
  } catch (e) {
    error.value = apiError(e)
  } finally {
    busy.value = null
  }
}
async function remove(p) {
  try {
    await ElMessageBox.confirm(`删除“${p.name}”的模型配置？`, '删除模型', { type: 'warning' })
  } catch {
    return
  }
  try {
    await axios.delete(`/settings/providers/${p.id}/`)
    await load()
  } catch (e) {
    error.value = apiError(e)
  }
}
onMounted(load)
</script>
