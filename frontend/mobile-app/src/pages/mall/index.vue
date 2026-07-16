<template>
  <view class="mall-page">
    <!-- 分类导航 -->
    <view class="category-bar">
      <view class="cat-item" :class="{ active: activeCat === '' }" @click="activeCat = ''">全部</view>
      <view class="cat-item" :class="{ active: activeCat === 'food' }" @click="switchCat('food')">吃</view>
      <view class="cat-item" :class="{ active: activeCat === 'drink' }" @click="switchCat('drink')">喝</view>
      <view class="cat-item" :class="{ active: activeCat === 'use' }" @click="switchCat('use')">用</view>
      <view class="cat-item" :class="{ active: activeCat === 'wear' }" @click="switchCat('wear')">穿</view>
    </view>

    <!-- 搜索栏 -->
    <view class="search-bar">
      <input class="search-input" placeholder="搜索商品" v-model="keyword" @confirm="search" />
    </view>

    <!-- 商品列表 -->
    <view class="product-list">
      <view class="product-card" v-for="item in products" :key="item.id" @click="viewDetail(item)">
        <image class="product-img" :src="item.cover_image || '/static/placeholder.png'" mode="aspectFill"></image>
        <view class="product-info">
          <text class="product-name">{{ item.name }}</text>
          <view class="product-tags">
            <text class="tag" v-if="item.is_recommended">推荐</text>
            <text class="tag cat-tag">{{ catLabels[item.category] || item.category }}</text>
          </view>
          <view class="product-bottom">
            <view class="price-group">
              <text class="price-now">¥{{ item.selling_price }}</text>
              <text class="price-old">¥{{ item.original_price }}</text>
            </view>
            <text class="sales">已售{{ item.sales_count || 0 }}</text>
          </view>
          <view class="contrib-info">
            <text>消费贡献值 +{{ Math.floor(item.selling_price * 0.2 * 0.5 * 10) }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty" v-if="!loading && products.length === 0">
      <text class="empty-icon">🛍</text>
      <text class="empty-text">暂无商品</text>
    </view>

    <!-- 加载提示 -->
    <view class="loading-tip" v-if="loading && page > 1">
      <text>加载中...</text>
    </view>
    <view class="loading-tip" v-if="!loading && products.length > 0 && noMore">
      <text>— 没有更多了 —</text>
    </view>
  </view>
</template>

<script>
import { getProducts } from '../../api/index'

export default {
  data() {
    return {
      activeCat: '',
      keyword: '',
      products: [],
      loading: false,
      noMore: false,
      page: 1,
      catLabels: { food: '吃', drink: '喝', use: '用', wear: '穿' }
    }
  },
  onLoad() { this.loadProducts() },
  onPullDownRefresh() { this.page = 1; this.loadProducts().then(() => uni.stopPullDownRefresh()) },
  onReachBottom() { this.page++; this.loadProducts() },
  methods: {
    async loadProducts() {
      this.loading = true
      try {
        const params = { page: this.page, size: 20 }
        if (this.activeCat) params.category = this.activeCat
        const res = await getProducts(params)
        if (this.page === 1) {
          this.products = res.items || []
        } else {
          const items = res.items || []
          if (items.length === 0) this.noMore = true
          else this.products.push(...items)
        }
      } catch (e) {
        uni.showToast({ title: '加载失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },
    switchCat(cat) {
      this.activeCat = cat
      this.page = 1
      this.loadProducts()
    },
    search() { this.page = 1; this.loadProducts() },
    viewDetail(item) {
      uni.navigateTo({ url: `/pages/product/detail?id=${item.id}` })
    }
  }
}
</script>

<style scoped>
.mall-page { background: #f5f5f5; min-height: 100vh; }
.category-bar { display: flex; background: #fff; padding: 10px 0; position: sticky; top: 0; z-index: 10; }
.cat-item { flex: 1; text-align: center; padding: 8px 0; font-size: 14px; color: #666; border-radius: 20px; margin: 0 5px; }
.cat-item.active { background: #409eff; color: #fff; font-weight: bold; }
.search-bar { padding: 10px 12px; background: #fff; margin-bottom: 8px; }
.search-input { background: #f5f5f5; border-radius: 20px; padding: 8px 16px; font-size: 14px; }
.product-list { padding: 0 12px; }
.product-card { background: #fff; border-radius: 12px; margin-bottom: 10px; overflow: hidden; display: flex; }
.product-img { width: 120px; height: 120px; flex-shrink: 0; }
.product-info { flex: 1; padding: 10px; }
.product-name { font-size: 14px; font-weight: 500; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.product-tags { display: flex; gap: 5px; margin-top: 5px; }
.tag { font-size: 11px; padding: 1px 6px; border-radius: 3px; background: #f0f9ff; color: #409eff; }
.cat-tag { background: #f0fff4; color: #67c23a; }
.product-bottom { display: flex; justify-content: space-between; align-items: center; margin-top: 5px; }
.price-now { font-size: 18px; font-weight: bold; color: #f56c6c; }
.price-old { font-size: 12px; color: #ccc; text-decoration: line-through; margin-left: 5px; }
.sales { font-size: 11px; color: #999; }
.contrib-info { margin-top: 3px; }
.contrib-info text { font-size: 11px; color: #409eff; background: #f0f9ff; padding: 1px 6px; border-radius: 3px; }
.empty { text-align: center; padding: 60px 0; color: #999; }
.empty-icon { font-size: 50px; display: block; }
.empty-text { font-size: 14px; display: block; margin-top: 10px; }
.loading-tip { text-align: center; padding: 15px; color: #ccc; font-size: 13px; }
</style>
