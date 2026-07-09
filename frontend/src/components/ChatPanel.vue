<script setup lang="ts">
/**
 * 聊天面板（消息列表 + 输入框）
 */
import { ref, nextTick, watch } from 'vue'
import type { ChatMessage } from '@/types'

const props = defineProps<{
  messages: ChatMessage[]
  sending: boolean
  placeholder?: string
  sendLabel?: string
}>()

const emit = defineEmits<{
  send: [message: string]
}>()

const inputText = ref('')
const messagesContainer = ref<HTMLDivElement>()

function handleSend() {
  const text = inputText.value.trim()
  if (!text || props.sending) return
  emit('send', text)
  inputText.value = ''
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

/** 安全HTML转义 */
function escapeHtml(str: string): string {
  const div = document.createElement('div')
  div.appendChild(document.createTextNode(str))
  return div.innerHTML
}

/** 将换行符转为 <br> */
function formatText(text: string): string {
  return escapeHtml(text).replace(/\n/g, '<br>')
}

// 自动滚动到底部
watch(
  () => props.messages.length,
  () => {
    nextTick(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    })
  },
)
</script>

<template>
  <div class="chat-panel">
    <div ref="messagesContainer" class="chat-messages">
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="msg"
        :class="msg.type"
      >
        <div v-html="formatText(msg.text)" />
        <div v-if="msg.tools_used?.length" class="tools">
          工具: {{ msg.tools_used.join(', ') }}
        </div>
      </div>
      <div v-if="sending" class="msg bot loading">思考中...</div>
    </div>
    <div class="chat-input">
      <input
        v-model="inputText"
        type="text"
        :placeholder="placeholder ?? '输入你的问题...'"
        autocomplete="off"
        @keydown="handleKeydown"
      >
      <button :disabled="sending" @click="handleSend">
        {{ sendLabel ?? '发送' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.msg {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
}

.msg.user {
  align-self: flex-end;
  background: var(--primary);
  color: white;
  border-bottom-right-radius: 4px;
}

.msg.bot {
  align-self: flex-start;
  background: var(--card);
  border: 1px solid var(--border);
  border-bottom-left-radius: 4px;
}

.msg.loading {
  color: var(--text-sec);
  font-style: italic;
}

.tools {
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px solid var(--border);
  font-size: 11px;
  color: var(--text-sec);
}

.chat-input {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: var(--card);
  border-top: 1px solid var(--border);
}

.chat-input input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: 20px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input input:focus {
  border-color: var(--primary);
}

.chat-input button {
  padding: 10px 20px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.2s;
}

.chat-input button:hover:not(:disabled) {
  background: var(--primary-dark);
}

.chat-input button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
