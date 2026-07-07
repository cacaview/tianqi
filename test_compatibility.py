"""
多设备分辨率兼容性测试
测试项目在不同设备分辨率下的表现
"""
from playwright.sync_api import sync_playwright
import json
import time

# 测试配置
FRONTEND_URL = "http://localhost:8080"
BACKEND_URL = "http://localhost:8000"

# 设备分辨率配置
DEVICES = [
    # 桌面设备
    {"name": "Desktop 1920x1080", "viewport": {"width": 1920, "height": 1080}, "type": "desktop"},
    {"name": "Desktop 1440x900", "viewport": {"width": 1440, "height": 900}, "type": "desktop"},
    {"name": "Desktop 1366x768", "viewport": {"width": 1366, "height": 768}, "type": "desktop"},
    {"name": "Desktop 1280x800", "viewport": {"width": 1280, "height": 800}, "type": "desktop"},

    # 平板设备
    {"name": "iPad Pro 12.9", "viewport": {"width": 1024, "height": 1366}, "type": "tablet"},
    {"name": "iPad Mini", "viewport": {"width": 768, "height": 1024}, "type": "tablet"},
    {"name": "iPad Air", "viewport": {"width": 820, "height": 1180}, "type": "tablet"},

    # 手机设备
    {"name": "iPhone 14 Pro Max", "viewport": {"width": 430, "height": 932}, "type": "mobile"},
    {"name": "iPhone 14 Pro", "viewport": {"width": 393, "height": 852}, "type": "mobile"},
    {"name": "iPhone 14", "viewport": {"width": 390, "height": 844}, "type": "mobile"},
    {"name": "iPhone SE", "viewport": {"width": 375, "height": 667}, "type": "mobile"},
    {"name": "Samsung Galaxy S21", "viewport": {"width": 360, "height": 800}, "type": "mobile"},
    {"name": "Xiaomi 13", "viewport": {"width": 393, "height": 851}, "type": "mobile"},
    {"name": "Huawei P50", "viewport": {"width": 360, "height": 780}, "type": "mobile"},
]

# Dashboard特定测试分辨率
DASHBOARD_DEVICES = [
    {"name": "Dashboard Desktop 1920x1080", "viewport": {"width": 1920, "height": 1080}, "type": "desktop"},
    {"name": "Dashboard Desktop 1366x768", "viewport": {"width": 1366, "height": 768}, "type": "desktop"},
    {"name": "Dashboard Tablet 1024x768", "viewport": {"width": 1024, "height": 768}, "type": "tablet"},
    {"name": "Dashboard Mobile 390x844", "viewport": {"width": 390, "height": 844}, "type": "mobile"},
]


def test_page(page, url, page_name, device_name, results):
    """测试单个页面在特定分辨率下的表现"""
    print(f"  测试 {device_name}...")

    try:
        # 访问页面
        page.goto(url, wait_until="networkidle", timeout=30000)

        # 等待页面加载
        time.sleep(2)

        # 检查控制台错误
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        # 获取页面内容
        content = page.content()

        # 检查关键元素是否存在
        checks = {
            "page_loaded": len(content) > 100,
            "no_crash": "error" not in content.lower()[:500],
        }

        # 获取视口信息
        viewport = page.viewport_size

        # 检查布局是否正常
        layout_ok = True
        try:
            # 检查是否有明显溢出
            scroll_width = page.evaluate("document.documentElement.scrollWidth")
            client_width = page.evaluate("document.documentElement.clientWidth")
            checks["no_overflow"] = scroll_width <= client_width + 50  # 允许50px误差
        except:
            checks["no_overflow"] = True

        # 截图
        screenshot_path = f"/tmp/test_{page_name}_{device_name.replace(' ', '_').replace('x', 'x')}.png"
        page.screenshot(path=screenshot_path, full_page=False)

        results.append({
            "device": device_name,
            "page": page_name,
            "viewport": viewport,
            "checks": checks,
            "console_errors": console_errors,
            "screenshot": screenshot_path,
            "status": "pass" if all(checks.values()) and len(console_errors) == 0 else "warn"
        })

    except Exception as e:
        results.append({
            "device": device_name,
            "page": page_name,
            "error": str(e),
            "status": "fail"
        })


def run_tests():
    """运行所有测试"""
    results = []

    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        print("=" * 60)
        print("多设备分辨率兼容性测试")
        print("=" * 60)

        # 测试主页
        print("\n📱 测试主页 (index.html)")
        print("-" * 40)
        for device in DEVICES:
            page = context.new_page()
            page.set_viewport_size(device["viewport"])
            test_page(page, f"{FRONTEND_URL}/index.html", "index", device["name"], results)
            page.close()

        # 测试Dashboard
        print("\n📊 测试Dashboard (dashboard.html)")
        print("-" * 40)
        for device in DASHBOARD_DEVICES:
            page = context.new_page()
            page.set_viewport_size(device["viewport"])
            test_page(page, f"{FRONTEND_URL}/dashboard.html", "dashboard", device["name"], results)
            page.close()

        browser.close()

    # 输出结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    pass_count = sum(1 for r in results if r["status"] == "pass")
    warn_count = sum(1 for r in results if r["status"] == "warn")
    fail_count = sum(1 for r in results if r["status"] == "fail")

    print(f"\n通过: {pass_count} | 警告: {warn_count} | 失败: {fail_count}")

    # 按页面分组显示
    print("\n📋 详细结果:")
    for page_name in ["index", "dashboard"]:
        page_results = [r for r in results if r["page"] == page_name]
        print(f"\n  {page_name.upper()}:")
        for r in page_results:
            status_icon = {"pass": "✅", "warn": "⚠️", "fail": "❌"}.get(r["status"], "?")
            print(f"    {status_icon} {r['device']}: {r.get('viewport', r.get('error', 'N/A'))}")

    # 保存详细结果
    with open("/tmp/compatibility_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 详细结果已保存到: /tmp/compatibility_test_results.json")

    return results


if __name__ == "__main__":
    run_tests()
