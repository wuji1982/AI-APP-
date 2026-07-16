<template>
  <view class="group-buy-page">
    <!-- 级别切换 -->
    <view class="level-tabs">
      <view class="tab" :class="{ active: currentLevel === 'junior' }" @click="switchLevel('junior')">初级团</view>
      <view class="tab" :class="{ active: currentLevel === 'senior' }" @click="switchLevel('senior')">高级团</view>
      <view class="tab" :class="{ active: currentLevel === 'svip' }" @click="switchLevel('svip')">SVIP团</view>
    </view>

    <!-- 场次列表 -->
    <scroll-view scroll-y class="session-list">
      <view v-if="loading" class="loading-state">
        <text>加载中...</text>
      </view>
      <view v-else-if="sessions.length === 0" class="empty-state">
        <text class="empty-icon">🎯</text>
        <text class="empty-text">暂无拼团场次</text>
        <text class="empty-desc">每天10:00-22:00开放拼团</text>
      </view>
      <view v-else class="session-card" v-for="s in sessions" :key="s.id" @click="goDetail(s)">
        <view class="session-header">
          <text class="session-no">{{ s.session_no }}</text>
          <text class="session-status" :class="'status-' + s.status">{{ getStatusText(s.status) }}</text>
        </view>
        <view class="session-info">
          <view class="info-item">
            <text class="info-label">参团金额</text>
            <text class="info-value price">¥{{ s.total_price }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">参与人数</text>
            <text class="info-value">{{ s.current_players }}/{{ s.total_players }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">拼中名额</text>
            <text class="info-value">{{ s.winner_count }}人</text>
          </view>
        </view>
        <view class="session-progress">
          <view class="progress-bar">
            <view class="progress-fill" :style="{ width: getProgress(s) + '%' }"></view>
          </view>
          <text class="progress-text">{{ getProgress(s) }}%</text>
        </view>
        <view class="session-footer">
          <text class="session-time">{{ s.start_time }}</text>
          <view class="join-btn" :class="{ disabled: s.status !== 'active' && s.status !== 'pending' }">
            <text>{{ s.status === 'active' || s.status === 'pending' ? '立即参团' : '已结束' }}</text>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import { getSessions } from '../../api/index'

export default {
  data() {
    return {
      currentLevel: 'junior',
      sessions: [],
      loading: false
    }
  },
  onLoad() {
    this.loadSessions()
  },
  onPullDownRefresh() {
    this.loadSessions().then(() => uni.stopPullDownRefresh())
  },
  methods: {
    async loadSessions() {
      this.loading = true
      try {
        const res = await getSessions(this.currentLevel)
        this.sessions = res.sessions || res.items || []
      } catch (e) {
        console.error('加载拼团场次失败', e)
        this.sessions = []
      } finally {
        this.loading = false
      }
    },
    switchLevel(level) {
      this.currentLevel = level
      this.loadSessions()
    },
    getStatusText(status) {
      const map = { pending: '待开团', active: '进行中', full: '已满员', completed: '已完成', cancelled: '已取消', expired: '已过期' }
      return map[status] || status
    },
    getProgress(s) {
      if (!s.total_players) return 0
      return Math.min(100, Math.round((s.current_players / s.total_players) * 100))
    },
    goDetail(s) {
      uni.navigateTo({ url: `/pages/group-buy/detail?id=${s.id}` })
    }
  }
}
</script>

<style scoped>
.group-buy-page { background: #f5f5f5; min-height: 100vh; padding-bottom: 60px; }
.level-tabs { display: flex; background: #fff; padding: 10px 15px; gap: 10px; }
.tab { flex: 1; text-align: center; padding: 10px 0; border-radius: 20px; font-size: 14px; color: #666; background: #f5f5f5; }
.tab.active { background: #ff6b35; color: #fff; font-weight: bold; }
.session-list { height: calc(100vh - 120px); padding: 12px; }
.loading-state, .empty-state { text-align: center; padding: 60px 20px; color: #999; }
.empty-icon { font-size: 48px; display: block; margin-bottom: 12px; }
.empty-text { font-size: 16px; display: block; margin-bottom: 4px; }
.empty-desc { font-size: 13px; display: block; color: #ccc; }
.session-card { background: #fff; border-radius: 12px; padding: 16px; margin-bottom: 12px; }
.session-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.session-no { font-size: 14px; font-weight: 600; color: #333; }
.session-status { font-size: 12px; padding: 3px 10px; border-radius: 10px; }
.status-pending { background: #fff7e6; color: #fa8c16; }
.status-active { background: #e6f7ff; color: #1890ff; }
.status-full { background: #f6ffed; color: #52c41a; }
.status-completed { background: #f5f5f5; color: #999; }
.session-info { display: flex; margin-bottom: 12px; }
.info-item { flex: 1; }
.info-label { font-size: 12px; color: #999; display: block; }
.info-value { font-size: 14px; color: #333; display: block; margin-top: 2px; }
.info-value.price { color: #ff4d4f; font-weight: bold; font-size: 16px; }
.session-progress { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.progress-bar { flex: 1; height: 6px; background: #f0f0f0; border-radius: 3px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #ff6b35, #ff8c5a); border-radius: 3px; }
.progress-text { font-size: 12px; color: #ff6b35; min-width: 36px; text-align: right; }
.session-footer { display: flex; justify-content: space-between; align-items: center; }
.session-time { font-size: 12px; color: #999; }
.join-btn { padding: 6px 20px; background: #ff6b35; color: #fff; border-radius: 16px; font-size: 13px; }
.join-btn.disabled { background: #d9d9d9; color: #999; }
</style>
