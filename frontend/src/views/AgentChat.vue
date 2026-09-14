<template>
  <main class="agent-chat-page modern-page">
    <div class="agent-workspace">
      <aside class="panel task-rail">
        <p class="eyebrow">RESEARCH ASSISTANT</p>
        <h1>科研任务助手</h1>
        <p>把研究目标转化为明确、可验证的下一步。</p>
        <button
          v-for="item in tasks"
          :key="item.id"
          class="task-choice"
          :class="{ active: task === item.id }"
          @click="selectTask(item)"
        >
          <el-icon><component :is="item.icon" /></el-icon
          ><span
            ><strong>{{ item.name }}</strong
            ><small>{{ item.description }}</small></span
          >
        </button>
        <div class="task-tip">建议提供研究领域、已有进展和现实约束，让建议更贴近你的课题。</div>
      </aside>
      <ResearchConversation
        :key="task"
        endpoint="/agent/chat/"
        :title="currentTask.name"
        :context="{ task }"
        :prompt="prompt"
        :empty-title="currentTask.name"
        :empty-description="currentTask.description"
        :placeholder="currentTask.example"
      />
    </div>
  </main>
</template>
<script setup>
import { computed, ref } from 'vue'
import ResearchConversation from '@/components/ResearchConversation.vue'
const tasks = [
  {
    id: 'plan',
    name: '任务拆解',
    icon: 'List',
    description: '制定阶段计划与验收标准',
    example: '我正在研究…，希望在四周内完成…，请帮我拆解任务。',
  },
  {
    id: 'hypothesis',
    name: '研究假设',
    icon: 'Aim',
    description: '明确变量、对照与证伪条件',
    example: '我的研究问题是…，请提出可检验假设和验证方法。',
  },
  {
    id: 'method',
    name: '方法选择',
    icon: 'Operation',
    description: '比较方法适用条件与局限',
    example: '针对…问题，我在考虑…方法，请比较适用条件和风险。',
  },
  {
    id: 'review',
    name: '方案检查',
    icon: 'CircleCheck',
    description: '找出证据缺口与方法问题',
    example: '请检查以下研究方案的论证、可行性与证据缺口：',
  },
]
const task = ref('plan'),
  prompt = ref(''),
  currentTask = computed(() => tasks.find((item) => item.id === task.value))
function selectTask(item) {
  task.value = item.id
  prompt.value = ''
}
</script>
