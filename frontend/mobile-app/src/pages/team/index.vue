<template>
  <view class="team-page">
    <!-- 团队概览 -->
    <view class="overview-card">
      <view class="overview-item">
        <text class="ov-value">{{ teamStats.direct_count || 0 }}</text>
        <text class="ov-label">直属成员</text>
      </view>
      <view class="overview-item">
        <text class="ov-value">{{ teamStats.total_count || 0 }}</text>
        <text class="ov-label">团队总人数</text>
      </view>
      <view class="overview-item">
        <text class="ov-value">{{ teamStats.month_sales || '0.00' }}</text>
        <text class="ov-label">本月团队消费</text>
      </view>
    </view>

    <!-- 层级切换 -->
    <view class="level-tabs">
      <view class="tab" :class="{ active: currentLevel === 1 }" @click="switchLevel(1)">直属</view>
      <view class="tab" :class="{ active: currentLevel === 2 }" @click="switchLevel(2)">间接1层</view>
      <view class="tab" :class="{ active: currentLevel === 3 }" @click="switchLevel(3)">间接2层</view>
      <view class="tab" :class="{ active: currentLevel === 4 }" @click="switchLevel(4)">间接3层</view>
    </view>

    <!-- 成员列表 -->
    <view class="member-list">
      <view class="member-item" v-for="m in members" :key="m.user_id">
        <view class="member-avatar">
          <text class="avatar-text">{{ (m.nickname || '用')[0] }}</text>
        </view>
        <view class="member-info">
          <text class="member-name">{{ m.nickname || '用户' + m.user_id }}</text>
          <text class="member-phone">{{ m.phone }}</text>
        </view>
        <view class="member-stats">
          <text class="stats-value">¥{{ m.total_amount || 0 }}</text>
          <text class="stats-label">消费额</text>
        </view>
      </view>
      <view class="empty" v-if="members.length === 0">
        <text>该层级暂无成员</text>
      </view>
    </view>
  </view>
</template>

<script>
import { getMyTeam } from '../../api/index'

export default {
  data() {
    return {
      currentLevel: 1,
      members: [],
      teamStats: {}
    }
  },
  onLoad() { this.loadTeam() },
  methods: {
    async loadTeam() {
      try {
        const res = await getMyTeam(this.currentLevel)
        this.members = res.items || res.members || []
        this.teamStats = res.stats || { direct_count: 0, total_count: 0, month_sales: '0.00' }
      } catch (e) {
        const msg = e.message === '未登录' ? '请先登录' : '加载失败'
        uni.showToast({ title: msg, icon: 'none' })
      }
    },
    switchLevel(level) {
      this.currentLevel = level
      this.loadTeam()
    }
  }
}
</script>

<style scoped>
.team-page { background: #f5f5f5; min-height: 100vh; }
.overview-card { background: linear-gradient(135deg, #409eff, #67c23a); margin: 12px; border-radius: 12px; padding: 20px; display: flex; }
.overview-item { flex: 1; text-align: center; }
.ov-value { font-size: 22px; font-weight: bold; color: #fff; display: block; }
.ov-label { font-size: 12px; color: rgba(255,255,255,0.8); display: block; margin-top: 4px; }
.level-tabs { display: flex; background: #fff; margin: 0 12px; border-radius: 12px 12px 0 0; overflow: hidden; }
.tab { flex: 1; text-align: center; padding: 12px 0; font-size: 13px; color: #666; border-bottom: 2px solid transparent; }
.tab.active { color: #409eff; font-weight: bold; border-bottom-color: #409eff; }
.member-list { background: #fff; margin: 0 12px 12px; border-radius: 0 0 12px 12px; padding: 0 16px; }
.member-item { display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #f5f5f5; }
.member-item:last-child { border-bottom: none; }
.member-avatar { width: 40px; height: 40px; border-radius: 50%; background: #409eff; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.avatar-text { color: #fff; font-size: 16px; font-weight: bold; }
.member-info { flex: 1; margin-left: 12px; }
.member-name { font-size: 14px; font-weight: 500; display: block; }
.member-phone { font-size: 12px; color: #999; display: block; margin-top: 2px; }
.member-stats { text-align: right; }
.stats-value { font-size: 14px; font-weight: bold; color: #f56c6c; display: block; }
.stats-label { font-size: 11px; color: #ccc; display: block; }
.empty { text-align: center; padding: 40px 0; color: #999; }
</style>
