/** 灾害预警数据类型定义 */

/** 预警级别 */
export type AlertLevel = 'red' | 'orange' | 'yellow' | 'blue'

/** 单条预警 */
export interface DisasterAlert {
  level: AlertLevel
  level_name: string
  type_name: string
  title: string
  content: string
  source: string
  start_time: string
  regions: string[]
}

/** 预警响应 */
export interface AlertResponse {
  alerts: DisasterAlert[]
}

/** 预警统计 */
export interface AlertSummary {
  total: number
  by_level: {
    red: number
    orange: number
    yellow: number
    blue: number
  }
  alerts: DisasterAlert[]
}

/** 台风位置 */
export interface TyphoonPosition {
  lat: number
  lon: number
}

/** 台风预报路径点 */
export interface ForecastTrackPoint {
  lat: number
  lon: number
}

/** 台风数据 */
export interface Typhoon {
  name: string
  code: string
  intensity: string
  max_wind_speed: number
  position: TyphoonPosition
  move_direction: string
  move_speed: number
  impact_regions: string[]
  forecast_track: ForecastTrackPoint[]
}

/** 地图数据响应（Dashboard用） */
export interface MapData {
  weather_points: WeatherPoint[]
  typhoons: Typhoon[]
  alerts: AlertSummary
}

import type { WeatherPoint } from './weather'
export type { WeatherPoint }


/** 地震信息 */
export interface Earthquake {
  id: string
  source: string
  hypocenter: string
  magnitude: number
  max_intensity?: string
  latitude?: number
  longitude?: number
  depth_km?: number
  occurred_at?: string
  url?: string
}

/** 地震预警 (EEW) */
export interface EEWAlert {
  id: string
  source: string
  hypocenter: string
  magnitude: number
  expected_max_intensity?: string
  latitude?: number
  longitude?: number
  depth_km?: number
  alert_time?: string
  is_cancelled: boolean
}
