<template>
  <view class="wallet-page">
    <!-- 资产总览 -->
    <view class="asset-overview">
      <view class="asset-item">
        <text class="asset-label">余额</text>
        <text class="asset-value">¥{{ wallet.balance?.toFixed(2) || '0.00' }}</text>
      </view>
      <view class="asset-item">
        <text class="asset-label">消费券</text>
        <text class="asset-value">¥{{ wallet.coupon_balance?.toFixed(2) || '0.00' }}</text>
      </view>
      <view class="asset-item">
        <text class="asset-label">贡献值</text>
        <text class="asset-value">{{ wallet.contribution_value?.toFixed(2) || '0.00' }}</text>
      </view>
      <view class="asset-item">
        <text class="asset-label">增值积分</text>
        <text class="asset-value">{{ wallet.points?.toFixed(2) || '0.00' }}</text>
      </view>
    </view>

    <!-- 功能列表 -->
    <view class="func-list">
      <view class="func-item" @click="goTo('/pages/order/index')">
        <text>我的拼团订单</text>
        <text class="arrow">></text>
      </view>
      <view class="func-item" @click="showPointsPool">
        <text>积分池状态</text>
        <text class="arrow">></text>
      </view>
      <view class="func-item" @click="showConvertDialog">
        <text>积分兑换消费券</text>
        <text class="arrow">></text>
      </view>
      <view class="func-item" @click="goTo('/pages/coupon/index')">
        <text>我的消费券</text>
        <text class="arrow">></text>
      </view>
      <view class="func-item" @click="goTo('/pages/contribution/index')">
        <text>贡献值明细</text>
        <text class="arrow">></text>
      </view>
      <view class="func-item" @click="showBalanceLog">
        <text>余额流水</text>
        <text class="arrow">></text>
      </view>
    </view>

    <!-- 积分池弹窗 -->
    <view class="dialog" v-if="showPool" @click="showPool = false">
      <view class="dialog-content" @click.stop>
        <text class="dialog-title">积分池状态</text>
        <text>总发行量: {{ poolInfo.total_supply?.toLocaleString() }}</text>
        <text>已发放: {{ poolInfo.total_issued?.toLocaleString() }}</text>
        <text>已通缩: {{ poolInfo.total_deflated?.toLocaleString() }}</text>
        <text>当前单价: ¥{{ poolInfo.current_unit_price?.toFixed(4) }}</text>
        <text>剩余可发: {{ poolInfo.remaining?.toLocaleString() }}</text>
      </view>
    </view>
  </view>
</template>

<script>
import { getWallet, getPointsPool, convertPoints } from '../../api/index'

export default {
  data() {
    return {
      wallet: {},
      poolInfo: {},
      showPool: false,
    }
  },
  onShow() {
    this.loadWallet()
  },
  methods: {
    async loadWallet() {
      try {
        this.wallet = await getWallet()
      } catch (e) {
        const msg = e.message === '未登录' ? '请先登录' : '加载失败'
        uni.showToast({ title: msg, icon: 'none' })
      }
    },
    async showPointsPool() {
      try {
        this.poolInfo = await getPointsPool()
        this.showPool = true
      } catch (e) {
        const msg = e.message === '未登录' ? '请先登录' : '加载失败'
        uni.showToast({ title: msg, icon: 'none' })
      }
    },
    async showConvertDialog() {
      uni.showModal({
        title: '积分兑换消费券',
        editable: true,
        placeholderText: '请输入兑换积分数量',
        success: (res) => {
          if (res.confirm && res.content) {
            const points = parseFloat(res.content)
            if (isNaN(points) || points <= 0) {
              uni.showToast({ title: '请输入有效数量', icon: 'none' })
              return
            }
            convertPoints(points).then(() => {
              uni.showToast({ title: '兑换成功', icon: 'success' })
              this.loadWallet()
            }).catch(() => {
              uni.showToast({ title: '兑换失败，请先登录', icon: 'none' })
            })
          }
        }
      })
    },
    showBalanceLog() {
      uni.showToast({ title: '余额流水开发中', icon: 'none' })
    },
    goTo(url) {
      uni.navigateTo({ url })
    }
  }
}
</script>

<style scoped>
.wallet-page { padding: 0; }
.asset-overview { background: linear-gradient(135deg, #409eff, #67c23a); padding: 30px 20px; display: flex; flex-wrap: wrap; }
.asset-item { width: 50%; padding: 10px 0; color: #fff; }
.asset-label { font-size: 13px; opacity: 0.8; display: block; }
.asset-value { font-size: 22px; font-weight: bold; display: block; margin-top: 5px; }
.func-list { background: #fff; margin-top: 12px; }
.func-item { display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; border-bottom: 1px solid #f5f5f5; }
.arrow { color: #ccc; }
.dialog { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 999; }
.dialog-content { background: #fff; border-radius: 12px; padding: 20px; width: 80%; }
.dialog-title { font-size: 18px; font-weight: bold; display: block; margin-bottom: 15px; }
</style>
