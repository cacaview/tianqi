/**
 * 聊天 API 服务
 */
import { apiClient } from './client'
import type { ChatRequest, ChatResponse } from '@/types'

export const chatApi = {
  /** 发送消息 */
  async send(request: ChatRequest): Promise<ChatResponse> {
    return apiClient.post<ChatResponse>('/api/chat/send', request)
  },
}
