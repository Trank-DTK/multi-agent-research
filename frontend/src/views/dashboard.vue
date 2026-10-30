<template>
  <main class="dashboard">
    <header class="dashboard-heading">
      <div>
        <p class="eyebrow"><span></span> 科研空间 / WORKSPACE</p>
        <h1>科研工作台</h1>
        <p class="heading-description">把灵感变成研究，让每一步都有迹可循。</p>
      </div>
      <span class="date-label">
        <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
          <rect x="3" y="4.5" width="14" height="13" rx="3" />
          <path d="M6.5 2.5v4m7-4v4M3 9h14m-10 4h1m4 0h1" />
        </svg>
        {{ today }}
      </span>
    </header>

    <section class="research-hero" aria-labelledby="hero-title">
      <div class="hero-grid" aria-hidden="true"></div>
      <div class="hero-copy">
        <span class="hero-label"><span></span> 多智能体 · 科研协作</span>
        <h2 id="hero-title">下一个发现，<br /><span>从一个好问题开始。</span></h2>
        <p>串联文献、数据与写作，<br class="compact-break" />让智能助手陪你推进研究。</p>
        <div class="hero-actions">
          <router-link to="/collaboration" class="hero-button">
            开始协作研究 <span aria-hidden="true">↗</span>
          </router-link>
          <router-link to="/chat" class="hero-secondary">
            先聊聊研究想法 <span aria-hidden="true">→</span>
          </router-link>
        </div>
        <div class="hero-caption"><span></span> 连接知识，让探索更进一步</div>
      </div>

      <div class="research-map" aria-hidden="true">
        <div class="map-glow"></div>
        <svg class="network-lines" viewBox="0 0 440 330" fill="none">
          <defs>
            <linearGradient
              id="research-orbit-gradient"
              x1="60"
              y1="35"
              x2="390"
              y2="300"
              gradientUnits="userSpaceOnUse"
            >
              <stop stop-color="#62d7f0" stop-opacity="0.64" />
              <stop offset="0.48" stop-color="#7298f4" stop-opacity="0.16" />
              <stop offset="1" stop-color="#62d7f0" stop-opacity="0.52" />
            </linearGradient>
          </defs>
          <circle
            cx="220"
            cy="165"
            r="133"
            stroke="#719bd0"
            stroke-opacity="0.14"
            stroke-dasharray="2 7"
          />
          <circle cx="220" cy="165" r="102" stroke="#85caf4" stroke-opacity="0.12" />
          <ellipse
            cx="220"
            cy="165"
            rx="182"
            ry="73"
            transform="rotate(-29 220 165)"
            stroke="url(#research-orbit-gradient)"
          />
          <ellipse
            cx="220"
            cy="165"
            rx="173"
            ry="76"
            transform="rotate(36 220 165)"
            stroke="url(#research-orbit-gradient)"
          />
          <path
            d="M114 76 220 165l133-34M220 165l-87 106"
            stroke="#87ccf1"
            stroke-opacity="0.4"
            stroke-dasharray="3 5"
          />
          <path
            d="m213 31 7-4 7 4m-7-4v13M380 230v12m-6-6h12M64 199v8m-4-4h8"
            stroke="#8bb7e8"
            stroke-opacity="0.4"
          />
          <g fill="#b4f3ff">
            <circle cx="93" cy="208" r="3" />
            <circle cx="291" cy="49" r="3.5" />
            <circle cx="366" cy="195" r="2.5" />
            <circle cx="184" cy="296" r="2" />
          </g>
          <g fill="#79a0d4" fill-opacity="0.55">
            <circle cx="55" cy="82" r="1.5" />
            <circle cx="392" cy="69" r="1.5" />
            <circle cx="301" cy="276" r="1.5" />
            <circle cx="34" cy="267" r="1.5" />
          </g>
        </svg>
        <div class="map-center">
          <span class="center-orbit"></span>
          <el-icon><Connection /></el-icon>
          <strong>研究协作</strong><small>CONNECTED IDEAS</small>
        </div>
        <div class="map-node node-one">
          <span class="node-icon"
            ><el-icon><Document /></el-icon
          ></span>
          <div><strong>文献检索</strong><small>知识与证据</small></div>
          <span class="node-point"></span>
        </div>
        <div class="map-node node-two">
          <span class="node-icon"
            ><el-icon><DataAnalysis /></el-icon
          ></span>
          <div><strong>数据分析</strong><small>假设与验证</small></div>
          <span class="node-point"></span>
        </div>
        <div class="map-node node-three">
          <span class="node-icon"
            ><el-icon><EditPen /></el-icon
          ></span>
          <div><strong>论文写作</strong><small>结构与表达</small></div>
          <span class="node-point"></span>
        </div>
        <span class="map-coordinate">IDEA · EVIDENCE · DISCOVERY</span>
      </div>
    </section>

    <section class="workflow" aria-labelledby="workflow-title">
      <div class="section-heading">
        <div>
          <h2 id="workflow-title">从问题到成果</h2>
          <p>按研究阶段，找到合适的工具</p>
        </div>
        <span class="section-note">你的研究，由你掌握节奏 <span aria-hidden="true">↗</span></span>
      </div>
      <div class="steps">
        <router-link v-for="(step, index) in steps" :key="step.path" :to="step.path">
          <span class="step-number">0{{ index + 1 }}</span>
          <div>
            <strong>{{ step.label }}</strong
            ><small>{{ step.text }}</small>
          </div>
          <span class="step-arrow" aria-hidden="true">↗</span>
        </router-link>
      </div>
    </section>

    <section class="tools-section" aria-labelledby="tools-title">
      <div class="section-heading">
        <div>
          <h2 id="tools-title">探索科研工具</h2>
          <p>为不同的研究任务，选择专业助手</p>
        </div>
        <label class="tool-search">
          <el-icon><Search /></el-icon>
          <input
            v-model="query"
            type="search"
            aria-label="搜索科研工具"
            placeholder="搜索工具或功能"
          />
        </label>
      </div>
      <div class="tool-grid">
        <router-link
          v-for="tool in filteredTools"
          :key="tool.path"
          :to="tool.path"
          class="tool-card"
        >
          <div class="tool-top">
            <span class="tool-symbol" :class="'tone-' + tool.path.slice(1)">
              <el-icon><component :is="tool.icon" /></el-icon>
            </span>
            <span class="card-arrow" aria-hidden="true">↗</span>
          </div>
          <h3>{{ tool.label }}</h3>
          <p>{{ tool.description }}</p>
        </router-link>
      </div>
      <p v-if="!filteredTools.length" class="search-empty" role="status">
        没有找到相关工具，试试“文献”“数据”或“写作”。
      </p>
    </section>

    <footer class="dashboard-footer">
      <span
        ><span class="footer-mark" aria-hidden="true">✳</span> 研知协作 / Research Workspace</span
      >
      <span>专注问题本身，探索更多可能。</span>
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
  width: 100%;
  max-width: 1460px;
  margin: auto;
  padding: 36px 42px 22px;
}
.dashboard-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  margin-bottom: 28px;
}
.eyebrow {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 10px;
  letter-spacing: 2.1px;
  color: var(--success-color);
  font-weight: 650;
  margin: 0 0 10px;
}
.eyebrow > span {
  width: 17px;
  height: 2px;
  background: var(--accent-gradient, var(--success-color));
  border-radius: 2px;
}
h1 {
  font-size: clamp(26px, 2.3vw, 34px);
  line-height: 1.4;
  letter-spacing: -0.8px;
  font-weight: 700;
  margin: 0 0 8px;
}
.heading-description,
.section-heading p {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
  margin: 0;
}
.date-label {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  gap: 9px;
  padding: 10px 14px;
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  box-shadow: 0 2px 5px #10244103;
}
.date-label svg {
  width: 17px;
  height: 17px;
  stroke: var(--success-color);
  stroke-width: 1.3;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.research-hero {
  position: relative;
  isolation: isolate;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 300px;
  padding: 30px 36px;
  overflow: hidden;
  color: #f3f8ff;
  border: 1px solid #6eabe32b;
  border-radius: 22px;
  background:
    radial-gradient(ellipse at 83% 20%, #174d7047, transparent 58%),
    radial-gradient(ellipse at 58% 115%, #18458b59, transparent 65%),
    linear-gradient(112deg, #10233e 0%, #0c1d36 52%, #0c1b30 100%);
  box-shadow:
    0 12px 36px #0c234517,
    inset 0 1px 0 #b5deff12;
}
.hero-grid {
  position: absolute;
  z-index: -1;
  inset: 0;
  opacity: 0.22;
  background-image:
    linear-gradient(#7cb0d81a 1px, transparent 1px),
    linear-gradient(90deg, #7cb0d81a 1px, transparent 1px);
  background-size: 38px 38px;
  mask-image: linear-gradient(90deg, transparent 25%, #000 100%);
}
.hero-copy {
  position: relative;
  z-index: 1;
  flex: 1 0 auto;
}
.hero-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  font-size: 10px;
  letter-spacing: 1.5px;
  color: #b4ddeb;
  border: 1px solid #95d2ed24;
  border-radius: 6px;
  background: #85bde90a;
}
.hero-label > span {
  width: 5px;
  height: 5px;
  border: 1px solid #9ce4f3;
  transform: rotate(45deg);
}
.research-hero h2 {
  font-size: clamp(29px, 2.65vw, 39px);
  line-height: 1.48;
  font-weight: 650;
  margin: 17px 0 14px;
  letter-spacing: -0.6px;
}
.research-hero h2 > span {
  color: #c8ebfb;
}
.research-hero p {
  font-size: 13px;
  line-height: 1.9;
  color: #a8bbd1;
  margin: 0 0 23px;
}
.compact-break {
  display: none;
}
.hero-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 20px;
}
.hero-button {
  display: inline-flex;
  align-items: center;
  gap: 25px;
  min-height: 0;
  padding: 11px 17px;
  border: 1px solid #c4f3ffad;
  border-radius: 9px;
  background: linear-gradient(115deg, #def5fc, #a9dbee);
  color: #143449;
  text-decoration: none;
  font-size: 13px;
  font-weight: 650;
  box-shadow:
    0 3px 16px #56c2e31c,
    inset 0 1px 0 #ffffffa3;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}
.hero-button > span {
  font-size: 19px;
  line-height: 1;
}
.hero-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 23px #56c2e33d;
}
.hero-secondary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #b9cbdc;
  text-decoration: none;
  font-size: 12px;
  transition: color 0.2s;
}
.hero-secondary:hover {
  color: #e7f6ff;
}
.hero-button:focus-visible,
.hero-secondary:focus-visible {
  outline: 2px solid #b8ecff;
  outline-offset: 5px;
}
.hero-caption {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-top: 25px;
  font-size: 10px;
  letter-spacing: 0.8px;
  color: #7e98b5;
}
.hero-caption > span {
  width: 21px;
  height: 1px;
  background: #6a91ac;
}
.research-map {
  position: relative;
  flex: 0 1 440px;
  width: 440px;
  min-width: 300px;
  height: 278px;
  margin: -17px -22px -17px 0;
}
.map-glow {
  position: absolute;
  width: 230px;
  height: 230px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  background: radial-gradient(circle, #43b6d21c, #1b79ad0a 55%, transparent 72%);
}
.network-lines {
  width: 100%;
  height: 100%;
  overflow: visible;
}
.map-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 7px;
  width: 114px;
  height: 114px;
  border: 1px solid #96e2fb6b;
  border-radius: 50%;
  background: radial-gradient(circle at 36% 23%, #244f6c, #15334e 65%, #133047);
  box-shadow:
    0 0 34px #41b0cf1c,
    inset 0 0 22px #8bd6ee0c;
}
.center-orbit {
  position: absolute;
  inset: -8px;
  border: 1px solid #8bd6ee24;
  border-radius: 50%;
}
.center-orbit::after {
  position: absolute;
  content: '';
  width: 4px;
  height: 4px;
  right: 13px;
  top: 20px;
  border-radius: 50%;
  background: #b4f1ff;
  box-shadow: 0 0 9px #a0efffc9;
}
.map-center .el-icon {
  font-size: 29px;
  color: #b3edff;
}
.map-center strong {
  font-size: 12px;
  letter-spacing: 2px;
  font-weight: 500;
  color: #d2e9f5;
}
.map-center small {
  font-size: 5px;
  letter-spacing: 1.6px;
  color: #88adca;
}
.map-node {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 137px;
  padding: 12px 13px;
  border: 1px solid #6fa6c642;
  border-radius: 11px;
  background: linear-gradient(125deg, #203e58ed, #152c45f5);
  box-shadow:
    0 8px 20px #030d1a24,
    inset 0 1px 0 #b2ddf10a;
}
.node-icon {
  display: grid;
  place-items: center;
  width: 29px;
  height: 32px;
  color: #a5dcec;
  background: #a1d9ef0c;
  border: 1px solid #a5dcec14;
  border-radius: 7px;
  font-size: 16px;
}
.map-node strong {
  display: block;
  font-size: 11px;
  font-weight: 500;
  color: #d4e5f2;
}
.map-node small {
  display: block;
  margin-top: 5px;
  font-size: 8px;
  letter-spacing: 0.6px;
  color: #8eacc2;
}
.node-point {
  width: 3px;
  height: 3px;
  margin-left: 5px;
  border-radius: 50%;
  background: #7ba9c6;
}
.node-one {
  top: 26px;
  left: 13px;
  transform: rotate(-3deg);
}
.node-two {
  top: 107px;
  right: -2px;
  transform: rotate(3deg);
}
.node-three {
  bottom: 23px;
  left: 50px;
  transform: rotate(-2deg);
}
.map-coordinate {
  position: absolute;
  bottom: 0;
  right: 12px;
  color: #789bb555;
  font-size: 6px;
  letter-spacing: 2px;
}
.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin: 32px 0 18px;
}
.section-heading .section-kicker {
  margin-bottom: 6px;
  color: var(--success-color);
  font-size: 9px;
  font-weight: 650;
  letter-spacing: 1.8px;
}
.section-heading h2 {
  font-size: 19px;
  font-weight: 650;
  letter-spacing: -0.4px;
  line-height: 1.5;
  margin: 0 0 4px;
}
.section-note {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 11px;
  color: var(--text-secondary);
}
.section-note > span {
  color: var(--success-color);
}
.steps {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  padding: 7px;
  border: 1px solid var(--border-color);
  border-radius: 15px;
  background: var(--bg-secondary);
  box-shadow: inset 0 1px 0 var(--surface-highlight, #ffffff0a);
}
.steps a {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 0;
  padding: 18px;
  text-decoration: none;
  color: var(--text-primary);
  border-radius: 9px;
  transition: background 0.2s;
}
.steps a + a::before {
  position: absolute;
  content: '';
  top: 16px;
  bottom: 16px;
  left: 0;
  width: 1px;
  background: var(--border-color);
}
.steps a:hover {
  background: var(--accent-soft);
}
.step-number {
  font-size: 27px;
  font-weight: 300;
  letter-spacing: -1.5px;
  font-variant-numeric: tabular-nums;
  color: var(--success-color);
  opacity: 0.6;
}
.steps strong {
  display: block;
  font-size: 13px;
  font-weight: 600;
}
.steps small {
  display: block;
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 6px;
  line-height: 1.5;
}
.step-arrow {
  margin-left: auto;
  color: var(--text-secondary);
  font-size: 16px;
  transition:
    transform 0.2s,
    color 0.2s;
}
.steps a:hover .step-arrow {
  color: var(--success-color);
  transform: translate(2px, -2px);
}
.tool-search {
  display: flex;
  align-items: center;
  gap: 9px;
  min-height: 41px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  padding: 10px 13px;
  border-radius: 10px;
  color: var(--text-secondary);
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}
.tool-search > .el-icon {
  font-size: 15px;
}
.tool-search input {
  background: none;
  border: 0;
  color: var(--text-primary);
  width: 171px;
  min-width: 0;
  padding: 0;
  font-size: 12px;
  outline: none;
}
.tool-search input::placeholder {
  color: var(--text-secondary);
  opacity: 0.8;
}
.tool-search input:focus-visible {
  outline: none;
}
.tool-search:focus-within {
  border-color: var(--success-color);
  box-shadow: 0 0 0 3px var(--accent-soft);
}
.tool-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}
.tool-card {
  position: relative;
  display: grid;
  grid-template-columns: 43px minmax(0, 1fr) 28px;
  column-gap: 16px;
  align-content: center;
  min-width: 0;
  overflow: hidden;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 15px;
  padding: 22px;
  text-decoration: none;
  color: var(--text-primary);
  box-shadow: inset 0 1px 0 var(--surface-highlight, #ffffff0a);
  transition:
    transform 0.22s,
    border-color 0.22s,
    box-shadow 0.22s;
}
.tool-card::before {
  position: absolute;
  content: '';
  top: 0;
  left: 22px;
  right: 22px;
  height: 2px;
  background: var(--accent-gradient, var(--success-color));
  opacity: 0;
  transition: opacity 0.22s;
}
.tool-card:hover {
  transform: translateY(-4px);
  border-color: var(--accent-line, var(--success-color));
  box-shadow: var(--surface-shadow, 0 10px 25px #1024410d);
}
.tool-card:hover::before,
.tool-card:focus-visible::before {
  opacity: 1;
}
.tool-card:focus-visible,
.steps a:focus-visible {
  outline: 2px solid var(--success-color);
  outline-offset: 3px;
}
.tool-top {
  display: contents;
}
.tool-symbol {
  grid-column: 1;
  grid-row: 1 / 3;
  align-self: center;
  display: grid;
  place-items: center;
  width: 43px;
  height: 43px;
  border: 1px solid color-mix(in srgb, var(--success-color) 14%, transparent);
  border-radius: 12px;
  background: var(--accent-soft);
  color: var(--success-color);
  font-size: 23px;
}
.card-arrow {
  grid-column: 3;
  grid-row: 1 / 3;
  align-self: center;
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border: 1px solid var(--border-color);
  border-radius: 50%;
  color: var(--text-secondary);
  font-size: 14px;
  transition:
    transform 0.22s,
    color 0.22s,
    background 0.22s,
    border-color 0.22s;
}
.tool-card:hover .card-arrow {
  color: var(--success-color);
  border-color: var(--accent-line, var(--success-color));
  background: var(--accent-soft);
  transform: rotate(6deg);
}
.tool-card h3 {
  grid-column: 2;
  grid-row: 1;
  font-size: 16px;
  font-weight: 650;
  letter-spacing: -0.25px;
  margin: 0 0 7px;
}
.tool-card > p {
  grid-column: 2;
  grid-row: 2;
  flex: 1;
  font-size: 12px;
  line-height: 1.85;
  color: var(--text-secondary);
  min-height: 0;
  margin: 0;
}
.dashboard-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-top: 31px;
  padding: 21px 0 0;
  border-top: 1px solid var(--border-color);
  font-size: 10px;
  color: var(--text-secondary);
}
.dashboard-footer > span:first-child {
  display: flex;
  align-items: center;
  gap: 8px;
}
.footer-mark {
  color: var(--success-color);
  font-size: 18px;
  line-height: 1;
}
.search-empty {
  padding: 44px 20px;
  text-align: center;
  color: var(--text-secondary);
  border: 1px dashed var(--border-color);
  border-radius: 15px;
  background: var(--bg-secondary);
  font-size: 13px;
}

@media (max-width: 1280px) {
  .dashboard {
    padding: 30px;
  }
  .research-hero {
    padding: 31px;
  }
  .research-map {
    min-width: 275px;
    height: 285px;
    margin-right: -15px;
    margin-left: -15px;
  }
  .map-node {
    min-width: 119px;
    padding: 10px;
    gap: 7px;
  }
  .node-point {
    display: none;
  }
  .node-one {
    top: 25px;
    left: -4px;
  }
  .node-two {
    right: -8px;
    top: 103px;
  }
  .node-three {
    bottom: 20px;
    left: 16px;
  }
  .hero-actions {
    gap: 16px;
  }
  .hero-secondary {
    font-size: 11px;
  }
  .steps a {
    gap: 12px;
    padding: 16px 13px;
  }
  .tool-card {
    padding: 21px 20px 17px;
  }
}
@media (max-width: 1080px) {
  .research-hero h2 {
    font-size: 30px;
  }
  .research-map {
    min-width: 245px;
    margin-left: -38px;
    opacity: 0.85;
  }
  .hero-copy {
    max-width: 440px;
  }
  .hero-actions {
    align-items: flex-start;
    flex-direction: column;
    gap: 13px;
  }
  .hero-caption {
    margin-top: 20px;
  }
  .map-center {
    width: 100px;
    height: 100px;
  }
  .node-icon {
    width: 23px;
    font-size: 14px;
  }
  .map-node {
    min-width: 107px;
    padding: 8px;
  }
  .node-one {
    left: 0;
  }
  .node-two {
    top: 92px;
    right: -12px;
  }
  .section-note {
    font-size: 10px;
  }
  .step-arrow {
    display: none;
  }
  .tool-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 760px) {
  .dashboard {
    padding: 26px 22px 20px;
  }
  .dashboard-heading {
    gap: 15px;
  }
  .date-label {
    padding: 9px 11px;
    font-size: 10px;
    gap: 6px;
  }
  .research-hero {
    min-height: 320px;
    padding: 30px;
  }
  .research-map {
    min-width: 245px;
    margin-right: -28px;
    margin-left: -65px;
  }
  .research-hero h2 {
    font-size: 29px;
  }
  .research-hero p {
    font-size: 12px;
    max-width: 285px;
  }
  .section-note {
    display: none;
  }
  .steps a {
    gap: 9px;
    padding: 16px 10px;
  }
  .step-number {
    font-size: 24px;
  }
  .steps strong {
    font-size: 12px;
  }
  .steps small {
    font-size: 10px;
  }
}
@media (max-width: 600px) {
  .dashboard {
    padding: 24px 18px 20px;
  }
  .dashboard-heading {
    align-items: flex-start;
    flex-direction: column;
    gap: 16px;
    margin-bottom: 21px;
  }
  .eyebrow {
    font-size: 8px;
    letter-spacing: 1.7px;
  }
  h1 {
    font-size: 28px;
  }
  .heading-description {
    font-size: 12px;
  }
  .date-label {
    background: transparent;
    padding: 0;
    border: 0;
    box-shadow: none;
    font-size: 11px;
  }
  .research-hero {
    min-height: 338px;
    padding: 28px 25px;
    border-radius: 17px;
  }
  .research-map {
    position: absolute;
    width: 295px;
    height: 295px;
    right: -118px;
    bottom: -73px;
    margin: 0;
    opacity: 0.32;
    pointer-events: none;
  }
  .map-node,
  .map-coordinate {
    display: none;
  }
  .hero-copy {
    flex: 1 1 auto;
  }
  .hero-label {
    font-size: 9px;
  }
  .research-hero h2 {
    font-size: clamp(26px, 6.6vw, 33px);
    letter-spacing: -0.7px;
  }
  .research-hero p {
    margin-bottom: 20px;
  }
  .compact-break {
    display: inline;
  }
  .hero-actions {
    gap: 15px;
  }
  .hero-caption {
    margin-top: 23px;
    font-size: 9px;
  }
  .section-heading {
    margin: 27px 0 16px;
  }
  .section-heading h2 {
    font-size: 18px;
  }
  .section-heading p {
    font-size: 12px;
  }
  .section-heading .section-kicker {
    font-size: 8px;
  }
  .steps {
    grid-template-columns: 1fr;
    padding: 5px;
    border-radius: 13px;
  }
  .steps a {
    gap: 18px;
    padding: 17px;
  }
  .steps a + a::before {
    top: 0;
    left: 15px;
    right: 15px;
    width: auto;
    height: 1px;
  }
  .steps strong {
    font-size: 13px;
  }
  .steps small {
    font-size: 11px;
  }
  .step-arrow {
    display: inline;
  }
  .tools-section .section-heading {
    align-items: flex-start;
    flex-direction: column;
    gap: 16px;
  }
  .tool-search,
  .tool-search input {
    width: 100%;
  }
  .tool-grid {
    gap: 12px;
  }
  .tool-card {
    display: flex;
    flex-direction: column;
    padding: 18px 17px 15px;
    border-radius: 12px;
  }
  .tool-symbol {
    align-self: flex-start;
    width: 38px;
    height: 38px;
    font-size: 21px;
    border-radius: 10px;
  }
  .card-arrow {
    position: absolute;
    top: 18px;
    right: 16px;
    width: 23px;
    height: 23px;
    font-size: 12px;
  }
  .tool-card h3 {
    font-size: 14px;
    margin-top: 16px;
  }
  .tool-card > p {
    font-size: 11px;
    min-height: 60px;
  }
  .dashboard-footer {
    align-items: flex-start;
    flex-direction: column;
    gap: 10px;
    margin-top: 25px;
    padding-top: 18px;
    font-size: 9px;
  }
}
@media (max-width: 380px) {
  .dashboard {
    padding-right: 16px;
    padding-left: 16px;
  }
  .research-hero {
    padding: 26px 21px;
  }
  .research-hero h2 {
    font-size: 25px;
  }
  .tool-grid {
    grid-template-columns: 1fr;
  }
  .tool-card {
    padding: 21px;
  }
  .tool-card > p {
    min-height: 0;
    font-size: 12px;
  }
}
@media (prefers-reduced-motion: reduce) {
  .dashboard *,
  .dashboard *::before,
  .dashboard *::after {
    transition: none;
  }
  .hero-button:hover,
  .tool-card:hover,
  .tool-card:hover .card-arrow,
  .steps a:hover .step-arrow {
    transform: none;
  }
}
</style>
