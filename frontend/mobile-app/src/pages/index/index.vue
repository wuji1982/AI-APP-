<template>
  <view class="home-page">
    <!-- 轮播图 -->
    <swiper class="banner-swiper" indicator-dots autoplay circular :interval="4000" :duration="500">
      <swiper-item v-for="b in banners" :key="b.id">
        <image class="banner-img" :src="b.image_url || b.image" mode="aspectFill" @click="onBannerClick(b)"></image>
      </swiper-item>
      <swiper-item v-if="banners.length === 0">
        <view class="banner-placeholder">
          <text class="banner-title">AI Agent 共享商城</text>
          <text class="banner-desc">全量智能赋能 · 消费增值共享</text>
        </view>
      </swiper-item>
    </swiper>

    <!-- 公告滚动条 -->
    <view class="announce-bar" v-if="announcements.length > 0" @click="showAnnounce">
      <text class="announce-icon">📢</text>
      <swiper class="announce-swiper" vertical autoplay circular :interval="3000">
        <swiper-item v-for="(a, i) in announcements" :key="i">
          <text class="announce-text">{{ a.title || a }}</text>
        </swiper-item>
      </swiper>
      <text class="announce-more">›</text>
    </view>

    <!-- 功能入口 -->
    <view class="quick-entry">
      <view class="entry-item" @click="goTo('/pages/group-buy/index')">
        <view class="entry-icon" style="background:linear-gradient(135deg,#ff6b35,#ff8c5a);">
          <text>🎯</text>
        </view>
        <text class="entry-label">拼团专区</text>
      </view>
      <view class="entry-item" @click="goTo('/pages/mall/index')">
        <view class="entry-icon" style="background:linear-gradient(135deg,#409eff,#66b1ff);">
          <text>🛍</text>
        </view>
        <text class="entry-label">商城购物</text>
      </view>
      <view class="entry-item" @click="goTo('/pages/cart/index')">
        <view class="entry-icon" style="background:linear-gradient(135deg,#e6a23c,#f0c78a);">
          <text>🛒</text>
        </view>
        <text class="entry-label">购物车</text>
      </view>
      <view class="entry-item" @click="goTo('/pages/order/index')">
        <view class="entry-icon" style="background:linear-gradient(135deg,#67c23a,#95d475);">
          <text>📋</text>
        </view>
        <text class="entry-label">我的订单</text>
      </view>
    </view>

    <!-- 拼团倒计时专区 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">🔥 拼团进行中</text>
        <text class="section-more" @click="goTo('/pages/group-buy/index')">查看更多 ›</text>
      </view>
      <scroll-view scroll-x class="group-scroll">
        <view class="group-card" v-for="item in activeSessions" :key="item.id" @click="joinSession(item.id)">
          <view class="card-header">
            <text class="level-tag" :class="item.level">{{ levelText(item.level) }}</text>
            <text class="price">¥{{ item.total_price }}</text>
          </view>
          <view class="card-body">
            <text class="card-info">{{ item.current_players || 0 }}/{{ item.total_players }}人</text>
            <view class="progress-bar">
              <view class="progress-fill" :style="{ width: getProgress(item) + '%' }"></view>
            </view>
          </view>
          <!-- 倒计时 -->
          <view class="countdown-bar" v-if="item.countdown">
            <text class="countdown-label">距结束</text>
            <text class="countdown-time">{{ item.countdown }}</text>
          </view>
        </view>
      </scroll-view>
      <view class="empty-hint" v-if="activeSessions.length === 0">
        <text>暂无进行中的拼团</text>
      </view>
    </view>

    <!-- 推荐商品 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">✨ 推荐商品</text>
      </view>
      <view class="product-grid">
        <view class="product-item" v-for="p in products" :key="p.id" @click="viewProduct(p)">
          <image class="product-img" :src="p.cover_image || '/static/placeholder.png'" mode="aspectFill"></image>
          <view class="product-info">
            <text class="product-name">{{ p.name }}</text>
            <view class="product-price">
              <text class="price-now">¥{{ p.selling_price }}</text>
              <text class="price-old">¥{{ p.original_price }}</text>
            </view>
            <text class="contrib-tag">贡献值 +{{ Math.floor(p.selling_price * 0.2 * 0.5 * 10) }}</text>
          </view>
        </view>
      </view>
      <view class="empty-hint" v-if="products.length === 0">
        <text>暂无推荐商品</text>
      </view>
    </view>
  </view>
</template>

<script>
import { getBanners, getAnnouncements, getProducts, getSessions } from '../../api/index'

export default {
  data() {
    return {
      banners: [],
      announcements: [],
      activeSessions: [],
      products: [],
      countdownTimer: null,
    }
  },
  onLoad() {
    this.loadData()
    this.startCountdown()
  },
  onUnload() {
    if (this.countdownTimer) clearInterval(this.countdownTimer)
  },
  onPullDownRefresh() {
    this.loadData().then(() => uni.stopPullDownRefresh())
  },
  methods: {
    async loadData() {
      try {
        const [bannerRes, announceRes, sessRes, prodRes] = await Promise.all([
          getBanners('home').catch(() => ({ items: [] })),
          getAnnouncements(1).catch(() => ({ items: [] })),
          getSessions('junior').catch(() => ({ items: [] })),
          getProducts({ page: 1, size: 8 }).catch(() => ({ items: [] }))
        ])
        this.banners = bannerRes.items || bannerRes || []
        this.announcements = (announceRes.items || announceRes || []).slice(0, 5)
        const allSessions = sessRes.sessions || sessRes.items || []
        // 只保留进行中的场次并计算倒计时
        this.activeSessions = allSessions
          .filter(s => s.status === 'active' || s.status === 'pending')
          .slice(0, 5)
          .map(s => {
            s.countdown = this.calcCountdown(s)
            return s
          })
        this.products = prodRes.items || []
      } catch (e) {
        console.error('加载数据失败', e)
      }
    },
    calcCountdown(session) {
      // 模拟：距当天22:00的倒计时
      const now = new Date()
      const end = new Date(now)
      end.setHours(22, 0, 0, 0)
      if (now > end) return '已结束'
      const diff = Math.floor((end - now) / 1000)
      const h = String(Math.floor(diff / 3600)).padStart(2, '0')
      const m = String(Math.floor((diff % 3600) / 60)).padStart(2, '0')
      const s = String(diff % 60).padStart(2, '0')
      return `${h}:${m}:${s}`
    },
    startCountdown() {
      this.countdownTimer = setInterval(() => {
        this.activeSessions.forEach(s => {
          s.countdown = this.calcCountdown(s)
        })
      }, 1000)
    },
    getProgress(item) {
      if (!item.total_players) return 0
      return Math.min(100, Math.round(((item.current_players || 0) / item.total_players) * 100))
    },
    levelText(level) {
      return { svip: 'SVIP团', senior: '高级团', junior: '初级团' }[level] || '初级团'
    },
    goTo(url) {
      uni.navigateTo({ url })
    },
    joinSession(id) {
      uni.navigateTo({ url: `/pages/group-buy/detail?id=${id}` })
    },
    viewProduct(p) {
      uni.navigateTo({ url: `/pages/product/detail?id=${p.id}` })
    },
    onBannerClick(b) {
      if (b.link_url) {
        uni.navigateTo({ url: b.link_url })
      }
    },
    showAnnounce() {
      uni.showModal({
        title: '平台公告',
        content: this.announcements.map(a => a.title || a).join('\n\n'),
        showCancel: false
      })
    }
  }
}
</script>

<style scoped>
.home-page { background: #f5f5f5; min-height: 100vh; padding-bottom: 20px; }

/* 轮播图 */
.banner-swiper { height: 180px; }
.banner-img { width: 100%; height: 180px; }
.banner-placeholder {
  height: 180px; background: linear-gradient(135deg, #409eff, #67c23a);
  display: flex; flex-direction: column; align-items: center; justify-content: center; color: #fff;
}
.banner-title { font-size: 22px; font-weight: bold; }
.banner-desc { font-size: 14px; opacity: 0.85; margin-top: 8px; }

/* 公告栏 */
.announce-bar {
  display: flex; align-items: center; background: #fffbe6; padding: 8px 12px;
  border-bottom: 1px solid #fff1b8;
}
.announce-icon { font-size: 16px; margin-right: 8px; }
.announce-swiper { flex: 1; height: 24px; }
.announce-text { font-size: 13px; color: #d48806; line-height: 24px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.announce-more { font-size: 18px; color: #d48806; margin-left: 8px; }

/* 功能入口 */
.quick-entry { display: flex; justify-content: space-around; padding: 20px 15px; background: #fff; }
.entry-item { text-align: center; }
.entry-icon {
  width: 50px; height: 50px; border-radius: 14px; color: #fff; font-size: 22px;
  display: flex; align-items: center; justify-content: center; margin: 0 auto 8px;
}
.entry-label { font-size: 12px; color: #666; }

/* 通用section */
.section { margin-top: 12px; background: #fff; padding: 15px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.section-title { font-size: 16px; font-weight: bold; }
.section-more { font-size: 13px; color: #409eff; }

/* 拼团卡片 - 横向滚动 */
.group-scroll { white-space: nowrap; }
.group-card {
  display: inline-block; width: 200px; border: 1px solid #f0f0f0; border-radius: 12px;
  padding: 12px; margin-right: 10px; vertical-align: top; white-space: normal;
}
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.level-tag { padding: 2px 8px; border-radius: 4px; font-size: 11px; color: #fff; }
.level-tag.junior { background: #909399; }
.level-tag.senior { background: #e6a23c; }
.level-tag.svip { background: linear-gradient(135deg, #f56c6c, #e6a23c); }
.price { font-size: 18px; font-weight: bold; color: #f56c6c; }
.card-body { margin-bottom: 8px; }
.card-info { font-size: 12px; color: #666; display: block; margin-bottom: 4px; }
.progress-bar { height: 5px; background: #f0f0f0; border-radius: 3px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #ff6b35, #ff8c5a); border-radius: 3px; transition: width 0.3s; }

/* 倒计时 */
.countdown-bar { display: flex; align-items: center; gap: 4px; background: #fff7e6; border-radius: 4px; padding: 3px 8px; }
.countdown-label { font-size: 11px; color: #d48806; }
.countdown-time { font-size: 13px; color: #d48806; font-weight: bold; font-family: monospace; }

/* 商品网格 */
.product-grid { display: flex; flex-wrap: wrap; gap: 10px; }
.product-item { width: calc(50% - 5px); background: #fafafa; border-radius: 10px; overflow: hidden; }
.product-img { width: 100%; height: 150px; }
.product-info { padding: 8px 10px; }
.product-name { font-size: 13px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.4; }
.product-price { display: flex; gap: 6px; align-items: baseline; margin-top: 5px; }
.price-now { color: #f56c6c; font-weight: bold; font-size: 16px; }
.price-old { color: #ccc; text-decoration: line-through; font-size: 12px; }
.contrib-tag { font-size: 10px; color: #409eff; background: #f0f9ff; padding: 1px 5px; border-radius: 3px; margin-top: 4px; display: inline-block; }

.empty-hint { text-align: center; padding: 30px 0; color: #ccc; font-size: 13px; }
</style>
