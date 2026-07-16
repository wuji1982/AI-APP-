<template>
  <view class="friends-page">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <text class="nav-back" @click="goBack">←</text>
      <text class="nav-title">好友</text>
      <text class="nav-add" @click="openAddModal">➕</text>
    </view>

    <!-- 搜索框 -->
    <view class="search-bar">
      <view class="search-wrap">
        <text class="search-icon">🔍</text>
        <input
          class="search-input"
          v-model="searchKeyword"
          placeholder="搜索好友昵称/备注"
          @input="onSearch"
        />
        <text v-if="searchKeyword" class="search-clear" @click="searchKeyword = ''">✕</text>
      </view>
    </view>

    <!-- 好友申请 -->
    <view v-if="imStore.friendApplications.length > 0" class="section">
      <view class="section-header">
        <text class="section-title">好友申请</text>
        <view class="section-badge">{{ pendingApps.length }}</view>
      </view>
      <view
        v-for="req in pendingApps"
        :key="req.fromUserID"
        class="request-item"
      >
        <view class="request-avatar">
          <image v-if="req.fromFaceURL" :src="req.fromFaceURL" class="avatar-img" />
          <text v-else>{{ req.fromNickname?.[0] || '👤' }}</text>
        </view>
        <view class="request-info">
          <text class="request-name">{{ req.fromNickname }}</text>
          <text class="request-msg">{{ req.reqMsg || '请求添加好友' }}</text>
        </view>
        <view class="request-actions">
          <view class="btn-accept" @click="acceptRequest(req)">接受</view>
          <view class="btn-reject" @click="rejectRequest(req)">拒绝</view>
        </view>
      </view>
    </view>

    <!-- 快捷入口 -->
    <view v-if="!searchKeyword" class="quick-entries">
      <view class="entry-item" @click="openAddModal">
        <view class="entry-icon add"><text>👤+</text></view>
        <text class="entry-label">添加好友</text>
      </view>
      <view class="entry-item" @click="showCreateGroup">
        <view class="entry-icon group"><text>👥</text></view>
        <text class="entry-label">创建群聊</text>
      </view>
      <view class="entry-item" @click="showFriendTeam">
        <view class="entry-icon team"><text>🏢</text></view>
        <text class="entry-label">我的团队</text>
      </view>
    </view>

    <!-- 好友列表 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">我的好友</text>
        <text class="section-count">{{ filteredFriends.length }}人</text>
      </view>

      <view
        v-for="friend in filteredFriends"
        :key="friend.userID"
        class="friend-item"
        @click="openFriendDetail(friend)"
      >
        <view class="friend-avatar" :style="{ background: getAvatarBg(friend) }">
          <image v-if="friend.faceURL" :src="friend.faceURL" class="avatar-img" />
          <text v-else>{{ friend.nickname?.[0] || friend.remark?.[0] || '👤' }}</text>
        </view>
        <view class="friend-info">
          <text class="friend-name">{{ friend.remark || friend.nickname }}</text>
          <text class="friend-remark" v-if="friend.remark">昵称: {{ friend.nickname }}</text>
        </view>
        <view class="friend-actions" @click.stop="showFriendMenu(friend)">
          <text class="action-more">⋯</text>
        </view>
      </view>

      <view v-if="filteredFriends.length === 0" class="empty-state">
        <text class="empty-icon">👥</text>
        <text class="empty-text">{{ searchKeyword ? '未找到好友' : '暂无好友' }}</text>
        <text class="empty-hint" v-if="!searchKeyword">点击上方➕添加好友</text>
      </view>
    </view>

    <!-- 好友详情弹窗 -->
    <view v-if="showDetailModal" class="modal-mask" @click="showDetailModal = false">
      <view class="modal-content detail-modal" @click.stop>
        <view class="detail-header">
          <view class="detail-avatar" :style="{ background: getAvatarBg(currentFriend) }">
            <image v-if="currentFriend.faceURL" :src="currentFriend.faceURL" class="avatar-img" />
            <text v-else>{{ currentFriend.nickname?.[0] || '👤' }}</text>
          </view>
          <text class="detail-name">{{ currentFriend.remark || currentFriend.nickname }}</text>
          <text class="detail-phone" v-if="currentFriend.userID">ID: {{ currentFriend.userID }}</text>
        </view>
        <view class="detail-actions">
          <view class="detail-btn primary" @click="chatWith(currentFriend)">
            <text>💬 发消息</text>
          </view>
          <view class="detail-btn outline" @click="setRemark(currentFriend)">
            <text>✏️ 设置备注</text>
          </view>
        </view>
        <view class="modal-footer" @click="showDetailModal = false">关闭</view>
      </view>
    </view>

    <!-- 添加好友弹窗 -->
    <view v-if="showAddModal" class="modal-mask" @click="showAddModal = false">
      <view class="modal-content" @click.stop>
        <text class="modal-title">添加好友</text>
        <input
          class="modal-input"
          v-model="searchPhone"
          placeholder="输入手机号搜索"
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
          <view class="modal-btn cancel" @click="showAddModal = false">取消</view>
          <view class="modal-btn confirm" @click="doSearch">搜索</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useIMStore } from '@/stores/im'

const imStore = useIMStore()

const searchKeyword = ref('')
const showAddModal = ref(false)
const showDetailModal = ref(false)
const searchPhone = ref('')
const searchResult = ref(null)
const currentFriend = ref({})

// 待处理的好友申请
const pendingApps = computed(() => {
  return imStore.friendApplications.filter(a => a.handleResult === 0)
})

// 搜索过滤好友列表
const filteredFriends = computed(() => {
  if (!searchKeyword.value) return imStore.friends
  const keyword = searchKeyword.value.toLowerCase()
  return imStore.friends.filter(f =>
    (f.nickname && f.nickname.toLowerCase().includes(keyword)) ||
    (f.remark && f.remark.toLowerCase().includes(keyword))
  )
})

const getAvatarBg = (friend) => {
  const colors = ['#e6f7ff', '#f6ffed', '#fff7e6', '#fff0f6', '#f0f5ff']
  const idx = (friend.userID || '').charCodeAt(0) % colors.length
  return colors[idx]
}

const onSearch = () => {}

const openFriendDetail = (friend) => {
  currentFriend.value = friend
  showDetailModal.value = true
}

const chatWith = (friend) => {
  showDetailModal.value = false
  const name = encodeURIComponent(friend.remark || friend.nickname || '聊天')
  uni.navigateTo({
    url: `/pages/chat/index?user_id=${friend.userID}&name=${name}&conv_id=c2c_${friend.userID}`
  })
}

const setRemark = (friend) => {
  showDetailModal.value = false
  uni.showModal({
    title: '设置备注',
    editable: true,
    placeholderText: '输入备注名',
    success: (res) => {
      if (res.confirm && res.content) {
        imStore.setFriendRemark([friend.userID], res.content)
        uni.showToast({ title: '备注已设置', icon: 'success' })
      }
    }
  })
}

const openAddModal = () => {
  showAddModal.value = true
  searchResult.value = null
  searchPhone.value = ''
}

const doSearch = () => {
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
  showAddModal.value = false
  searchResult.value = null
  searchPhone.value = ''
}

const acceptRequest = (req) => {
  imStore.handleFriendApplication(req.fromUserID, true)
  uni.showToast({ title: '已添加好友', icon: 'success' })
}

const rejectRequest = (req) => {
  imStore.handleFriendApplication(req.fromUserID, false)
  uni.showToast({ title: '已拒绝', icon: 'none' })
}

const showFriendMenu = (friend) => {
  uni.showActionSheet({
    itemList: ['发送消息', '设置备注', '删除好友', '加入黑名单'],
    success: (res) => {
      switch (res.tapIndex) {
        case 0: chatWith(friend); break
        case 1: setRemark(friend); break
        case 2: deleteFriend(friend); break
        case 3: blockUser(friend); break
      }
    }
  })
}

const deleteFriend = (friend) => {
  uni.showModal({
    title: '确认删除',
    content: `确定要删除好友"${friend.remark || friend.nickname}"吗？`,
    success: (res) => {
      if (res.confirm) {
        imStore.removeFriend(friend.userID)
        uni.showToast({ title: '已删除好友', icon: 'success' })
      }
    }
  })
}

const blockUser = (friend) => {
  uni.showModal({
    title: '加入黑名单',
    content: `确定要将"${friend.remark || friend.nickname}"加入黑名单吗？`,
    success: (res) => {
      if (res.confirm) {
        imStore.blockUser(friend.userID)
        uni.showToast({ title: '已加入黑名单', icon: 'success' })
      }
    }
  })
}

const showCreateGroup = () => {
  uni.showModal({
    title: '创建群聊',
    content: '选择2位以上好友创建群聊',
    success: (res) => {
      if (res.confirm) {
        uni.showToast({ title: '群聊创建开发中', icon: 'none' })
      }
    }
  })
}

const showFriendTeam = () => {
  uni.navigateTo({ url: '/pages/team/index' })
}

const goBack = () => uni.navigateBack()

onMounted(() => {
  // 如果IM已登录但好友列表为空，尝试刷新
  if (imStore.loginStatus && imStore.friends.length === 0) {
    imStore.refreshFriends()
    imStore.refreshFriendApplications()
  }
})
</script>

<style scoped>
.friends-page {
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
.nav-back { font-size: 24px; color: #333; }
.nav-title { font-size: 18px; font-weight: 600; color: #333; }
.nav-add { font-size: 20px; color: #1890ff; }

.search-bar { padding: 10px 15px; background: #fff; }
.search-wrap {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 20px;
  padding: 0 12px;
  height: 36px;
}
.search-icon { font-size: 14px; margin-right: 6px; }
.search-input { flex: 1; font-size: 14px; background: transparent; }
.search-clear { font-size: 14px; color: #999; padding: 4px; }

.section {
  background: #fff;
  margin: 10px 15px;
  border-radius: 12px;
  overflow: hidden;
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 15px;
  border-bottom: 1px solid #f5f5f5;
}
.section-title { font-size: 14px; color: #666; font-weight: 500; }
.section-count { font-size: 12px; color: #999; }
.section-badge {
  min-width: 20px;
  height: 20px;
  background: #ff4d4f;
  color: #fff;
  font-size: 11px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
}

/* 快捷入口 */
.quick-entries {
  display: flex;
  padding: 15px;
  gap: 10px;
}
.entry-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 14px 10px;
  background: #fff;
  border-radius: 12px;
}
.entry-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  margin-bottom: 8px;
}
.entry-icon.add { background: #e6f7ff; }
.entry-icon.group { background: #f0f9ff; }
.entry-icon.team { background: #fff7e6; }
.entry-label { font-size: 12px; color: #666; }

.request-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  border-bottom: 1px solid #f5f5f5;
}
.request-item:last-child { border-bottom: none; }
.request-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #fff3e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  overflow: hidden;
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; }
.request-info { flex: 1; margin-left: 12px; }
.request-name { font-size: 15px; color: #333; display: block; }
.request-msg { font-size: 12px; color: #999; display: block; margin-top: 2px; }
.request-actions { display: flex; gap: 8px; }
.btn-accept {
  padding: 6px 14px;
  background: #1890ff;
  color: #fff;
  border-radius: 14px;
  font-size: 13px;
}
.btn-reject {
  padding: 6px 14px;
  background: #f5f5f5;
  color: #666;
  border-radius: 14px;
  font-size: 13px;
}

.friend-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  border-bottom: 1px solid #f5f5f5;
}
.friend-item:last-child { border-bottom: none; }
.friend-item:active { background: #f9f9f9; }
.friend-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}
.online-dot {
  width: 10px;
  height: 10px;
  background: #52c41a;
  border: 2px solid #fff;
  border-radius: 50%;
  position: absolute;
  bottom: 0;
  right: 0;
}
.friend-info { flex: 1; margin-left: 12px; }
.friend-name { font-size: 15px; color: #333; display: block; }
.friend-remark { font-size: 12px; color: #999; display: block; margin-top: 2px; }
.friend-actions { padding: 5px 10px; }
.action-more { font-size: 20px; color: #999; }

.empty-state {
  text-align: center;
  padding: 40px 20px;
}
.empty-icon { font-size: 40px; display: block; margin-bottom: 12px; }
.empty-text { font-size: 14px; color: #999; display: block; }
.empty-hint { font-size: 13px; color: #bbb; display: block; margin-top: 6px; }

/* 好友详情弹窗 */
.detail-modal { width: 320px; padding: 0; overflow: hidden; }
.detail-header {
  text-align: center;
  padding: 30px 20px 20px;
  background: linear-gradient(135deg, #e6f7ff, #f0f5ff);
}
.detail-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
  margin: 0 auto 12px;
  overflow: hidden;
}
.detail-name { font-size: 18px; font-weight: 600; color: #333; display: block; }
.detail-phone { font-size: 13px; color: #999; display: block; margin-top: 4px; }
.detail-actions {
  display: flex;
  gap: 12px;
  padding: 20px;
}
.detail-btn {
  flex: 1;
  height: 40px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}
.detail-btn.primary { background: #1890ff; color: #fff; }
.detail-btn.outline { background: #f5f5f5; color: #666; }

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
.modal-actions { display: flex; gap: 12px; }
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
.modal-footer {
  text-align: center;
  padding: 12px;
  background: #f5f5f5;
  font-size: 15px;
  color: #666;
  border-radius: 0 0 16px 16px;
}
</style>
