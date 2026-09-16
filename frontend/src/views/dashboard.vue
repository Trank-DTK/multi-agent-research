<template>
  <main class="dashboard">
    <header class="dashboard-heading">
      <div>
        <p class="eyebrow">YOUR RESEARCH, CONNECTED</p>
        <h1>科研工作台</h1>
        <p>把灵感变成研究，让每一步都有迹可循。</p>
      </div>
      <span class="date-label">{{ today }}</span>
    </header>
    <section class="research-hero">
      <div>
        <span class="hero-label">多智能体 · 科研协作</span>
        <h2>下一个发现，<br />从一个好问题开始。</h2>
        <p>串联文献、数据与写作，让智能助手陪你推进研究。</p>
        <router-link to="/collaboration" class="hero-button"
          >开始协作研究 <span>↗</span></router-link
        ><router-link to="/chat" class="hero-secondary">先聊聊研究想法 →</router-link>
      </div>
      <div class="research-map" aria-hidden="true">
        <div class="orbit orbit-one"></div>
        <div class="orbit orbit-two"></div>
        <div class="map-center">
          <el-icon><Connection /></el-icon><span>研究协作</span>
        </div>
        <span class="map-node node-one">文献检索</span
        ><span class="map-node node-two">数据分析</span
        ><span class="map-node node-three">论文写作</span><span class="map-dot"></span>
      </div>
    </section>
    <section class="workflow">
      <div class="section-heading">
        <div>
          <h2>从问题到成果</h2>
          <p>按研究阶段，找到合适的工具</p>
        </div>
        <span class="section-note">你的研究，由你掌握节奏</span>
      </div>
      <div class="steps">
        <router-link v-for="(step, index) in steps" :key="step.path" :to="step.path"
          ><span class="step-number">0{{ index + 1 }}</span>
          <div>
            <strong>{{ step.label }}</strong
            ><small>{{ step.text }}</small>
          </div>
          <span class="step-arrow">↗</span></router-link
        >
      </div>
    </section>
    <section>
      <div class="section-heading">
        <div>
          <h2>探索科研工具</h2>
          <p>为不同的研究任务，选择专业助手</p>
        </div>
        <label class="tool-search"
          ><el-icon><Search /></el-icon
          ><input
            v-model="query"
            type="search"
            aria-label="搜索科研工具"
            placeholder="搜索工具或功能"
        /></label>
      </div>
      <div class="tool-grid">
        <router-link
          v-for="(tool, index) in filteredTools"
          :key="tool.path"
          :to="tool.path"
          class="tool-card"
          ><div class="tool-top">
            <span class="tool-symbol" :class="'tone-' + (index % 4)"
              ><el-icon><component :is="tool.icon" /></el-icon></span
            ><span class="card-arrow">↗</span>
          </div>
          <h3>{{ tool.label }}</h3>
          <p>{{ tool.description }}</p>
          <span class="tool-link">打开工具 <span>→</span></span></router-link
        >
      </div>
      <p v-if="!filteredTools.length" class="search-empty">
        没有找到相关工具，试试“文献”“数据”或“写作”。
      </p>
    </section>
    <footer class="dashboard-footer">
      <span>研知协作 / Research Workspace</span><span>专注问题本身，探索更多可能。</span>
    </footer>
  </main>
</template>
<script setup>
import { computed, ref } from 'vue'
import { navigation } from '@/navigation'
defineOptions({ name: 'ResearchDashboard' })
const query = ref('')
const today = new Intl.DateTimeFormat('zh-CN', {
  month: 'long',
  day: 'numeric',
  weekday: 'long',
}).format(new Date())
const filteredTools = computed(() =>
  navigation
    .slice(1)
    .filter((tool) =>
      (tool.label + tool.description).toLowerCase().includes(query.value.trim().toLowerCase()),
    ),
)
const steps = [
  { path: '/documents', label: '积累文献', text: '建立研究知识库' },
  { path: '/analysis', label: '分析与验证', text: '从数据中寻找证据' },
  { path: '/writing', label: '组织与表达', text: '将研究转化为论文' },
]
</script>
<style scoped>
.dashboard {
  max-width: 1440px;
  margin: auto;
  padding: 38px 48px 20px;
}
.dashboard-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}
.eyebrow {
  font-size: 10px;
  letter-spacing: 2.2px;
  color: var(--success-color);
  font-weight: 650;
  margin: 0 0 10px;
}
h1 {
  font-size: 28px;
  letter-spacing: -1px;
  margin: 0 0 10px;
}
.dashboard-heading p:not(.eyebrow),
.section-heading p {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}
.date-label {
  font-size: 12px;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  padding: 9px 13px;
  border-radius: 8px;
  background: var(--bg-secondary);
}
.research-hero {
  display: flex;
  justify-content: space-between;
  background: #153b76;
  color: #fff;
  border-radius: 18px;
  min-height: 290px;
  padding: 34px 38px;
  overflow: hidden;
}
.hero-label {
  font-size: 11px;
  letter-spacing: 2px;
  color: #bad3ff;
}
.research-hero h2 {
  font-size: 34px;
  line-height: 1.45;
  margin: 16px 0 12px;
  letter-spacing: 1px;
}
.research-hero p {
  font-size: 13px;
  color: #bfd0ea;
  margin-bottom: 25px;
}
.hero-button {
  display: inline-flex;
  gap: 24px;
  padding: 12px 17px;
  border-radius: 7px;
  background: #deebff;
  color: #21477e;
  text-decoration: none;
  font-size: 13px;
  font-weight: 650;
}
.hero-secondary {
  color: #d2e2fa;
  text-decoration: none;
  font-size: 12px;
  margin-left: 20px;
}
.research-map {
  width: 300px;
  min-width: 240px;
  position: relative;
  display: grid;
  place-items: center;
}
.orbit {
  position: absolute;
  border: 1px solid #82aeeb55;
  border-radius: 50%;
  width: 195px;
  height: 195px;
}
.orbit-two {
  width: 290px;
  height: 290px;
}
.map-center {
  width: 108px;
  height: 108px;
  border-radius: 50%;
  background: #28528d;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 12px;
  border: 1px solid #6f99d0;
}
.map-center .el-icon {
  font-size: 28px;
  color: #deebff;
}
.map-node {
  position: absolute;
  padding: 10px 15px;
  background: #264d85;
  border: 1px solid #638bbc;
  border-radius: 8px;
  font-size: 11px;
}
.node-one {
  top: 15px;
  left: 15px;
}
.node-two {
  right: -3px;
  top: 100px;
}
.node-three {
  bottom: 2px;
  left: 25px;
}
.map-dot {
  position: absolute;
  right: 45px;
  top: 10px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #deebff;
}
.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  margin: 30px 0 18px;
}
.section-heading h2 {
  font-size: 18px;
  margin: 0 0 7px;
}
.section-note {
  font-size: 11px;
  color: var(--text-tertiary);
}
.steps {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}
.steps a {
  display: flex;
  gap: 15px;
  align-items: center;
  padding: 21px;
  text-decoration: none;
  color: var(--text-primary);
}
.steps a + a {
  border-left: 1px solid var(--border-color);
}
.step-number {
  font-size: 23px;
  color: var(--text-tertiary);
  font-weight: 300;
}
.steps strong {
  font-size: 13px;
}
.steps small {
  display: block;
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 6px;
}
.step-arrow {
  margin-left: auto;
  color: var(--text-tertiary);
}
.tool-search {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  padding: 9px 12px;
  border-radius: 8px;
  color: var(--text-tertiary);
}
.tool-search input {
  background: none;
  border: 0;
  color: var(--text-primary);
  width: 155px;
  font-size: 12px;
  outline: none;
}
.tool-search:focus-within {
  outline: 2px solid var(--success-color);
}
.tool-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}
.tool-card {
  display: block;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  text-decoration: none;
  color: var(--text-primary);
  transition:
    transform 0.2s,
    border-color 0.2s;
}
.tool-card:hover {
  transform: translateY(-3px);
  border-color: var(--success-color);
  box-shadow: var(--card-shadow);
}
.tool-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.tool-symbol {
  display: grid;
  place-items: center;
  width: 39px;
  height: 39px;
  border-radius: 10px;
  background: var(--accent-soft);
  color: var(--success-color);
  font-size: 21px;
}
.tone-1 {
  background: #ecedf8;
  color: #6464aa;
}
.tone-2 {
  background: #f8eedf;
  color: #aa7935;
}
.tone-3 {
  background: #e7eff8;
  color: #4e79a7;
}
.card-arrow {
  color: var(--text-tertiary);
}
.tool-card h3 {
  font-size: 14px;
  margin: 17px 0 9px;
}
.tool-card p {
  font-size: 12px;
  line-height: 1.8;
  color: var(--text-secondary);
  min-height: 43px;
  margin: 0;
}
.tool-link {
  display: flex;
  justify-content: space-between;
  border-top: 1px solid var(--border-color);
  padding-top: 12px;
  margin-top: 16px;
  font-size: 11px;
  color: var(--text-secondary);
}
.dashboard-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 32px;
  padding: 20px 0 0;
  border-top: 1px solid var(--border-color);
  font-size: 10px;
  color: var(--text-tertiary);
}
.search-empty {
  padding: 40px;
  text-align: center;
  color: var(--text-secondary);
}
@media (max-width: 1250px) {
  .dashboard {
    padding: 30px;
  }
  .tool-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .research-map {
    width: 240px;
  }
  .hero-secondary {
    display: block;
    margin: 16px 0 0;
  }
}
@media (max-width: 600px) {
  .dashboard {
    padding: 24px 16px;
  }
  .date-label,
  .research-map,
  .section-note {
    display: none;
  }
  .research-hero {
    padding: 26px;
  }
  .research-hero h2 {
    font-size: 28px;
  }
  .steps {
    grid-template-columns: 1fr;
  }
  .steps a + a {
    border-left: 0;
    border-top: 1px solid var(--border-color);
  }
  .section-heading {
    align-items: flex-start;
    flex-direction: column;
  }
  .tool-grid {
    gap: 10px;
  }
  .tool-card {
    padding: 15px;
  }
  .dashboard-footer {
    gap: 15px;
    line-height: 1.8;
  }
  .tool-search {
    width: 100%;
  }
  .tool-search input {
    width: 100%;
  }
}
</style>
