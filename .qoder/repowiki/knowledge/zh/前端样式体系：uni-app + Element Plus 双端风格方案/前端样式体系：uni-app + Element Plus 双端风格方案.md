---
kind: frontend_style
name: 前端样式体系：uni-app + Element Plus 双端风格方案
category: frontend_style
scope:
    - '**'
source_files:
    - frontend/mobile-app/uni.scss
    - frontend/mobile-app/App.vue
    - frontend/mobile-app/pages.json
    - frontend/web-admin/package.json
    - frontend/web-admin/src/main.ts
    - frontend/web-admin/src/views/Layout.vue
---

本仓库包含两个独立的前端应用，分别面向移动端与 Web 管理后台，采用不同的 UI 技术栈与样式策略。

## 1. 移动端（uni-app）
- 框架：基于 uni-app（Vue 2/3 兼容），使用 view、text、image 等跨端标签。
- 样式语言：原生 CSS（scss 仅用于全局变量定义），所有页面样式以 style scoped 内联在 .vue 文件中。
- 设计变量：通过 uni.scss 集中声明主题色（primary/success/warning/danger/info）、背景色、文本色、边框色等 SCSS 变量，供全局引用。
- 全局样式：App.vue 中为 page 根节点设置统一背景色与字体族；pages.json 的 globalStyle 配置导航栏样式与 TabBar 选中色（#409eff）。
- 组件库：未引入第三方 UI 库，按钮、卡片、进度条等均为手写样式，遵循统一的圆角（8px/12px）、间距（15px/20px）与颜色语义规范。
- 响应式策略：依赖 uni-app 的 rpx 单位与 flex 布局，适配多端尺寸。

## 2. Web 管理后台（Vue 3 + Vite）
- 框架：Vue 3 + TypeScript + Vite，路由使用 vue-router，状态管理使用 Pinia。
- UI 组件库：Element Plus（v2.5+），通过 main.ts 全局注册并引入其默认样式 element-plus/dist/index.css。
- 图标：使用 @element-plus/icons-vue 官方图标集。
- 图表：ECharts + vue-echarts 用于数据看板。
- 样式组织：页面级 style scoped 覆盖 Element Plus 默认主题（如侧边栏深色 #1d1e1f、激活态 #409eff、主内容区 #f5f7fa），整体沿用与移动端一致的蓝色系品牌色。
- 布局约定：Layout.vue 固定左侧 220px 侧边栏 + 顶部 header + 主内容区的经典后台布局结构。

## 3. 跨端一致性约定
- 品牌主色：两端统一使用 #409eff（Element Plus 默认蓝）作为强调色。
- 语义化配色：success(#67c23a)、warning(#e6a23c)、danger(#f56c6c)、info(#909399) 在两端的 SCSS 变量与内联样式中保持一致。
- 无 Tailwind / PostCSS / Sass 编译链：移动端未启用 Sass 预处理器（仅 uni.scss 被 uni-app 内置支持），Web 端也未配置 tailwind.config 或 postcss 插件。

## 开发者应遵循的规则
1. 新增页面优先复用 uni.scss 中的变量，避免硬编码颜色值。
2. 移动端样式一律使用 style scoped，禁止污染全局命名空间。
3. Web 后台如需覆盖 Element Plus 主题，应在对应视图文件的 style scoped 中以类名精确选择器覆盖，不要修改全局 CSS。
4. 保持两端品牌色一致，新增语义色时同步更新 uni.scss 与相关组件。
5. 不使用外部 CSS 框架（Tailwind、Bootstrap 等），维持轻量与可控性。