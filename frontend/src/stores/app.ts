/**
 * 应用全局状态
 *
 * Pinia store 管理语言选择和城市选择状态
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Language } from '@/types'
import { CITIES, getCityById } from '@/composables/useCities'

export const useAppStore = defineStore('app', () => {
  /** 当前语言 */
  const currentLang = ref<Language>('zh')

  /** 当前选中城市 ID */
  const selectedCityId = ref<string>('nanning')

  /** 当前选中城市对象 */
  const selectedCity = computed(() => getCityById(selectedCityId.value) ?? CITIES.nanning)

  /** 设置语言 */
  function setLanguage(lang: Language) {
    currentLang.value = lang
  }

  /** 选择城市 */
  function selectCity(cityId: string) {
    if (CITIES[cityId]) {
      selectedCityId.value = cityId
    }
  }

  return {
    currentLang,
    selectedCityId,
    selectedCity,
    setLanguage,
    selectCity,
  }
})
