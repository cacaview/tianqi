# ADR-003: 前端构建工具链

## 状态

已批准

## 背景

原前端为两个纯 HTML 文件（index.html / dashboard.html），内联全部 CSS 和 JS（约 1400 行），无法模块化、无法 tree-shaking、无法代码分割。

## 决策

引入 **Vite + Vue 3 + TypeScript** 构建工具链。

### 选择理由

| 方案 | 优点 | 缺点 |
|------|------|------|
| Vite + Vue 3（**选用**） | 快速 HMR、Composition API、TypeScript、生态丰富 | 增加构建步骤 |
| 保持纯 HTML | 零构建依赖、部署简单 | 无法模块化、无法组件复用 |
| React | 生态最大 | 对本项目偏重、学习成本高 |
| Next.js / Nuxt | SSR 支持 | 过度工程化 |

## 后果

- 组件化开发：ChatPanel / CitySidebar / WeatherCard / AlertCard 等
- TypeScript 类型安全
- API 调用层抽取为独立 service 模块
- baseURL 从环境变量读取，适配不同部署环境
- 开发体验提升（HMR、热重载）
