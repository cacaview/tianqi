# ADR-002: 外部 API Mock 策略

## 状态

已批准

## 背景

项目依赖外部 API（Open-Meteo / QWeather / NHC / LLM），测试时需要 mock 这些调用。

## 决策

采用 **respx** 作为 HTTP mock 库。

### 选择理由

| 方案 | 优点 | 缺点 |
|------|------|------|
| respx（**选用**） | 专为 httpx 设计、拦截真实 HTTP 请求、验证 URL/参数/headers | 仅支持 httpx |
| unittest.mock.patch | 标准库、轻量级 | 不验证 HTTP 层行为、mock 粒度粗 |
| responses 库 | 功能简单 | 仅支持 requests，不支持 httpx |
| pytest-httpx | 功能类似 respx | 社区较小 |

## 后果

- 测试中可精确验证外部 API 调用的 URL、参数、headers
- Mock 配置简洁（`respx.get(url).mock(return_value=...)`)
- 与 httpx 深度集成，覆盖网络层行为
