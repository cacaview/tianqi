/**
 * 聊天组合式函数
 */
import { ref } from 'vue'
import type { ChatMessage } from '@/types'
import { chatApi } from '@/api'

export function useChat() {
  const messages = ref<ChatMessage[]>([])
  const sending = ref(false)
  const error = ref<string | null>(null)

  /** 添加欢迎消息 */
  function addWelcome(text: string) {
    messages.value.push({
      id: crypto.randomUUID(),
      type: 'bot',
      text,
      timestamp: Date.now(),
    })
  }

  /** 发送消息 */
  async function sendMessage(
    text: string,
    language: string,
    latitude: number,
    longitude: number,
  ) {
    if (!text.trim() || sending.value) return

    // 添加用户消息
    messages.value.push({
      id: crypto.randomUUID(),
      type: 'user',
      text: text.trim(),
      timestamp: Date.now(),
    })

    sending.value = true
    error.value = null

    try {
      const resp = await chatApi.send({
        message: text.trim(),
        language,
        latitude,
        longitude,
      })

      // 添加机器人回复
      messages.value.push({
        id: crypto.randomUUID(),
        type: 'bot',
        text: resp.reply,
        tools_used: resp.tools_used,
        timestamp: Date.now(),
      })
    } catch (e) {
      error.value = e instanceof Error ? e.message : '请求失败'
      messages.value.push({
        id: crypto.randomUUID(),
        type: 'bot',
        text: '请求失败，请检查后端服务是否启动。',
        timestamp: Date.now(),
      })
    } finally {
      sending.value = false
    }
  }

  /** 清空消息 */
  function clearMessages() {
    messages.value = []
  }

  return {
    messages,
    sending,
    error,
    addWelcome,
    sendMessage,
    clearMessages,
  }
}
