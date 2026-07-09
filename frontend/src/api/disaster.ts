/**
 * 灾害预警 API 服务
 */
import { apiClient } from './client'
import type { AlertResponse, MapData } from '@/types'
import type { Earthquake, EEWAlert } from '@/types/disaster'

export const disasterApi = {
  /** 获取灾害预警 */
  async getAlerts(regions: string): Promise<AlertResponse> {
    return apiClient.get<AlertResponse>('/api/disaster/alerts', {
      params: { regions },
    })
  },

  /** 获取地图数据（Dashboard） */
  async getMapData(): Promise<MapData> {
    return apiClient.get<MapData>('/api/disaster/map-data')
  },

  /** 获取地震列表 */
  async getEarthquakes(source: string = 'cenc'): Promise<{earthquakes: Earthquake[], total: number}> {
    return apiClient.get('/api/disaster/earthquakes', { params: { source } })
  },

  /** 获取地震预警 (EEW) */
  async getEEWAlerts(): Promise<{earthquakes: EEWAlert[]}> {
    return apiClient.get('/api/disaster/eew')
  },
}
