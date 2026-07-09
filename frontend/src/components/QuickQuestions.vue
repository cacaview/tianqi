<script setup lang="ts">
/**
 * 快捷问题按钮
 */
import type { QuickQuestion } from '@/types'

defineProps<{
  questions: QuickQuestion[]
}>()

const emit = defineEmits<{
  send: [message: string]
}>()
</script>

<template>
  <div class="quick-btns">
    <button
      v-for="(q, i) in questions"
      :key="i"
      class="quick-btn"
      @click="emit('send', q.msg)"
    >
      {{ q.text }}
    </button>
  </div>
</template>

<style scoped>
.quick-btns {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.quick-btn {
  padding: 8px 12px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--text);
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
  text-align: left;
  transition: all 0.2s;
}

.quick-btn:hover {
  background: var(--bg);
  border-color: var(--primary);
}
</style>
