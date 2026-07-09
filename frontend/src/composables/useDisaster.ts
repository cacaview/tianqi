/**
 * 灾害预警组合式函数
 */
import { ref } from 'vue'
import type { DisasterAlert, MapData } from '@/types'
import { disasterApi } from '@/api'

export function useDisaster() {
  const alerts = ref<DisasterAlert[]>([])
  const mapData = ref<MapData | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAlerts(regions: string) {
    loading.value = true
    error.value = null
    try {
      const resp = await disasterApi.getAlerts(regions)
      alerts.value = resp.alerts
    } catch (e) {
      error.value = e instanceof Error ? e.message : '获取预警失败'
      console.error('获取预警失败:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchMapData() {
    loading.value = true
    error.value = null
    try {
      mapData.value = await disasterApi.getMapData()
    } catch (e) {
      error.value = e instanceof Error ? e.message : '获取地图数据失败'
      console.error('获取地图数据失败:', e)
    } finally {
      loading.value = false
    }
  }

  return {
    alerts,
    mapData,
    loading,
    error,
    fetchAlerts,
    fetchMapData,
  }
}
