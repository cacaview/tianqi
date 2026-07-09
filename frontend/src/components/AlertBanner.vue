<script setup lang="ts">
/**
 * 灾害预警横幅
 */
import type { DisasterAlert } from '@/types'

defineProps<{
  alert: DisasterAlert | null
  noAlertText?: string
}>()
</script>

<template>
  <div class="alert-card">
    <strong>
      <template v-if="alert">
        ⚠️ {{ alert.level_name }}级 {{ alert.type_name }}: {{ alert.title }}
      </template>
      <template v-else>
        {{ noAlertText ?? '当前无重大气象灾害预警' }}
      </template>
    </strong>
  </div>
</template>

<style scoped>
.alert-card {
  background: var(--card);
  border-radius: 8px;
  padding: 10px 12px;
  border: 1px solid var(--border);
  font-size: 12px;
  line-height: 1.5;
}
</style>
