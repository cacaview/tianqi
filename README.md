# 🌬️ 万语风 PolyWind

> 面向中国—东盟的多语言气象智能决策助手

**Slogan**: 万种语言，一种风 —— 以AI连接气象与世界

---

## 📖 项目介绍

万语风 (PolyWind) 是一个基于 LLM Agent 的多语言智能气象服务应用，将天气预报转化为面向公众和行业的可执行决策建议。覆盖广西及东盟地区，支持 **7 种语言**交互（中/英/越/泰/印尼/缅/老）。

### 核心功能

- 🌤️ **多语言智能天气问答** — 自然语言查询天气，支持7种语言
- 🌀 **台风路径实时追踪** — NHC 数据源 + 模拟数据降级
- ⚠️ **灾害预警系统** — 暴雨/台风/高温/雷暴多灾种预警
- 🌾 **农业气象建议** — 水稻/甘蔗等作物风险评估
- 🚛 **物流气象风险** — 跨境运输路线天气风险评估
- 📊 **数据可视化 Dashboard** — ECharts + Leaflet 地图

---

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | Python 3.11+ / FastAPI / LangChain / LangGraph |
| **前端** | 纯 HTML/CSS/JS（MVP），Vite + Vue 3（规划中） |
| **数据源** | Open-Meteo API / QWeather / NHC |
| **LLM** | DashScope 通义千问 / 自定义 OpenAI 兼容端点 |
| **缓存** | Redis（可选） |
| **测试** | pytest + respx + httpx TestClient |
| **部署** | Docker + Nginx + GitHub Actions |

---

## 🚀 快速开始

### 方式一：本地开发

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -e ".[dev]"

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 5. 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 6. 打开浏览器
# API 文档: http://localhost:8000/docs
# 健康检查: http://localhost:8000/health
```

### 方式二：Docker Compose（推荐）

```bash
# 配置环境变量
export DASHSCOPE_API_KEY=your_key_here

# 一键启动
docker-compose up -d

# 访问
# 前端: http://localhost
# API: http://localhost:8000
# 文档: http://localhost:8000/docs
```

---

## 🧪 运行测试

```bash
cd backend

# 运行所有测试
python -m pytest tests/ -v

# 运行测试并生成覆盖率报告
python -m pytest tests/ --cov=app --cov-report=term-missing

# 仅运行单元测试
python -m pytest tests/ -v -m "not integration"
```

---

## 📁 项目结构

```
polywind/
├── backend/
│   ├── app/
│   │   ├── api/                    # 接口层
│   │   │   ├── routes/             # 路由定义
│   │   │   ├── schemas.py          # 请求/响应 DTO
│   │   │   ├── deps.py             # 依赖注入容器
│   │   │   ├── weather.py          # 天气 API
│   │   │   ├── chat.py             # 对话 API
│   │   │   ├── disaster.py         # 灾害预警 API
│   │   │   └── health.py           # 健康检查 API
│   │   ├── core/                   # 公共层
│   │   │   ├── config.py           # 多环境配置
│   │   │   ├── constants.py        # 常量定义
│   │   │   ├── exceptions.py       # 统一错误码
│   │   │   └── logging.py          # 结构化日志
│   │   ├── middleware/             # 中间件
│   │   │   ├── error_handler.py    # 全局异常处理
│   │   │   ├── request_id.py       # 请求 ID
│   │   │   └── security.py         # 安全响应头
│   │   ├── services/               # 业务层
│   │   │   ├── weather_service.py  # 气象数据服务
│   │   │   ├── disaster_service.py # 灾害预警服务
│   │   │   └── agent_service.py    # LLM Agent 服务
│   │   ├── tools/                  # LangChain 工具
│   │   └── main.py                 # 应用入口
│   ├── tests/                      # 测试目录
│   ├── pyproject.toml              # 项目配置
│   ├── Dockerfile                  # 容器构建
│   └── .pre-commit-config.yaml     # Git hooks
├── frontend/                       # 前端静态文件
├── .github/workflows/ci.yml        # CI/CD 流水线
├── docker-compose.yml              # 容器编排
├── nginx.conf                      # Nginx 配置
├── CHANGELOG.md                    # 变更日志
└── README.md                       # 本文件
```

---

## 🏗️ 架构说明

### 分层架构

```
┌─────────────────────────────────────────────────┐
│                   接口层 (API)                    │
│  参数校验 → 依赖注入 → 调用业务层 → 格式化响应    │
├─────────────────────────────────────────────────┤
│                 业务层 (Services)                 │
│  天气服务 / 灾害服务 / Agent 服务                 │
├─────────────────────────────────────────────────┤
│                 公共层 (Core)                     │
│  配置 / 常量 / 异常 / 日志 / 安全                 │
└─────────────────────────────────────────────────┘
```

### 依赖注入

使用 FastAPI 原生 `Depends()` + 工厂模式，通过 `deps.py` 统一管理 Service 生命周期。

### 外部调用韧性

所有外部 HTTP 调用（Open-Meteo / QWeather / NHC）均配备：
- 连接池复用（httpx.AsyncClient）
- 超时控制（可配置）
- 指数退避重试（tenacity）
- 结构化错误日志

---

## 🌐 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查（含依赖连通性） |
| `/metrics` | GET | 运行指标 |
| `/api/weather/current` | GET | 当前天气 |
| `/api/weather/forecast` | GET | 天气预报 |
| `/api/weather/cities` | GET | 东盟城市列表 |
| `/api/chat/send` | POST | 智能对话 |
| `/api/disaster/alerts` | GET | 灾害预警汇总 |
| `/api/disaster/typhoons` | GET | 台风列表 |
| `/api/disaster/agriculture` | GET | 农业气象建议 |
| `/api/disaster/logistics` | GET | 物流气象风险 |
| `/api/disaster/map-data` | GET | 地图可视化数据 |

完整 API 文档请访问: `http://localhost:8000/docs`

---

## 🔧 配置说明

所有配置通过环境变量管理，优先级：`环境变量` > `.env` 文件 > 默认值。

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `POLYWIND_ENV` | `development` | 运行环境 |
| `DASHSCOPE_API_KEY` | - | 通义千问 API Key |
| `OPENAI_API_KEY` | - | OpenAI 兼容 API Key |
| `LLM_MODEL` | `qwen-plus` | LLM 模型名称 |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis 连接 |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | CORS 允许来源 |
| `PORT` | `8000` | 服务端口 |

---

## 🤝 开发规范

### Git 提交规范

```
<type>(<scope>): <subject>

type:
  feat     新功能
  fix      修复
  docs     文档
  style    代码格式
  refactor 重构
  test     测试
  chore    构建/工具
```

### 代码质量

```bash
# Lint
ruff check app/

# Format
ruff format app/

# Type check
mypy app/
```

---

## 📄 License

MIT License
