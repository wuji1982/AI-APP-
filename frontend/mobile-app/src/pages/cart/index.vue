<template>
  <view class="cart-page">
    <!-- 顶部标题栏 -->
    <view class="cart-header">
      <text class="header-title">购物车 ({{ cartItems.length }})</text>
      <text class="header-edit" @click="toggleEdit">{{ isEditing ? '完成' : '编辑' }}</text>
    </view>

    <!-- 购物车列表 -->
    <view class="cart-list" v-if="cartItems.length > 0">
      <view class="cart-item" v-for="item in cartItems" :key="item.id" :class="{ invalid: !item.valid }">
        <view class="check-box" @click="toggleSelect(item)">
          <text class="check-icon" :class="{ checked: item.selected }">{{ item.selected ? '✓' : '' }}</text>
        </view>
        <image class="item-img" :src="item.cover_image || '/static/placeholder.png'" mode="aspectFill" @click="goProduct(item)"></image>
        <view class="item-info" @click="goProduct(item)">
          <text class="item-name">{{ item.product_name }}</text>
          <text class="item-invalid" v-if="!item.valid">已失效</text>
          <view class="item-bottom">
            <text class="item-price">¥{{ item.price }}</text>
            <view class="qty-control">
              <text class="qty-btn" @click.stop="changeQty(item, -1)">-</text>
              <text class="qty-val">{{ item.quantity }}</text>
              <text class="qty-btn" @click.stop="changeQty(item, 1)">+</text>
            </view>
          </view>
        </view>
        <view class="delete-btn" v-if="isEditing" @click="removeItem(item)">
          <text>删除</text>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <text class="empty-icon">🛒</text>
      <text class="empty-text">购物车是空的</text>
      <button class="go-shop-btn" @click="goMall">去逛逛</button>
    </view>

    <!-- 底部结算栏 -->
    <view class="bottom-bar" v-if="cartItems.length > 0">
      <view class="select-all" @click="toggleSelectAll">
        <text class="check-icon" :class="{ checked: isAllSelected }">{{ isAllSelected ? '✓' : '' }}</text>
        <text>全选</text>
      </view>
      <view class="total-info" v-if="!isEditing">
        <text>合计: </text>
        <text class="total-price">¥{{ totalPrice.toFixed(2) }}</text>
      </view>
      <button class="settle-btn" v-if="!isEditing" @click="handleSettle" :disabled="selectedCount === 0">
        结算({{ selectedCount }})
      </button>
      <button class="delete-all-btn" v-else @click="deleteSelected" :disabled="selectedCount === 0">
        删除({{ selectedCount }})
      </button>
    </view>
  </view>
</template>

<script>
import { getCart, updateCart, removeCartItem, selectAllCart } from '../../api/index'

export default {
  data() {
    return {
      cartItems: [],
      isEditing: false,
      loading: false
    }
  },
  computed: {
    isAllSelected() {
      return this.cartItems.length > 0 && this.cartItems.every(i => i.selected)
    },
    selectedCount() {
      return this.cartItems.filter(i => i.selected && i.valid).length
    },
    totalPrice() {
      return this.cartItems
        .filter(i => i.selected && i.valid)
        .reduce((sum, i) => sum + i.price * i.quantity, 0)
    }
  },
  onShow() {
    this.loadCart()
  },
  methods: {
    async loadCart() {
      const token = uni.getStorageSync('token')
      if (!token) { uni.navigateTo({ url: '/pages/login/index' }); return }
      this.loading = true
      try {
        const res = await getCart()
        this.cartItems = res.items || []
      } catch(e) {
        uni.showToast({ title: '请先登录', icon: 'none' })
      } finally {
        this.loading = false
      }
    },
    toggleSelect(item) {
      if (!item.valid) return
      item.selected = !item.selected
      this.syncSelect()
    },
    async syncSelect() {
      try {
        const ids = this.cartItems.filter(i => i.selected).map(i => i.id)
        await selectAllCart(false)
        if (ids.length > 0) {
          const { selectCartItems } = require('../../api/index')
          await selectCartItems(ids)
        }
      } catch(e) {}
    },
    async toggleSelectAll() {
      const newVal = !this.isAllSelected
      this.cartItems.forEach(i => i.selected = newVal)
      try {
        await selectAllCart(newVal)
      } catch(e) {}
    },
    async changeQty(item, delta) {
      const newQty = item.quantity + delta
      if (newQty < 1 || newQty > (item.stock || 999)) return
      item.quantity = newQty
      try {
        await updateCart(item.id, newQty)
      } catch(e) {}
    },
    async removeItem(item) {
      uni.showModal({
        title: '提示',
        content: '确定删除该商品吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await removeCartItem(item.id)
              this.cartItems = this.cartItems.filter(i => i.id !== item.id)
              uni.showToast({ title: '已删除', icon: 'success' })
            } catch(e) {
              uni.showToast({ title: '删除失败', icon: 'none' })
            }
          }
        }
      })
    },
    async deleteSelected() {
      const selected = this.cartItems.filter(i => i.selected)
      if (selected.length === 0) return
      uni.showModal({
        title: '提示',
        content: `确定删除选中的${selected.length}件商品吗？`,
        success: async (res) => {
          if (res.confirm) {
            try {
              for (const item of selected) {
                await removeCartItem(item.id)
              }
              this.cartItems = this.cartItems.filter(i => !i.selected)
              this.isEditing = false
              uni.showToast({ title: '已删除', icon: 'success' })
            } catch(e) {}
          }
        }
      })
    },
    toggleEdit() {
      this.isEditing = !this.isEditing
    },
    goProduct(item) {
      if (item.valid) {
        uni.navigateTo({ url: `/pages/product/detail?id=${item.product_id}` })
      }
    },
    goMall() {
      uni.switchTab({ url: '/pages/mall/index' })
    },
    handleSettle() {
      if (this.selectedCount === 0) return
      uni.navigateTo({ url: '/pages/checkout/index?source=cart' })
    }
  }
}
</script>

<style scoped>
.cart-page { background: #f5f5f5; min-height: 100vh; padding-bottom: 70px; }
.cart-header { background: #fff; padding: 15px; display: flex; justify-content: space-between; align-items: center; }
.header-title { font-size: 16px; font-weight: bold; }
.header-edit { font-size: 14px; color: #409eff; }
.cart-list { padding: 10px; }
.cart-item { background: #fff; border-radius: 10px; padding: 12px; margin-bottom: 8px; display: flex; align-items: center; }
.cart-item.invalid { opacity: 0.5; }
.check-box { width: 24px; height: 24px; border: 2px solid #ddd; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 10px; flex-shrink: 0; }
.check-icon { font-size: 14px; color: #fff; }
.check-icon.checked { background: #409eff; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; }
.item-img { width: 80px; height: 80px; border-radius: 8px; flex-shrink: 0; margin-right: 10px; }
.item-info { flex: 1; min-width: 0; }
.item-name { font-size: 14px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.item-invalid { font-size: 12px; color: #999; background: #f5f5f5; padding: 1px 6px; border-radius: 3px; margin-top: 4px; display: inline-block; }
.item-bottom { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; }
.item-price { font-size: 16px; font-weight: bold; color: #f56c6c; }
.qty-control { display: flex; align-items: center; }
.qty-btn { width: 26px; height: 26px; border: 1px solid #ddd; display: flex; align-items: center; justify-content: center; font-size: 16px; color: #666; }
.qty-val { width: 32px; height: 26px; border-top: 1px solid #ddd; border-bottom: 1px solid #ddd; display: flex; align-items: center; justify-content: center; font-size: 13px; }
.delete-btn { margin-left: 8px; }
.delete-btn text { color: #f56c6c; font-size: 13px; }
.empty-state { text-align: center; padding: 80px 0; }
.empty-icon { font-size: 60px; display: block; }
.empty-text { font-size: 15px; color: #999; display: block; margin: 15px 0; }
.go-shop-btn { background: #409eff; color: #fff; border: none; border-radius: 20px; padding: 10px 40px; font-size: 14px; }
.bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #fff; display: flex; align-items: center; padding: 10px 15px; box-shadow: 0 -2px 8px rgba(0,0,0,0.08); z-index: 100; }
.select-all { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.total-info { flex: 1; text-align: right; font-size: 14px; margin-right: 10px; }
.total-price { color: #f56c6c; font-weight: bold; font-size: 18px; }
.settle-btn { background: #f56c6c; color: #fff; border: none; border-radius: 20px; padding: 8px 20px; font-size: 14px; }
.settle-btn[disabled] { background: #ccc; }
.delete-all-btn { background: #f56c6c; color: #fff; border: none; border-radius: 20px; padding: 8px 20px; font-size: 14px; margin-left: auto; }
</style>
