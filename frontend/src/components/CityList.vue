<script setup lang="ts">
/**
 * 城市列表组件
 *
 * 用于桌面侧边栏和移动面板
 */
import { useAppStore } from '@/stores/app'
import { getCityList } from '@/composables/useCities'
import type { WeatherCurrent } from '@/types'

defineProps<{
  weatherData?: Record<string, WeatherCurrent | null>
}>()

const emit = defineEmits<{
  select: [cityId: string]
}>()

const store = useAppStore()
const cities = getCityList()
</script>

<template>
  <div class="city-list">
    <div
      v-for="city in cities"
      :key="city.id"
      class="city-item"
      :class="{ active: store.selectedCityId === city.id }"
      @click="emit('select', city.id)"
    >
      <span>{{ city.flag }} {{ city.name }}</span>
      <span class="temp">{{ weatherData?.[city.id]?.temperature ?? '--' }}°C</span>
    </div>
  </div>
</template>

<style scoped>
.city-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.city-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 13px;
}

.city-item:hover {
  background: rgba(0, 0, 0, 0.05);
}

.city-item.active {
  background: rgba(26, 115, 232, 0.1);
  color: var(--primary);
  font-weight: 500;
}

.temp {
  font-weight: 600;
  font-size: 12px;
}
</style>
