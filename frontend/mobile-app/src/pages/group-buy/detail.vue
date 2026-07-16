<template>
  <view class="detail-page">
    <view class="session-card">
      <view class="session-header">
        <text class="level-badge" :class="session.level">
          {{ session.level === 'svip' ? 'SVIP级团' : session.level === 'senior' ? '高级团' : '初级团' }}
        </text>
        <text class="session-price">¥{{ session.total_price }}</text>
      </view>
      <view class="session-info">
        <text>法库啤酒 6瓶/箱</text>
        <text>对应 {{ session.box_multiplier || '?' }} 箱</text>
      </view>
    </view>

    <view class="progress-section">
      <view class="progress-header">
        <text>参团进度</text>
        <text class="progress-text">{{ session.current_players || 0 }}/{{ session.total_players || 31 }} 人</text>
      </view>
      <view class="progress-bar-wrap">
        <view class="progress-bar-bg">
          <view class="progress-bar-fill" :style="{ width: progressPercent + '%' }"></view>
        </view>
        <view class="avatars">
          <view class="avatar-dot" v-for="i in Math.min(session.current_players || 0, 31)" :key="i"
            :style="{ background: i <= 30 ? '#409eff' : '#f56c6c' }">
          </view>
        </view>
      </view>
      <view class="progress-legend">
        <view class="legend-item"><view class="dot blue"></view><text>拼失败(30人)</text></view>
        <view class="legend-item"><view class="dot red"></view><text>拼中(1人)</text></view>
      </view>
    </view>

    <view class="rules-section">
      <text class="section-title">拼团规则</text>
      <view class="rule-item">
        <text class="rule-label">成团机制</text>
        <text class="rule-value">31人参与, 仅1人拼中, 30人拼失败</text>
      </view>
      <view class="rule-item">
        <text class="rule-label">拼中权益</text>
        <text class="rule-value">商品权益10% + 贡献值20% + 增值积分20%</text>
      </view>
      <view class="rule-item">
        <text class="rule-label">拼失败保障</text>
        <text class="rule-value">本金全额退回 + 广告补贴0.7% + 推荐人补贴0.1%</text>
      </view>
      <view class="rule-item">
        <text class="rule-label">限购规则</text>
        <text class="rule-value">单ID单组最多参与5单, 单日无场次上限</text>
      </view>
    </view>

    <view class="calc-section">
      <text class="section-title">收益测算</text>
      <view class="calc-grid">
        <view class="calc-item">
          <text class="calc-label">拼中商品权益</text>
          <text class="calc-value green">¥{{ (session.total_price * 0.1).toFixed(2) }}</text>
        </view>
        <view class="calc-item">
          <text class="calc-label">拼中贡献值</text>
          <text class="calc-value blue">{{ (session.total_price * 0.2 * 10 * 0.5).toFixed(0) }}</text>
        </view>
        <view class="calc-item">
          <text class="calc-label">拼中积分</text>
          <text class="calc-value blue">{{ (session.total_price * 0.2).toFixed(2) }}</text>
        </view>
        <view class="calc-item">
          <text class="calc-label">失败广告补贴(每人)</text>
          <text class="calc-value orange">¥{{ (session.total_price * 0.007).toFixed(2) }}</text>
        </view>
        <view class="calc-item">
          <text class="calc-label">失败推荐补贴(每人)</text>
          <text class="calc-value orange">¥{{ (session.total_price * 0.001).toFixed(2) }}</text>
        </view>
      </view>
    </view>

    <view class="bottom-bar">
      <view class="bar-info">
        <text>参团金额</text>
        <text class="bar-price">¥{{ session.total_price || '---' }}</text>
      </view>
      <button class="join-btn" :disabled="!canJoin" @click="handleJoin">
        {{ joinText }}
      </button>
    </view>
  </view>
</template>

<script>
import { getSessions, joinGroupBuy } from '../../api/index'

export default {
  data() {
    return {
      session: {},
      canJoin: true,
      joinText: '立即参团',
      joining: false,
    }
  },
  computed: {
    progressPercent() {
      const total = this.session.total_players || 31
      const current = this.session.current_players || 0
      return Math.min((current / total) * 100, 100)
    }
  },
  onLoad(options) {
    if (options.id) { this.loadSession(options.id) }
  },
  methods: {
    async loadSession(id) {
      try {
        const res = await getSessions()
        const list = res.items || []
        this.session = list.find(s => s.id == id) || { id, total_price: 288, total_players: 31, current_players: 0, level: 'junior', box_multiplier: 1 }
      } catch (e) { uni.showToast({ title: '加载失败', icon: 'none' }) }
    },
    async handleJoin() {
      if (this.joining) return
      const token = uni.getStorageSync('token')
      if (!token) { uni.navigateTo({ url: '/pages/login/index' }); return }
      uni.showModal({
        title: '确认参团',
        content: `确定参与${this.session.level === 'svip' ? 'SVIP团' : this.session.level === 'senior' ? '高级团' : '初级团'}吗？\n参团金额: ¥${this.session.total_price}`,
        success: async (res) => {
          if (res.confirm) {
            this.joining = true
            this.joinText = '参团中...'
            try {
              const result = await joinGroupBuy(this.session.id)
              if (result.code === 0 || result.success) {
                uni.showToast({ title: '参团成功!', icon: 'success' })
                this.canJoin = false
                this.joinText = '已参团'
                this.loadSession(this.session.id)
              }
            } catch (e) { uni.showToast({ title: e.message || '参团失败', icon: 'none' }) }
            finally { this.joining = false; if (this.canJoin) this.joinText = '立即参团' }
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.detail-page { padding-bottom: 80px; background: #f5f5f5; }
.session-card { background: #fff; margin: 12px; border-radius: 12px; padding: 16px; }
.session-header { display: flex; justify-content: space-between; align-items: center; }
.level-badge { padding: 4px 12px; border-radius: 20px; color: #fff; font-size: 13px; font-weight: bold; }
.level-badge.junior { background: #909399; }
.level-badge.senior { background: #e6a23c; }
.level-badge.svip { background: linear-gradient(135deg, #f56c6c, #e6a23c); }
.session-price { font-size: 28px; font-weight: bold; color: #f56c6c; }
.session-info { margin-top: 10px; display: flex; gap: 15px; }
.session-info text { font-size: 13px; color: #666; }
.progress-section { background: #fff; margin: 0 12px; border-radius: 12px; padding: 16px; }
.progress-header { display: flex; justify-content: space-between; margin-bottom: 10px; }
.progress-header text:first-child { font-weight: bold; }
.progress-text { color: #409eff; font-weight: bold; }
.progress-bar-bg { height: 10px; background: #eee; border-radius: 5px; overflow: hidden; }
.progress-bar-fill { height: 100%; background: linear-gradient(90deg, #409eff, #67c23a); border-radius: 5px; transition: width 0.5s; }
.avatars { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 10px; }
.avatar-dot { width: 16px; height: 16px; border-radius: 50%; }
.progress-legend { display: flex; gap: 20px; margin-top: 10px; }
.legend-item { display: flex; align-items: center; gap: 5px; }
.dot { width: 10px; height: 10px; border-radius: 50%; }
.dot.blue { background: #409eff; }
.dot.red { background: #f56c6c; }
.legend-item text { font-size: 12px; color: #999; }
.rules-section, .calc-section { background: #fff; margin: 12px; border-radius: 12px; padding: 16px; }
.section-title { font-size: 16px; font-weight: bold; display: block; margin-bottom: 12px; }
.rule-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
.rule-label { font-size: 13px; color: #666; }
.rule-value { font-size: 13px; color: #333; font-weight: 500; max-width: 60%; text-align: right; }
.calc-grid { display: flex; flex-wrap: wrap; gap: 10px; }
.calc-item { width: calc(50% - 5px); background: #f9f9f9; border-radius: 8px; padding: 10px; }
.calc-label { font-size: 12px; color: #999; display: block; }
.calc-value { font-size: 18px; font-weight: bold; display: block; margin-top: 4px; }
.calc-value.green { color: #67c23a; }
.calc-value.blue { color: #409eff; }
.calc-value.orange { color: #e6a23c; }
.bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #fff; padding: 10px 16px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 -2px 10px rgba(0,0,0,0.05); z-index: 100; }
.bar-info text:first-child { font-size: 12px; color: #999; display: block; }
.bar-price { font-size: 24px; font-weight: bold; color: #f56c6c; }
.join-btn { background: linear-gradient(135deg, #f56c6c, #e6a23c); color: #fff; border: none; border-radius: 25px; padding: 12px 40px; font-size: 16px; font-weight: bold; }
.join-btn[disabled] { opacity: 0.5; }
</style>
