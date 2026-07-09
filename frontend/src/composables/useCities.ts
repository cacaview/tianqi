/**
 * 城市数据常量
 */
import type { City } from '@/types'

/** 东盟城市列表 */
export const CITIES: Record<string, City> = {
  nanning: { id: 'nanning', name: '南宁', name_en: 'Nanning', lat: 22.82, lon: 108.32, country: 'CN', flag: '🇨🇳' },
  hanoi: { id: 'hanoi', name: '河内', name_en: 'Hanoi', lat: 21.03, lon: 105.85, country: 'VN', flag: '🇻🇳' },
  bangkok: { id: 'bangkok', name: '曼谷', name_en: 'Bangkok', lat: 13.76, lon: 100.5, country: 'TH', flag: '🇹🇭' },
  jakarta: { id: 'jakarta', name: '雅加达', name_en: 'Jakarta', lat: -6.21, lon: 106.85, country: 'ID', flag: '🇮🇩' },
  manila: { id: 'manila', name: '马尼拉', name_en: 'Manila', lat: 14.6, lon: 120.98, country: 'PH', flag: '🇵🇭' },
  kuala_lumpur: { id: 'kuala_lumpur', name: '吉隆坡', name_en: 'KL', lat: 3.14, lon: 101.69, country: 'MY', flag: '🇲🇾' },
  singapore: { id: 'singapore', name: '新加坡', name_en: 'Singapore', lat: 1.35, lon: 103.82, country: 'SG', flag: '🇸🇬' },
  phnom_penh: { id: 'phnom_penh', name: '金边', name_en: 'Phnom Penh', lat: 11.56, lon: 104.92, country: 'KH', flag: '🇰🇭' },
  vientiane: { id: 'vientiane', name: '万象', name_en: 'Vientiane', lat: 17.97, lon: 102.63, country: 'LA', flag: '🇱🇦' },
  yangon: { id: 'yangon', name: '仰光', name_en: 'Yangon', lat: 16.87, lon: 96.2, country: 'MM', flag: '🇲🇲' },
}

/** 获取城市列表数组 */
export function getCityList(): City[] {
  return Object.values(CITIES)
}

/** 根据ID获取城市 */
export function getCityById(id: string): City | undefined {
  return CITIES[id]
}
