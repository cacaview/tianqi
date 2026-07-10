<script setup lang="ts">
/**
 * 数据可视化仪表板视图（原 dashboard.html）
 *
 * 包含 Leaflet 地图、ECharts 图表、台风追踪、预警列表
 */
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import L from 'leaflet'
import * as echarts from 'echarts'
import AppHeader from '@/components/AppHeader.vue'
import { useDisaster } from '@/composables/useDisaster'
import type { WeatherPoint, Typhoon, AlertSummary, DisasterAlert } from '@/types'

const { mapData, fetchMapData } = useDisaster()

const lastUpdate = ref('--')
const mapContainer = ref<HTMLDivElement>()
const tempChartContainer = ref<HTMLDivElement>()
const humidityChartContainer = ref<HTMLDivElement>()
const precipChartContainer = ref<HTMLDivElement>()
const alertChartContainer = ref<HTMLDivElement>()

let map: L.Map | null = null
let tempChart: echarts.ECharts | null = null
let humidityChart: echarts.ECharts | null = null
let precipChart: echarts.ECharts | null = null
let alertChart: echarts.ECharts | null = null
const cityMarkers: Record<string, L.Marker> = {}
const typhoonLayers: L.Layer[] = []
let refreshTimer: ReturnType<typeof setInterval> | null = null

/** 初始化地图 */
function initMap() {
  if (!mapContainer.value) return
  map = L.map(mapContainer.value).setView([15, 110], 5)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '© OpenStreetMap contributors © CARTO',
    maxZoom: 18,
  }).addTo(map)
}

/** 初始化 ECharts */
function initCharts() {
  if (tempChartContainer.value) tempChart = echarts.init(tempChartContainer.value)
  if (humidityChartContainer.value) humidityChart = echarts.init(humidityChartContainer.value)
  if (precipChartContainer.value) precipChart = echarts.init(precipChartContainer.value)
  if (alertChartContainer.value) alertChart = echarts.init(alertChartContainer.value)
}

/** 图表通用配置 */
const chartBaseOption = {
  backgroundColor: 'transparent',
  textStyle: { color: '#9aa0a6' },
  tooltip: { trigger: 'axis' as const },
  grid: { left: 40, right: 20, top: 20, bottom: 30 },
  xAxis: {
    type: 'category' as const,
    axisLine: { lineStyle: { color: '#3c4043' } },
    axisLabel: { color: '#9aa0a6', fontSize: 10 },
    data: [] as string[],
  },
  yAxis: {
    type: 'value' as const,
    axisLine: { lineStyle: { color: '#3c4043' } },
    axisLabel: { color: '#9aa0a6' },
    splitLine: { lineStyle: { color: '#3c4043', opacity: 0.3 } },
  },
  series: [{
    type: 'bar' as const,
    barWidth: '50%',
    itemStyle: { borderRadius: [4, 4, 0, 0] },
  }],
}

/** 更新城市地图标记 */
function updateCityMarkers(points: WeatherPoint[]) {
  if (!map) return
  const m = map
  Object.values(cityMarkers).forEach(marker => m.removeLayer(marker))

  points.forEach(city => {
    const temp = city.temperature ?? 0
    const color = temp > 35 ? '#ea4335' : temp > 30 ? '#fbbc04' : temp > 20 ? '#34a853' : '#4285f4'

    const icon = L.divIcon({
      html: `<div style="background:${color};width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:11px;border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.3)">${temp}°</div>`,
      className: '',
      iconSize: [32, 32],
      iconAnchor: [16, 16],
    })

    const marker = L.marker([city.lat, city.lon], { icon })
      .addTo(m)
      .bindPopup(`
        <div style="min-width:120px">
          <div style="font-size:16px;font-weight:600;margin-bottom:8px">${city.name}</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:12px">
            <div>🌡️ ${city.temperature}°C</div>
            <div>💧 ${city.humidity}%</div>
            <div>🌬️ ${city.wind_speed}km/h</div>
            <div>🌧️ ${city.precipitation}mm</div>
          </div>
        </div>
      `)
    cityMarkers[city.id] = marker
  })
}

/** 更新台风标记 */
function updateTyphoonMarkers(typhoons: Typhoon[]) {
  if (!map) return
  const m = map
  typhoonLayers.forEach(layer => m.removeLayer(layer))
  typhoonLayers.length = 0

  typhoons.forEach(t => {
    const intensityColor = t.intensity === 'TY' || t.intensity === 'STY' ? '#ea4335' : '#fbbc04'

    const icon = L.divIcon({
      html: `<div style="background:${intensityColor};width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:20px;border:3px solid white;box-shadow:0 2px 10px rgba(0,0,0,0.4)">🌀</div>`,
      className: '',
      iconSize: [40, 40],
      iconAnchor: [20, 20],
    })

    const marker = L.marker([t.position.lat, t.position.lon], { icon })
      .addTo(m)
      .bindPopup(`
        <div style="min-width:150px">
          <div style="font-size:16px;font-weight:600;margin-bottom:8px">🌀 ${t.name}</div>
          <div style="font-size:12px">
            <div>强度: ${t.intensity}</div>
            <div>风速: ${t.max_wind_speed} km/h</div>
            <div>位置: ${t.position.lat}°N, ${t.position.lon}°E</div>
            <div>移动: ${t.move_direction || '未知'} ${t.move_speed || 0} km/h</div>
          </div>
        </div>
      `)
    typhoonLayers.push(marker)

    // 预报路径
    if (t.forecast_track?.length) {
      const pathCoords: [number, number][] = [[t.position.lat, t.position.lon]]
      t.forecast_track.forEach(p => pathCoords.push([p.lat, p.lon]))
      const polyline = L.polyline(pathCoords, {
        color: '#ea4335',
        weight: 2,
        opacity: 0.7,
        dashArray: '5, 10',
      }).addTo(m)
      typhoonLayers.push(polyline)
    }
  })
}

/** 更新图表 */
function updateCharts(points: WeatherPoint[], alertSummary: AlertSummary) {
  const cityNames = points.map(c => c.name)

  // 温度
  tempChart?.setOption({
    ...chartBaseOption,
    xAxis: { ...chartBaseOption.xAxis, data: cityNames },
    series: [{
      ...chartBaseOption.series[0],
      data: points.map(c => c.temperature),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#ea4335' },
          { offset: 1, color: '#fbbc04' },
        ]),
      },
    }],
  })

  // 湿度
  humidityChart?.setOption({
    ...chartBaseOption,
    xAxis: { ...chartBaseOption.xAxis, data: cityNames },
    series: [{ ...chartBaseOption.series[0], data: points.map(c => c.humidity), itemStyle: { color: '#4285f4' } }],
  })

  // 降水
  precipChart?.setOption({
    ...chartBaseOption,
    xAxis: { ...chartBaseOption.xAxis, data: cityNames },
    series: [{ ...chartBaseOption.series[0], data: points.map(c => c.precipitation), itemStyle: { color: '#34a853' } }],
  })

  // 预警饼图
  const byLevel = alertSummary.by_level
  alertChart?.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 4, borderColor: '#1a2634', borderWidth: 2 },
      label: { color: '#9aa0a6', fontSize: 11 },
      data: [
        { value: byLevel.red, name: '红色', itemStyle: { color: '#ea4335' } },
        { value: byLevel.orange, name: '橙色', itemStyle: { color: '#fbbc04' } },
        { value: byLevel.yellow, name: '黄色', itemStyle: { color: '#fcd34d' } },
        { value: byLevel.blue, name: '蓝色', itemStyle: { color: '#4285f4' } },
      ],
    }],
  })
}

/** 仪表板计算属性 */
const stats = ref({ temp: '--', humidity: '--', wind: '--', alertCount: 0 })
const typhoonBadge = ref('🌀 无活跃台风')
const latestAlerts = ref<DisasterAlert[]>([])
const typhoons = ref<Typhoon[]>([])
const cityPoints = ref<WeatherPoint[]>([])

/** 加载数据 */
async function loadData() {
  await fetchMapData()
  const data = mapData.value
  if (!data) return

  lastUpdate.value = new Date().toLocaleTimeString()
  cityPoints.value = data.weather_points
  typhoons.value = data.typhoons
  latestAlerts.value = data.alerts.alerts

  // 更新城市标记
  await nextTick()
  updateCityMarkers(data.weather_points)
  updateTyphoonMarkers(data.typhoons)
  updateCharts(data.weather_points, data.alerts)

  // 计算统计
  const pts = data.weather_points
  if (pts.length > 0) {
    stats.value = {
      temp: (pts.reduce((s, c) => s + (c.temperature || 0), 0) / pts.length).toFixed(1),
      humidity: String(Math.round(pts.reduce((s, c) => s + (c.humidity || 0), 0) / pts.length)),
      wind: (pts.reduce((s, c) => s + (c.wind_speed || 0), 0) / pts.length).toFixed(1),
      alertCount: data.alerts.total,
    }
  }

  // 台风徽章
  if (data.typhoons.length === 0) {
    typhoonBadge.value = '🌀 无活跃台风'
  } else {
    typhoonBadge.value = `🌀 ${data.typhoons.length}个活跃台风`
  }
}

/** 聚焦城市 */
function focusCity(lat: number, lon: number) {
  map?.setView([lat, lon], 8)
}

/** 窗口大小变化时重绘图表 */
function handleResize() {
  tempChart?.resize()
  humidityChart?.resize()
  precipChart?.resize()
  alertChart?.resize()
}

onMounted(async () => {
  await nextTick()
  initMap()
  initCharts()
  await loadData()

  window.addEventListener('resize', handleResize)
  refreshTimer = setInterval(loadData, 5 * 60 * 1000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (refreshTimer) clearInterval(refreshTimer)
  map?.remove()
  tempChart?.dispose()
  humidityChart?.dispose()
  precipChart?.dispose()
  alertChart?.dispose()
})
</script>

<template>
  <div class="dashboard-view">
    <AppHeader title="气象数据可视化">
      <template #right>
        <div class="header-right">
          <span class="update-time">最后更新: {{ lastUpdate }}</span>
          <button class="refresh-btn" @click="loadData">刷新</button>
        </div>
      </template>
    </AppHeader>

    <div class="dashboard-content">
      <div class="main-grid">
      <!-- 左栏：地图和图表 -->
      <div class="left-column">
        <div class="card">
          <div class="card-header">
            <span class="card-title">🌏 东盟气象态势</span>
            <span
              class="card-badge"
              :class="typhoons.length ? 'badge-danger' : 'badge-success'"
            >
              {{ typhoonBadge }}
            </span>
          </div>
          <div class="map-container">
            <div ref="mapContainer" id="map"></div>
          </div>
        </div>

        <div class="charts-grid">
          <div class="card">
            <div class="card-header"><span class="card-title">📊 温度分布</span></div>
            <div ref="tempChartContainer" class="chart-container"></div>
          </div>
          <div class="card">
            <div class="card-header"><span class="card-title">💧 湿度分布</span></div>
            <div ref="humidityChartContainer" class="chart-container"></div>
          </div>
          <div class="card">
            <div class="card-header"><span class="card-title">🌧️ 降水量</span></div>
            <div ref="precipChartContainer" class="chart-container"></div>
          </div>
          <div class="card">
            <div class="card-header"><span class="card-title">⚠️ 预警统计</span></div>
            <div ref="alertChartContainer" class="chart-container"></div>
          </div>
        </div>
      </div>

      <!-- 右栏：统计和列表 -->
      <div class="right-column">
        <div class="card">
          <div class="card-header"><span class="card-title">📈 实时概况</span></div>
          <div class="weather-stats">
            <div class="stat-card">
              <div class="stat-icon">🌡️</div>
              <div class="stat-value">{{ stats.temp }}°C</div>
              <div class="stat-label">平均温度</div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">💧</div>
              <div class="stat-value">{{ stats.humidity }}%</div>
              <div class="stat-label">平均湿度</div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">🌬️</div>
              <div class="stat-value">{{ stats.wind }}km/h</div>
              <div class="stat-label">平均风速</div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">⚠️</div>
              <div class="stat-value">{{ stats.alertCount }}</div>
              <div class="stat-label">活跃预警</div>
            </div>
          </div>
        </div>

        <!-- 台风列表 -->
        <div class="card">
          <div class="card-header"><span class="card-title">🌀 台风动态</span></div>
          <div v-if="!typhoons.length" style="text-align: center; padding: 20px; color: #9aa0a6">
            当前无活跃台风
          </div>
          <div v-for="t in typhoons" :key="t.code" class="typhoon-card">
            <div class="typhoon-header">
              <span class="typhoon-name">🌀 {{ t.name }} <small style="color: #9aa0a6; font-size: 12px">{{ t.code }}</small></span>
              <span class="typhoon-status">{{ t.intensity }}</span>
            </div>
            <div class="typhoon-stats">
              <div class="typhoon-stat">
                <div class="label">风速</div>
                <div class="value">{{ t.max_wind_speed }} km/h</div>
              </div>
              <div class="typhoon-stat">
                <div class="label">位置</div>
                <div class="value">{{ t.position.lat }}°N</div>
              </div>
              <div class="typhoon-stat">
                <div class="label">移动</div>
                <div class="value">{{ t.move_speed || 0 }} km/h</div>
              </div>
            </div>
            <div class="typhoon-regions">影响区域: {{ (t.impact_regions || []).join(', ') }}</div>
          </div>
        </div>

        <!-- 预警列表 -->
        <div class="card">
          <div class="card-header"><span class="card-title">⚠️ 灾害预警</span></div>
          <div v-if="!latestAlerts.length" style="text-align: center; padding: 20px; color: #9aa0a6">
            暂无预警信息
          </div>
          <div class="alert-list">
            <div
              v-for="(a, i) in latestAlerts.slice(0, 10)"
              :key="i"
              class="alert-item"
              :class="a.level"
            >
              <div class="alert-title">⚠️ {{ a.level_name }}级 {{ a.type_name }}</div>
              <div style="font-size: 12px; margin: 6px 0">{{ a.title }}</div>
              <div class="alert-meta">{{ a.source }} · {{ new Date(a.start_time).toLocaleDateString() }}</div>
            </div>
          </div>
        </div>

        <!-- 城市天气 -->
        <div class="card">
          <div class="card-header"><span class="card-title">🌤️ 城市天气</span></div>
          <div class="city-grid">
            <div
              v-for="c in cityPoints"
              :key="c.id"
              class="city-card"
              @click="focusCity(c.lat, c.lon)"
            >
              <div class="city-name">{{ c.name }}</div>
              <div class="city-temp">{{ c.temperature }}°C</div>
              <div class="city-details">湿度 {{ c.humidity }}% · 风速 {{ c.wind_speed }}km/h</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<style scoped>
/* 暗色主题变量 */
.dashboard-view {
  --bg: #0f1419;
  --card: #1a2634;
  --card-hover: #243447;
  --text: #e8eaed;
  --text-sec: #9aa0a6;
  --border: #3c4043;
  --success: #34a853;
  --warning: #fbbc04;
  --danger: #ea4335;
  --gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg);
  color: var(--text);
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dashboard-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding-top: 16px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.update-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
}

.refresh-btn {
  padding: 5px 10px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  cursor: pointer;
  font-size: 11px;
  transition: all 0.2s ease;
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.6);
}

.main-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 16px;
  padding: 16px;
  max-width: 1600px;
  margin: 0 auto;
}

.card {
  background: var(--card);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid var(--border);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.card-title { font-size: 14px; font-weight: 600; }

.card-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.badge-success { background: rgba(52, 168, 83, 0.2); color: var(--success); }
.badge-danger { background: rgba(234, 67, 53, 0.2); color: var(--danger); }

.map-container {
  height: 500px;
  border-radius: 8px;
  overflow: hidden;
}

#map { height: 100%; width: 100%; }

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.chart-container { height: 200px; }

.weather-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.stat-card {
  text-align: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.stat-icon { font-size: 24px; margin-bottom: 8px; }
.stat-value { font-size: 24px; font-weight: 700; }
.stat-label { font-size: 11px; color: var(--text-sec); margin-top: 4px; }

.alert-list { display: flex; flex-direction: column; gap: 8px; max-height: 400px; overflow-y: auto; }

.alert-item {
  padding: 12px;
  border-radius: 8px;
  border-left: 4px solid;
  background: rgba(255, 255, 255, 0.05);
}

.alert-item.red { border-color: var(--danger); }
.alert-item.orange { border-color: var(--warning); }
.alert-item.yellow { border-color: #fcd34d; }
.alert-item.blue { border-color: #4285f4; }

.alert-title { font-size: 13px; font-weight: 500; margin-bottom: 4px; }
.alert-meta { font-size: 11px; color: var(--text-sec); }

.typhoon-card {
  padding: 14px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border);
  margin-bottom: 12px;
}

.typhoon-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.typhoon-name { font-size: 16px; font-weight: 600; display: flex; align-items: center; gap: 6px; }
.typhoon-status { font-size: 11px; padding: 3px 8px; border-radius: 10px; background: rgba(234, 67, 53, 0.2); color: var(--danger); }

.typhoon-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 10px; }
.typhoon-stat { text-align: center; padding: 8px; background: rgba(0, 0, 0, 0.2); border-radius: 6px; }
.typhoon-stat .label { font-size: 10px; color: var(--text-sec); }
.typhoon-stat .value { font-size: 14px; font-weight: 600; margin-top: 2px; }
.typhoon-regions { font-size: 12px; color: var(--text-sec); }

.city-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }

.city-card {
  padding: 12px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: background 0.2s;
}

.city-card:hover { background: var(--card-hover); }
.city-name { font-size: 13px; font-weight: 500; margin-bottom: 6px; }
.city-temp { font-size: 22px; font-weight: 700; }
.city-details { font-size: 11px; color: var(--text-sec); margin-top: 4px; }

/* 响应式 */
@media (max-width: 1024px) {
  .main-grid { grid-template-columns: 1fr; }
  .charts-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .weather-stats { grid-template-columns: repeat(2, 1fr); }
  .city-grid { grid-template-columns: 1fr; }
  .map-container { height: 350px; }
}
</style>
