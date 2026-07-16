<template>
  <view class="pay-page">
    <view class="pay-card">
      <text class="pay-label">支付金额</text>
      <text class="pay-amount">¥{{ amount.toFixed(2) }}</text>
      <text class="pay-order">订单号: {{ orderNo }}</text>
    </view>

    <view class="pay-methods">
      <view class="section-title">选择支付方式</view>
      <view class="method-item" :class="{ active: payMethod === 'balance' }" @click="payMethod = 'balance'">
        <text class="method-icon">💰</text>
        <view class="method-info">
          <text class="method-name">余额支付</text>
          <text class="method-desc">当前余额 ¥{{ balance.toFixed(2) }}</text>
        </view>
        <view class="radio" :class="{ checked: payMethod === 'balance' }"></view>
      </view>
      <view class="method-item" :class="{ active: payMethod === 'alipay' }" @click="payMethod = 'alipay'">
        <text class="method-icon">🅰️</text>
        <view class="method-info">
          <text class="method-name">支付宝</text>
          <text class="method-desc">模拟支付</text>
        </view>
        <view class="radio" :class="{ checked: payMethod === 'alipay' }"></view>
      </view>
      <view class="method-item" :class="{ active: payMethod === 'wechat' }" @click="payMethod = 'wechat'">
        <text class="method-icon">💬</text>
        <view class="method-info">
          <text class="method-name">微信支付</text>
          <text class="method-desc">模拟支付</text>
        </view>
        <view class="radio" :class="{ checked: payMethod === 'wechat' }"></view>
      </view>
    </view>

    <button class="pay-btn" @click="handlePay" :disabled="paying">
      {{ paying ? '支付中...' : '确认支付' }}
    </button>

    <!-- 支付结果弹窗 -->
    <view class="result-mask" v-if="showResult">
      <view class="result-card">
        <text class="result-icon">{{ paySuccess ? '✅' : '❌' }}</text>
        <text class="result-title">{{ paySuccess ? '支付成功' : '支付失败' }}</text>
        <text class="result-amount">¥{{ amount.toFixed(2) }}</text>
        <text class="result-desc" v-if="!paySuccess">{{ payError }}</text>
        <button class="result-btn" @click="afterPay">{{ paySuccess ? '查看订单' : '返回' }}</button>
      </view>
    </view>
  </view>
</template>

<script>
import { getOrderDetail, getWallet } from '../../api/index'

export default {
  data() {
    return {
      orderId: null,
      orderNo: '',
      amount: 0,
      balance: 0,
      payMethod: 'balance',
      paying: false,
      showResult: false,
      paySuccess: false,
      payError: ''
    }
  },
  onLoad(options) {
    this.orderId = options.order_id
    this.loadOrderInfo()
    this.loadBalance()
  },
  methods: {
    async loadOrderInfo() {
      try {
        const res = await getOrderDetail(this.orderId)
        this.orderNo = res.order_no
        this.amount = res.actual_amount
      } catch(e) {}
    },
    async loadBalance() {
      try {
        const res = await getWallet()
        this.balance = res.balance || 0
      } catch(e) {}
    },
    handlePay() {
      if (this.payMethod === 'balance' && this.balance < this.amount) {
        this.payError = '余额不足'
        this.paySuccess = false
        this.showResult = true
        return
      }
      this.paying = true
      // 模拟支付过程
      setTimeout(() => {
        this.paying = false
        this.paySuccess = true
        this.showResult = true
      }, 1500)
    },
    afterPay() {
      this.showResult = false
      if (this.paySuccess) {
        uni.redirectTo({ url: `/pages/order/detail?id=${this.orderId}` })
      } else {
        uni.navigateBack()
      }
    }
  }
}
</script>

<style scoped>
.pay-page { background: #f5f5f5; min-height: 100vh; padding: 15px; }
.pay-card { background: #fff; border-radius: 12px; padding: 30px; text-align: center; margin-bottom: 15px; }
.pay-label { font-size: 14px; color: #999; display: block; }
.pay-amount { font-size: 36px; font-weight: bold; color: #f56c6c; display: block; margin: 10px 0; }
.pay-order { font-size: 13px; color: #999; display: block; }
.pay-methods { background: #fff; border-radius: 12px; padding: 15px; margin-bottom: 20px; }
.section-title { font-size: 15px; font-weight: bold; margin-bottom: 12px; }
.method-item { display: flex; align-items: center; padding: 14px 0; border-bottom: 1px solid #f5f5f5; }
.method-item:last-child { border-bottom: none; }
.method-icon { font-size: 24px; margin-right: 12px; }
.method-info { flex: 1; }
.method-name { font-size: 15px; display: block; }
.method-desc { font-size: 12px; color: #999; display: block; margin-top: 2px; }
.radio { width: 20px; height: 20px; border: 2px solid #ddd; border-radius: 50%; }
.radio.checked { border-color: #409eff; background: #409eff; position: relative; }
.radio.checked::after { content: ''; position: absolute; top: 4px; left: 4px; width: 8px; height: 8px; background: #fff; border-radius: 50%; }
.pay-btn { background: #409eff; color: #fff; border: none; border-radius: 25px; padding: 14px 0; font-size: 16px; font-weight: bold; }
.pay-btn[disabled] { background: #ccc; }
.result-mask { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 999; }
.result-card { background: #fff; border-radius: 16px; padding: 30px; width: 80%; text-align: center; }
.result-icon { font-size: 50px; display: block; }
.result-title { font-size: 20px; font-weight: bold; display: block; margin: 10px 0; }
.result-amount { font-size: 24px; color: #f56c6c; font-weight: bold; display: block; margin-bottom: 10px; }
.result-desc { font-size: 14px; color: #f56c6c; display: block; margin-bottom: 15px; }
.result-btn { background: #409eff; color: #fff; border: none; border-radius: 20px; padding: 10px 40px; font-size: 15px; margin-top: 10px; }
</style>
