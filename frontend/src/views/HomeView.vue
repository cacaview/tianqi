<script setup lang="ts">
/**
 * 首页视图（原 index.html）
 *
 * 包含桌面端侧边栏 + 聊天区，以及移动端面板
 */
import { ref, onMounted, watch } from 'vue'
import { useAppStore } from '@/stores/app'
import { useI18n } from '@/composables/useI18n'
import { CITIES, getCityList } from '@/composables/useCities'
import { useWeather } from '@/composables/useWeather'
import { useChat } from '@/composables/useChat'
import { useDisaster } from '@/composables/useDisaster'
import AppHeader from '@/components/AppHeader.vue'
import CityList from '@/components/CityList.vue'
import WeatherCard from '@/components/WeatherCard.vue'
import AlertBanner from '@/components/AlertBanner.vue'
import QuickQuestions from '@/components/QuickQuestions.vue'
import ChatPanel from '@/components/ChatPanel.vue'
import MobileNav from '@/components/MobileNav.vue'
import type { WeatherCurrent } from '@/types'

const store = useAppStore()
const { t } = useI18n(() => store.currentLang)
const { currentWeather, fetchCurrent } = useWeather()
const { messages, sending, addWelcome, sendMessage } = useChat()
const { alerts, fetchAlerts } = useDisaster()

const activeMobilePanel = ref('chat')
const weatherCache = ref<Record<string, WeatherCurrent | null>>({})
const loadingAllCities = ref(false)

/** 选择城市 */
async function handleSelectCity(cityId: string) {
  store.selectCity(cityId)
  const city = CITIES[cityId]
  if (city) {
    await fetchCurrent(city.lat, city.lon)
    weatherCache.value[cityId] = currentWeather.value
  }
}

/** 预加载所有城市的温度 */
async function fetchAllCitiesWeather() {
  loadingAllCities.value = true
  const cityList = getCityList()

  // 并发获取所有城市的天气
  const promises = cityList.map(async (city) => {
    try {
      const response = await fetch(`/api/weather/current?latitude=${city.lat}&longitude=${city.lon}`)
      if (response.ok) {
        const data = await response.json()
        weatherCache.value[city.id] = data
      }
    } catch (error) {
      console.error(`Failed to fetch weather for ${city.id}:`, error)
      weatherCache.value[city.id] = null
    }
  })

  await Promise.all(promises)
  loadingAllCities.value = false
}

/** 发送聊天消息 */
async function handleSendMessage(text: string) {
  const city = store.selectedCity
  if (!city) return
  await sendMessage(text, store.currentLang, city.lat, city.lon)
}

/** 移动端导航 */
function handleMobileNav(panel: string) {
  activeMobilePanel.value = panel
  if (panel === 'alerts') {
    fetchAlerts('guangxi,vietnam,thailand')
  }
}

/** 初始化 */
onMounted(async () => {
  addWelcome(t.value.welcome)

  // 加载默认城市天气（立即显示）
  await handleSelectCity('nanning')

  // 并发加载所有城市的温度（后台加载）
  fetchAllCitiesWeather()

  // 加载预警
  fetchAlerts('guangxi')

  // 修复聊天区域宽度问题
  fixChatAreaWidth()
})

/** 修复聊天区域宽度 */
function fixChatAreaWidth() {
  const chatArea = document.querySelector('.chat-area') as HTMLElement
  if (chatArea) {
    // 使用固定宽度，因为calc在Grid布局中计算异常
    chatArea.style.width = '920px'
    chatArea.style.minWidth = '0'
  }
}

// 语言切换时更新欢迎消息
watch(() => store.currentLang, () => {
  if (messages.value.length === 1 && messages.value[0]?.type === 'bot') {
    messages.value[0] = {
      ...messages.value[0],
      text: t.value.welcome,
    }
  }
})
</script>

<template>
  <div class="home-view">
    <AppHeader>
      <template #right>
        <div class="lang-switch">
          <button
            v-for="lang in (['zh','en','vi','th','id'] as const)"
            :key="lang"
            class="lang-btn"
            :class="{ active: store.currentLang === lang }"
            @click="store.setLanguage(lang)"
          >
            {{ { zh:'中文', en:'EN', vi:'VN', th:'TH', id:'ID' }[lang] }}
          </button>
        </div>
      </template>
    </AppHeader>

    <div class="main">
      <!-- 桌面端侧边栏 -->
      <aside class="sidebar">
        <div class="section-title">{{ t.cities }}</div>
        <CityList :weather-data="weatherCache" @select="handleSelectCity" />

        <div class="section-title">{{ t.weather }}</div>
        <WeatherCard
          :city-name="store.selectedCity?.name ?? ''"
          :city-full-name="store.selectedCity?.name_en"
          :weather="currentWeather"
        />

        <div class="section-title">{{ t.alerts }}</div>
        <AlertBanner
          :alert="alerts[0] ?? null"
          :no-alert-text="t.noalert"
        />

        <div class="section-title">{{ t.quickQuestions }}</div>
        <QuickQuestions
          :questions="t.questions"
          @send="handleSendMessage"
        />
      </aside>

      <!-- 聊天区 -->
      <div class="chat-area">
        <div class="chat-header">
          <div class="section-title" style="margin-bottom: 4px">{{ t.chat }}</div>
          <div style="font-size: 12px; color: var(--text-sec)">{{ t.subtitle }}</div>
        </div>
        <ChatPanel
          :messages="messages"
          :sending="sending"
          :placeholder="t.placeholder"
          :send-label="t.send"
          @send="handleSendMessage"
        />
      </div>
    </div>

    <!-- 移动端底部导航 -->
    <MobileNav @navigate="handleMobileNav" />

    <!-- 移动端天气面板 -->
    <div class="mobile-panel" :class="{ active: activeMobilePanel === 'weather' }">
      <div class="section-title">{{ t.selectCity }}</div>
      <CityList :weather-data="weatherCache" @select="handleSelectCity" />

      <div class="mobile-weather-card">
        <div class="city-name">{{ store.selectedCity?.name }}</div>
        <div class="temp">{{ currentWeather?.temperature ?? '--' }}°C</div>
        <div class="details" v-if="currentWeather">
          <div class="detail-item">
            <div class="detail-label">体感</div>
            <div class="detail-value">{{ currentWeather.feels_like }}°C</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">湿度</div>
            <div class="detail-value">{{ currentWeather.humidity }}%</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">风速</div>
            <div class="detail-value">{{ currentWeather.wind_speed }}km/h</div>
          </div>
        </div>
      </div>

      <div class="section-title">{{ t.alerts }}</div>
      <AlertBanner
        :alert="alerts[0] ?? null"
        :no-alert-text="t.noalert"
      />
    </div>

    <!-- 移动端预警面板 -->
    <div class="mobile-panel" :class="{ active: activeMobilePanel === 'alerts' }">
      <div class="section-title">{{ t.alerts }}</div>
      <div v-for="(a, i) in alerts" :key="i" class="alert-card">
        <strong>⚠️ {{ a.level_name }}级 {{ a.type_name }}</strong>
        <p style="margin-top: 6px">{{ a.title }}</p>
        <p style="margin-top: 4px; font-size: 11px; color: #666">{{ a.content }}</p>
      </div>
      <div v-if="!alerts.length" class="alert-card">
        <strong>{{ t.noalert }}</strong>
      </div>
    </div>

    <!-- 移动端聊天面板 -->
    <div class="mobile-panel chat-active" :class="{ active: activeMobilePanel === 'chat' }">
      <ChatPanel
        :messages="messages"
        :sending="sending"
        :placeholder="t.placeholder"
        :send-label="t.send"
        @send="handleSendMessage"
      />
    </div>
  </div>
</template>

<style scoped>
/* 继承全局变量 */
.home-view {
  height: 100vh;
  overflow: hidden;
}

.main {
  display: grid;
  grid-template-columns: 280px 1fr;
  height: 100vh;
  padding-top: 56px;
  padding-bottom: 60px;
}

.sidebar {
  background: var(--card);
  border-right: 1px solid var(--border);
  overflow-y: auto;
  padding: 12px;
  position: fixed;
  left: 0;
  top: 56px;
  bottom: 60px;
  width: 280px;
}

.section-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-sec);
  text-transform: uppercase;
  margin: 12px 0 8px;
  letter-spacing: 0.5px;
}

.section-title:first-child {
  margin-top: 0;
}

.chat-area {
  display: flex;
  flex-direction: column;
  margin-left: 280px;
  min-width: 0;
  height: 100%;
}

.chat-header {
  padding: 10px 16px;
  background: var(--card);
  border-bottom: 1px solid var(--border);
}

/* 语言切换按钮 */
.lang-switch {
  display: flex;
  gap: 3px;
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

/* 移动端面板 - 桌面端完全隐藏 */
.mobile-panel,
.mobile-panel.active,
.mobile-panel.chat-active,
.mobile-panel.active.chat-active {
  display: none !important;
}

/* 移动端面板 - 移动端激活时显示（在媒体查询中定义） */

/* 移动端天气卡片 */
.mobile-weather-card {
  background: var(--gradient);
  color: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
}

.mobile-weather-card .city-name {
  font-size: 18px;
  font-weight: 600;
}

.mobile-weather-card .temp {
  font-size: 48px;
  font-weight: 300;
}

.mobile-weather-card .details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 16px;
}

.detail-item {
  text-align: center;
}

.detail-label {
  font-size: 11px;
  opacity: 0.8;
}

.detail-value {
  font-size: 16px;
  font-weight: 600;
}

/* 移动端预警卡片 */
.alert-card {
  background: var(--card);
  border-radius: 8px;
  padding: 10px 12px;
  border: 1px solid var(--border);
  margin-bottom: 8px;
  font-size: 12px;
}

/* 响应式 */
@media (max-width: 768px) {
  .main {
    grid-template-columns: 1fr;
    padding-top: 56px;
    padding-bottom: 70px;
  }

  .sidebar {
    display: none;
  }

  .chat-area {
    margin-left: 0;
  }

  /* 移动端：隐藏所有移动端面板 */
  .mobile-panel {
    display: none !important;
  }

  /* 移动端：仅显示激活的面板 */
  .mobile-panel.active {
    display: block !important;
  }

  /* 移动端：聊天面板特殊处理 */
  .mobile-panel.active.chat-active {
    display: flex !important;
    flex-direction: column;
  }
}
</style>
