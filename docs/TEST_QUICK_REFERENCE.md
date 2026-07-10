# 🚀 浏览器MCP测试快速参考

## 环境准备

```bash
# 终端1：启动后端
cd /Users/user/code/tianqi/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 终端2：启动前端
cd /Users/user/code/tianqi/frontend
npm run dev
```

---

## 📌 核心命令速查

### 页面操作
```typescript
browser_navigate("http://localhost:5173")        // 导航
browser_navigate_back()                          // 返回
browser_wait_for("文本内容")                      // 等待文本出现
browser_wait_for_time(1000)                      // 等待1秒
```

### 元素交互
```typescript
browser_snapshot()                               // 获取页面结构（最重要！）
browser_click("元素描述")                         // 点击元素
browser_type("输入框描述", "文本内容")              // 输入文本
browser_press_key("Enter")                       // 按键
browser_select_option("下拉框", ["选项"])          // 选择
```

### 调试验证
```typescript
browser_take_screenshot("文件名.png", "viewport", "css")  // 截图
browser_console_messages("error")                          // 控制台错误
browser_network_requests(filter="/api/", static=false)     // 网络请求
browser_evaluate(() => { return document.title })          // 执行JS
```

---

## 🎯 测试模块速查

### 模块1：首页加载（2分钟）
```typescript
await browser_navigate("http://localhost:5173")
await browser_wait_for("万语风 PolyWind")
await browser_take_screenshot("01_home.png", "viewport", "css")
await browser_snapshot()  // 验证WeatherCard存在
```

### 模块2：语言切换（3分钟）
```typescript
// 依次点击：中文 → EN → VN → TH → ID
await browser_snapshot()
await browser_click("语言按钮 'EN'")
await browser_take_screenshot("02_en.png", "viewport", "css")
// 重复其他语言...
```

### 模块3：城市选择（3分钟）
```typescript
// 依次选择：南宁 → 河内 → 曼谷 → 雅加达 → 吉隆坡
await browser_snapshot()
await browser_click("城市 '河内'")
await browser_wait_for("WeatherCard")
await browser_take_screenshot("03_hanoi.png", "viewport", "css")
```

### 模块4：聊天对话（5分钟）
```typescript
await browser_snapshot()
await browser_type("聊天输入框", "明天南宁会下雨吗？")
await browser_press_key("Enter")
await browser_wait_for("思考中...")
await browser_wait_for_time(3000)  // 等待AI响应
await browser_take_screenshot("04_chat.png", "viewport", "css")
```

---

## 🔍 调试技巧

### 找不到元素？
```typescript
// 方法1：获取完整页面结构
await browser_snapshot()

// 方法2：搜索文本
await browser_find("WeatherCard")

// 方法3：使用正则搜索
await browser_find("/天气|weather/i")
```

### API调用问题？
```typescript
// 查看所有API请求
const requests = await browser_network_requests(filter="/api/", static=false)

// 查看特定请求的响应
await browser_network_request(index=3, part="response-body")
```

### 控制台错误？
```typescript
// 查看所有错误
await browser_console_messages("error")

// 检查特定变量
await browser_evaluate(() => {
  return JSON.stringify(window.__pinia_state)
})
```

---

## 📊 测试检查清单

### ✅ P0：必须通过
- [ ] 页面加载完整（< 3秒）
- [ ] 默认城市天气显示
- [ ] 至少3种语言切换
- [ ] 城市选择响应
- [ ] 聊天发送和接收
- [ ] 控制台无ERROR

### ⚠️ P1：重要
- [ ] 所有5种语言切换
- [ ] 所有东盟城市选择
- [ ] 移动端响应式
- [ ] 加载状态提示
- [ ] 错误处理友好

### 💡 P2：建议
- [ ] 仪表板图表渲染
- [ ] 地图交互
- [ ] 性能优化
- [ ] 无障碍访问

---

## 🐛 常见问题速解

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 页面空白 | 前端未启动 | `npm run dev` |
| API错误 | 后端未启动 | `uvicorn app.main:app --reload` |
| 找不到元素 | 页面未加载 | `browser_wait_for("文本")` |
| 元素不可交互 | loading中 | 等待loading消失 |
| 语言未切换 | 未点击按钮 | `browser_click("按钮")` |

---

## 📝 测试结果模板

```markdown
## 测试执行记录

**日期**: 2026-07-10
**测试人**: ________
**环境**: localhost

### 结果汇总
- 总用例数: 15
- 通过: __
- 失败: __
- 跳过: __

### 失败用例详情
| 用例 | 步骤 | 预期 | 实际 | 原因 |
|------|------|------|------|------|
| TC-X.X | X | X | X | X |

### 建议和反馈
1. ________
2. ________
```

---

## 🎬 完整测试脚本

```typescript
// 一键执行所有测试
async function runAllTests() {
  console.log('🚀 开始测试...\n')
  
  const startTime = Date.now()
  const results = { passed: 0, failed: 0, errors: [] }
  
  // 1. 首页加载
  console.log('1️⃣ 首页加载测试')
  try {
    await browser_navigate("http://localhost:5173")
    await browser_wait_for("万语风 PolyWind")
    await browser_take_screenshot("test_01.png", "viewport", "css")
    results.passed++
    console.log('   ✅ 通过\n')
  } catch (e) {
    results.failed++
    results.errors.push(`首页加载: ${e.message}`)
    console.log('   ❌ 失败\n')
  }
  
  // 2. 语言切换
  console.log('2️⃣ 语言切换测试')
  try {
    await browser_snapshot()
    await browser_click("语言按钮 'EN'")
    await browser_wait_for_time(500)
    await browser_take_screenshot("test_02.png", "viewport", "css")
    results.passed++
    console.log('   ✅ 通过\n')
  } catch (e) {
    results.failed++
    results.errors.push(`语言切换: ${e.message}`)
    console.log('   ❌ 失败\n')
  }
  
  // 3. 城市选择
  console.log('3️⃣ 城市选择测试')
  try {
    await browser_snapshot()
    await browser_click("城市 '河内'")
    await browser_wait_for("WeatherCard")
    await browser_take_screenshot("test_03.png", "viewport", "css")
    results.passed++
    console.log('   ✅ 通过\n')
  } catch (e) {
    results.failed++
    results.errors.push(`城市选择: ${e.message}`)
    console.log('   ❌ 失败\n')
  }
  
  // 4. 聊天对话
  console.log('4️⃣ 聊天对话测试')
  try {
    await browser_snapshot()
    await browser_type("聊天输入框", "测试消息")
    await browser_press_key("Enter")
    await browser_wait_for_time(3000)
    await browser_take_screenshot("test_04.png", "viewport", "css")
    results.passed++
    console.log('   ✅ 通过\n')
  } catch (e) {
    results.failed++
    results.errors.push(`聊天对话: ${e.message}`)
    console.log('   ❌ 失败\n')
  }
  
  // 输出报告
  const duration = ((Date.now() - startTime) / 1000).toFixed(2)
  console.log('════════════════════════════════════════')
  console.log('📊 测试报告')
  console.log('════════════════════════════════════════')
  console.log(`⏱️  耗时: ${duration}秒`)
  console.log(`✅ 通过: ${results.passed}`)
  console.log(`❌ 失败: ${results.failed}`)
  
  if (results.errors.length > 0) {
    console.log('\n❌ 失败详情:')
    results.errors.forEach(e => console.log(`   - ${e}`))
  }
  
  console.log('\n════════════════════════════════════════')
  
  return results.failed === 0
}
```

---

**详细测试计划**: `/Users/user/code/tianqi/docs/TEST_PLAN.md`
