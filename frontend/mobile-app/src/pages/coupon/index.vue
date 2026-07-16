<template>
  <view class="coupon-page">
    <!-- 余额卡片 -->
    <view class="balance-card">
      <text class="balance-label">消费券余额</text>
      <text class="balance-value">¥{{ balance || '0.00' }}</text>
      <text class="balance-tip">可在商城消费时抵扣</text>
    </view>

    <!-- 积分兑换入口 -->
    <view class="exchange-card" @click="goExchange">
      <view class="exchange-left">
        <text class="exchange-title">积分兑换消费券</text>
        <text class="exchange-desc">将增值积分兑换为消费券</text>
      </view>
      <view class="exchange-btn">去兑换 ></view>
    </view>

    <!-- 消费券明细 -->
    <view class="list-section">
      <text class="section-title">消费券明细</text>
      <view class="record-list">
        <view class="record-item" v-for="item in records" :key="item.id">
          <view class="record-left">
            <text class="record-title">{{ item.title }}</text>
            <text class="record-time">{{ item.created_at }}</text>
          </view>
          <text class="record-amount" :class="item.type === 'income' ? 'green' : 'red'">
            {{ item.type === 'income' ? '+' : '-' }}¥{{ item.amount }}
          </text>
        </view>
        <view class="empty" v-if="records.length === 0">
          <text>暂无消费券记录</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { getMyCoupons } from '../../api/index'

export default {
  data() {
    return {
      balance: '0.00',
      records: []
    }
  },
  onLoad() { this.loadData() },
  methods: {
    async loadData() {
      try {
        const res = await getMyCoupons()
        this.balance = res.total_balance || '0.00'
        this.records = res.records || []
      } catch (e) {
        const msg = e.message === '未登录' ? '请先登录' : '加载失败'
        uni.showToast({ title: msg, icon: 'none' })
      }
    },
    goExchange() {
      uni.navigateTo({ url: '/pages/wallet/index' })
    }
  }
}
</script>

<style scoped>
.coupon-page { background: #f5f5f5; min-height: 100vh; }
.balance-card { background: linear-gradient(135deg, #e6a23c, #f56c6c); margin: 12px; border-radius: 12px; padding: 24px; text-align: center; }
.balance-label { font-size: 14px; color: rgba(255,255,255,0.8); display: block; }
.balance-value { font-size: 36px; font-weight: bold; color: #fff; display: block; margin: 8px 0; }
.balance-tip { font-size: 12px; color: rgba(255,255,255,0.6); display: block; }
.exchange-card { background: #fff; margin: 0 12px 12px; border-radius: 12px; padding: 16px; display: flex; justify-content: space-between; align-items: center; }
.exchange-title { font-size: 15px; font-weight: bold; display: block; }
.exchange-desc { font-size: 12px; color: #999; display: block; margin-top: 4px; }
.exchange-btn { background: #409eff; color: #fff; padding: 8px 20px; border-radius: 20px; font-size: 13px; }
.list-section { background: #fff; margin: 0 12px; border-radius: 12px; padding: 16px; }
.section-title { font-size: 16px; font-weight: bold; display: block; margin-bottom: 12px; }
.record-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f5f5f5; }
.record-item:last-child { border-bottom: none; }
.record-title { font-size: 14px; display: block; }
.record-time { font-size: 12px; color: #ccc; display: block; margin-top: 2px; }
.record-amount { font-size: 16px; font-weight: bold; }
.record-amount.green { color: #67c23a; }
.record-amount.red { color: #f56c6c; }
.empty { text-align: center; padding: 40px 0; color: #999; }
</style>
