# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **安全**: 全局异常处理器，结构化 JSON 错误响应
- **安全**: CORS 按环境配置，生产环境限制来源域名
- **安全**: XSS 防护（前端消息转义）
- **安全**: 接口限流（内存限流器，30 次/分钟/IP）
- **安全**: 安全响应头（CSP / X-Frame-Options / X-Content-Type-Options）
- **安全**: API Key 日志脱敏工具
- **架构**: 依赖注入容器（FastAPI Depends + 工厂模式）
- **架构**: 请求/响应 DTO（Pydantic schemas），完整字段校验
- **架构**: 统一错误码体系（13 个业务错误码）
- **架构**: 常量模块，消除所有魔法数字
- **可观测**: structlog 结构化日志，替代 print()
- **可观测**: 请求 ID 中间件（X-Request-ID 生成与传播）
- **可观测**: 健康检查增强（Open-Meteo 连通性检测 + /metrics 端点）
- **韧性**: httpx 客户端复用（连接池）
- **韧性**: 外部 API 调用重试（tenacity 指数退避）
- **韧性**: 可配置超时时间
- **测试**: 58 个测试用例（单元 + 集成）
- **测试**: respx mock 外部 HTTP 调用
- **测试**: 覆盖率 79%+
- **配置**: 多环境支持（development / staging / production）
- **配置**: 启动时配置校验（必填项快速失败）
- **部署**: 多阶段 Dockerfile（非 root 运行 + HEALTHCHECK）
- **部署**: docker-compose.yml（backend + frontend + Redis）
- **部署**: GitHub Actions CI/CD（lint → test → build → push）
- **部署**: systemd 进程守护配置
- **工具**: pyproject.toml 统一依赖管理
- **工具**: ruff lint + format
- **工具**: pre-commit hooks

### Changed
- 前端 XSS 漏洞修复（innerHTML → textContent + escapeHtml）
- CORS 从 `["*"]` 改为环境变量配置
- 所有 `print()` 替换为 structlog 结构化日志
- WeatherService httpx 客户端从每次创建改为复用
- DisasterService 全局单例改为 DI 容器管理

### Fixed
- `.gitignore` 增强，防止敏感文件泄露
- `.env` 中的真实 API Key 已替换为占位符
- disaster 路由返回值从元组改为 HTTPException

## [0.1.0] - 2024-01-01

### Added
- 初始 MVP 版本
- 多语言智能天气问答（7 种语言）
- 气象数据可视化 Dashboard
- 灾害预警系统（暴雨/台风/高温）
- 台风路径实时追踪
- 农业气象建议
- 物流气象风险评估
- LangChain Agent + Open-Meteo API 集成
