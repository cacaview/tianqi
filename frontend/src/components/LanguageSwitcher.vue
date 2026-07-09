<script setup lang="ts">
/**
 * 语言切换器
 */
import { useAppStore } from '@/stores/app'
import type { Language } from '@/types'

const store = useAppStore()

const languages: { code: Language; label: string }[] = [
  { code: 'zh', label: '中文' },
  { code: 'en', label: 'EN' },
  { code: 'vi', label: 'VN' },
  { code: 'th', label: 'TH' },
  { code: 'id', label: 'ID' },
]
</script>

<template>
  <div class="lang-switch">
    <button
      v-for="lang in languages"
      :key="lang.code"
      class="lang-btn"
      :class="{ active: store.currentLang === lang.code }"
      @click="store.setLanguage(lang.code)"
    >
      {{ lang.label }}
    </button>
  </div>
</template>

<style scoped>
.lang-switch {
  display: flex;
  gap: 3px;
  flex-wrap: wrap;
  max-width: 180px;
  justify-content: flex-end;
}

.lang-btn {
  padding: 4px 8px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: transparent;
  color: white;
  border-radius: 14px;
  cursor: pointer;
  font-size: 10px;
  transition: all 0.2s;
  min-width: 32px;
  white-space: nowrap;
}

.lang-btn.active,
.lang-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: white;
}
</style>
