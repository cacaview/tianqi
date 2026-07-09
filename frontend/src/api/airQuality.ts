/**
 * 空气质量 API 服务
 */
import { apiClient } from './client'
import type { AirQualityCurrentResponse } from '@/types'

export const airQualityApi = {
  /** 获取当前空气质量 */
  async getCurrent(latitude: number, longitude: number): Promise<AirQualityCurrentResponse> {
    return apiClient.get<AirQualityCurrentResponse>('/api/air-quality/current', {
      params: { latitude, longitude },
    })
  },
}
