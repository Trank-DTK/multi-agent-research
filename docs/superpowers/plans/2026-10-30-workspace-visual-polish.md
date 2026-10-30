# Workspace Visual Polish Implementation Plan

**Goal:** 精致、科技感的蓝色科研工作台，适合长时间阅读。
**Architecture:** 在现有 Vue 组件和 CSS 变量上升级，不改变 API 与业务数据流。首页及导航分别在组件内维护；共享主题与任务页面统一由原主题及 workspace 样式管理。
**Tech Stack:** Vue 3, CSS, Element Plus, Vite。
**Spec:** ../specs/2026-10-30-workspace-visual-design.md

## Global Constraints
保留真实数据和全部行为；明暗主题；桌面及窄屏；不增加运行时依赖；装饰 pointer-events:none；reduced motion。

## Tasks
- [x] 主题与共享控件：更新 theme.css/workspace.css 的色阶、光影、焦点、排版、按钮、面板。修复写作章节标题输入框与共享标题类冲突。
- [x] 首页：dashboard.vue 科研关系图与主视觉、三列工具卡、步骤导航、响应式。
- [x] 导航：ResponsiveNav.vue 品牌、图标底座、选中指示、账户菜单、移动端。
- [x] 对话：ChatInterface.vue/ResearchConversation.vue 头像、空状态、消息、输入区视觉。保持流式与 Markdown。
- [x] 验证：改动文件 lint、生产构建、既有前端测试；桌面/窄屏、明暗模式截图与溢出检查；独立代码审查。清理临时预览。

## Review Focus
CSS scoped 选择器覆盖、导航宽度和主区偏移一致、输入框不受标题布局影响、Markdown 可读性、禁用和键盘焦点、窄屏水平溢出、长聊天和弹窗、现有部署修改不受影响。

## Execution note
用户要求继续，直接在已授权范围执行，其他部署相关未提交修改保持原样。纯视觉变化按上级指令以构建、回归和视觉检查验证。

## Verification
- 既有 Markdown/流式测试：7 项通过。
- 相关 Vue 文件 ESLint 与 Prettier 检查通过。
- 实际 Chrome：1440px 明暗首页、主要任务页，390px 手机页面与菜单，768px 平板页面及注册页；未发现页面横向溢出。
- 修正审查发现：删除图标对比度、蓝底白字对比度、手机论文标题压缩。
- 模拟页面和临时检查脚本已清理。截图位于本机 visualizations/research-polish。
- 当前 Docker Desktop 未运行；只生成前端静态产物，不更改或启动用户的部署配置。
- 最终生产构建（vue-tsc + Vite + PWA）通过；只有既有大包体积与 Browserslist 数据更新提示。
