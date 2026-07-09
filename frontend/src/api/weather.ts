/**
 * 气象 API 服务
 */
import { apiClient } from './client'
import type { LifestyleIndicesResponse, MinutelyPrecipitation, WeatherCurrent, WeatherForecast, WeatherReport } from '@/types'

export const weatherApi = {
  /** 获取当前天气 */
  async getCurrent(latitude: number, longitude: number): Promise<WeatherCurrent> {
    return apiClient.get<WeatherCurrent>('/api/weather/current', {
      params: { latitude, longitude },
    })
  },

  /** 获取天气预报 */
  async getForecast(latitude: number, longitude: number): Promise<WeatherForecast> {
    return apiClient.get<WeatherForecast>('/api/weather/forecast', {
      params: { latitude, longitude },
    })
  },

  /** 获取分钟级降水预报 */
  async getMinutelyPrecipitation(latitude: number, longitude: number): Promise<MinutelyPrecipitation> {
    return apiClient.get<MinutelyPrecipitation>('/api/weather/minutely-precipitation', {
      params: { latitude, longitude },
    })
  },

  /** 获取生活指数 */
  async getLifestyleIndices(latitude: number, longitude: number, language: string = 'zh'): Promise<LifestyleIndicesResponse> {
    return apiClient.get<LifestyleIndicesResponse>('/api/weather/lifestyle-indices', {
      params: { latitude, longitude, language },
    })
  },

  /** 获取天气报告 */
  async getWeatherReport(latitude: number, longitude: number, language: string = 'zh'): Promise<WeatherReport> {
    return apiClient.get<WeatherReport>('/api/weather/report', {
      params: { latitude, longitude, language },
    })
  },
}
