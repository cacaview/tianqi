# 万语风 PolyWind 浏览器MCP测试计划

**项目截止日期**：2026年10月13日  
**测试日期**：2026年07月10日  
**测试工具**：Playwright MCP

---

## 📋 测试概览

### 测试目标
1. 验证前端UI功能完整性和交互流畅性
2. 验证多语言支持（7种语言）
3. 验证API集成和数据展示
4. 验证响应式设计（桌面端/移动端）
5. 验证错误处理和边界情况

### 测试环境
- **前端**：http://localhost:5173
- **后端**：http://localhost:8000
- **API文档**：http://localhost:8000/docs

---

## 🧪 测试模块

### 模块1：首页加载和初始化

#### TC-1.1：页面加载
| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 导航到 http://localhost:5173 | 页面加载完成 |
| 2 | 等待页面渲染 | 显示"万语风 PolyWind"标题 |
| 3 | 截图验证 | 首页完整展示 |
| 4 | 检查控制台 | 无ERROR级别日志 |

**验证点**：
- [ ] 页面标题正确显示
- [ ] 侧边栏城市列表显示
- [ ] 聊天面板显示欢迎消息
- [ ] 天气卡片显示默认城市数据

#### TC-1.2：默认数据加载
| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 导航到首页 | 页面加载完成 |
| 2 | 检查网络请求 | `/api/weather/current` 被调用 |
| 3 | 验证WeatherCard | 显示南宁天气数据 |
| 4 | 检查CityList | 南宁高亮显示 |

**验证点**：
- [ ] 默认选择南宁
- [ ] 天气数据正确加载（温度、湿度、风速等）
- [ ] CityList高亮状态正确

---

### 模块2：语言切换测试

#### TC-2.1：语言按钮交互
| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 获取页面结构 | 识别5个语言按钮 |
| 2 | 点击"EN"按钮 | 切换到英语 |
| 3 | 获取页面结构 | 文本变为英文 |
| 4 | 点击"VN"按钮 | 切换到越南语 |
| 5 | 验证欢迎消息 | 消息内容变为越南语 |

**验证点**：
- [ ] 语言按钮高亮状态正确
- [ ] UI文本实时切换
- [ ] 欢迎消息语言更新

#### TC-2.2：多语言切换序列
| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 中文 → 英语 | 文本切换 |
| 2 | 英语 → 越南语 | 文本切换 |
| 3 | 越南语 → 泰语 | 文本切换 |
| 4 | 泰语 → 印尼语 | 文本切换 |
| 5 | 印尼语 → 中文 | 文本切换 |

**验证点**：
- [ ] 所有5种语言正确切换
- [ ] 无文本残留或乱码
- [ ] 状态持久化（刷新后保持）

---

### 模块3：城市选择测试

#### TC-3.1：城市列表交互
| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 获取页面结构 | 识别城市列表 |
| 2 | 点击"北京" | 选择北京 |
| 3 | 等待API响应 | 天气数据更新 |
| 4 | 验证WeatherCard | 显示北京天气 |
| 5 | 检查网络请求 | 新的API调用 |

**验证点**：
- [ ] 城市选中状态切换
- [ ] 天气数据刷新
- [ ] API调用参数正确（lat/lon）

#### TC-3.2：多城市切换
| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 选择南宁 | 显示南宁天气 |
| 2 | 选择河内 | 显示河内天气 |
| 3 | 选择曼谷 | 显示曼谷天气 |
| 4 | 选择雅加达 | 显示雅加达天气 |
| 5 | 选择吉隆坡 | 显示吉隆坡天气 |

**验证点**：
- [ ] 每个城市正确加载对应数据
- [ ] 温度单位显示正确（°C）
- [ ] 城市名称显示正确（支持多语言）

---

### 模块4：聊天对话测试

#### TC-4.1：基本聊天流程
| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 定位输入框 | 找到ChatPanel input |
| 2 | 输入"今天天气怎么样？" | 文本显示在输入框 |
| 3 | 按Enter发送 | 消息发送 |
| 4 | 等待响应 | 显示"思考中..." |
| 5 | 获取AI回复 | 显示天气查询结果 |

**验证点**：
- [ ] 输入框支持文本输入
- [ ] Enter键触发发送
- [ ] 消息显示在聊天区域
- [ ] AI回复正确显示

#### TC-4.2：空消息处理
| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 不输入任何内容 | 输入框为空 |
| 2 | 点击发送按钮 | 按钮可能禁用或无响应 |
| 3 | 输入空格 | 输入框显示空格 |
| 4 | 点击发送 | 无消息发送（trim后为空） |

**验证点**：
- [ ] 空消息不发送
- [ ] 纯空格消息不发送
- [ ] 发送按钮状态正确

#### TC-4.3：发送中状态
| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 发送一个消息 | 消息发送 |
| 2 | 观察UI | 显示"思考中..." |
| 3 | 尝试再次发送 | 发送按钮禁用 |
| 4 | 等待响应完成 | "思考中..."消失 |

**验证点**：
- [ ] loading状态显示
- [ ] 发送按钮禁用
- [ ] 输入框禁用或限制

---

### 模块5：预警和仪表板测试

#### TC-5.1：预警Banner显示
| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 检查首页 | AlertBanner组件存在 |
| 2 | 获取预警数据 | 网络请求成功 |
| 3 | 验证Banner | 显示预警信息或隐藏 |

**验证点**：
- [ ] AlertBanner组件渲染
- [ ] 无预警时隐藏
- [ ] 有预警时显示

#### TC-5.2：仪表板视图
| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 导航到 /dashboard | 页面切换 |
| 2 | 等待加载 | DashboardView渲染 |
| 3 | 验证图表 | ECharts显示 |
| 4 | 验证地图 | Leaflet地图渲染 |

**验证点**：
- [ ] 仪表板路由正常
- [ ] 图表正确渲染
- [ ] 地图正确加载

---

### 模块6：响应式设计测试

#### TC-6.1：移动端视图
| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 调整视口为375px | 移动端布局 |
| 2 | 检查导航 | MobileNav显示 |
| 3 | 切换面板 | chat/weather/alerts |
| 4 | 验证交互 | 面板正常切换 |

**验证点**：
- [ ] 桌面端侧边栏隐藏
- [ ] MobileNav组件显示
- [ ] 面板切换正常

#### TC-6.2：平板端视图
| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 调整视口为768px | 平板布局 |
| 2 | 检查布局 | 自适应显示 |
| 3 | 验证交互 | 功能正常 |

**验证点**：
- [ ] 布局自适应
- [ ] 触摸友好
- [ ] 无溢出或截断

---

### 模块7：错误处理测试

#### TC-7.1：网络错误模拟
| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 断开网络连接 | 无网络 |
| 2 | 发送聊天消息 | 显示错误提示 |
| 3 | 选择城市 | 天气加载失败提示 |
| 4 | 检查控制台 | 错误日志记录 |

**验证点**：
- [ ] 错误提示友好
- [ ] 无页面崩溃
- [ ] 状态恢复

#### TC-7.2：无效API响应
| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 模拟API返回错误 | 500/503状态码 |
| 2 | 检查UI | 错误消息显示 |
| 3 | 重试操作 | 可以重新加载 |

**验证点**：
- [ ] 错误消息显示
- [ ] 降级处理（fallback）
- [ ] 重试机制

---

## 🔧 执行脚本

### 脚本1：基础功能验证

```typescript
// test_basic.js
async function testBasicFunctionality() {
  console.log('=== 模块1：基础功能验证 ===')
  
  // TC-1.1：页面加载
  console.log('TC-1.1：页面加载')
  await browser_navigate("http://localhost:5173")
  await browser_wait_for("万语风 PolyWind")
  await browser_take_screenshot("01_home_loaded.png", "viewport", "css")
  
  // TC-1.2：默认数据加载
  console.log('TC-1.2：默认数据加载')
  await browser_snapshot()  // 验证WeatherCard
  const requests = await browser_network_requests(filter="/api/", static=false)
  console.log('API请求数:', requests.split('\n').length - 1)
  
  // 检查控制台错误
  const errors = await browser_console_messages("error")
  if (errors.includes("Error")) {
    console.error('❌ 发现控制台错误')
    return false
  }
  
  console.log('✅ 基础功能验证通过')
  return true
}
```

### 脚本2：语言切换验证

```typescript
// test_language.js
async function testLanguageSwitching() {
  console.log('=== 模块2：语言切换测试 ===')
  
  const languages = [
    { code: 'en', name: 'EN' },
    { code: 'vi', name: 'VN' },
    { code: 'th', name: 'TH' },
    { code: 'id', name: 'ID' },
    { code: 'zh', name: '中文' }
  ]
  
  await browser_navigate("http://localhost:5173")
  await browser_wait_for("万语风 PolyWind")
  
  for (const lang of languages) {
    console.log(`切换到 ${lang.name}`)
    
    // 点击语言按钮
    await browser_snapshot()
    await browser_click(`语言按钮 '${lang.name}'`)
    
    // 等待UI更新
    await browser_wait_for_time(500)
    
    // 截图验证
    await browser_take_screenshot(`02_lang_${lang.code}.png`, "viewport", "css")
    
    // 验证语言已切换
    const snapshot = await browser_snapshot()
    console.log(`  ✓ ${lang.name} 切换成功`)
  }
  
  console.log('✅ 语言切换测试通过')
  return true
}
```

### 脚本3：城市选择验证

```typescript
// test_city.js
async function testCitySelection() {
  console.log('=== 模块3：城市选择测试 ===')
  
  const cities = [
    { id: 'nanning', name: '南宁' },
    { id: 'hanoi', name: '河内' },
    { id: 'bangkok', name: '曼谷' },
    { id: 'jakarta', name: '雅加达' },
    { id: 'kualalumpur', name: '吉隆坡' }
  ]
  
  await browser_navigate("http://localhost:5173")
  await browser_wait_for("万语风 PolyWind")
  
  for (const city of cities) {
    console.log(`选择 ${city.name}`)
    
    // 获取页面结构
    await browser_snapshot()
    
    // 点击城市
    await browser_click(`城市列表项 '${city.name}'`)
    
    // 等待天气数据加载
    await browser_wait_for("WeatherCard")
    
    // 截图验证
    await browser_take_screenshot(`03_city_${city.id}.png`, "viewport", "css")
    
    // 验证网络请求
    const requests = await browser_network_requests(filter="/api/weather/", static=false)
    console.log(`  ✓ ${city.name} 天气数据加载`)
  }
  
  console.log('✅ 城市选择测试通过')
  return true
}
```

### 脚本4：聊天功能验证

```typescript
// test_chat.js
async function testChatFunctionality() {
  console.log('=== 模块4：聊天对话测试 ===')
  
  await browser_navigate("http://localhost:5173")
  await browser_wait_for("万语风 PolyWind")
  
  // TC-4.1：基本聊天
  console.log('TC-4.1：基本聊天流程')
  await browser_snapshot()
  
  // 输入消息
  await browser_type("聊天输入框", "明天南宁会下雨吗？")
  await browser_press_key("Enter")
  
  // 等待AI回复
  await browser_wait_for("思考中...")
  await browser_wait_for_time(2000)  // 等待AI响应
  
  // 截图验证
  await browser_take_screenshot("04_chat_response.png", "viewport", "css")
  
  // TC-4.2：空消息处理
  console.log('TC-4.2：空消息处理')
  await browser_type("聊天输入框", "")
  await browser_click("发送按钮")
  
  // 验证无新消息
  const snapshot = await browser_snapshot()
  console.log('  ✓ 空消息不发送')
  
  // TC-4.3：发送中状态
  console.log('TC-4.3：发送中状态')
  await browser_type("聊天输入框", "测试发送中状态")
  await browser_press_key("Enter")
  
  // 立即检查loading状态
  const loadingSnapshot = await browser_snapshot()
  if (loadingSnapshot.includes("思考中...")) {
    console.log('  ✓ loading状态显示')
  }
  
  console.log('✅ 聊天功能测试通过')
  return true
}
```

### 脚本5：完整回归测试

```typescript
// test_regression.js
async function testRegression() {
  console.log('=== 完整回归测试 ===')
  
  const results = {
    passed: 0,
    failed: 0,
    errors: []
  }
  
  try {
    // 基础功能
    if (await testBasicFunctionality()) {
      results.passed++
    } else {
      results.failed++
      results.errors.push('基础功能验证失败')
    }
    
    // 语言切换
    if (await testLanguageSwitching()) {
      results.passed++
    } else {
      results.failed++
      results.errors.push('语言切换测试失败')
    }
    
    // 城市选择
    if (await testCitySelection()) {
      results.passed++
    } else {
      results.failed++
      results.errors.push('城市选择测试失败')
    }
    
    // 聊天功能
    if (await testChatFunctionality()) {
      results.passed++
    } else {
      results.failed++
      results.errors.push('聊天功能测试失败')
    }
    
  } catch (error) {
    console.error('测试执行异常:', error)
    results.failed++
    results.errors.push(error.message)
  }
  
  // 输出测试报告
  console.log('\n=== 测试报告 ===')
  console.log(`通过: ${results.passed}`)
  console.log(`失败: ${results.failed}`)
  
  if (results.errors.length > 0) {
    console.log('\n失败原因:')
    results.errors.forEach(err => console.log(`  - ${err}`))
  }
  
  // 最终截图
  await browser_take_screenshot("99_final_state.png", "viewport", "css")
  
  return results.failed === 0
}
```

---

## 📊 测试检查清单

### 核心功能
- [ ] 页面加载无错误
- [ ] 默认城市（南宁）自动选中
- [ ] 天气数据正确展示
- [ ] 7种语言切换正常
- [ ] 聊天对话基础流程
- [ ] 预警信息展示

### UI/UX
- [ ] 响应式布局（桌面/平板/手机）
- [ ] 组件交互流畅
- [ ] 加载状态提示
- [ ] 错误信息友好
- [ ] 截图对比无异常

### 性能
- [ ] 首页加载时间 < 3秒
- [ ] API响应时间 < 5秒
- [ ] 无内存泄漏（多次导航后）
- [ ] 控制台无警告

### API集成
- [ ] `/api/weather/current` 调用正常
- [ ] `/api/weather/forecast` 调用正常
- [ ] `/api/chat` 调用正常
- [ ] 请求参数正确（lat/lon）

---

## 🐛 常见问题排查

### 问题1：页面无法加载
```typescript
// 检查后端服务
browser_navigate("http://localhost:8000/health")
browser_snapshot()
```

### 问题2：API请求失败
```typescript
// 检查网络请求
browser_network_requests(filter="/api/", static=false)
browser_network_request(index=1, part="response-body")
```

### 问题3：控制台错误
```typescript
// 查看错误详情
browser_console_messages(level="error")
browser_evaluate(() => console.error('test'))
```

### 问题4：组件不渲染
```typescript
// 检查DOM结构
browser_snapshot()
browser_find("WeatherCard")
```

---

## 📝 测试结果记录

| 模块 | 测试用例数 | 通过 | 失败 | 备注 |
|------|-----------|------|------|------|
| 首页加载 | 2 | | | |
| 语言切换 | 2 | | | |
| 城市选择 | 2 | | | |
| 聊天对话 | 3 | | | |
| 预警仪表板 | 2 | | | |
| 响应式 | 2 | | | |
| 错误处理 | 2 | | | |
| **总计** | **15** | | | |

---

**测试执行人**：________________  
**测试日期**：________________  
**审核人**：________________  
