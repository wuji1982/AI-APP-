<template>
  <view class="store-page">
    <!-- 月份选择 -->
    <view class="month-bar">
      <text class="month-arrow" @click="prevMonth"><</text>
      <text class="month-text">{{ currentMonth }}</text>
      <text class="month-arrow" @click="nextMonth">></text>
    </view>

    <!-- 排名规则 -->
    <view class="rule-card">
      <text class="rule-title">门店阶梯分红规则</text>
      <view class="rule-items">
        <view class="rule-item"><text>3-5万</text><text class="rate">0.5%</text></view>
        <view class="rule-item"><text>5-10万</text><text class="rate">0.5%</text></view>
        <view class="rule-item"><text>10-50万</text><text class="rate">0.5%</text></view>
        <view class="rule-item"><text>50万+</text><text class="rate">1.0%</text></view>
      </view>
    </view>

    <!-- 排名列表 -->
    <view class="rank-list">
      <text class="section-title">门店排名</text>
      <view class="rank-item" v-for="(item, index) in rankings" :key="item.store_id">
        <view class="rank-badge" :class="'top' + (index + 1)" v-if="index < 3">
          <text>{{ index + 1 }}</text>
        </view>
        <view class="rank-num" v-else>
          <text>{{ index + 1 }}</text>
        </view>
        <view class="rank-info">
          <text class="rank-name">{{ item.store_name }}</text>
          <text class="rank-area">{{ item.province }} {{ item.city }}</text>
        </view>
        <view class="rank-stats">
          <text class="rank-amount">¥{{ item.monthly_sales }}</text>
          <text class="rank-dividend">分红 ¥{{ item.dividend_amount }}</text>
        </view>
      </view>
      <view class="empty" v-if="rankings.length === 0">
        <text>暂无排名数据</text>
      </view>
    </view>
  </view>
</template>

<script>
import { getStoreRanking } from '../../api/index'

export default {
  data() {
    return {
      currentMonth: '',
      year: 0,
      month: 0,
      rankings: []
    }
  },
  onLoad() {
    const now = new Date()
    this.year = now.getFullYear()
    this.month = now.getMonth() + 1
    this.updateMonthText()
    this.loadRanking()
  },
  methods: {
    updateMonthText() {
      this.currentMonth = `${this.year}年${this.month}月`
    },
    prevMonth() {
      this.month--
      if (this.month < 1) { this.month = 12; this.year-- }
      this.updateMonthText()
      this.loadRanking()
    },
    nextMonth() {
      this.month++
      if (this.month > 12) { this.month = 1; this.year++ }
      this.updateMonthText()
      this.loadRanking()
    },
    async loadRanking() {
      try {
        const ym = `${this.year}${String(this.month).padStart(2, '0')}`
        const res = await getStoreRanking(ym)
        this.rankings = res.items || res.rankings || []
      } catch (e) {
        const msg = e.message === '未登录' ? '请先登录' : '加载失败'
        uni.showToast({ title: msg, icon: 'none' })
      }
    }
  }
}
</script>

<style scoped>
.store-page { background: #f5f5f5; min-height: 100vh; }
.month-bar { background: #fff; display: flex; justify-content: center; align-items: center; padding: 12px; gap: 20px; }
.month-arrow { font-size: 20px; color: #409eff; font-weight: bold; padding: 0 10px; }
.month-text { font-size: 16px; font-weight: bold; }
.rule-card { background: #fff; margin: 12px; border-radius: 12px; padding: 16px; }
.rule-title { font-size: 14px; font-weight: bold; display: block; margin-bottom: 10px; }
.rule-items { display: flex; gap: 8px; }
.rule-item { flex: 1; text-align: center; background: #f9f9f9; border-radius: 8px; padding: 8px 4px; }
.rule-item text:first-child { font-size: 12px; color: #666; display: block; }
.rate { font-size: 14px; font-weight: bold; color: #f56c6c; display: block; margin-top: 2px; }
.rank-list { background: #fff; margin: 0 12px 12px; border-radius: 12px; padding: 16px; }
.section-title { font-size: 16px; font-weight: bold; display: block; margin-bottom: 12px; }
.rank-item { display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #f5f5f5; }
.rank-item:last-child { border-bottom: none; }
.rank-badge { width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.rank-badge text { color: #fff; font-size: 14px; font-weight: bold; }
.rank-badge.top1 { background: linear-gradient(135deg, #ffd700, #ffb300); }
.rank-badge.top2 { background: linear-gradient(135deg, #c0c0c0, #a0a0a0); }
.rank-badge.top3 { background: linear-gradient(135deg, #cd7f32, #b87333); }
.rank-num { width: 30px; text-align: center; flex-shrink: 0; }
.rank-num text { font-size: 14px; color: #999; }
.rank-info { flex: 1; margin-left: 12px; }
.rank-name { font-size: 14px; font-weight: 500; display: block; }
.rank-area { font-size: 12px; color: #999; display: block; margin-top: 2px; }
.rank-stats { text-align: right; }
.rank-amount { font-size: 14px; font-weight: bold; color: #333; display: block; }
.rank-dividend { font-size: 12px; color: #67c23a; display: block; margin-top: 2px; }
.empty { text-align: center; padding: 40px 0; color: #999; }
</style>
