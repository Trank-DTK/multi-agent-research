<template>
  <PublicFrame>
    <main id="home-page" ref="content">
      <section class="hero" id="home">
        <div class="hero-grid" aria-hidden="true"></div>
        <div class="hero-scene" aria-hidden="true">
          <ResearchField />
          <div class="scene-label label-evidence"><span></span>知识与证据</div>
          <div class="scene-label label-reasoning"><span></span>协作与推理</div>
          <div class="scene-label label-discovery"><span></span>探索与发现</div>
          <div class="scene-fade"></div>
        </div>
        <div class="hero-content">
          <div class="hero-eyebrow intro intro-one">
            <span class="eyebrow-line"></span>让每一种可能，彼此连接
          </div>
          <h1>
            <span class="title-line"><span>让探索，</span></span
            ><span class="title-line"><span class="hero-accent">越过边界。</span></span>
          </h1>
          <p class="hero-description intro intro-three">
            从一个值得追问的问题，<br />到文献、数据与智能体共同抵达的答案。
          </p>
          <div class="hero-actions intro intro-four">
            <RouterLink to="/register" class="button button-white button-large"
              >开启我的研究空间 <svg><use href="#public-arrow" /></svg></RouterLink
            ><RouterLink to="/#workspace" class="text-link"
              ><span class="play-disc">↗</span>看看它如何工作</RouterLink
            >
          </div>
          <div class="hero-context intro intro-five">
            <span>文献检索</span><i></i><span>多智能体协作</span><i></i><span>数据分析</span><i></i
            ><span>论文写作</span>
          </div>
        </div>
        <RouterLink class="scroll-cue" to="/#capabilities"
          ><span class="scroll-track"><span></span></span><span>向下探索</span></RouterLink
        >
        <div class="hero-side-note" aria-hidden="true">IDEAS BECOME DISCOVERIES</div>
      </section>
      <section class="capability-section section-shell" id="capabilities">
        <header class="section-heading reveal">
          <span class="section-index">01 / 能力</span>
          <h2>不止是回答。<br /><span>是让研究，向前一步。</span></h2>
          <p>
            把分散的工具，连接成一个连贯的研究空间。<br />你专注问题，智能助手参与每一个关键环节。
          </p>
        </header>
        <div class="capability-list">
          <RouterLink to="/documents" class="capability-row reveal"
            ><div class="capability-number">01</div>
            <div class="capability-icon">
              <svg><use href="#public-file" /></svg>
            </div>
            <h3>从海量信息中，<br />找到值得相信的证据。</h3>
            <p>集中管理参考文献。围绕已上传资料提问，提取结论、比较方法，让每个观点有据可循。</p>
            <span class="round-arrow"
              ><svg><use href="#public-arrow" /></svg></span
          ></RouterLink>
          <RouterLink to="/collaboration" class="capability-row reveal"
            ><div class="capability-number">02</div>
            <div class="capability-icon">
              <svg><use href="#public-network" /></svg>
            </div>
            <h3>让不同的思考，<br />在同一个问题上交汇。</h3>
            <p>文献分析、实验设计与研究评审协同推进，把一个开放问题转化为可继续执行的研究方案。</p>
            <span class="round-arrow"
              ><svg><use href="#public-arrow" /></svg></span
          ></RouterLink>
          <RouterLink to="/analysis" class="capability-row reveal"
            ><div class="capability-number">03</div>
            <div class="capability-icon">
              <svg><use href="#public-chart" /></svg>
            </div>
            <h3>读懂数据，<br />也让想法被清晰表达。</h3>
            <p>预览与分析数据，生成可视化，再从大纲到章节组织论文，让发现逐步成为成果。</p>
            <span class="round-arrow"
              ><svg><use href="#public-arrow" /></svg></span
          ></RouterLink>
        </div>
      </section>
      <section class="workspace-section" id="workspace">
        <div class="section-shell">
          <header class="workspace-heading reveal">
            <div>
              <span class="section-index">02 / 工作空间</span>
              <h2>复杂留给研究。<br /><span>清晰，留在眼前。</span></h2>
            </div>
            <RouterLink to="/dashboard" class="text-link"
              >进入科研工作区 <svg><use href="#public-arrow" /></svg
            ></RouterLink>
          </header>
          <div class="product-perspective reveal">
            <div class="product-aura" aria-hidden="true"></div>
            <RouterLink to="/dashboard" class="product-window" aria-label="进入科研工作台"
              ><div class="window-bar">
                <span class="window-dots"><i></i><i></i><i></i></span
                ><span class="window-title">研知协作 / 科研工作台</span
                ><span class="window-open">进入工作台 ↗</span>
              </div>
              <img
                :src="workspacePreview"
                width="1440"
                height="1000"
                loading="lazy"
                alt="研知协作科研工作台，含研究流程与工具导航；截图使用演示数据" />
              <div class="window-shine" aria-hidden="true"></div
            ></RouterLink>
          </div>
          <div class="workspace-caption reveal">
            <span>连接文献、数据与写作的同一个空间</span><small>界面示意 · 数据为演示内容</small>
          </div>
        </div>
      </section>
      <section class="workflow-section section-shell" id="workflow">
        <header class="section-heading reveal">
          <span class="section-index">03 / 研究流程</span>
          <h2>从灵感出发。<br /><span>每一步，都有所抵达。</span></h2>
        </header>
        <div class="journey-grid">
          <article class="journey-step reveal">
            <div class="journey-top">
              <span>01</span><span class="journey-line"></span
              ><svg><use href="#public-file" /></svg>
            </div>
            <h3>建立你的知识底座</h3>
            <p>上传文献、整理资料，围绕问题积累研究证据。</p>
            <RouterLink to="/documents"
              >进入文献空间 <svg><use href="#public-arrow" /></svg
            ></RouterLink>
          </article>
          <article class="journey-step reveal">
            <div class="journey-top">
              <span>02</span><span class="journey-line"></span
              ><svg><use href="#public-network" /></svg>
            </div>
            <h3>让问题得到充分推演</h3>
            <p>讨论假设、比较方法，借助智能体组织研究方案。</p>
            <RouterLink to="/collaboration"
              >探索协作研究 <svg><use href="#public-arrow" /></svg
            ></RouterLink>
          </article>
          <article class="journey-step reveal">
            <div class="journey-top">
              <span>03</span><span class="journey-line"></span><svg><use href="#public-pen" /></svg>
            </div>
            <h3>把发现，写成成果</h3>
            <p>分析数据、梳理论证，将研究进展转化为论文表达。</p>
            <RouterLink to="/writing"
              >打开写作空间 <svg><use href="#public-arrow" /></svg
            ></RouterLink>
          </article>
        </div>
      </section>
      <section class="model-section section-shell">
        <div class="model-layout reveal">
          <div class="model-orbit" aria-hidden="true">
            <div class="model-ring ring-one"></div>
            <div class="model-ring ring-two"></div>
            <div class="model-core">
              <svg><use href="#public-spark" /></svg>
            </div>
            <span class="model-text-one">云端模型</span><span class="model-text-two">本地模型</span>
          </div>
          <div class="model-copy">
            <span class="section-index">你的研究，你来选择</span>
            <h2>智能，可以很强大。<br /><span>也可以由你定义。</span></h2>
            <p>
              连接你习惯的云端供应商，或使用本地模型。<br />配置自己的模型、API Key 与服务地址。
            </p>
            <div class="provider-names">
              <span>DeepSeek</span><span>OpenRouter</span><span>Qwen</span><span>OpenAI</span
              ><span>Ollama</span><span>LM Studio</span>
            </div>
          </div>
        </div>
      </section>
      <section class="closing-section">
        <div class="closing-glow" aria-hidden="true"></div>
        <div class="section-shell closing-content reveal">
          <span class="section-index">留一个空间，给下一次发现</span>
          <h2>好问题，<br />值得一个更好的起点。</h2>
          <RouterLink to="/register" class="button button-white button-large"
            >开始我的下一步 <svg><use href="#public-arrow" /></svg></RouterLink
          ><RouterLink to="/dashboard" class="closing-preview">先进入科研工作区 ↗</RouterLink>
        </div>
      </section>
      <footer class="site-footer section-shell">
        <RouterLink class="brand" to="/"
          ><span class="brand-emblem"><img src="/favicon.ico" alt="" /></span
          ><strong>研知协作<span>RESEARCH WORKSPACE</span></strong></RouterLink
        >
        <p>让知识彼此连接，让研究继续发生。</p>
        <div class="footer-links">
          <RouterLink to="/login">登录</RouterLink><RouterLink to="/register">注册</RouterLink
          ><RouterLink to="/settings">模型设置</RouterLink>
        </div>
      </footer>
    </main>
  </PublicFrame>
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import PublicFrame from '@/components/PublicFrame.vue'
import ResearchField from '@/components/ResearchField.vue'
import workspacePreview from '@/assets/workspace-preview.png'
defineOptions({ name: 'PublicLanding' })
const content = ref(null)
let observer
onMounted(() => {
  if (!window.IntersectionObserver) return
  observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries)
        if (entry.isIntersecting) {
          entry.target.classList.add('visible')
          observer.unobserve(entry.target)
        }
    },
    { threshold: 0.12, rootMargin: '0px 0px -25px 0px' },
  )
  content.value.querySelectorAll('.reveal').forEach((element) => observer.observe(element))
})
onBeforeUnmount(() => observer?.disconnect())
</script>
