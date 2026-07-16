<template>
  <view class="checkout-page">
    <!-- 收货地址 -->
    <view class="address-card" @click="chooseAddress">
      <view v-if="selectedAddress" class="addr-info">
        <view class="addr-top">
          <text class="addr-name">{{ selectedAddress.receiver_name }}</text>
          <text class="addr-phone">{{ selectedAddress.receiver_phone }}</text>
        </view>
        <text class="addr-detail">{{ selectedAddress.province }}{{ selectedAddress.city }}{{ selectedAddress.district }} {{ selectedAddress.detail }}</text>
      </view>
      <view v-else class="no-addr">
        <text>请选择收货地址</text>
      </view>
      <text class="addr-arrow">></text>
    </view>

    <!-- 商品列表 -->
    <view class="goods-section">
      <view class="goods-item" v-for="item in goodsList" :key="item.id || item.product_id">
        <image class="goods-img" :src="item.cover_image || item.cover || '/static/placeholder.png'" mode="aspectFill"></image>
        <view class="goods-info">
          <text class="goods-name">{{ item.product_name || item.name }}</text>
          <view class="goods-bottom">
            <text class="goods-price">¥{{ item.price || item.selling_price }}</text>
            <text class="goods-qty">x{{ item.quantity }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 备注 -->
    <view class="remark-section">
      <text class="remark-label">订单备注</text>
      <input class="remark-input" v-model="remark" placeholder="选填，请输入备注信息" />
    </view>

    <!-- 金额明细 -->
    <view class="amount-section">
      <view class="amount-row">
        <text>商品金额</text>
        <text>¥{{ totalAmount.toFixed(2) }}</text>
      </view>
      <view class="amount-row">
        <text>消费券抵扣</text>
        <text class="deduct">-¥{{ couponDeduct.toFixed(2) }}</text>
      </view>
      <view class="amount-row total-row">
        <text>实付金额</text>
        <text class="actual">¥{{ actualAmount.toFixed(2) }}</text>
      </view>
    </view>

    <!-- 提交订单 -->
    <view class="submit-bar">
      <view class="submit-total">
        <text>合计: </text>
        <text class="submit-price">¥{{ actualAmount.toFixed(2) }}</text>
      </view>
      <button class="submit-btn" @click="submitOrder" :disabled="submitting">
        {{ submitting ? '提交中...' : '提交订单' }}
      </button>
    </view>
  </view>
</template>

<script>
import { getCart, getAddresses, createOrder } from '../../api/index'

export default {
  data() {
    return {
      goodsList: [],
      selectedAddress: null,
      remark: '',
      couponDeduct: 0,
      submitting: false,
      source: '' // 'cart' or 'buy'
    }
  },
  computed: {
    totalAmount() {
      return this.goodsList.reduce((sum, i) => sum + (i.price || i.selling_price || 0) * (i.quantity || 1), 0)
    },
    actualAmount() {
      return Math.max(0, this.totalAmount - this.couponDeduct)
    }
  },
  onLoad(options) {
    this.source = options.source || 'cart'
    if (this.source === 'cart') {
      this.loadCartItems()
    }
    this.loadDefaultAddress()
  },
  methods: {
    async loadCartItems() {
      try {
        const res = await getCart()
        this.goodsList = (res.items || []).filter(i => i.selected && i.valid)
      } catch(e) {
        uni.showToast({ title: '加载失败', icon: 'none' })
      }
    },
    async loadDefaultAddress() {
      try {
        const res = await getAddresses()
        const addrs = res.items || []
        this.selectedAddress = addrs.find(a => a.is_default) || addrs[0] || null
      } catch(e) {}
    },
    chooseAddress() {
      uni.navigateTo({ url: '/pages/address/index?select=1' })
    },
    setSelectedAddress(addr) {
      this.selectedAddress = addr
    },
    async submitOrder() {
      if (!this.selectedAddress) {
        uni.showToast({ title: '请选择收货地址', icon: 'none' }); return
      }
      if (this.goodsList.length === 0) {
        uni.showToast({ title: '没有可结算的商品', icon: 'none' }); return
      }
      this.submitting = true
      try {
        const cartItemIds = this.goodsList.map(i => i.id).filter(Boolean)
        const res = await createOrder({
          address_id: this.selectedAddress.id,
          cart_item_ids: cartItemIds.length > 0 ? cartItemIds : null,
          remark: this.remark
        })
        uni.showToast({ title: '下单成功', icon: 'success' })
        setTimeout(() => {
          uni.redirectTo({ url: `/pages/pay/index?order_id=${res.data?.order_id || res.order_id}` })
        }, 1000)
      } catch(e) {
        uni.showToast({ title: e.message || '下单失败', icon: 'none' })
      } finally {
        this.submitting = false
      }
    }
  }
}
</script>

<style scoped>
.checkout-page { background: #f5f5f5; min-height: 100vh; padding-bottom: 70px; }
.address-card { background: #fff; margin: 10px; border-radius: 10px; padding: 15px; display: flex; align-items: center; }
.addr-info { flex: 1; }
.addr-top { display: flex; gap: 10px; margin-bottom: 5px; }
.addr-name { font-size: 15px; font-weight: bold; }
.addr-phone { font-size: 14px; color: #666; }
.addr-detail { font-size: 13px; color: #666; }
.no-addr { flex: 1; color: #999; font-size: 14px; }
.addr-arrow { color: #ccc; font-size: 18px; margin-left: 8px; }
.goods-section { background: #fff; margin: 0 10px 10px; border-radius: 10px; padding: 10px; }
.goods-item { display: flex; padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
.goods-item:last-child { border-bottom: none; }
.goods-img { width: 80px; height: 80px; border-radius: 8px; flex-shrink: 0; }
.goods-info { flex: 1; margin-left: 10px; display: flex; flex-direction: column; justify-content: space-between; }
.goods-name { font-size: 14px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.goods-bottom { display: flex; justify-content: space-between; align-items: center; }
.goods-price { font-size: 15px; font-weight: bold; color: #f56c6c; }
.goods-qty { font-size: 13px; color: #999; }
.remark-section { background: #fff; margin: 0 10px 10px; border-radius: 10px; padding: 12px 15px; display: flex; align-items: center; }
.remark-label { font-size: 14px; color: #333; margin-right: 10px; flex-shrink: 0; }
.remark-input { flex: 1; font-size: 14px; }
.amount-section { background: #fff; margin: 0 10px 10px; border-radius: 10px; padding: 15px; }
.amount-row { display: flex; justify-content: space-between; padding: 6px 0; font-size: 14px; color: #666; }
.deduct { color: #67c23a; }
.total-row { border-top: 1px solid #f5f5f5; padding-top: 10px; margin-top: 5px; }
.actual { color: #f56c6c; font-size: 18px; font-weight: bold; }
.submit-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #fff; display: flex; align-items: center; justify-content: space-between; padding: 10px 15px; box-shadow: 0 -2px 8px rgba(0,0,0,0.08); }
.submit-total { font-size: 14px; }
.submit-price { color: #f56c6c; font-size: 20px; font-weight: bold; }
.submit-btn { background: #f56c6c; color: #fff; border: none; border-radius: 22px; padding: 10px 30px; font-size: 15px; }
.submit-btn[disabled] { background: #ccc; }
</style>
