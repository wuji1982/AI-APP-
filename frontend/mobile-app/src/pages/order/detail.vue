<template>
  <view class="order-detail-page">
    <!-- 订单状态 -->
    <view class="status-bar" :class="'status-' + order.status">
      <text class="status-icon">{{ statusIcon }}</text>
      <text class="status-text">{{ statusText }}</text>
    </view>

    <!-- 收货地址 -->
    <view class="section-card">
      <view class="section-title">收货信息</view>
      <text class="addr-text">{{ order.address || '无' }}</text>
    </view>

    <!-- 商品列表 -->
    <view class="section-card">
      <view class="section-title">商品信息</view>
      <view class="goods-item" v-for="(item, idx) in order.items" :key="idx">
        <view class="goods-info">
          <text class="goods-name">{{ item.product_name }}</text>
          <view class="goods-meta">
            <text class="goods-price">¥{{ item.unit_price }}</text>
            <text class="goods-qty">x{{ item.quantity }}</text>
          </view>
        </view>
        <text class="goods-subtotal">¥{{ item.subtotal }}</text>
      </view>
    </view>

    <!-- 金额明细 -->
    <view class="section-card">
      <view class="amount-row">
        <text>商品总额</text>
        <text>¥{{ order.total_amount?.toFixed(2) }}</text>
      </view>
      <view class="amount-row" v-if="order.coupon_deduct > 0">
        <text>消费券抵扣</text>
        <text class="green">-¥{{ order.coupon_deduct?.toFixed(2) }}</text>
      </view>
      <view class="amount-row highlight">
        <text>实付金额</text>
        <text class="red">¥{{ order.actual_amount?.toFixed(2) }}</text>
      </view>
    </view>

    <!-- 订单信息 -->
    <view class="section-card">
      <view class="section-title">订单信息</view>
      <view class="info-row">
        <text class="label">订单编号</text>
        <text class="value" @click="copyOrderNo">{{ order.order_no }} 复制</text>
      </view>
      <view class="info-row">
        <text class="label">下单时间</text>
        <text class="value">{{ formatTime(order.created_at) }}</text>
      </view>
      <view class="info-row" v-if="order.paid_at">
        <text class="label">支付时间</text>
        <text class="value">{{ formatTime(order.paid_at) }}</text>
      </view>
      <view class="info-row" v-if="order.completed_at">
        <text class="label">完成时间</text>
        <text class="value">{{ formatTime(order.completed_at) }}</text>
      </view>
      <view class="info-row" v-if="order.remark">
        <text class="label">备注</text>
        <text class="value">{{ order.remark }}</text>
      </view>
    </view>

    <!-- 底部操作 -->
    <view class="bottom-actions" v-if="order.status">
      <button class="action-btn cancel" v-if="order.status === 'pending' || order.status === 'paid'" @click="handleCancel">取消订单</button>
      <button class="action-btn pay" v-if="order.status === 'pending'" @click="handlePay">去支付</button>
      <button class="action-btn confirm" v-if="order.status === 'shipped'" @click="handleConfirm">确认收货</button>
    </view>
  </view>
</template>

<script>
import { getOrderDetail, cancelOrder, confirmReceive } from '../../api/index'

export default {
  data() {
    return { order: {} }
  },
  computed: {
    statusText() {
      const map = { pending: '待付款', paid: '待发货', shipped: '待收货', completed: '已完成', cancelled: '已取消' }
      return map[this.order.status] || '未知'
    },
    statusIcon() {
      const map = { pending: '💰', paid: '📦', shipped: '🚚', completed: '✅', cancelled: '❌' }
      return map[this.order.status] || '📋'
    }
  },
  onLoad(options) {
    if (options.id) this.loadOrder(options.id)
  },
  methods: {
    async loadOrder(id) {
      try {
        this.order = await getOrderDetail(id)
      } catch(e) {
        uni.showToast({ title: '加载失败', icon: 'none' })
      }
    },
    copyOrderNo() {
      if (!this.order.order_no) return
      uni.setClipboardData({ data: this.order.order_no, success: () => uni.showToast({ title: '已复制', icon: 'success' }) })
    },
    handlePay() {
      uni.redirectTo({ url: `/pages/pay/index?order_id=${this.order.id}` })
    },
    async handleCancel() {
      uni.showModal({ title: '提示', content: '确定取消该订单吗？', success: async (res) => {
        if (res.confirm) {
          try {
            await cancelOrder(this.order.id)
            uni.showToast({ title: '已取消', icon: 'success' })
            this.loadOrder(this.order.id)
          } catch(e) { uni.showToast({ title: e.message || '取消失败', icon: 'none' }) }
        }
      }})
    },
    async handleConfirm() {
      uni.showModal({ title: '提示', content: '确认已收到商品？', success: async (res) => {
        if (res.confirm) {
          try {
            await confirmReceive(this.order.id)
            uni.showToast({ title: '已确认收货', icon: 'success' })
            this.loadOrder(this.order.id)
          } catch(e) { uni.showToast({ title: e.message || '操作失败', icon: 'none' }) }
        }
      }})
    },
    formatTime(t) {
      if (!t) return ''
      return typeof t === 'string' ? t.replace('T', ' ').substring(0, 19) : t
    }
  }
}
</script>

<style scoped>
.order-detail-page { background: #f5f5f5; min-height: 100vh; padding-bottom: 70px; }
.status-bar { padding: 25px 20px; color: #fff; display: flex; align-items: center; gap: 10px; }
.status-pending { background: linear-gradient(135deg, #ffa500, #ff6b35); }
.status-paid { background: linear-gradient(135deg, #409eff, #67c23a); }
.status-shipped { background: linear-gradient(135deg, #67c23a, #409eff); }
.status-completed { background: linear-gradient(135deg, #67c23a, #52c41a); }
.status-cancelled { background: linear-gradient(135deg, #909399, #606266); }
.status-icon { font-size: 30px; }
.status-text { font-size: 20px; font-weight: bold; }
.section-card { background: #fff; margin: 10px; border-radius: 10px; padding: 15px; }
.section-title { font-size: 15px; font-weight: bold; margin-bottom: 10px; }
.addr-text { font-size: 14px; color: #666; line-height: 1.5; }
.goods-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
.goods-item:last-child { border-bottom: none; }
.goods-name { font-size: 14px; flex: 1; }
.goods-meta { display: flex; gap: 10px; margin-top: 4px; }
.goods-price { font-size: 13px; color: #666; }
.goods-qty { font-size: 13px; color: #999; }
.goods-subtotal { font-size: 14px; font-weight: bold; color: #333; }
.amount-row { display: flex; justify-content: space-between; padding: 6px 0; font-size: 14px; color: #666; }
.amount-row.highlight { border-top: 1px solid #f5f5f5; padding-top: 10px; margin-top: 5px; }
.green { color: #67c23a; }
.red { color: #f56c6c; font-weight: bold; font-size: 16px; }
.info-row { display: flex; justify-content: space-between; padding: 6px 0; font-size: 13px; }
.label { color: #999; }
.value { color: #333; }
.bottom-actions { position: fixed; bottom: 0; left: 0; right: 0; background: #fff; display: flex; justify-content: flex-end; gap: 10px; padding: 10px 15px; box-shadow: 0 -2px 8px rgba(0,0,0,0.08); }
.action-btn { padding: 8px 20px; border-radius: 20px; font-size: 14px; border: none; }
.action-btn.cancel { background: #f5f5f5; color: #666; }
.action-btn.pay { background: #f56c6c; color: #fff; }
.action-btn.confirm { background: #409eff; color: #fff; }
</style>
