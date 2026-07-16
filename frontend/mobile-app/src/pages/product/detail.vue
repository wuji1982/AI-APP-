<template>
  <view class="product-detail">
    <!-- 商品图片轮播 -->
    <swiper class="product-swiper" indicator-dots autoplay circular>
      <swiper-item v-for="(img, idx) in imageList" :key="idx">
        <image class="swiper-img" :src="img" mode="aspectFill"></image>
      </swiper-item>
      <swiper-item v-if="imageList.length === 0">
        <view class="no-img">暂无图片</view>
      </swiper-item>
    </swiper>

    <!-- 价格信息 -->
    <view class="price-section">
      <view class="price-row">
        <text class="price-now">¥{{ product.selling_price }}</text>
        <text class="price-old">¥{{ product.original_price }}</text>
        <text class="discount-tag" v-if="product.original_price > product.selling_price">省¥{{ (product.original_price - product.selling_price).toFixed(2) }}</text>
      </view>
      <view class="sales-row">
        <text>已售 {{ product.sales_count || 0 }}</text>
        <text>库存 {{ product.stock || 0 }}</text>
      </view>
      <view class="contrib-row">
        <text>消费贡献值 +{{ contribAmount }}</text>
      </view>
    </view>

    <!-- 商品名称 -->
    <view class="title-section">
      <view class="product-tags">
        <text class="tag" v-if="product.is_recommended">推荐</text>
        <text class="tag cat-tag">{{ catLabels[product.category] || product.category }}</text>
      </view>
      <text class="product-name">{{ product.name }}</text>
    </view>

    <!-- 规格选择 -->
    <view class="sku-section" v-if="product.skus && product.skus.length > 0">
      <text class="section-label">规格</text>
      <view class="sku-list">
        <view class="sku-item" :class="{ active: selectedSku === sku.id }" v-for="sku in product.skus" :key="sku.id" @click="selectSku(sku)">
          <text>{{ sku.sku_name }}</text>
          <text class="sku-price">¥{{ sku.price }}</text>
        </view>
      </view>
    </view>

    <!-- 数量选择 -->
    <view class="quantity-section">
      <text class="section-label">数量</text>
      <view class="quantity-control">
        <text class="qty-btn" @click="changeQty(-1)">-</text>
        <text class="qty-value">{{ quantity }}</text>
        <text class="qty-btn" @click="changeQty(1)">+</text>
      </view>
    </view>

    <!-- 商品描述 -->
    <view class="desc-section">
      <text class="section-label">商品详情</text>
      <rich-text :nodes="product.description || '暂无描述'"></rich-text>
    </view>

    <!-- 评价区域 -->
    <view class="review-section">
      <view class="section-header">
        <text class="section-label">商品评价 ({{ reviewStats.total || 0 }})</text>
        <text class="avg-rating" v-if="reviewStats.avg_rating">好评率 {{ reviewStats.avg_rating }}分</text>
      </view>
      <view class="review-list" v-if="reviews.length > 0">
        <view class="review-item" v-for="r in reviews" :key="r.id">
          <view class="review-user">
            <text class="user-name">{{ r.user_name }}</text>
            <view class="stars">
              <text v-for="s in r.rating" :key="s">★</text>
            </view>
          </view>
          <text class="review-content">{{ r.content || '此用户未留下评价内容' }}</text>
          <text class="review-time">{{ formatTime(r.created_at) }}</text>
        </view>
      </view>
      <view class="empty-review" v-else>
        <text>暂无评价</text>
      </view>
    </view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar">
      <view class="bar-left">
        <view class="bar-btn" @click="toggleFavorite">
          <text>{{ isFavorited ? '❤️' : '🤍' }}</text>
          <text>收藏</text>
        </view>
        <view class="bar-btn" @click="goCart">
          <text>🛒</text>
          <text>购物车</text>
        </view>
      </view>
      <view class="bar-right">
        <button class="btn-cart" @click="handleAddCart">加入购物车</button>
        <button class="btn-buy" @click="handleBuyNow">立即购买</button>
      </view>
    </view>
  </view>
</template>

<script>
import { getProductDetail, addToCart, addFavorite, removeFavorite, checkFavorite, getProductReviews } from '../../api/index'

export default {
  data() {
    return {
      product: {},
      quantity: 1,
      selectedSku: null,
      isFavorited: false,
      reviews: [],
      reviewStats: {},
      catLabels: { food: '吃', drink: '喝', use: '用', wear: '穿' }
    }
  },
  computed: {
    imageList() {
      if (this.product.images) {
        try { return JSON.parse(this.product.images) } catch(e) {}
      }
      return this.product.cover_image ? [this.product.cover_image] : []
    },
    contribAmount() {
      return Math.floor((this.product.selling_price || 0) * 0.2 * 0.5 * 10)
    }
  },
  onLoad(options) {
    if (options.id) {
      this.loadProduct(options.id)
      this.loadReviews(options.id)
      this.checkFav(options.id)
    }
  },
  methods: {
    async loadProduct(id) {
      try {
        const res = await getProductDetail(id)
        this.product = res
      } catch(e) {
        uni.showToast({ title: '商品不存在', icon: 'none' })
      }
    },
    async loadReviews(id) {
      try {
        const res = await getProductReviews(id)
        this.reviews = res.items || []
        this.reviewStats = { avg_rating: res.avg_rating, total: res.total }
      } catch(e) {}
    },
    async checkFav(id) {
      try {
        const res = await checkFavorite(id)
        this.isFavorited = res.is_favorited
      } catch(e) {}
    },
    selectSku(sku) {
      this.selectedSku = this.selectedSku === sku.id ? null : sku.id
    },
    changeQty(delta) {
      const next = this.quantity + delta
      if (next >= 1 && next <= (this.product.stock || 999)) {
        this.quantity = next
      }
    },
    async toggleFavorite() {
      const token = uni.getStorageSync('token')
      if (!token) { uni.navigateTo({ url: '/pages/login/index' }); return }
      try {
        if (this.isFavorited) {
          await removeFavorite(this.product.id)
          this.isFavorited = false
          uni.showToast({ title: '已取消收藏', icon: 'none' })
        } else {
          await addFavorite(this.product.id)
          this.isFavorited = true
          uni.showToast({ title: '收藏成功', icon: 'success' })
        }
      } catch(e) {
        uni.showToast({ title: '请先登录', icon: 'none' })
      }
    },
    async handleAddCart() {
      const token = uni.getStorageSync('token')
      if (!token) { uni.navigateTo({ url: '/pages/login/index' }); return }
      try {
        await addToCart({ product_id: this.product.id, sku_id: this.selectedSku, quantity: this.quantity })
        uni.showToast({ title: '已加入购物车', icon: 'success' })
      } catch(e) {
        uni.showToast({ title: e.message || '操作失败', icon: 'none' })
      }
    },
    handleBuyNow() {
      const token = uni.getStorageSync('token')
      if (!token) { uni.navigateTo({ url: '/pages/login/index' }); return }
      // 直接加入购物车然后结算
      this.handleAddCart().then(() => {
        uni.navigateTo({ url: '/pages/checkout/index?source=cart' })
      })
    },
    goCart() {
      uni.navigateTo({ url: '/pages/cart/index' })
    },
    formatTime(t) {
      if (!t) return ''
      return t.substring(0, 10)
    }
  }
}
</script>

<style scoped>
.product-detail { background: #f5f5f5; min-height: 100vh; padding-bottom: 70px; }
.product-swiper { height: 300px; }
.swiper-img { width: 100%; height: 100%; }
.no-img { height: 300px; display: flex; align-items: center; justify-content: center; color: #999; background: #eee; }
.price-section { background: #fff; padding: 15px; }
.price-row { display: flex; align-items: baseline; gap: 8px; }
.price-now { font-size: 26px; font-weight: bold; color: #f56c6c; }
.price-old { font-size: 14px; color: #ccc; text-decoration: line-through; }
.discount-tag { background: #fff0f0; color: #f56c6c; font-size: 12px; padding: 2px 6px; border-radius: 3px; }
.sales-row { display: flex; gap: 15px; margin-top: 8px; font-size: 13px; color: #999; }
.contrib-row { margin-top: 6px; }
.contrib-row text { font-size: 12px; color: #409eff; background: #f0f9ff; padding: 2px 8px; border-radius: 3px; }
.title-section { background: #fff; padding: 15px; margin-top: 8px; }
.product-tags { display: flex; gap: 5px; margin-bottom: 6px; }
.tag { font-size: 11px; padding: 1px 6px; border-radius: 3px; background: #f0f9ff; color: #409eff; }
.cat-tag { background: #f0fff4; color: #67c23a; }
.product-name { font-size: 16px; font-weight: 500; line-height: 1.5; }
.sku-section, .quantity-section, .desc-section, .review-section { background: #fff; padding: 15px; margin-top: 8px; }
.section-label { font-size: 15px; font-weight: bold; margin-bottom: 10px; display: block; }
.sku-list { display: flex; flex-wrap: wrap; gap: 8px; }
.sku-item { padding: 8px 14px; border: 1px solid #ddd; border-radius: 6px; font-size: 13px; display: flex; gap: 5px; }
.sku-item.active { border-color: #409eff; color: #409eff; background: #f0f9ff; }
.sku-price { color: #f56c6c; }
.quantity-section { display: flex; align-items: center; justify-content: space-between; }
.quantity-control { display: flex; align-items: center; gap: 0; }
.qty-btn { width: 32px; height: 32px; border: 1px solid #ddd; display: flex; align-items: center; justify-content: center; font-size: 18px; color: #666; }
.qty-value { width: 40px; height: 32px; border-top: 1px solid #ddd; border-bottom: 1px solid #ddd; display: flex; align-items: center; justify-content: center; font-size: 14px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.avg-rating { font-size: 13px; color: #f56c6c; }
.review-item { padding: 10px 0; border-bottom: 1px solid #f5f5f5; }
.review-user { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
.user-name { font-size: 13px; color: #666; }
.stars text { color: #f7ba2a; font-size: 14px; }
.review-content { font-size: 14px; color: #333; display: block; }
.review-time { font-size: 12px; color: #999; margin-top: 4px; display: block; }
.empty-review { text-align: center; padding: 20px; color: #999; font-size: 14px; }
.bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #fff; display: flex; align-items: center; padding: 8px 12px; box-shadow: 0 -2px 8px rgba(0,0,0,0.08); z-index: 100; }
.bar-left { display: flex; gap: 12px; }
.bar-btn { text-align: center; font-size: 11px; color: #666; }
.bar-btn text:first-child { font-size: 20px; display: block; }
.bar-right { flex: 1; display: flex; gap: 0; margin-left: 12px; }
.btn-cart { flex: 1; background: #ffa500; color: #fff; border: none; border-radius: 20px 0 0 20px; padding: 10px 0; font-size: 14px; }
.btn-buy { flex: 1; background: #f56c6c; color: #fff; border: none; border-radius: 0 20px 20px 0; padding: 10px 0; font-size: 14px; }
</style>
