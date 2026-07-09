# ADR-001: 后端依赖注入方案

## 状态

已批准

## 背景

项目需要在 FastAPI 中管理 Service 的生命周期和依赖关系。原代码通过模块级实例化和全局函数获取 Service，导致跨请求状态共享和测试困难。

## 决策

采用 **FastAPI 原生 `Depends()` + 工厂模式**，在 `deps.py` 中定义 Service 工厂函数，通过 `Annotated` 类型别名简化使用。

### 选择理由

| 方案 | 优点 | 缺点 |
|------|------|------|
| FastAPI Depends()（**选用**） | 零额外依赖、与 FastAPI 深度集成、学习成本低 | 复杂依赖关系时代码稍冗长 |
| dependency-injector 库 | 功能强大、支持复杂 DI 容器 | 增加依赖、学习成本高、项目规模不需要 |
| 手动工厂 | 完全控制 | 与 FastAPI 集成差、重复造轮子 |

## 后果

- Service 生命周期由 FastAPI 管理，请求级作用域清晰
- 测试时可轻松替换 Mock Service
- `Annotated` 类型别名（如 `WeatherServiceDep`）使路由签名简洁
