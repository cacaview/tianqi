# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**万语风 PolyWind** — 多语言AI气象决策助手，面向中国-东盟区域，支持7种语言（zh/en/vi/th/id/my/lo）。为"AI+众创气象服务"创新大赛作品，截止日期 2026年10月13日。

**Tech Stack**: Python 3.11+ / FastAPI / LangChain+LangGraph / Open-Meteo API / NHC / QWeather

## Development Commands

```bash
# Backend setup
cd backend && pip install -e ".[dev]"

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Or with Docker
docker compose up --build

# Lint & format
ruff check . --fix
ruff format .

# Type check
mypy app/

# Tests (single test)
cd backend && python -m pytest tests/test_weather_service.py -v

# All tests with coverage
python -m pytest tests/ --cov=app --cov-report=term-missing

# Coverage threshold: 79% (configured in pyproject.toml)

# Frontend
cd frontend && npm run dev      # Dev server (http://localhost:5173, proxy /api → :8000)
npm run build                    # Production build → dist/
npm run preview                  # Preview production build
npx vue-tsc --noEmit             # TypeScript type check
```

## Architecture

```
backend/
├── app/
│   ├── api/          # FastAPI routers + Pydantic schemas (DTOs)
│   ├── services/     # Business logic (weather, disaster, agent)
│   ├── tools/        # LangChain @tool functions (8 tools)
│   ├── core/         # Config, constants, exceptions, logging
│   ├── middleware/    # Request ID, security headers, error handling
│   └── models/       # ORM models (currently empty)
└── tests/            # pytest + respx mocks, 58 test cases
frontend/             # Vite + Vue 3 + TypeScript (src/views/, src/components/, src/composables/)
```

### Key Patterns

- **Dependency Injection**: Use `api/deps.py` with `Annotated[T, Depends(factory)]` — singletons for services
- **Error Handling**: Extend `AppError` from `core/exceptions.py` with `ErrorCode` enum; global handler in middleware
- **Logging**: Use `structlog.get_logger()` — structured JSON in production, console in dev
- **Service Pattern**: Services use httpx with tenacity retry (3 attempts, exponential backoff)
- **LLM Fallback**: Agent service tries LangChain agent → falls back to rule-based keyword matching
- **Testing**: Use `respx` to mock external HTTP, `httpx.AsyncClient` with `ASGITransport` for API tests

### External Data Sources

- **Open-Meteo** (free, no key): Primary weather data for 15 ASEAN cities
- **NHC** (free): Typhoon tracking, filters Western Pacific (WP/CP/SH prefixes)
- **QWeather** (requires `QWEATHER_API_KEY`): Chinese disaster warnings, with mock fallback
- **LLM**: DashScope (`DASHSCOPE_API_KEY`) or OpenAI-compatible endpoint (`LLM_BASE_URL` + `OPENAI_API_KEY`)

## Code Conventions

- Python: ruff format (line-length 120), mypy strict mode, target py311
- Pydantic v2 models in `api/schemas.py` for all request/response types
- All API routes return `ErrorResponse` on failure, never raw exceptions
- Frontend: Vite + Vue 3 + TypeScript (Composition API `<script setup>`)，ECharts/Leaflet 按需加载，XSS 防护 via `escapeHtml()`；旧版 HTML 保留在 `frontend/legacy/`
- Env vars prefixed with `POLYWIND_ENV` in `Settings` class
- Pre-commit hooks enforce trailing whitespace, ruff lint+format, YAML/TOML checks

## Environment Variables

Required (at least one LLM key in production):
- `DASHSCOPE_API_KEY` — DashScope/Qwen access
- `LLM_BASE_URL` + `OPENAI_API_KEY` — OpenAI-compatible endpoint
- `QWEATHER_API_KEY` — QWeather alerts (optional, has mock fallback)
- `REDIS_URL` — Caching (optional, in-memory fallback)
- `POLYWIND_ENV` — development/staging/production

Frontend (Vite):
- `VITE_API_BASE_URL` — Backend API base URL (default: empty, uses Vite dev proxy)

---

## Discovered Data Sources（外部数据源调研，2026-07）

> 以下为经 MCP + GitHub CLI 搜索调研发现的可用数据源，按优先级排列，供后续开发参考。

### 中国专属 API（优先集成）

| 数据源 | 费用 | URL | 数据类型 |
|--------|------|-----|----------|
| **和风天气 QWeather** | 免费层 1000次/天 | `dev.qweather.com` | 实时天气、30天预报、分钟级降水、AQI、灾害预警、生活指数、台风追踪 |
| **心知天气 Seniverse** | 14天免费试用 | `seniverse.com/api` | 27种生活指数、1km网格数据、雷电数据、FY-4A卫星云图、路况天气 |
| **彩云天气 Caiyun** | 免费层可用 | `docs.caiyunapp.com` | 分钟级降水(2小时)、AQI、台风、预警；有官方MCP Server + Python SDK |
| **UAPI** | **完全免费无需注册** | `uapis.cn` | 实时天气、7天预报、AQI、18种生活指数；零摩擦，适合快速原型 |
| **中国气象局CMA** | 免费（非官方API） | `weather.cma.cn/api/` | 全国预报(1-7天)、实时观测、站点搜索、预警；社区维护，可能变动 |

### 空气质量

| 数据源 | 费用 | 特点 |
|--------|------|------|
| **AQICN / WAQI** | 免费(需token注册) | 11000+ 站点，PM2.5/PM10/NO2/CO/SO2/O3，1000 req/s |
| **OpenAQ** | 完全免费开源 | 全球政府监测站数据，适合历史分析 |

### 灾害预警

| 数据源 | 费用 | 类型 |
|--------|------|------|
| **地震速报 API** (api.ruseo.cn) | 免费 | 国内外地震速报，5-20分钟更新 |
| **Wolfx 防灾 API** (wolfx.jp) | 免费无需注册 | 地震+EEW预警，JMA/CENC/USGS 数据，HTTP+WebSocket |
| **天气天 API** (tianqiapi.com) | 免费层 | 全国气象预警（暴雨/大风/雷电/高温/雾），按省查询 |
| **星图云灾害捕手** | 付费 | 11种标准+30种扩展预警类型，最全面 |

### 卫星雷达

| 数据源 | 费用 | 特点 |
|--------|------|------|
| **风云卫星NSMC** (satellite.nsmc.org.cn) | 免费(注册) | FY-4A 每15分钟全盘成像，官方来源 |
| **RainViewer API** | 免费无key | 1200+ 雷达站覆盖中国，5分钟刷新 |
| **AWS Himawari-9** | AWS S3公开数据 | 向日葵9号，覆盖东亚和西太平洋 |

### AI/ML 气象预测模型

| 模型 | 来源 | 特点 |
|------|------|------|
| **Pangu-Weather** | 华为 (Nature 2023) | 已开源，3D深度学习全球预报 |
| **FuXi** | 复旦大学 | 已开源，有 AWS SageMaker 部署方案 |
| **GraphCast** | Google DeepMind | NCEP已业务化运行 |

### 推荐集成组合

```
核心天气:     QWeather (主力) + UAPI (免费备用) + Open-Meteo (已有)
分钟级降水:   彩云天气 (最强) + UAPI (免费)
空气质量:     AQICN/WAQI (免费全面)
灾害预警:     QWeather预警 + Wolfx地震API + 天气天API
卫星雷达:     风云卫星NSMC + RainViewer雷达
生活指数:     UAPI (18种) / Seniverse (27种)
AI预测:       Open-Meteo (已含CMA GRAPES + GraphCast)
```

---

## Development Roadmap（功能开发路线图，2026-07 调研）

> 基于 MCP + GitHub CLI 对开源天气项目（Breezy Weather 10.6k⭐、wind-layer 702⭐、wego 8.5k⭐、weather-mcp-server 246⭐）及行业最佳实践的调研结果。

### 核心策略

**最高效路径**：结合 Open-Meteo 免费 API 扩展（分钟级降水、AQI、花粉、历史数据）+ LLM 驱动的自然语言生成（穿衣建议、天气报告、个性化推荐）。无需新基础设施投入即可媲美商业天气应用。

### P0 — 立即实施（最高 ROI）

| 功能 | 复杂度 | 实现方式 |
|------|--------|----------|
| **分钟级降水预报** | 低 | Open-Meteo `minutely_15` 参数，零新 API 成本 |
| **AI 穿衣/生活指数** | 低-中 | LLM 从现有天气数据生成穿衣、洗车、运动等建议 |
| **自然语言天气报告** | 低 | 优化现有 Agent prompt 生成多语言结构化叙述 |
| **空气质量 (PM2.5/AQI)** | 低 | Open-Meteo Air Quality API（免费） |

### P1 — 近期（体验升级）

| 功能 | 复杂度 | 实现方式 |
|------|--------|----------|
| **个性化预警规则** | 中 | 用户自定义阈值 + 浏览器推送通知 |
| **交互式天气地图** | 中-高 | wind-layer (WebGL) + MapLibre GL JS |
| **24小时逐时预报图表** | 低-中 | ECharts 双轴图表 |
| **深色模式 + 动态主题** | 低 | CSS 变量 + `prefers-color-scheme` |
| **PWA 支持** | 中 | Service Worker + Web App Manifest |

### P2 — 中期（差异化）

| 功能 | 复杂度 | 实现方式 |
|------|--------|----------|
| **LLM 分层推理** | 中 | LangGraph 多尺度分析（逐时/6h/日） |
| **花粉/过敏原数据** | 低 | Open-Meteo Air Quality API |
| **历史天气对比** | 中 | Open-Meteo Historical API (1940-至今) |
| **Weather MCP Server** | 低-中 | Python MCP SDK 暴露现有 API 给 Claude/Cursor |

### P3 — 长期（生态系统）

| 功能 | 实现方式 |
|------|----------|
| 多渠道通知（Telegram / 邮件 / 微信公众号） | Bot API + SMTP |
| 城市天气对比面板 | ECharts 对比图表 |
| 天气数据故事生成 | LLM 年度气候回顾 |
| 语音天气播报 | Web Speech API / TTS |
| AI 天气场景图片 | 图像生成模型 |
| 社区天气报告 | 众包数据收集 |
| 智能家居集成 | IFTTT / Webhook |

### 关键开源参考

- **Breezy Weather** (10.6k⭐): 50+ 数据源，Material 3 设计，16天预报，花粉/UV，开源天气应用标杆
- **wind-layer** (702⭐): WebGL 风场/粒子可视化，支持 MapLibre/Mapbox/Leaflet/OpenLayers
- **wego** (8.5k⭐): 终端天气客户端，聚合 8 个后端数据源包括 Open-Meteo
- **weather-mcp-server** (246⭐): Claude MCP 天气集成，16 个工具，AI 助手集成范例

---

## Enterprise & Social Features Research（企业与社会功能调研，2026-07）

> 基于CLI搜索 + 3个并行研究代理的综合分析，涵盖22个数据源、14项新功能提案。
> 详细报告见 `docs/research-enterprise-social-features.md`

### 新增可集成免费API（已验证）

| API | 数据内容 | 费用 | 注册 | 优先级 |
|-----|---------|------|------|--------|
| **Open-Meteo Marine** | 浪高/浪向/海流/海温，5km分辨率，16天预报 | 免费 | 无需 | P0 |
| **Open-Meteo Flood** | 河流流量模拟（GloFAS），92天预报，1940年至今 | 免费 | 无需 | P0 |
| **Open-Meteo Air Quality** | PM2.5/PM10/CO/NO2/SO2/O3/UV指数 | 免费 | 无需 | P0 |
| **Open-Meteo Historical** | 1940年至今历史气象数据 | 免费 | 无需 | P0 |
| **AQICN / WAQI** | 11000+站点AQI，3-8天预报，1000 req/s | 免费 | Token免费 | P0 |
| **USGS Earthquake** | 全球地震目录+PAGER预警+ShakeMap | 免费 | 无需 | P0 |
| **NASA FIRMS** | MODIS/VIIRS卫星近实时火点，3小时内 | 免费 | MAP_KEY免费 | P1 |
| **RainViewer** | 1200+雷达站降水回波，5分钟刷新 | 免费 | 无需 | P1 |
| **data.gov.my** | 马来西亚7天预报+天气预警+地震预警 | 免费 | 无需 | P1 |
| **EMSC SeismicPortal** | 全球地震事件，FDSN标准接口 | 免费 | 无需 | P2 |
| **OpenAQ** | 全球政府站空气质量历史数据，100+国家 | 免费 | Key免费 | P2 |

**限制性数据源**：StormGlass（免费层10次/天）、ASMC（无REST API需爬虫）、AHA Centre ADINET（无REST API）、MET Malaysia（1000次/天）、风云卫星NSMC（注册审核7天）

**关键发现**：Open-Meteo一站式提供天气/海洋/洪水/空气质量/UV共5大类免费数据；花粉API仅覆盖欧洲，东盟需LLM推断；Wolfx中国地震EEW是同类项目罕见的差异化优势。

### 企业级功能提案（7项）

| # | 功能 | 复杂度 | 目标行业 | 数据源 |
|---|------|--------|----------|--------|
| E1 | **海事气象决策引擎** Marine Weather Decision | 中 | 航运/渔业/海洋旅游 | Open-Meteo Marine + 台风服务 |
| E2 | **农业气象保险指数** Agro-Weather Index | 高 | 保险/农业合作社（亚太$8.7B市场） | Open-Meteo Historical + Soil Moisture |
| E3 | **建筑工地气象安全** Construction Safety | **低-中** | 建筑/工程管理（东盟2000万+工人） | Open-Meteo逐时预报 + UV + AQI |
| E4 | **可再生能源发电预测** Renewable Energy | 中 | 光伏/风电/电网调度 | Open-Meteo Solar + Wind API |
| E5 | **中国-东盟灾害协同预警** Cross-Border Hub | 高 | 跨国供应链/政府应急 | Wolfx + ASMC + 多源关联 |
| E6 | **智慧农业气象决策** Smart Agro-Weather | 中 | 农业企业/合作社（稻米/橡胶/棕榈油） | Open-Meteo Soil Moisture + 蒸散发 |
| E7 | **企业气象API托管** Weather APIaaS | 高 | 物流/外卖/出行平台 | 全部现有API封装 + Webhook |

### 社会/社区功能提案（7项）

| # | 功能 | 复杂度 | 社会价值 | 优先级 |
|---|------|--------|----------|--------|
| S1 | **AI多语言天气播报频道** Weather Broadcast | 中 | ⭐⭐⭐⭐⭐ 推送至WhatsApp/Telegram/WeChat/LINE | **P0** |
| S2 | **城市天气健康指数排行榜** Health Index | **低-中** | ⭐⭐⭐⭐ 综合评分0-100，城市对比排行 | **P0** |
| S3 | **跨国烟霾协作监测** Haze Monitoring | 高 | ⭐⭐⭐⭐⭐ NASA FIRMS+AQICN+ASMC+众包 | P2 |
| S4 | **众包天气观测站** Crowdsourced Weather | 中 | ⭐⭐⭐⭐ 手机拍照上报，弥补站点稀疏区 | P1 |
| S5 | **个人气象日记** Weather Journal | 低-中 | ⭐⭐⭐ 天气-健康关联追踪，可导出分享 | P1 |
| S6 | **社区天气照片墙** Photo Wall | 中 | ⭐⭐⭐ AI分类+地理标记，灾害时变灾情地图 | P2 |
| S7 | **天气应急互助圈** Emergency Mutual Aid | 高 | ⭐⭐⭐⭐⭐ AI匹配供需，7语言实时互译 | P3 |

### 大赛前推荐实施（P0，1-2周）

1. **城市健康指数排行榜** — 复杂度最低，完全基于现有数据，ECharts已有
2. **AI多语言天气播报** — 复用现有7语言Agent + WhatsApp/Telegram Bot
3. **Open-Meteo扩展集成** — Marine/Flood/AQ/Historical，零新API成本
4. **建筑工地气象安全决策** — 基于现有逐时预报+阈值判断，差异化明显

### 技术架构建议

- **新增数据层**：PostgreSQL + PostGIS（UGC功能需要，当前 `app/models/` 为空）
- **多平台推送**：新建 `notification_service.py`，定义 `NotificationChannel` Protocol，各平台为插件实现
- **新Service模式**：复用 httpx + tenacity + structlog + Pydantic schema 现有模式
- **前端新增组件**：CityHealthIndex.vue / MarineWeather.vue / ConstructionSafety.vue / HazeMonitor.vue
