<script setup lang="ts">
/**
 * 应用顶部导航菜单栏
 */
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import LanguageSwitcher from './LanguageSwitcher.vue'

defineProps<{
  title?: string
  subtitle?: string
}>()

const router = useRouter()
const route = useRoute()
const mobileMenuOpen = ref(false)

const menuItems = [
  { path: '/', icon: '💬', label: '智能对话', description: 'AI天气助手' },
  { path: '/dashboard', icon: '📊', label: '数据仪表板', description: '可视化分析' },
]

const isActive = (path: string) => route.path === path

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}
</script>

<template>
  <header class="header">
    <div class="header-left">
      <div class="logo">
        <span class="logo-icon">🌬️</span>
        <div class="logo-text">
          <span class="logo-title">{{ title ?? '万语风' }}</span>
          <small v-if="subtitle" class="logo-subtitle">{{ subtitle }}</small>
        </div>
      </div>
    </div>

    <!-- 桌面端菜单 -->
    <nav class="desktop-menu">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="menu-item"
        :class="{ active: isActive(item.path) }"
        @click="closeMobileMenu"
      >
        <span class="menu-icon">{{ item.icon }}</span>
        <span class="menu-label">{{ item.label }}</span>
      </router-link>
    </nav>

    <div class="header-right">
      <LanguageSwitcher />

      <!-- 移动端菜单按钮 -->
      <button class="mobile-menu-btn" @click="toggleMobileMenu">
        <span class="menu-hamburger">☰</span>
      </button>
    </div>

    <!-- 移动端下拉菜单 -->
    <div class="mobile-menu" :class="{ open: mobileMenuOpen }">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="mobile-menu-item"
        :class="{ active: isActive(item.path) }"
        @click="closeMobileMenu"
      >
        <span class="mobile-menu-icon">{{ item.icon }}</span>
        <div class="mobile-menu-content">
          <span class="mobile-menu-label">{{ item.label }}</span>
          <span class="mobile-menu-desc">{{ item.description }}</span>
        </div>
      </router-link>
    </div>
  </header>
</template>

<style scoped>
.header {
  background: var(--gradient);
  color: white;
  padding: max(var(--safe-top, 0px), 12px) 20px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000; /* 提高z-index确保在Leaflet地图之上 */
  backdrop-filter: blur(10px);
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 28px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 1px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.logo-subtitle {
  font-size: 10px;
  opacity: 0.9;
  margin-top: 2px;
  font-weight: 400;
}

/* 桌面端菜单 */
.desktop-menu {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(255, 255, 255, 0.1);
  padding: 6px 8px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 14px;
  color: white;
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.2);
}

.menu-item.active {
  background: rgba(255, 255, 255, 0.3);
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.menu-icon {
  font-size: 18px;
}

.menu-label {
  letter-spacing: 0.5px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 移动端菜单按钮 */
.mobile-menu-btn {
  display: none;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 8px;
  padding: 6px 10px;
  color: white;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mobile-menu-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.menu-hamburger {
  display: block;
  line-height: 1;
}

/* 移动端下拉菜单 */
.mobile-menu {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border-bottom: 2px solid var(--primary);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease, opacity 0.3s ease;
  opacity: 0;
}

.mobile-menu.open {
  max-height: 300px;
  opacity: 1;
}

.mobile-menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  color: var(--text);
  text-decoration: none;
  border-bottom: 1px solid var(--border);
  transition: background 0.2s ease;
}

.mobile-menu-item:last-child {
  border-bottom: none;
}

.mobile-menu-item:hover {
  background: var(--bg);
}

.mobile-menu-item.active {
  background: rgba(26, 115, 232, 0.1);
  color: var(--primary);
}

.mobile-menu-icon {
  font-size: 24px;
}

.mobile-menu-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.mobile-menu-label {
  font-size: 15px;
  font-weight: 600;
}

.mobile-menu-desc {
  font-size: 12px;
  color: var(--text-sec);
}

/* 响应式 */
@media (max-width: 768px) {
  .desktop-menu {
    display: none;
  }

  .mobile-menu-btn {
    display: block;
  }

  .mobile-menu {
    display: block;
  }
}
</style>
