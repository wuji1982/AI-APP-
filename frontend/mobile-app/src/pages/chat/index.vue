<template>
  <view class="chat-page">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <text class="nav-back" @click="goBack">←</text>
      <view class="nav-center">
        <text class="nav-title">{{ chatName }}</text>
        <text v-if="isGroupChat" class="nav-subtitle">{{ groupMembers.length }}人</text>
      </view>
      <text class="nav-more" @click="showChatMenu">⋯</text>
    </view>

    <!-- 消息列表 -->
    <scroll-view
      class="chat-area"
      scroll-y
      :scroll-into-view="scrollToView"
      :scroll-with-animation="true"
      @scrolltoupper="loadMoreHistory"
    >
      <view v-if="isLoadingMore" class="loading-more">
        <text>加载中...</text>
      </view>
      <view v-if="!imStore.hasMoreMessages && displayMessages.length > 0" class="no-more">
        <text>没有更多消息了</text>
      </view>

      <template v-for="(msg, index) in displayMessages" :key="msg.clientMsgID || index">
        <!-- 时间分隔 -->
        <view v-if="msg.type === 'time'" class="time-separator">
          <text>{{ msg.text }}</text>
        </view>
        <!-- 消息气泡 -->
        <view v-else class="message-item" :class="{ 'is-self': msg.isSelf }">
          <view class="msg-avatar">
            <image v-if="msg.senderFaceUrl" :src="msg.senderFaceUrl" class="avatar-img" />
            <text v-else>{{ msg.senderNickname?.[0] || '👤' }}</text>
          </view>
          <view class="msg-content">
            <text v-if="!msg.isSelf && isGroupChat" class="msg-name">{{ msg.senderNickname }}</text>
            <view class="msg-bubble" :class="{ 'image-bubble': msg.contentType === 201 }">
              <!-- 文本消息 -->
              <text v-if="msg.contentType === 101" class="msg-text">{{ msg.content }}</text>
              <!-- 图片消息 -->
              <image v-else-if="msg.contentType === 201" :src="msg.picture?.sourcePicture?.url || msg.content" class="msg-image" mode="widthFix" @click="previewImage(msg.picture?.sourcePicture?.url || msg.content)" />
            </view>
            <view class="msg-meta">
              <text class="msg-time">{{ formatTime(msg.sendTime) }}</text>
            </view>
          </view>
        </view>
      </template>

      <!-- 对方正在输入 -->
      <view v-if="isTyping" class="typing-indicator">
        <view class="msg-avatar"><text>👤</text></view>
        <view class="typing-bubble">
          <text class="typing-dot">●</text>
          <text class="typing-dot">●</text>
          <text class="typing-dot">●</text>
        </view>
      </view>
    </scroll-view>

    <!-- 输入区域 -->
    <view class="input-area">
      <view class="input-tools">
        <text class="tool-icon" @click="toggleVoice">{{ isVoiceMode ? '⌨️' : '🎤' }}</text>
      </view>
      <view class="input-wrapper">
        <!-- 文字输入 -->
        <input
          v-if="!isVoiceMode"
          class="msg-input"
          v-model="inputMessage"
          :placeholder="inputPlaceholder"
          @confirm="sendMessage"
          @focus="onInputFocus"
        />
        <!-- 语音按钮 -->
        <view v-else class="voice-btn" @click="startVoice" @longpress="recording = true" @touchend="stopVoice">
          <text>{{ recording ? '松开结束' : '按住说话' }}</text>
        </view>
      </view>
      <view class="input-actions">
        <text class="action-icon" :class="{ active: showEmojiPanel }" @click="toggleEmoji">😊</text>
        <text class="action-icon" :class="{ active: showMorePanel }" @click="toggleMore">➕</text>
        <view v-if="inputMessage && !isVoiceMode" class="send-btn" @click="sendMessage">发送</view>
      </view>
    </view>

    <!-- 更多功能面板 -->
    <view v-if="showMorePanel" class="extra-panel">
      <view class="extra-grid">
        <view class="extra-item" @click="chooseImage">
          <view class="extra-icon-wrap"><text class="extra-icon">🖼️</text></view>
          <text class="extra-label">相册</text>
        </view>
        <view class="extra-item" @click="takePhoto">
          <view class="extra-icon-wrap"><text class="extra-icon">📷</text></view>
          <text class="extra-label">拍摄</text>
        </view>
        <view class="extra-item" @click="chooseFile">
          <view class="extra-icon-wrap"><text class="extra-icon">📁</text></view>
          <text class="extra-label">文件</text>
        </view>
        <view class="extra-item" @click="shareLocation">
          <view class="extra-icon-wrap"><text class="extra-icon">📍</text></view>
          <text class="extra-label">位置</text>
        </view>
        <view class="extra-item" @click="shareProduct">
          <view class="extra-icon-wrap"><text class="extra-icon">🛍️</text></view>
          <text class="extra-label">商品</text>
        </view>
        <view class="extra-item" @click="redPacket">
          <view class="extra-icon-wrap"><text class="extra-icon">🧧</text></view>
          <text class="extra-label">红包</text>
        </view>
      </view>
    </view>

    <!-- 表情面板 -->
    <view v-if="showEmojiPanel" class="extra-panel">
      <scroll-view scroll-y class="emoji-scroll">
        <view class="emoji-grid">
          <text
            v-for="(emoji, idx) in emojiList"
            :key="idx"
            class="emoji-item"
            @click="insertEmoji(emoji)"
          >{{ emoji }}</text>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useIMStore } from '@/stores/im'

const imStore = useIMStore()

const chatName = ref('')
const chatUserId = ref('')
const chatGroupId = ref('')
const convID = ref('')
const isGroupChat = ref(false)
const inputMessage = ref('')
const inputPlaceholder = ref('输入消息...')
const scrollToView = ref('')
const isLoadingMore = ref(false)
const showMorePanel = ref(false)
const showEmojiPanel = ref(false)
const isVoiceMode = ref(false)
const recording = ref(false)
const isTyping = ref(false)
const groupMembers = ref([])

// 表情列表
const emojiList = ['😀','😃','😄','😁','😆','😅','🤣','😂','🙂','🙃','😉','😊','😇','🥰','😍','🤩','😘','😗','😚','😙','😋','😛','😜','🤪','😝','🤑','🤗','🤭','🤫','🤔','🤐','🤨','😐','😑','😶','😏','😒','🙄','😬','🤥','😌','😔','😪','🤤','😴','😷','🤒','🤕','🤢','🤮','🥵','🥶','🥴','😵','🤯','🤠','🥳','😎','🤓','🧐']

// 当前会话消息（从store获取）
const currentMessages = computed(() => imStore.currentMessages)

// 判断消息是否是自己发的
const isSelfMsg = (msg) => {
  return msg.sendID === imStore.currentUserID
}

// 带时间分隔的消息列表
const displayMessages = computed(() => {
  const result = []
  let lastTime = 0

  currentMessages.value.forEach((msg) => {
    const msgTime = msg.sendTime || 0
    // 间隔超过5分钟显示时间
    if (msgTime - lastTime > 300000) {
      result.push({
        type: 'time',
        text: formatMsgTime(msgTime)
      })
    }
    result.push({ ...msg, type: 'message', isSelf: isSelfMsg(msg) })
    lastTime = msgTime
  })

  return result
})

const loadMessages = async () => {
  if (!convID.value) return
  await imStore.loadMessages(convID.value)
  scrollToBottom()
}

const loadMoreHistory = async () => {
  if (isLoadingMore.value || !imStore.hasMoreMessages) return
  isLoadingMore.value = true
  // 获取最早消息的ID作为起点
  const oldestMsg = currentMessages.value[0]
  const startID = oldestMsg?.clientMsgID || ''
  await imStore.loadMessages(convID.value, startID)
  isLoadingMore.value = false
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

  const recvID = isGroupChat.value ? '' : chatUserId.value
  const groupID = isGroupChat.value ? chatGroupId.value : ''

  await imStore.sendTextMessage(recvID, groupID, inputMessage.value)
  inputMessage.value = ''
  showMorePanel.value = false
  showEmojiPanel.value = false
  scrollToBottom()
}

const scrollToBottom = () => {
  nextTick(() => {
    scrollToView.value = `msg-${currentMessages.value.length - 1}`
  })
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

const formatMsgTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 86400000 && date.getDate() === now.getDate()) {
    return `今天 ${formatTime(timestamp)}`
  }
  const yesterday = new Date(now.getTime() - 86400000)
  if (date.getDate() === yesterday.getDate() && date.getMonth() === yesterday.getMonth()) {
    return `昨天 ${formatTime(timestamp)}`
  }
  return `${date.getMonth() + 1}月${date.getDate()}日 ${formatTime(timestamp)}`
}

const goBack = () => {
  imStore.clearCurrentChat()
  uni.navigateBack()
}

const showChatMenu = () => {
  const items = isGroupChat.value
    ? ['群公告', '群成员', '清空聊天记录', '退出群聊']
    : ['查看资料', '清空聊天记录', '投诉']
  uni.showActionSheet({
    itemList: items,
    success: (res) => {
      console.log('选择了', res.tapIndex)
    }
  })
}

const toggleVoice = () => {
  isVoiceMode.value = !isVoiceMode.value
  showMorePanel.value = false
  showEmojiPanel.value = false
}

const toggleEmoji = () => {
  showEmojiPanel.value = !showEmojiPanel.value
  showMorePanel.value = false
}

const toggleMore = () => {
  showMorePanel.value = !showMorePanel.value
  showEmojiPanel.value = false
}

const onInputFocus = () => {
  showMorePanel.value = false
  showEmojiPanel.value = false
}

const insertEmoji = (emoji) => {
  inputMessage.value += emoji
}

const startVoice = () => {}
const stopVoice = () => {
  if (recording.value) {
    uni.showToast({ title: '语音功能开发中', icon: 'none' })
    recording.value = false
  }
}

const chooseImage = () => {
  uni.chooseImage({
    count: 1,
    success: (res) => {
      // TODO: 上传图片到服务器后创建图片消息
      uni.showToast({ title: '图片发送开发中', icon: 'none' })
      showMorePanel.value = false
    }
  })
}

const takePhoto = () => {
  uni.chooseImage({
    count: 1,
    sourceType: ['camera'],
    success: (res) => {
      uni.showToast({ title: '拍照发送开发中', icon: 'none' })
    }
  })
}

const chooseFile = () => {
  uni.showToast({ title: '文件发送开发中', icon: 'none' })
}

const shareLocation = () => {
  uni.showToast({ title: '位置分享开发中', icon: 'none' })
}

const shareProduct = () => {
  uni.showToast({ title: '商品分享开发中', icon: 'none' })
}

const redPacket = () => {
  uni.showToast({ title: '红包功能开发中', icon: 'none' })
}

const previewImage = (url) => {
  uni.previewImage({ urls: [url] })
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const options = currentPage?.$page?.options || currentPage?.options || {}

  chatUserId.value = options.user_id || ''
  chatGroupId.value = options.group_id || ''
  convID.value = options.conv_id || ''
  chatName.value = decodeURIComponent(options.name || '聊天')
  isGroupChat.value = !!chatGroupId.value

  // 如果没有convID，根据聊天类型生成
  if (!convID.value) {
    if (isGroupChat.value) {
      convID.value = `sg_${chatGroupId.value}`
    } else {
      convID.value = `c2c_${chatUserId.value}`
    }
  }

  loadMessages()
})

onUnmounted(() => {
  // 离开聊天页时清除当前聊天状态
  imStore.clearCurrentChat()
})
</script>

<style scoped>
.chat-page {
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
.nav-center { display: flex; flex-direction: column; align-items: center; }
.nav-title { font-size: 17px; font-weight: 600; color: #333; }
.nav-subtitle { font-size: 11px; color: #999; }
.nav-more { font-size: 24px; color: #666; }

.chat-area {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
}

/* 时间分隔 */
.time-separator {
  text-align: center;
  padding: 12px 0;
}
.time-separator text {
  font-size: 12px;
  color: #bbb;
  background: #e8e8e8;
  padding: 3px 10px;
  border-radius: 4px;
}

.loading-more, .no-more {
  text-align: center;
  padding: 10px;
  color: #ccc;
  font-size: 12px;
}

.message-item {
  display: flex;
  margin-bottom: 16px;
  align-items: flex-start;
}
.message-item.is-self { flex-direction: row-reverse; }

.msg-avatar {
  width: 38px;
  height: 38px;
  border-radius: 6px;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
  overflow: hidden;
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; }

.msg-content {
  max-width: 65%;
  margin: 0 10px;
}
.msg-name {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
  display: block;
}
.msg-bubble {
  padding: 10px 14px;
  border-radius: 12px;
  background: #fff;
  word-break: break-all;
}
.is-self .msg-bubble {
  background: #1890ff;
  color: #fff;
}
.msg-text { font-size: 15px; line-height: 1.5; }
.msg-image { max-width: 200px; border-radius: 8px; }
.msg-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
}
.msg-time { font-size: 11px; color: #bbb; }
.msg-status { font-size: 11px; }

/* 正在输入 */
.typing-indicator {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}
.typing-bubble {
  display: flex;
  gap: 4px;
  padding: 10px 14px;
  background: #fff;
  border-radius: 12px;
  margin-left: 10px;
}
.typing-dot {
  color: #999;
  font-size: 12px;
  animation: typingBlink 1.4s infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typingBlink { 0%, 80%, 100% { opacity: 0.3; } 40% { opacity: 1; } }

/* 输入区域 */
.input-area {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  background: #fff;
  border-top: 1px solid #eee;
  gap: 8px;
}
.input-tools { flex-shrink: 0; }
.tool-icon { font-size: 24px; padding: 4px; }
.input-wrapper { flex: 1; }
.msg-input {
  width: 100%;
  height: 36px;
  background: #f5f5f5;
  border-radius: 18px;
  padding: 0 15px;
  font-size: 15px;
}
.voice-btn {
  height: 36px;
  background: #f5f5f5;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #666;
}
.input-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.action-icon { font-size: 24px; padding: 4px; }
.action-icon.active { color: #1890ff; }
.send-btn {
  padding: 6px 16px;
  background: #1890ff;
  color: #fff;
  border-radius: 16px;
  font-size: 14px;
}

/* 更多面板 */
.extra-panel {
  background: #fff;
  border-top: 1px solid #eee;
  padding-bottom: env(safe-area-inset-bottom);
}
.extra-grid {
  display: flex;
  flex-wrap: wrap;
  padding: 20px;
  gap: 16px;
}
.extra-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 60px;
}
.extra-icon-wrap {
  width: 52px;
  height: 52px;
  background: #f5f5f5;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 6px;
}
.extra-icon { font-size: 26px; }
.extra-label { font-size: 12px; color: #666; }

/* 表情面板 */
.emoji-scroll { height: 200px; padding: 10px; }
.emoji-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.emoji-item {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  border-radius: 8px;
}
.emoji-item:active { background: #f0f0f0; }
</style>
