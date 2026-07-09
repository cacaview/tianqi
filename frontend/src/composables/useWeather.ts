/**
 * 天气数据组合式函数
 */
import { ref } from 'vue'
import type { WeatherCurrent, WeatherForecast } from '@/types'
import { weatherApi } from '@/api'

export function useWeather() {
  const currentWeather = ref<WeatherCurrent | null>(null)
  const forecast = ref<WeatherForecast | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchCurrent(latitude: number, longitude: number) {
    loading.value = true
    error.value = null
    try {
      currentWeather.value = await weatherApi.getCurrent(latitude, longitude)
    } catch (e) {
      error.value = e instanceof Error ? e.message : '获取天气数据失败'
      console.error('获取天气失败:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchForecast(latitude: number, longitude: number) {
    loading.value = true
    error.value = null
    try {
      forecast.value = await weatherApi.getForecast(latitude, longitude)
    } catch (e) {
      error.value = e instanceof Error ? e.message : '获取预报数据失败'
      console.error('获取预报失败:', e)
    } finally {
      loading.value = false
    }
  }

  return {
    currentWeather,
    forecast,
    loading,
    error,
    fetchCurrent,
    fetchForecast,
  }
}
