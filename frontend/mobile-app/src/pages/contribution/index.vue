<template>
  <view class="contrib-page">
    <!-- 顶部汇总 -->
    <view class="summary-card">
      <view class="summary-item">
        <text class="summary-value">{{ totalContribution || 0 }}</text>
        <text class="summary-label">累计贡献值</text>
      </view>
      <view class="summary-divider"></view>
      <view class="summary-item">
        <text class="summary-value">{{ weeklyCoupon || '0.00' }}</text>
        <text class="summary-label">本周消费券</text>
      </view>
    </view>

    <!-- 规则说明 -->
    <view class="rule-card">
      <text class="rule-title">递减兑换规则</text>
      <text class="rule-desc">当周消费券 = 贡献值 × 日利率(0.05%) × 7</text>
      <text class="rule-desc">每周一自动结算到消费券余额</text>
    </view>

    <!-- 贡献值明细列表 -->
    <view class="list-section">
      <text class="section-title">贡献值明细</text>
      <view class="record-list">
        <view class="record-item" v-for="item in records" :key="item.id">
          <view class="record-left">
            <text class="record-role">{{ roleLabels[item.role] || item.role }}</text>
            <text class="record-source">{{ item.source_type }}</text>
          </view>
          <view class="record-right">
            <text class="record-value" :class="item.type === 'earn' ? 'green' : 'red'">
              {{ item.type === 'earn' ? '+' : '-' }}{{ item.amount }}
            </text>
            <text class="record-time">{{ item.created_at }}</text>
          </view>
        </view>
        <view class="empty" v-if="records.length === 0">
          <text>暂无贡献值记录</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { getMyContributions } from '../../api/index'

export default {
  data() {
    return {
      totalContribution: 0,
      weeklyCoupon: '0.00',
      records: [],
      roleLabels: {
        consumer: '消费者',
        merchant: '商家',
        referral_merchant: '推荐商家',
        referral_consumer: '推荐消费者',
        agent: '代理',
        platform: '平台'
      }
    }
  },
  onLoad() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const res = await getMyContributions()
        this.totalContribution = res.total_contribution || 0
        this.weeklyCoupon = res.weekly_coupon || '0.00'
        this.records = res.records || []
      } catch (e) {
        const msg = e.message === '未登录' ? '请先登录' : '加载失败'
        uni.showToast({ title: msg, icon: 'none' })
      }
    }
  }
}
</script>

<style scoped>
.contrib-page { background: #f5f5f5; min-height: 100vh; }
.summary-card { background: linear-gradient(135deg, #409eff, #67c23a); margin: 12px; border-radius: 12px; padding: 24px; display: flex; align-items: center; }
.summary-item { flex: 1; text-align: center; }
.summary-value { font-size: 28px; font-weight: bold; color: #fff; display: block; }
.summary-label { font-size: 13px; color: rgba(255,255,255,0.8); display: block; margin-top: 4px; }
.summary-divider { width: 1px; height: 40px; background: rgba(255,255,255,0.3); }
.rule-card { background: #fff; margin: 0 12px 12px; border-radius: 12px; padding: 16px; }
.rule-title { font-size: 14px; font-weight: bold; display: block; margin-bottom: 8px; }
.rule-desc { font-size: 12px; color: #999; display: block; line-height: 1.8; }
.list-section { background: #fff; margin: 0 12px; border-radius: 12px; padding: 16px; }
.section-title { font-size: 16px; font-weight: bold; display: block; margin-bottom: 12px; }
.record-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f5f5f5; }
.record-item:last-child { border-bottom: none; }
.record-left { }
.record-role { font-size: 14px; font-weight: 500; display: block; }
.record-source { font-size: 12px; color: #999; display: block; margin-top: 2px; }
.record-right { text-align: right; }
.record-value { font-size: 16px; font-weight: bold; display: block; }
.record-value.green { color: #67c23a; }
.record-value.red { color: #f56c6c; }
.record-time { font-size: 12px; color: #ccc; display: block; margin-top: 2px; }
.empty { text-align: center; padding: 40px 0; color: #999; }
</style>
