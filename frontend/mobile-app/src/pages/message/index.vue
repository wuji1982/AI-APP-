<template>
  <view class="message-page">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <text class="nav-title">消息</text>
      <view class="nav-actions">
        <text class="nav-icon" @click="showSearch">🔍</text>
        <text class="nav-icon" @click="showAddFriendModal = true">➕</text>
      </view>
    </view>

    <!-- 消息分类入口 -->
    <view class="msg-categories">
      <view class="category-item" @click="goNotification">
        <view class="cat-icon-wrap system">
          <text class="cat-icon">🔔</text>
        </view>
        <text class="cat-label">系统通知</text>
        <view v-if="systemUnread > 0" class="cat-badge">{{ systemUnread }}</view>
      </view>
      <view class="category-item" @click="goFriends">
        <view class="cat-icon-wrap friend">
          <text class="cat-icon">👥</text>
        </view>
        <text class="cat-label">好友申请</text>
        <view v-if="imStore.pendingFriendRequests > 0" class="cat-badge">{{ imStore.pendingFriendRequests }}</view>
      </view>
      <view class="category-item" @click="showGroupList">
        <view class="cat-icon-wrap group">
          <text class="cat-icon">🎯</text>
        </view>
        <text class="cat-label">拼团群聊</text>
        <view v-if="groupUnread > 0" class="cat-badge">{{ groupUnread }}</view>
      </view>
      <view class="category-item" @click="goAgent">
        <view class="cat-icon-wrap agent">
          <text class="cat-icon">🤖</text>
        </view>
        <text class="cat-label">AI助手</text>
      </view>
    </view>

    <!-- 连接状态提示 -->
    <view v-if="imStore.connecting" class="connect-status">
      <text>连接中...</text>
    </view>

    <!-- 会话列表 -->
    <view class="section-header">
      <text class="section-title">最近聊天</text>
      <text v-if="imStore.conversations.length > 0" class="section-action" @click="clearAllRead">全部已读</text>
    </view>

    <view class="conversation-list">
      <view
        v-for="conv in imStore.conversations"
        :key="conv.conversationID"
        class="conversation-item"
        @click="openChat(conv)"
        @longpress="onConvLongPress(conv)"
      >
        <view class="conv-avatar" :style="{ background: getAvatarBg(conv) }">
          <image v-if="conv.faceURL" :src="conv.faceURL" class="avatar-img" />
          <text v-else>{{ conv.showName?.[0] || '💬' }}</text>
          <view v-if="conv.unreadCount > 0" class="unread-badge">{{ conv.unreadCount > 99 ? '99+' : conv.unreadCount }}</view>
        </view>
        <view class="conv-info">
          <view class="conv-header">
            <text class="conv-name">{{ conv.showName || '未知会话' }}</text>
            <text class="conv-time">{{ formatTime(conv.latestMsgSendTime) }}</text>
          </view>
          <text class="conv-last-msg">{{ conv.latestMsg || '' }}</text>
        </view>
      </view>

      <!-- 空状态 -->
      <view v-if="imStore.conversations.length === 0" class="empty-state">
        <text class="empty-icon">💬</text>
        <text class="empty-text">暂无消息</text>
        <text class="empty-hint">添加好友或参与拼团开始聊天吧</text>
      </view>
    </view>

    <!-- 群聊列表弹窗 -->
    <view v-if="showGroupModal" class="modal-mask" @click="showGroupModal = false">
      <view class="modal-content group-modal" @click.stop>
        <text class="modal-title">拼团群聊</text>
        <view class="group-list">
          <view
            v-for="g in imStore.joinedGroups"
            :key="g.groupID"
            class="group-item"
            @click="openGroupChat(g)"
          >
            <view class="group-avatar">
              <image v-if="g.faceURL" :src="g.faceURL" class="avatar-img" />
              <text v-else>{{ g.groupName?.[0] || '🎯' }}</text>
            </view>
            <view class="group-info">
              <text class="group-name">{{ g.groupName }}</text>
              <text class="group-members">{{ g.memberCount }}人参与</text>
            </view>
            <text class="group-arrow">›</text>
          </view>
          <view v-if="imStore.joinedGroups.length === 0" class="empty-hint" style="padding: 30px 0; text-align: center;">
            暂无进行中的拼团群
          </view>
        </view>
        <view class="modal-footer" @click="showGroupModal = false">关闭</view>
      </view>
    </view>

    <!-- 添加好友弹窗 -->
    <view v-if="showAddFriendModal" class="modal-mask" @click="showAddFriendModal = false">
      <view class="modal-content" @click.stop>
        <text class="modal-title">添加好友</text>
        <input
          class="modal-input"
          v-model="searchPhone"
          placeholder="输入手机号搜索用户"
          type="number"
          maxlength="11"
        />
        <view v-if="searchResult" class="search-result">
          <view class="result-avatar"><text>👤</text></view>
          <view class="result-info">
            <text class="result-name">{{ searchResult.nickname }}</text>
            <text class="result-phone">{{ searchResult.phone }}</text>
          </view>
          <view class="result-btn" @click="doSendFriendRequest">添加</view>
        </view>
        <view class="modal-actions">
          <view class="modal-btn cancel" @click="showAddFriendModal = false">取消</view>
          <view class="modal-btn confirm" @click="doSearchUser">搜索</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useIMStore } from '@/stores/im'

const imStore = useIMStore()

const showAddFriendModal = ref(false)
const showGroupModal = ref(false)
const searchPhone = ref('')
const searchResult = ref(null)
const systemUnread = ref(0)

// 群聊未读数
const groupUnread = computed(() => {
  return imStore.conversations
    .filter(c => c.conversationType === 3)
    .reduce((sum, c) => sum + (c.unreadCount || 0), 0)
})

// 根据会话类型获取头像背景色
const getAvatarBg = (conv) => {
  if (conv.conversationType === 3) return '#f0f9ff'
  const colors = ['#e6f7ff', '#f6ffed', '#fff7e6', '#fff0f6', '#f0f5ff']
  const idx = (conv.userID || '').charCodeAt(0) % colors.length
  return colors[idx]
}

const openChat = (conv) => {
  // 标记已读
  if (conv.unreadCount > 0) {
    imStore.markAsRead(conv.conversationID)
  }
  const name = encodeURIComponent(conv.showName || '聊天')
  if (conv.conversationType === 3) {
    // 群聊
    uni.navigateTo({
      url: `/pages/chat/index?group_id=${conv.groupID}&name=${name}&conv_id=${conv.conversationID}`
    })
  } else {
    // 单聊
    uni.navigateTo({
      url: `/pages/chat/index?user_id=${conv.userID}&name=${name}&conv_id=${conv.conversationID}`
    })
  }
}

const openGroupChat = (g) => {
  showGroupModal.value = false
  const name = encodeURIComponent(g.groupName || '群聊')
  uni.navigateTo({
    url: `/pages/chat/index?group_id=${g.groupID}&name=${name}&conv_id=sg_${g.groupID}`
  })
}

const showGroupList = () => {
  showGroupModal.value = true
}

const goNotification = () => {
  uni.navigateTo({ url: '/pages/notification/index' })
}

const goFriends = () => {
  uni.navigateTo({ url: '/pages/friends/index' })
}

const goAgent = () => {
  uni.navigateTo({ url: '/pages/agent/index' })
}

const clearAllRead = () => {
  imStore.conversations.forEach(c => {
    if (c.unreadCount > 0) {
      imStore.markAsRead(c.conversationID)
    }
  })
  uni.showToast({ title: '已全部标记已读', icon: 'success' })
}

const onConvLongPress = (conv) => {
  uni.showActionSheet({
    itemList: ['标记已读', '删除会话'],
    success: (res) => {
      if (res.tapIndex === 0) {
        imStore.markAsRead(conv.conversationID)
      } else if (res.tapIndex === 1) {
        imStore.removeConversation(conv.conversationID)
        uni.showToast({ title: '已删除', icon: 'success' })
      }
    }
  })
}

const doSearchUser = () => {
  if (!searchPhone.value || searchPhone.value.length < 11) {
    uni.showToast({ title: '请输入11位手机号', icon: 'none' })
    return
  }
  // TODO: 调用后端API搜索用户
  searchResult.value = {
    user_id: '999',
    nickname: '用户' + searchPhone.value.slice(-4),
    phone: searchPhone.value.slice(0, 3) + '****' + searchPhone.value.slice(-4)
  }
}

const doSendFriendRequest = () => {
  if (!searchResult.value) return
  imStore.sendFriendRequest(searchResult.value.user_id, '请求添加好友')
  showAddFriendModal.value = false
  searchResult.value = null
  searchPhone.value = ''
}

const showSearch = () => {
  uni.showToast({ title: '搜索功能开发中', icon: 'none' })
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`

  return `${date.getMonth() + 1}/${date.getDate()}`
}

onMounted(() => {
  // 如果IM已登录但未加载数据，尝试刷新
  if (imStore.loginStatus && imStore.conversations.length === 0) {
    imStore.refreshConversations()
  }
})
</script>

<style scoped>
.message-page {
  background: #f5f5f5;
  min-height: 100vh;
}

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: #fff;
  border-bottom: 1px solid #eee;
}
.nav-title { font-size: 18px; font-weight: 600; color: #333; }
.nav-actions { display: flex; gap: 16px; }
.nav-icon { font-size: 20px; }

/* 消息分类入口 */
.msg-categories {
  display: flex;
  padding: 20px 15px;
  background: #fff;
  gap: 0;
}
.category-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}
.cat-icon-wrap {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: 8px;
}
.cat-icon-wrap.system { background: #fff7e6; }
.cat-icon-wrap.friend { background: #e6f7ff; }
.cat-icon-wrap.group { background: #f0f9ff; }
.cat-icon-wrap.agent { background: #f0f5ff; }
.cat-label { font-size: 12px; color: #666; }
.cat-badge {
  position: absolute;
  top: -4px;
  right: 10px;
  min-width: 18px;
  height: 18px;
  background: #ff4d4f;
  color: #fff;
  font-size: 10px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
}

.connect-status {
  text-align: center;
  padding: 6px;
  background: #fff7e6;
  font-size: 12px;
  color: #fa8c16;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px 10px;
}
.section-title { font-size: 14px; color: #999; }
.section-action { font-size: 13px; color: #1890ff; }

.conversation-list {
  background: #fff;
  margin: 0 15px 15px;
  border-radius: 12px;
  overflow: hidden;
}
.conversation-item {
  display: flex;
  align-items: center;
  padding: 14px 15px;
  border-bottom: 1px solid #f5f5f5;
}
.conversation-item:last-child { border-bottom: none; }
.conversation-item:active { background: #f9f9f9; }

.conv-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; }
.unread-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 16px;
  height: 16px;
  background: #ff4d4f;
  color: #fff;
  font-size: 10px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

.conv-info { flex: 1; margin-left: 12px; overflow: hidden; }
.conv-header { display: flex; justify-content: space-between; align-items: center; }
.conv-name { font-size: 15px; color: #333; font-weight: 500; }
.conv-time { font-size: 12px; color: #bbb; flex-shrink: 0; }
.conv-last-msg {
  font-size: 13px;
  color: #999;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}
.empty-icon { font-size: 48px; display: block; margin-bottom: 16px; }
.empty-text { font-size: 16px; color: #666; display: block; }
.empty-hint { font-size: 13px; color: #999; display: block; margin-top: 8px; }

/* 群聊弹窗 */
.group-modal { width: 340px; padding: 20px; }
.group-list { max-height: 360px; overflow-y: auto; }
.group-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
}
.group-item:last-child { border-bottom: none; }
.group-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #f0f9ff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  overflow: hidden;
}
.group-info { flex: 1; margin-left: 12px; }
.group-name { font-size: 15px; color: #333; display: block; font-weight: 500; }
.group-members { font-size: 12px; color: #999; display: block; margin-top: 2px; }
.group-arrow { font-size: 20px; color: #ccc; }
.modal-footer {
  margin-top: 16px;
  text-align: center;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 8px;
  font-size: 15px;
  color: #666;
}

/* 弹窗 */
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}
.modal-content {
  width: 320px;
  background: #fff;
  border-radius: 16px;
  padding: 24px;
}
.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 16px;
  text-align: center;
}
.modal-input {
  width: 100%;
  height: 44px;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 0 12px;
  font-size: 15px;
  margin-bottom: 12px;
  box-sizing: border-box;
}
.search-result {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 12px;
}
.result-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e6f7ff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}
.result-info { flex: 1; margin-left: 12px; }
.result-name { font-size: 15px; color: #333; display: block; }
.result-phone { font-size: 12px; color: #999; display: block; }
.result-btn {
  padding: 6px 16px;
  background: #1890ff;
  color: #fff;
  border-radius: 14px;
  font-size: 13px;
}
.modal-actions {
  display: flex;
  gap: 12px;
}
.modal-btn {
  flex: 1;
  height: 44px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
}
.modal-btn.cancel { background: #f5f5f5; color: #666; }
.modal-btn.confirm { background: #1890ff; color: #fff; }
</style>
