<template>
  <view class="notification-page">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <text class="nav-back" @click="goBack">←</text>
      <text class="nav-title">通知中心</text>
      <text v-if="unreadCount > 0" class="nav-action" @click="markAllRead">全部已读</text>
    </view>

    <!-- 通知分类Tab -->
    <view class="notif-tabs">
      <view
        v-for="tab in tabs"
        :key="tab.key"
        class="tab"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        <text>{{ tab.label }}</text>
        <view v-if="tab.count > 0" class="tab-badge">{{ tab.count }}</view>
      </view>
    </view>

    <!-- 通知列表 -->
    <scroll-view scroll-y class="notif-scroll" @scrolltoupper="refresh">
      <view class="notif-list">
        <view
          v-for="item in filteredNotifs"
          :key="item.id"
          class="notif-item"
          :class="{ unread: !item.read }"
          @click="readNotif(item)"
          @longpress="onNotifLongPress(item)"
        >
          <view class="notif-icon" :class="'type-' + item.type">
            <text>{{ typeIcons[item.type] || '📢' }}</text>
          </view>
          <view class="notif-content">
            <view class="notif-header">
              <text class="notif-title">{{ item.title }}</text>
              <text class="notif-time">{{ formatTime(item.time) }}</text>
            </view>
            <text class="notif-desc">{{ item.content }}</text>
            <view v-if="item.action_text" class="notif-action" @click.stop="handleAction(item)">
              <text>{{ item.action_text }}</text>
              <text class="action-arrow">›</text>
            </view>
          </view>
          <view class="unread-dot" v-if="!item.read"></view>
        </view>

        <view class="empty-state" v-if="filteredNotifs.length === 0">
          <text class="empty-icon">🔔</text>
          <text class="empty-text">暂无通知</text>
          <text class="empty-hint">{{ activeTab === 'all' ? '您还没有收到任何通知' : '该分类暂无通知' }}</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { request } from '@/api/index'

const activeTab = ref('all')
const typeIcons = { order: '📦', group: '🎯', system: '📢', activity: '🎁' }

const tabs = ref([
  { key: 'all', label: '全部', count: 0 },
  { key: 'order', label: '订单', count: 0 },
  { key: 'group', label: '拼团', count: 0 },
  { key: 'system', label: '系统', count: 0 },
  { key: 'activity', label: '活动', count: 0 }
])

const notifications = ref([])

const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

const filteredNotifs = computed(() => {
  if (activeTab.value === 'all') return notifications.value
  return notifications.value.filter(n => n.type === activeTab.value)
})

// 更新tab计数
const updateTabCounts = () => {
  tabs.value.forEach(tab => {
    if (tab.key === 'all') {
      tab.count = unreadCount.value
    } else {
      tab.count = notifications.value.filter(n => n.type === tab.key && !n.read).length
    }
  })
}

// 加载通知列表
const loadNotifications = async () => {
  try {
    const res = await request('/api/v1/notifications', 'GET')
    if (res && Array.isArray(res)) {
      notifications.value = res
    }
  } catch (e) {
    // 接口不存在时使用本地mock数据
    console.warn('通知接口不可用，使用mock数据:', e)
    notifications.value = [
      { id: 1, type: 'order', title: '订单已发货', content: '您的订单 ORD20240001 已发货，快递单号 SF1234567890', time: new Date().toISOString(), read: false, action_text: '查看物流' },
      { id: 2, type: 'group', title: '拼团成功', content: '恭喜！您参与的精酿啤酒初级团已成功，31人全部参团', time: new Date(Date.now() - 3600000).toISOString(), read: false, action_text: '查看详情' },
      { id: 3, type: 'system', title: '系统升级通知', content: '平台将于本周六凌晨2:00-4:00进行系统维护升级，届时部分功能可能暂时无法使用', time: new Date(Date.now() - 86400000).toISOString(), read: true, action_text: '' },
      { id: 4, type: 'order', title: '订单已完成', content: '您的订单 ORD20240002 已自动确认收货，贡献值已发放至您的账户', time: new Date(Date.now() - 172800000).toISOString(), read: true, action_text: '去评价' },
      { id: 5, type: 'activity', title: '新品上架', content: '法库精酿啤酒新口味上架，限时9折优惠，先到先得', time: new Date(Date.now() - 259200000).toISOString(), read: true, action_text: '去看看' },
      { id: 6, type: 'group', title: '拼团即将成团', content: '您参与的五常大米拼团还差2人即可成团，快邀请好友加入', time: new Date(Date.now() - 3600000 * 5).toISOString(), read: false, action_text: '邀请好友' },
      { id: 7, type: 'order', title: '退款到账通知', content: '您的退款 RFD20240001 已处理完成，金额 ¥29.90 已原路返回', time: new Date(Date.now() - 86400000 * 3).toISOString(), read: true, action_text: '查看详情' }
    ]
  }
  updateTabCounts()
}

const readNotif = (item) => {
  item.read = true
  updateTabCounts()
  if (item.action_text) {
    handleAction(item)
  }
}

const handleAction = (item) => {
  switch (item.type) {
    case 'order':
      uni.navigateTo({ url: '/pages/order/index' })
      break
    case 'group':
      uni.navigateTo({ url: '/pages/group-buy/index' })
      break
    case 'activity':
      uni.navigateTo({ url: '/pages/mall/index' })
      break
    default:
      break
  }
}

const markAllRead = () => {
  notifications.value.forEach(n => n.read = true)
  updateTabCounts()
  uni.showToast({ title: '已全部标记已读', icon: 'success' })
}

const onNotifLongPress = (item) => {
  uni.showActionSheet({
    itemList: item.read ? ['删除通知'] : ['标记已读', '删除通知'],
    success: (res) => {
      if (!item.read && res.tapIndex === 0) {
        item.read = true
        updateTabCounts()
      } else {
        notifications.value = notifications.value.filter(n => n.id !== item.id)
        updateTabCounts()
        uni.showToast({ title: '已删除', icon: 'success' })
      }
    }
  })
}

const refresh = () => {
  loadNotifications()
}

const formatTime = (t) => {
  const d = new Date(t)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
  if (diff < 604800000) return Math.floor(diff / 86400000) + '天前'
  return d.toLocaleDateString()
}

const goBack = () => uni.navigateBack()

onMounted(() => {
  loadNotifications()
})
</script>

<style scoped>
.notification-page {
  background: #f5f5f5;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
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
.nav-action { font-size: 14px; color: #1890ff; }

.notif-tabs {
  display: flex;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 10;
  border-bottom: 1px solid #f0f0f0;
}
.tab {
  flex: 1;
  text-align: center;
  padding: 12px 0;
  font-size: 14px;
  color: #666;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
.tab.active { color: #409eff; font-weight: bold; }
.tab.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 30%;
  right: 30%;
  height: 2px;
  background: #409eff;
  border-radius: 1px;
}
.tab-badge {
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

.notif-scroll { flex: 1; }
.notif-list { padding: 10px; }

.notif-item {
  background: #fff;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 8px;
  display: flex;
  align-items: flex-start;
  position: relative;
}
.notif-item.unread { background: #f0f9ff; }
.notif-item:active { background: #f9f9f9; }

.notif-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  margin-right: 12px;
}
.type-order { background: #fff7e6; }
.type-group { background: #f0f9ff; }
.type-system { background: #f5f5f5; }
.type-activity { background: #fff0f6; }

.notif-content { flex: 1; min-width: 0; }
.notif-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.notif-title { font-size: 14px; font-weight: 500; color: #333; }
.notif-time { font-size: 12px; color: #bbb; flex-shrink: 0; }
.notif-desc {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.notif-action {
  display: flex;
  align-items: center;
  margin-top: 8px;
  padding: 6px 12px;
  background: #f0f7ff;
  border-radius: 6px;
  font-size: 13px;
  color: #1890ff;
  width: fit-content;
}
.action-arrow { margin-left: 4px; font-size: 16px; }

.unread-dot {
  width: 8px;
  height: 8px;
  background: #f56c6c;
  border-radius: 50%;
  position: absolute;
  top: 14px;
  right: 14px;
}

.empty-state {
  text-align: center;
  padding: 80px 0;
}
.empty-icon { font-size: 50px; display: block; }
.empty-text { font-size: 16px; color: #666; display: block; margin-top: 12px; }
.empty-hint { font-size: 13px; color: #bbb; display: block; margin-top: 8px; }
</style>
