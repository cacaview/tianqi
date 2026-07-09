/** 气象数据类型定义 */

/** 当前天气响应 */
export interface WeatherCurrent {
  temperature: number
  feels_like: number
  humidity: number
  wind_speed: number
  precipitation: number
  wind_direction: number
}

/** 天气预报响应 */
export interface WeatherForecast {
  daily: WeatherForecastDay[]
}

export interface WeatherForecastDay {
  date: string
  temperature_max: number
  temperature_min: number
  precipitation_sum: number
  humidity: number
  wind_speed: number
}

/** 城市数据 */
export interface City {
  id: string
  name: string
  name_en: string
  lat: number
  lon: number
  country: string
  flag: string
}

/** 城市天气数据点（Dashboard用） */
export interface WeatherPoint {
  id: string
  name: string
  lat: number
  lon: number
  temperature: number
  humidity: number
  wind_speed: number
  precipitation: number
}

/** 分钟级降水数据点 */
export interface MinutelyPrecipitationPoint {
  time: string
  precipitation_mm: number
}

/** 分钟级降水预报响应 */
export interface MinutelyPrecipitation {
  latitude: number
  longitude: number
  timezone?: string
  minutely_15: MinutelyPrecipitationPoint[]
}

/** 当前空气质量 */
export interface AirQualityCurrent {
  pm2_5: number | null
  pm10: number | null
  no2: number | null
  co: number | null
  so2: number | null
  o3: number | null
  us_aqi: number | null
  european_aqi: number | null
}

/** 当前空气质量响应 */
export interface AirQualityCurrentResponse {
  latitude: number
  longitude: number
  timezone?: string
  current: AirQualityCurrent
}

/** 天气报告响应 */
export interface WeatherReport {
  report: string
  language: string
  location?: string
  generated_by: string
}

/** 生活指数项 */
export interface LifestyleIndex {
  name: string
  name_zh: string
  level: string
  level_zh: string
  description: string
  icon?: string
}

/** 生活指数响应 */
export interface LifestyleIndicesResponse {
  latitude: number
  longitude: number
  timezone?: string
  language: string
  indices: LifestyleIndex[]
  generated_by: string
}
