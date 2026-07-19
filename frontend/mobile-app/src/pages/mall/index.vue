<template>
  <view class="mall-page">
    <!-- 顶部搜索栏 -->
    <view class="top-bar">
      <view class="search-wrap">
        <text class="search-icon">🔍</text>
        <input class="search-input" placeholder="搜索商品" v-model="keyword" @confirm="onSearch" confirm-type="search" />
      </view>
    </view>

    <view class="mall-body">
      <!-- 左侧分类栏 -->
      <scroll-view scroll-y class="side-bar">
        <view
          v-for="cat in categories"
          :key="cat.key"
          class="side-item"
          :class="{ active: activeCat === cat.key }"
          @click="switchCat(cat.key)"
        >
          <text class="side-icon">{{ cat.icon }}</text>
          <text class="side-label">{{ cat.label }}</text>
        </view>
      </scroll-view>

      <!-- 右侧内容区 -->
      <scroll-view scroll-y class="main-content" @scrolltolower="loadMore">
        <!-- 子分类图标网格 -->
        <view class="sub-grid">
          <view
            v-for="sub in currentSubs"
            :key="sub.label"
            class="sub-item"
            :class="{ active: activeSub === sub.key }"
            @click="switchSub(sub.key)"
          >
            <view class="sub-icon-wrap" :style="{ background: sub.bg }">
              <text class="sub-icon">{{ sub.icon }}</text>
            </view>
            <text class="sub-label">{{ sub.label }}</text>
          </view>
        </view>

        <!-- 排序栏 -->
        <view class="sort-bar">
          <text class="sort-title">商品列表</text>
          <view class="sort-actions">
            <text class="sort-item" :class="{ active: sortBy === 'default' }" @click="sortBy = 'default'">综合</text>
            <text class="sort-item" :class="{ active: sortBy === 'sales' }" @click="sortBy = 'sales'">销量</text>
            <text class="sort-item" :class="{ active: sortBy === 'price_asc' }" @click="sortProducts('price_asc')">价格↑</text>
            <text class="sort-item" :class="{ active: sortBy === 'price_desc' }" @click="sortProducts('price_desc')">价格↓</text>
          </view>
        </view>

        <!-- 商品双列网格 -->
        <view class="product-grid">
          <view class="product-card" v-for="item in displayProducts" :key="item.id" @click="viewDetail(item)">
            <image class="product-img" :src="item.cover_image || '/static/placeholder.png'" mode="aspectFill"></image>
            <view class="product-info">
              <text class="product-name">{{ item.name }}</text>
              <view class="product-tags">
                <text class="tag hot" v-if="item.is_recommended">推荐</text>
                <text class="tag contrib">贡献值+{{ Math.floor(item.selling_price * 0.2 * 0.5 * 10) }}</text>
              </view>
              <view class="product-bottom">
                <text class="price-now">¥{{ item.selling_price }}</text>
                <text class="sales">{{ item.sales_count || 0 }}人付款</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 空状态 -->
        <view class="empty" v-if="!loading && displayProducts.length === 0">
          <text class="empty-icon">🛍️</text>
          <text class="empty-text">暂无商品</text>
          <text class="empty-hint">换个分类看看吧</text>
        </view>

        <!-- 加载状态 -->
        <view class="loading-tip" v-if="loading">
          <text>加载中...</text>
        </view>
        <view class="loading-tip" v-if="!loading && displayProducts.length > 0 && noMore">
          <text>— 没有更多了 —</text>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<script>
import { getProducts } from '../../api/index'

// 分类配置：主分类 + 子分类
const CATEGORIES = [
  {
    key: '', label: '精选', icon: '⭐',
    subs: [
      { key: '', label: '全部', icon: '🏷️', bg: '#f0f9ff' },
      { key: 'rec_food', label: '美食', icon: '🍜', bg: '#fff7e6' },
      { key: 'rec_drink', label: '酒水', icon: '🍺', bg: '#fff1f0' },
      { key: 'rec_use', label: '百货', icon: '🏠', bg: '#f6ffed' },
      { key: 'rec_wear', label: '服饰', icon: '👔', bg: '#f9f0ff' },
      { key: 'rec_gift', label: '礼盒', icon: '🎁', bg: '#fff0f6' },
    ]
  },
  {
    key: 'food', label: '食品', icon: '🍎',
    subs: [
      { key: '', label: '全部', icon: '🍎', bg: '#fff7e6' },
      { key: 'snack', label: '零食', icon: '🍪', bg: '#fff7e6' },
      { key: 'grain', label: '粮油', icon: '🌾', bg: '#f6ffed' },
      { key: 'tea', label: '茶叶', icon: '🍵', bg: '#f0f9ff' },
      { key: 'health', label: '滋补', icon: '💊', bg: '#fff0f6' },
      { key: 'fresh', label: '生鲜', icon: '🥬', bg: '#e6fffb' },
    ]
  },
  {
    key: 'drink', label: '酒水', icon: '🍷',
    subs: [
      { key: '', label: '全部', icon: '🍷', bg: '#fff1f0' },
      { key: 'beer', label: '啤酒', icon: '🍺', bg: '#fff7e6' },
      { key: 'baijiu', label: '白酒', icon: '🥃', bg: '#fff1f0' },
      { key: 'wine', label: '红酒', icon: '🍷', bg: '#f9f0ff' },
      { key: 'soft', label: '饮料', icon: '🥤', bg: '#e6f7ff' },
      { key: 'water', label: '矿泉水', icon: '💧', bg: '#e6fffb' },
    ]
  },
  {
    key: 'use', label: '百货', icon: '🏠',
    subs: [
      { key: '', label: '全部', icon: '🏠', bg: '#f6ffed' },
      { key: 'digital', label: '数码', icon: '📱', bg: '#f0f9ff' },
      { key: 'home', label: '家居', icon: '🛋️', bg: '#fff7e6' },
      { key: 'kitchen', label: '厨具', icon: '🍳', bg: '#f6ffed' },
      { key: 'beauty', label: '美妆', icon: '💄', bg: '#fff0f6' },
      { key: 'clean', label: '清洁', icon: '🧹', bg: '#e6fffb' },
    ]
  },
  {
    key: 'wear', label: '服饰', icon: '👗',
    subs: [
      { key: '', label: '全部', icon: '👗', bg: '#f9f0ff' },
      { key: 'men', label: '男装', icon: '👔', bg: '#f0f9ff' },
      { key: 'women', label: '女装', icon: '👗', bg: '#fff0f6' },
      { key: 'shoes', label: '鞋靴', icon: '👟', bg: '#fff7e6' },
      { key: 'bag', label: '箱包', icon: '👜', bg: '#f9f0ff' },
      { key: 'hat', label: '配饰', icon: '🧢', bg: '#e6f7ff' },
    ]
  },
]

export default {
  data() {
    return {
      categories: CATEGORIES,
      activeCat: '',
      activeSub: '',
      keyword: '',
      products: [],
      allProducts: [], // 当前分类下全量数据（用于前端排序）
      loading: false,
      noMore: false,
      page: 1,
      sortBy: 'default',
    }
  },
  computed: {
    currentSubs() {
      const cat = this.categories.find(c => c.key === this.activeCat)
      return cat ? cat.subs : []
    },
    displayProducts() {
      let list = [...this.allProducts]
      if (this.sortBy === 'sales') {
        list.sort((a, b) => (b.sales_count || 0) - (a.sales_count || 0))
      } else if (this.sortBy === 'price_asc') {
        list.sort((a, b) => a.selling_price - b.selling_price)
      } else if (this.sortBy === 'price_desc') {
        list.sort((a, b) => b.selling_price - a.selling_price)
      }
      return list
    }
  },
  onLoad() { this.loadProducts() },
  onPullDownRefresh() { this.page = 1; this.noMore = false; this.loadProducts().then(() => uni.stopPullDownRefresh()) },
  methods: {
    async loadProducts() {
      this.loading = true
      try {
        const params = { page: this.page, size: 20 }
        // 主分类过滤
        const catObj = this.categories.find(c => c.key === this.activeCat)
        if (catObj && catObj.key) {
          params.category = catObj.key
        }
        const res = await getProducts(params)
        const items = res.items || []
        if (this.page === 1) {
          this.allProducts = items
        } else {
          if (items.length === 0) {
            this.noMore = true
          } else {
            this.allProducts.push(...items)
          }
        }
      } catch (e) {
        uni.showToast({ title: '加载失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },
    loadMore() {
      if (this.noMore || this.loading) return
      this.page++
      this.loadProducts()
    },
    switchCat(catKey) {
      if (this.activeCat === catKey) return
      this.activeCat = catKey
      this.activeSub = ''
      this.sortBy = 'default'
      this.page = 1
      this.noMore = false
      this.allProducts = []
      this.loadProducts()
    },
    switchSub(subKey) {
      this.activeSub = subKey
      // 子分类目前映射到主分类过滤，后续可扩展为独立过滤
      this.page = 1
      this.noMore = false
      this.allProducts = []
      this.loadProducts()
    },
    sortProducts(type) {
      this.sortBy = type
    },
    onSearch() {
      this.page = 1
      this.noMore = false
      this.allProducts = []
      this.loadProducts()
    },
    viewDetail(item) {
      uni.navigateTo({ url: `/pages/product/detail?id=${item.id}` })
    }
  }
}
</script>

<style scoped>
.mall-page {
  background: #f5f5f5;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 顶部搜索栏 */
.top-bar {
  background: #fff;
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
}
.search-wrap {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 20px;
  padding: 0 12px;
  height: 36px;
}
.search-icon { font-size: 14px; margin-right: 6px; }
.search-input { flex: 1; font-size: 14px; background: transparent; }

/* 主体区域 */
.mall-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 左侧分类栏 */
.side-bar {
  width: 88px;
  background: #f8f8f8;
  height: calc(100vh - 52px);
  flex-shrink: 0;
}
.side-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 14px 0;
  position: relative;
  transition: all 0.2s;
}
.side-item.active {
  background: #fff;
}
.side-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: #ff4d4f;
  border-radius: 0 2px 2px 0;
}
.side-icon { font-size: 20px; margin-bottom: 4px; }
.side-label { font-size: 12px; color: #333; }
.side-item.active .side-label { color: #ff4d4f; font-weight: 600; }

/* 右侧内容区 */
.main-content {
  flex: 1;
  height: calc(100vh - 52px);
  background: #fff;
}

/* 子分类网格 */
.sub-grid {
  display: flex;
  flex-wrap: wrap;
  padding: 16px 8px 8px;
  background: #fff;
  border-bottom: 1px solid #f5f5f5;
}
.sub-item {
  width: 20%;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 12px;
}
.sub-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-bottom: 4px;
  transition: all 0.2s;
}
.sub-item.active .sub-icon-wrap {
  box-shadow: 0 0 0 2px #ff4d4f;
}
.sub-label { font-size: 11px; color: #666; }
.sub-item.active .sub-label { color: #ff4d4f; font-weight: 500; }

/* 排序栏 */
.sort-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: #fff;
  border-bottom: 1px solid #f5f5f5;
}
.sort-title { font-size: 13px; color: #999; }
.sort-actions { display: flex; gap: 16px; }
.sort-item { font-size: 12px; color: #666; }
.sort-item.active { color: #ff4d4f; font-weight: 500; }

/* 商品双列网格 */
.product-grid {
  display: flex;
  flex-wrap: wrap;
  padding: 8px;
  gap: 8px;
}
.product-card {
  width: calc(50% - 4px);
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #f5f5f5;
}
.product-card:active { opacity: 0.85; }
.product-img { width: 100%; height: 160px; }
.product-info { padding: 8px 10px 10px; }
.product-name {
  font-size: 13px;
  color: #333;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
  min-height: 36px;
}
.product-tags { display: flex; gap: 4px; margin-top: 6px; flex-wrap: wrap; }
.tag {
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 3px;
}
.tag.hot { background: #fff1f0; color: #ff4d4f; }
.tag.contrib { background: #f0f9ff; color: #1890ff; }
.product-bottom {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-top: 6px;
}
.price-now { font-size: 16px; font-weight: bold; color: #ff4d4f; }
.sales { font-size: 11px; color: #999; }

/* 空状态 */
.empty { text-align: center; padding: 80px 20px; }
.empty-icon { font-size: 50px; display: block; }
.empty-text { font-size: 15px; color: #666; display: block; margin-top: 12px; }
.empty-hint { font-size: 13px; color: #bbb; display: block; margin-top: 6px; }

.loading-tip { text-align: center; padding: 15px; color: #ccc; font-size: 13px; }
</style>
