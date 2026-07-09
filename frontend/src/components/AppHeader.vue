<script setup lang="ts">
/**
 * 应用顶部导航栏
 */
import LanguageSwitcher from './LanguageSwitcher.vue'

defineProps<{
  title?: string
  subtitle?: string
}>()
</script>

<template>
  <header class="header">
    <div class="logo">
      <span class="logo-icon">🌬️</span>
      <span>{{ title ?? '万语风' }}</span>
      <small v-if="subtitle">{{ subtitle }}</small>
    </div>
    <slot name="right">
      <LanguageSwitcher />
    </slot>
  </header>
</template>

<style scoped>
.header {
  background: var(--gradient);
  color: white;
  padding: max(var(--safe-top, 0px), 12px) 16px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
}

.logo-icon {
  font-size: 24px;
}

.logo small {
  font-size: 11px;
  opacity: 0.8;
  margin-left: 6px;
}
</style>
