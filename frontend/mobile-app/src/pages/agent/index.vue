<template>
  <view class="agent-chat">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <text class="nav-back" @click="goBack">←</text>
      <text class="nav-title">{{ agentName || 'AI助手' }}</text>
      <text class="nav-status" :class="{ active: isConnected }">●</text>
    </view>

    <!-- 对话区域 -->
    <scroll-view 
      class="chat-area" 
      scroll-y 
      :scroll-into-view="scrollToView"
      :scroll-with-animation="true"
    >
      <!-- 欢迎消息 -->
      <view v-if="messages.length === 0" class="welcome-card">
        <view class="welcome-avatar">🤖</view>
        <view class="welcome-title">你好，我是你的专属AI助手</view>
        <view class="welcome-desc">我可以帮你解答平台规则、收益分析、拼团策略等问题</view>
        <view class="quick-questions">
          <view 
            v-for="(q, i) in quickQuestions" 
            :key="i"
            class="quick-item"
            @click="sendQuickQuestion(q)"
          >
            {{ q }}
          </view>
        </view>
      </view>

      <!-- 消息列表 -->
      <view 
        v-for="(msg, index) in messages" 
        :key="index"
        :id="'msg-' + index"
        class="message-item"
        :class="{ 'is-user': msg.role === 'user', 'is-agent': msg.role === 'assistant' }"
      >
        <view class="msg-avatar">
          <text v-if="msg.role === 'user'">👤</text>
          <text v-else>🤖</text>
        </view>
        <view class="msg-content">
          <view class="msg-bubble">
            <text class="msg-text">{{ msg.content }}</text>
          </view>
          <view class="msg-time">{{ formatTime(msg.created_at) }}</view>
          <!-- 知识来源 -->
          <view v-if="msg.sources && msg.sources.length > 0" class="msg-sources">
            <text class="sources-label">参考来源：</text>
            <text v-for="(s, si) in msg.sources" :key="si" class="source-tag">
              {{ s.document_name || '知识库' }}
            </text>
          </view>
        </view>
      </view>

      <!-- 加载指示 -->
      <view v-if="isLoading" class="loading-indicator">
        <view class="loading-dots">
          <text class="dot">●</text>
          <text class="dot">●</text>
          <text class="dot">●</text>
        </view>
        <text class="loading-text">AI助手正在思考...</text>
      </view>
    </scroll-view>

    <!-- 输入区域 -->
    <view class="input-area">
      <view class="input-wrapper">
        <input 
          class="msg-input" 
          v-model="inputMessage" 
          placeholder="输入你的问题..."
          :disabled="isLoading"
          @confirm="sendMessage"
        />
        <view class="send-btn" :class="{ disabled: !inputMessage || isLoading }" @click="sendMessage">
          <text>发送</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

interface Message {
  role: 'user' | 'assistant'
  content: string
  created_at: string
  sources?: any[]
}

const agentName = ref('')
const isConnected = ref(false)
const isLoading = ref(false)
const inputMessage = ref('')
const messages = ref<Message[]>([])
const scrollToView = ref('')
const conversationId = ref('')

let socketTask: any = null

// 快捷问题
const quickQuestions = [
  '如何参与拼团？',
  '贡献值怎么计算？',
  '如何最大化收益？',
  '消费券如何使用？'
]

// 获取用户ID
const getUserId = () => {
  const userInfo = uni.getStorageSync('userInfo')
  return userInfo?.id || 0
}

// 连接WebSocket
const connectWebSocket = () => {
  const userId = getUserId()
  if (!userId) return

  const baseUrl = 'ws://localhost:8000'
  socketTask = uni.connectSocket({
    url: `${baseUrl}/ws/agent?user_id=${userId}`,
    success: () => {
      console.log('WebSocket连接成功')
      isConnected.value = true
      
      // 订阅频道
      socketTask.send({
        data: JSON.stringify({ action: 'subscribe' })
      })
    },
    fail: (err: any) => {
      console.error('WebSocket连接失败', err)
      isConnected.value = false
    }
  })

  // 监听消息
  socketTask.onMessage((res: any) => {
    try {
      const data = JSON.parse(res.data)
      
      if (data.type === 'agent_response') {
        messages.value.push({
          role: 'assistant',
          content: data.content,
          created_at: new Date().toISOString(),
          sources: data.sources || []
        })
        conversationId.value = data.conversation_id || ''
        isLoading.value = false
        scrollToBottom()
      } else if (data.type === 'stream_chunk') {
        // 流式响应处理
        const lastMsg = messages.value[messages.value.length - 1]
        if (lastMsg && lastMsg.role === 'assistant') {
          lastMsg.content += data.content
        } else {
          messages.value.push({
            role: 'assistant',
            content: data.content,
            created_at: new Date().toISOString()
          })
        }
        scrollToBottom()
      } else if (data.type === 'stream_end') {
        isLoading.value = false
      } else if (data.type === 'error') {
        messages.value.push({
          role: 'assistant',
          content: `❌ ${data.message}`,
          created_at: new Date().toISOString()
        })
        isLoading.value = false
        scrollToBottom()
      }
    } catch (e) {
      console.error('消息解析错误', e)
    }
  })

  socketTask.onClose(() => {
    isConnected.value = false
    console.log('WebSocket断开')
  })
}

// 发送消息
const sendMessage = () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const message = inputMessage.value.trim()
  
  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: message,
    created_at: new Date().toISOString()
  })
  
  inputMessage.value = ''
  isLoading.value = true
  scrollToBottom()

  // 通过WebSocket发送
  if (socketTask && isConnected.value) {
    socketTask.send({
      data: JSON.stringify({
        action: 'chat',
        message: message,
        conversation_id: conversationId.value || null
      })
    })
  } else {
    // 降级到HTTP请求
    sendViaHttp(message)
  }
}

// HTTP请求降级方案
const sendViaHttp = async (message: string) => {
  try {
    const res = await uni.request({
      url: 'http://localhost:8000/api/v1/agent/chat',
      method: 'POST',
      header: {
        'Authorization': `Bearer ${uni.getStorageSync('token')}`,
        'Content-Type': 'application/json'
      },
      data: {
        message,
        conversation_id: conversationId.value || null
      }
    })
    
    if (res.data) {
      messages.value.push({
        role: 'assistant',
        content: (res.data as any).answer || '抱歉，暂时无法回答',
        created_at: new Date().toISOString(),
        sources: (res.data as any).sources || []
      })
      conversationId.value = (res.data as any).conversation_id || ''
    }
  } catch (e) {
    messages.value.push({
      role: 'assistant',
      content: '❌ 网络错误，请稍后重试',
      created_at: new Date().toISOString()
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

// 快捷问题
const sendQuickQuestion = (question: string) => {
  inputMessage.value = question
  sendMessage()
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    scrollToView.value = `msg-${messages.value.length - 1}`
  })
}

// 格式化时间
const formatTime = (timeStr: string) => {
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

// 返回
const goBack = () => {
  uni.navigateBack()
}

onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (socketTask) {
    socketTask.close()
  }
})
</script>

<style scoped>
.agent-chat {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: #fff;
  border-bottom: 1px solid #eee;
}
.nav-back { font-size: 24px; color: #333; }
.nav-title { font-size: 18px; font-weight: 600; color: #333; }
.nav-status { color: #ccc; font-size: 12px; }
.nav-status.active { color: #52c41a; }

.chat-area {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.welcome-card {
  text-align: center;
  padding: 40px 20px;
  background: #fff;
  border-radius: 16px;
  margin-bottom: 20px;
}
.welcome-avatar { font-size: 48px; margin-bottom: 16px; }
.welcome-title { font-size: 20px; font-weight: 600; color: #333; margin-bottom: 8px; }
.welcome-desc { font-size: 14px; color: #666; margin-bottom: 24px; }

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}
.quick-item {
  padding: 10px 16px;
  background: #f0f7ff;
  border-radius: 20px;
  font-size: 13px;
  color: #1890ff;
}

.message-item {
  display: flex;
  margin-bottom: 20px;
  align-items: flex-start;
}
.message-item.is-user { flex-direction: row-reverse; }

.msg-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.msg-content {
  max-width: 70%;
  margin: 0 12px;
}
.msg-bubble {
  padding: 12px 16px;
  border-radius: 16px;
  background: #fff;
}
.is-user .msg-bubble {
  background: #1890ff;
  color: #fff;
}
.msg-text { font-size: 15px; line-height: 1.5; }
.msg-time { font-size: 11px; color: #999; margin-top: 4px; }

.msg-sources {
  margin-top: 8px;
  padding: 8px 12px;
  background: #f9f9f9;
  border-radius: 8px;
}
.sources-label { font-size: 11px; color: #999; }
.source-tag {
  display: inline-block;
  font-size: 11px;
  color: #1890ff;
  background: #e6f7ff;
  padding: 2px 8px;
  border-radius: 4px;
  margin: 2px 4px 0 0;
}

.loading-indicator {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
  border-radius: 16px;
  width: fit-content;
}
.loading-dots { display: flex; gap: 4px; margin-right: 8px; }
.dot { color: #1890ff; animation: blink 1.4s infinite; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink { 0%, 80%, 100% { opacity: 0.3; } 40% { opacity: 1; } }
.loading-text { font-size: 13px; color: #666; }

.input-area {
  padding: 12px 16px;
  background: #fff;
  border-top: 1px solid #eee;
  padding-bottom: calc(12px + env(safe-area-inset-bottom));
}
.input-wrapper {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 24px;
  padding: 4px 4px 4px 16px;
}
.msg-input {
  flex: 1;
  height: 40px;
  font-size: 15px;
  background: transparent;
}
.send-btn {
  padding: 8px 20px;
  background: #1890ff;
  color: #fff;
  border-radius: 20px;
  font-size: 14px;
}
.send-btn.disabled {
  background: #ccc;
}
</style>
