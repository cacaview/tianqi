/** 国际化翻译定义 */

export type Language = 'zh' | 'en' | 'vi' | 'th' | 'id'

export interface QuickQuestion {
  text: string
  msg: string
}

export interface Translation {
  cities: string
  weather: string
  chat: string
  subtitle: string
  send: string
  placeholder: string
  welcome: string
  noalert: string
  selectCity: string
  alerts: string
  quickQuestions: string
  questions: QuickQuestion[]
}

export type I18nMap = Record<Language, Translation>
