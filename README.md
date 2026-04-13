# 多智能体科研协作平台

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-green.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-4.2-green.svg)](https://www.djangoproject.com/)
[![Vue](https://img.shields.io/badge/vue-3.4-green.svg)](https://vuejs.org/)
[![Docker](https://img.shields.io/badge/docker-24.0-blue.svg)](https://www.docker.com/)

## 📋 项目简介

多智能体科研协作平台是一个基于大语言模型的多智能体协同系统，旨在帮助科研人员完成文献调研、实验设计、数据分析、论文写作等科研全流程任务。系统采用本地化部署方案，确保科研数据安全，同时支持自定义智能体和工具扩展。

### 核心特性

- 🤖 **多智能体协同**：文献助手、实验助手、评审助手协同工作，形成完整的科研工作流
- 📚 **RAG文献检索**：PDF文档解析、向量化存储、智能语义检索，快速定位关键信息
- 📊 **数据分析**：CSV/Excel数据上传、描述性统计、相关性分析、可视化图表
- ✍️ **论文写作**：智能大纲生成、章节自动撰写、学术润色、Word文档导出
- 🔍 **Critic评审**：自动评估研究质量，提供改进建议，支持反馈循环优化
- 🌙 **暗色模式**：支持亮色/暗色主题切换，保护视力
- 📱 **响应式设计**：完美适配PC、平板、手机等不同设备
- 📦 **PWA支持**：可安装为桌面应用，支持离线访问

## 🏗️ 技术架构

| 层级 | 技术栈 |
|------|--------|
| 前端 | Vue3 + Vite + Element Plus + ECharts |
| 后端 | Django + Django REST Framework |
| AI框架 | LangChain + LangChain Classic |
| LLM | Ollama (qwen2.5:7b) |
| 数据库 | PostgreSQL + pgvector（向量检索） |
| 缓存 | Redis |
| 部署 | Docker + Nginx + Gunicorn |


## 🚀 快速开始

### 环境要求

- **操作系统**：Windows 10+ / macOS 11+ / Linux
- **内存**：8GB以上（推荐16GB）
- **硬盘**：20GB可用空间
- **软件**：Docker & Docker Compose、Ollama

### 一键部署

```bash
# 1. 克隆项目
git clone https://github.com/your-username/multi-agent-research.git
cd multi-agent-research

# 2. 配置环境变量
cp .env.production .env
# 编辑 .env 文件，填入配置

# 3. 安装Ollama并下载模型
ollama pull qwen2.5:7b

# 4. 启动系统
docker-compose -f docker-compose.prod.yml up -d

# 5. 访问系统
# 打开浏览器访问 http://localhost
```


## 开发环境运行

```bash
# 后端
cd bakend
conda create -n multi_agent python=3.11
conda activate multi_agent
pip install -r requirements.txt
python manage.py runserver

# 前端
cd frontend
npm install
npm run dev

# 数据库（使用Docker）
docker-compose up db redis
```


## 项目结构
multi_agent_research/
├── bakend/                     # Django后端
│   ├── accounts/               # 用户认证模块
│   │   ├── views.py            # 注册/登录/用户信息
│   │   └── serializers.py      # 序列化器
│   ├── agents/                 # 智能体核心模块
│   │   ├── agent.py            # 基础智能体
│   │   ├── tools.py            # 基础工具（时间、计算器、随机数）
│   │   ├── literature_agent.py # 文献助手
│   │   ├── experiment_agent.py # 实验助手
│   │   ├── critic_agent.py     # 评审智能体
│   │   ├── orchestrator.py     # 任务编排器
│   │   ├── parallel_executor.py # 并行执行器
│   │   ├── workflow_dag.py     # 工作流DAG
│   │   ├── cache_service.py    # 缓存服务
│   │   └── audit_models.py     # 审计日志
│   ├── chat/                   # 对话模块
│   │   ├── models.py           # Conversation, Message
│   │   └── views.py            # 聊天API
│   ├── documents/              # 文献管理模块
│   │   ├── models.py           # Document, DocumentChunk
│   │   ├── services.py         # PDF解析、向量化
│   │   └── views.py            # 上传、检索API
│   ├── analysis/               # 数据分析模块
│   │   ├── models.py           # Dataset, AnalysisResult
│   │   ├── services.py         # pandas统计分析
│   │   └── views.py            # 分析API
│   ├── writing/                # 论文写作模块
│   │   ├── models.py           # Paper, Section, Citation
│   │   ├── services.py         # 写作服务
│   │   └── views.py            # 写作API
│   ├── core/                   # 核心工具
│   │   ├── exceptions.py       # 异常处理
│   │   ├── throttling.py       # API限流
│   │   └── validators.py       # 输入验证
│   └── backend/                # Django配置
├── frontend/                   # Vue前端
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   │   ├── login.vue       # 登录页
│   │   │   ├── register.vue    # 注册页
│   │   │   ├── dashboard.vue   # 仪表盘
│   │   │   ├── Chat.vue        # AI对话
│   │   │   ├── AgentChat.vue   # 智能体
│   │   │   ├── Documents.vue   # 文献管理
│   │   │   ├── LiteratureChat.vue # 文献助手
│   │   │   ├── Collaboration.vue  # 协作研究
│   │   │   ├── DataAnalysis.vue   # 数据分析
│   │   │   └── PaperWriting.vue   # 论文写作
│   │   ├── components/         # 公共组件
│   │   │   ├── ResponsiveNav.vue   # 响应式导航
│   │   │   ├── ThemeToggle.vue     # 主题切换
│   │   │   ├── SkeletonLoader.vue  # 骨架屏
│   │   │   └── WorkflowVisualizer.vue # 工作流可视化
│   │   ├── stores/             # Pinia状态管理
│   │   │   └── theme.js        # 主题Store
│   │   ├── composables/        # 组合式函数
│   │   │   ├── useResponsive.js    # 响应式
│   │   │   ├── useKeyboardShortcuts.js # 快捷键
│   │   │   └── useInfiniteScroll.js   # 无限滚动
│   │   ├── utils/              # 工具函数
│   │   │   ├── errorHandler.js # 错误处理
│   │   │   └── performance.js  # 性能监控
│   │   └── styles/             # 全局样式
│   │       └── theme.css       # 主题变量
|   ├──axios.js                 # HTTP请求
│   ├── public/                 # 静态资源
│   └── package.json
├── docker-compose.yml          # 开发环境Docker配置
├── docker-compose.prod.yml     # 生产环境Docker配置
├── Dockerfile                  # 后端镜像
├── Dockerfile.prod             # 生产环境镜像
├── nginx/                      # Nginx配置
├── test/                       # 测试脚本
│   └── e2e_test.py             # 端到端测试
├── docs/                       # 文档
│   ├── API.md                  # API文档
│   ├── DEPLOYMENT.md           # 部署指南
│   └── soft_copyright/         # 软著材料
├── .env.production             # 生产环境变量
└── README.md                   # 项目说明