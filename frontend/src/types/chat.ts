/** 聊天数据类型定义 */

/** 聊天请求 */
export interface ChatRequest {
  message: string
  language: string
  latitude: number
  longitude: number
  session_id?: string
}

/** 聊天响应 */
export interface ChatResponse {
  reply: string
  tools_used: string[]
}

/** 聊天消息（前端展示用） */
export interface ChatMessage {
  id: string
  type: 'user' | 'bot'
  text: string
  tools_used?: string[]
  timestamp: number
}
