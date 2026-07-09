<script setup lang="ts">
/**
 * 天气详情卡片
 */
import type { WeatherCurrent } from '@/types'

defineProps<{
  cityName: string
  cityFullName?: string
  weather: WeatherCurrent | null
}>()

const details = [
  { key: 'temperature', label: '气温', suffix: '°C' },
  { key: 'feels_like', label: '体感', suffix: '°C' },
  { key: 'humidity', label: '湿度', suffix: '%' },
  { key: 'wind_speed', label: '风速', suffix: 'km/h' },
  { key: 'precipitation', label: '降水', suffix: 'mm' },
  { key: 'wind_direction', label: '风向', suffix: '°' },
] as const
</script>

<template>
  <div class="weather-card">
    <h3>{{ cityName }} <template v-if="cityFullName">{{ cityFullName }}</template></h3>
    <div class="weather-grid">
      <div v-for="d in details" :key="d.key" class="weather-stat">
        <div class="label">{{ d.label }}</div>
        <div class="value">
          {{ weather?.[d.key] ?? '--' }}{{ d.suffix }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.weather-card {
  background: var(--card);
  border-radius: 12px;
  padding: 12px;
  border: 1px solid var(--border);
}

.weather-card h3 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 10px;
}

.weather-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.weather-stat {
  padding: 6px;
  background: var(--bg);
  border-radius: 6px;
  text-align: center;
}

.weather-stat .label {
  font-size: 11px;
  color: var(--text-sec);
}

.weather-stat .value {
  font-size: 16px;
  font-weight: 600;
  margin-top: 2px;
}
</style>
