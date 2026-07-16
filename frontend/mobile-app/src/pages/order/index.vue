<template>
  <view class="order-page">
    <!-- 状态Tab -->
    <view class="status-tabs">
      <view class="tab" :class="{ active: activeTab === '' }" @click="switchTab('')">全部</view>
      <view class="tab" :class="{ active: activeTab === 'pending' }" @click="switchTab('pending')">待付款</view>
      <view class="tab" :class="{ active: activeTab === 'paid' }" @click="switchTab('paid')">待发货</view>
      <view class="tab" :class="{ active: activeTab === 'shipped' }" @click="switchTab('shipped')">待收货</view>
      <view class="tab" :class="{ active: activeTab === 'completed' }" @click="switchTab('completed')">已完成</view>
    </view>

    <!-- 订单列表 -->
    <view class="order-list" v-if="orders.length > 0">
      <view class="order-card" v-for="order in orders" :key="order.id" @click="goDetail(order)">
        <view class="order-header">
          <text class="order-no">{{ order.order_no }}</text>
          <text class="order-status" :class="'st-' + order.status">{{ statusLabels[order.status] || order.status }}</text>
        </view>
        <view class="order-goods">
          <view class="goods-row" v-for="(item, idx) in (order.items || []).slice(0, 3)" :key="idx">
            <text class="goods-name">{{ item.product_name }}</text>
            <view class="goods-right">
              <text class="goods-price">¥{{ item.unit_price }}</text>
              <text class="goods-qty">x{{ item.quantity }}</text>
            </view>
          </view>
          <text class="more-goods" v-if="(order.items || []).length > 3">...共{{ order.items.length }}件商品</text>
        </view>
        <view class="order-footer">
          <text class="order-total">合计: <text class="total-price">¥{{ order.actual_amount }}</text></text>
          <view class="order-actions">
            <button class="mini-btn" v-if="order.status === 'pending'" @click.stop="goPay(order)">去支付</button>
            <button class="mini-btn outline" v-if="order.status === 'pending' || order.status === 'paid'" @click.stop="cancelOrder(order)">取消</button>
            <button class="mini-btn" v-if="order.status === 'shipped'" @click.stop="confirmReceive(order)">确认收货</button>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-else-if="!loading">
      <text class="empty-icon">📋</text>
      <text class="empty-text">暂无订单</text>
      <button class="go-shop-btn" @click="goMall">去购物</button>
    </view>

    <!-- 加载状态 -->
    <view class="loading-tip" v-if="loading">
      <text>加载中...</text>
    </view>
  </view>
</template>

<script>
import { getOrderList, cancelOrder as cancelOrderApi, confirmReceive as confirmReceiveApi } from '../../api/index'

export default {
  data() {
    return {
      activeTab: '',
      orders: [],
      loading: false,
      page: 1,
      statusLabels: { pending: '待付款', paid: '待发货', shipped: '待收货', completed: '已完成', cancelled: '已取消' }
    }
  },
  onShow() {
    this.page = 1
    this.loadOrders()
  },
  onPullDownRefresh() {
    this.page = 1
    this.loadOrders().then(() => uni.stopPullDownRefresh())
  },
  onReachBottom() {
    this.page++
    this.loadOrders()
  },
  methods: {
    switchTab(tab) {
      this.activeTab = tab
      this.page = 1
      this.loadOrders()
    },
    async loadOrders() {
      const token = uni.getStorageSync('token')
      if (!token) { uni.navigateTo({ url: '/pages/login/index' }); return }
      this.loading = true
      try {
        const params = { page: this.page, size: 20 }
        if (this.activeTab) params.status = this.activeTab
        const res = await getOrderList(params)
        const newOrders = res.orders || []
        if (this.page === 1) {
          this.orders = newOrders
        } else {
          this.orders.push(...newOrders)
        }
      } catch(e) {
        const msg = e.message === '未登录' ? '请先登录' : '加载失败'
        uni.showToast({ title: msg, icon: 'none' })
      } finally {
        this.loading = false
      }
    },
    goDetail(order) {
      uni.navigateTo({ url: `/pages/order/detail?id=${order.id}` })
    },
    goPay(order) {
      uni.navigateTo({ url: `/pages/pay/index?order_id=${order.id}` })
    },
    async cancelOrder(order) {
      uni.showModal({ title: '提示', content: '确定取消该订单吗？', success: async (res) => {
        if (res.confirm) {
          try {
            await cancelOrderApi(order.id)
            uni.showToast({ title: '已取消', icon: 'success' })
            this.page = 1; this.loadOrders()
          } catch(e) { uni.showToast({ title: e.message || '取消失败', icon: 'none' }) }
        }
      }})
    },
    async confirmReceive(order) {
      uni.showModal({ title: '提示', content: '确认已收到商品？', success: async (res) => {
        if (res.confirm) {
          try {
            await confirmReceiveApi(order.id)
            uni.showToast({ title: '已确认', icon: 'success' })
            this.page = 1; this.loadOrders()
          } catch(e) { uni.showToast({ title: e.message || '操作失败', icon: 'none' }) }
        }
      }})
    },
    goMall() {
      uni.switchTab({ url: '/pages/mall/index' })
    }
  }
}
</script>

<style scoped>
.order-page { background: #f5f5f5; min-height: 100vh; }
.status-tabs { display: flex; background: #fff; position: sticky; top: 0; z-index: 10; }
.tab { flex: 1; text-align: center; padding: 12px 0; font-size: 14px; color: #666; position: relative; }
.tab.active { color: #409eff; font-weight: bold; }
.tab.active::after { content: ''; position: absolute; bottom: 0; left: 30%; right: 30%; height: 2px; background: #409eff; border-radius: 1px; }
.order-list { padding: 10px; }
.order-card { background: #fff; border-radius: 10px; margin-bottom: 10px; padding: 12px; }
.order-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.order-no { font-size: 13px; color: #999; }
.order-status { font-size: 13px; font-weight: bold; }
.st-pending { color: #ffa500; }
.st-paid { color: #409eff; }
.st-shipped { color: #67c23a; }
.st-completed { color: #52c41a; }
.st-cancelled { color: #909399; }
.goods-row { display: flex; justify-content: space-between; align-items: center; padding: 4px 0; }
.goods-name { font-size: 14px; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.goods-right { display: flex; gap: 8px; flex-shrink: 0; }
.goods-price { font-size: 13px; color: #666; }
.goods-qty { font-size: 13px; color: #999; }
.more-goods { font-size: 12px; color: #999; display: block; margin-top: 4px; }
.order-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; padding-top: 10px; border-top: 1px solid #f5f5f5; }
.order-total { font-size: 14px; color: #333; }
.total-price { color: #f56c6c; font-weight: bold; }
.order-actions { display: flex; gap: 8px; }
.mini-btn { padding: 5px 14px; border-radius: 15px; font-size: 12px; background: #f56c6c; color: #fff; border: none; }
.mini-btn.outline { background: #fff; color: #666; border: 1px solid #ddd; }
.empty-state { text-align: center; padding: 80px 0; }
.empty-icon { font-size: 60px; display: block; }
.empty-text { font-size: 15px; color: #999; display: block; margin: 15px 0; }
.go-shop-btn { background: #409eff; color: #fff; border: none; border-radius: 20px; padding: 10px 40px; font-size: 14px; }
.loading-tip { text-align: center; padding: 15px; color: #999; font-size: 13px; }
</style>
