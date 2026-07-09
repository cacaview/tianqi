/**
 * 国际化翻译
 */
import { computed } from 'vue'
import type { Language, Translation, I18nMap } from '@/types'

/** 翻译数据 */
const i18n: I18nMap = {
  zh: {
    cities: '东盟城市', weather: '天气详情', chat: '智能对话', subtitle: '万种语言，一种风',
    send: '发送', placeholder: '输入你的问题...',
    welcome: '你好！我是万语风，你的多语言气象智能助手。你可以问我任何天气相关的问题。',
    noalert: '当前无重大气象灾害预警', selectCity: '选择城市', alerts: '灾害预警', quickQuestions: '快捷问题',
    questions: [
      { text: '🌤️ 今天天气如何？', msg: '今天天气怎么样' },
      { text: '🌀 有台风吗？', msg: '现在有台风吗' },
      { text: '⚠️ 有预警吗？', msg: '有灾害预警吗' },
      { text: '🌾 农业建议', msg: '农业气象有什么建议' },
    ],
  },
  en: {
    cities: 'ASEAN Cities', weather: 'Weather', chat: 'Chat', subtitle: 'One Wind, Many Languages',
    send: 'Send', placeholder: 'Ask about weather...',
    welcome: "Hello! I'm PolyWind, your multilingual weather assistant.",
    noalert: 'No severe weather alerts', selectCity: 'Select City', alerts: 'Alerts', quickQuestions: 'Quick Questions',
    questions: [
      { text: "🌤️ Today's weather?", msg: "What's the weather today" },
      { text: '🌀 Any typhoons?', msg: 'Are there any typhoons' },
      { text: '⚠️ Any alerts?', msg: 'Any weather alerts' },
      { text: '🌾 Farm advice', msg: 'Agricultural weather advice' },
    ],
  },
  vi: {
    cities: 'Thành phố ASEAN', weather: 'Thời tiết', chat: 'Trò chuyện', subtitle: 'Một làn gió, nhiều ngôn ngữ',
    send: 'Gửi', placeholder: 'Hỏi về thời tiết...',
    welcome: 'Xin chào! Tôi là PolyWind, trợ lý thời tiết đa ngôn ngữ.',
    noalert: 'Không có cảnh báo', selectCity: 'Chọn thành phố', alerts: 'Cảnh báo', quickQuestions: 'Câu hỏi nhanh',
    questions: [
      { text: '🌤️ Thời tiết hôm nay?', msg: 'thời tiết hôm nay' },
      { text: '🌀 Có bão không?', msg: 'có bão không' },
      { text: '⚠️ Có cảnh báo?', msg: 'có cảnh báo thời tiết' },
      { text: '🌾 Tư vấn nông nghiệp', msg: 'tư vấn thời tiết nông nghiệp' },
    ],
  },
  th: {
    cities: 'เมืองอาเซียน', weather: 'สภาพอากาศ', chat: 'แชท', subtitle: 'ลมเดียว หลายภาษา',
    send: 'ส่ง', placeholder: 'ถามเรื่องอากาศ...',
    welcome: 'สวัสดี! ฉันคือ PolyWind ผู้ช่วยสภาพอากาศ',
    noalert: 'ไม่มีการแจ้งเตือน', selectCity: 'เลือกเมือง', alerts: 'การแจ้งเตือน', quickQuestions: 'คำถามด่วน',
    questions: [
      { text: '🌤️ วันนี้อากาศเป็นอย่างไร?', msg: 'วันนี้อากาศเป็นอย่างไร' },
      { text: '🌀 มีพายุไหม?', msg: 'มีพายุไหม' },
      { text: '⚠️ มีการแจ้งเตือน?', msg: 'มีการแจ้งเตือนสภาพอากาศ' },
      { text: '🌾 คำแนะนำเกษตร', msg: 'คำแนะนำสภาพอากาศเกษตร' },
    ],
  },
  id: {
    cities: 'Kota ASEAN', weather: 'Cuaca', chat: 'Obrolan', subtitle: 'Satu Angin, Banyak Bahasa',
    send: 'Kirim', placeholder: 'Tanya cuaca...',
    welcome: 'Halo! Saya PolyWind, asisten cuaca multibahasa.',
    noalert: 'Tidak ada peringatan', selectCity: 'Pilih kota', alerts: 'Peringatan', quickQuestions: 'Pertanyaan Cepat',
    questions: [
      { text: '🌤️ Cuaca hari ini?', msg: 'cuaca hari ini' },
      { text: '🌀 Ada topan?', msg: 'ada topan' },
      { text: '⚠️ Ada peringatan?', msg: 'ada peringatan cuaca' },
      { text: '🌾 Saran pertanian', msg: 'saran cuaca pertanian' },
    ],
  },
}

/** 获取翻译函数 */
export function useI18n(currentLang: () => Language) {
  const t = computed<Translation>(() => i18n[currentLang()] ?? i18n.en)

  function setLang(lang: Language) {
    currentLang = () => lang
  }

  return { t, setLang, i18n }
}
