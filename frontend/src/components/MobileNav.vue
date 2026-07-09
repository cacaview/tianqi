<script setup lang="ts">
/**
 * 移动端底部导航栏
 */
import { ref } from 'vue'

const emit = defineEmits<{
  navigate: [panel: string]
}>()

const activePanel = ref('chat')

const navItems = [
  { panel: 'weather', icon: '🌤️', label: '天气' },
  { panel: 'alerts', icon: '⚠️', label: '预警' },
  { panel: 'chat', icon: '💬', label: '对话' },
]

function handleNav(panel: string) {
  activePanel.value = panel
  emit('navigate', panel)
}
</script>

<template>
  <div class="bottom-nav">
    <div class="bottom-nav-items">
      <button
        v-for="item in navItems"
        :key="item.panel"
        class="nav-item"
        :class="{ active: activePanel === item.panel }"
        @click="handleNav(item.panel)"
      >
        <span class="nav-item-icon">{{ item.icon }}</span>
        <span>{{ item.label }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.bottom-nav {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--card);
  border-top: 1px solid var(--border);
  padding: 8px 0;
  padding-bottom: max(var(--safe-bottom, 0px), 8px);
  z-index: 100;
}

@media (max-width: 768px) {
  .bottom-nav {
    display: block;
  }
}

.bottom-nav-items {
  display: flex;
  justify-content: space-around;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  background: none;
  border: none;
  color: var(--text-sec);
  font-size: 10px;
  cursor: pointer;
  padding: 4px 12px;
  transition: color 0.2s;
}

.nav-item.active {
  color: var(--primary);
}

.nav-item-icon {
  font-size: 20px;
}
</style>
