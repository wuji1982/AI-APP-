<template>
  <view class="mine-page">
    <!-- 用户信息头部 -->
    <view class="user-header">
      <view class="avatar-wrap">
        <image class="avatar" :src="userInfo.avatar || '/static/default-avatar.png'" mode="aspectFill"></image>
      </view>
      <view class="user-info">
        <text class="nickname">{{ userInfo.nickname || '未登录' }}</text>
        <text class="phone">{{ userInfo.phone || '点击登录' }}</text>
        <view class="level-badge" v-if="userInfo.agent_level">
          <text>{{ agentLevelLabels[userInfo.agent_level] }}</text>
        </view>
      </view>
      <view class="arrow" @click="goLogin">></view>
    </view>

    <!-- 资产概览 -->
    <view class="asset-card">
      <view class="asset-item" @click="goWallet">
        <text class="asset-value">{{ userInfo.balance || '0.00' }}</text>
        <text class="asset-label">余额</text>
      </view>
      <view class="asset-item">
        <text class="asset-value">{{ userInfo.contribution_value || '0' }}</text>
        <text class="asset-label">贡献值</text>
      </view>
      <view class="asset-item">
        <text class="asset-value">{{ userInfo.points || '0.00' }}</text>
        <text class="asset-label">积分</text>
      </view>
      <view class="asset-item">
        <text class="asset-value">{{ userInfo.coupon_balance || '0.00' }}</text>
        <text class="asset-label">消费券</text>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="menu-section">
      <view class="menu-item" @click="goPage('/pages/order/index')">
        <text class="menu-icon">📋</text>
        <text class="menu-text">我的订单</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="goPage('/pages/cart/index')">
        <text class="menu-icon">🛒</text>
        <text class="menu-text">购物车</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="goPage('/pages/address/index')">
        <text class="menu-icon">📍</text>
        <text class="menu-text">收货地址</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="goPage('/pages/wallet/index')">
        <text class="menu-icon">💰</text>
        <text class="menu-text">我的钱包</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="goPage('/pages/contribution/index')">
        <text class="menu-icon">🎯</text>
        <text class="menu-text">贡献值明细</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="goPage('/pages/coupon/index')">
        <text class="menu-icon">🎫</text>
        <text class="menu-text">消费券</text>
        <text class="menu-arrow">></text>
      </view>
    </view>

    <view class="menu-section">
      <view class="menu-item" @click="goPage('/pages/team/index')">
        <text class="menu-icon">👥</text>
        <text class="menu-text">我的团队</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="goPage('/pages/store/index')">
        <text class="menu-icon">🏪</text>
        <text class="menu-text">门店排名</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item agent-entry" @click="goPage('/pages/agent/index')">
        <text class="menu-icon">🤖</text>
        <text class="menu-text">我的AI助手</text>
        <view class="agent-badge"><text>智能体</text></view>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="shareInvite">
        <text class="menu-icon">🔗</text>
        <text class="menu-text">邀请好友</text>
        <text class="menu-arrow">></text>
      </view>
    </view>

    <view class="menu-section">
      <view class="menu-item" @click="goPage('/pages/settings/index')">
        <text class="menu-icon">⚙️</text>
        <text class="menu-text">设置</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="goPage('/pages/about/index')">
        <text class="menu-icon">ℹ️</text>
        <text class="menu-text">关于</text>
        <text class="menu-arrow">></text>
      </view>
    </view>
  </view>
</template>

<script>
import { getUserInfo } from '../../api/index'

export default {
  data() {
    return {
      userInfo: {},
      agentLevelLabels: {
        province: '省级代理',
        city: '市级代理',
        district: '区县代理',
        store: '门店'
      }
    }
  },
  onShow() {
    this.loadUserInfo()
  },
  methods: {
    async loadUserInfo() {
      const token = uni.getStorageSync('token')
      if (!token) {
        this.userInfo = {}
        return
      }
      try {
        const res = await getUserInfo()
        this.userInfo = res
      } catch (e) {
        this.userInfo = {}
      }
    },
    goLogin() {
      if (!this.userInfo.id) {
        uni.navigateTo({ url: '/pages/login/index' })
      }
    },
    goWallet() {
      uni.navigateTo({ url: '/pages/wallet/index' })
    },
    goPage(url) {
      uni.navigateTo({ url })
    },
    shareInvite() {
      const code = this.userInfo.id || ''
      const inviteUrl = `https://aixingmu.com/invite?code=${code}`
      uni.showActionSheet({
        itemList: ['复制邀请链接', '分享海报'],
        success: (res) => {
          if (res.tapIndex === 0) {
            uni.setClipboardData({
              data: `我在AI星木商城购物还能赚贡献值和积分，快来加入吧！\n${inviteUrl}`,
              success: () => uni.showToast({ title: '链接已复制', icon: 'success' })
            })
          } else {
            uni.showToast({ title: '海报功能开发中', icon: 'none' })
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.mine-page { background: #f5f5f5; min-height: 100vh; padding-bottom: 20px; }
.user-header { background: linear-gradient(135deg, #409eff, #67c23a); padding: 30px 20px; display: flex; align-items: center; }
.avatar-wrap { width: 60px; height: 60px; border-radius: 50%; overflow: hidden; border: 3px solid rgba(255,255,255,0.5); flex-shrink: 0; }
.avatar { width: 100%; height: 100%; }
.user-info { flex: 1; margin-left: 15px; }
.nickname { font-size: 18px; font-weight: bold; color: #fff; display: block; }
.phone { font-size: 14px; color: rgba(255,255,255,0.8); display: block; margin-top: 4px; }
.level-badge { display: inline-block; background: rgba(255,255,255,0.3); padding: 2px 10px; border-radius: 10px; margin-top: 5px; }
.level-badge text { font-size: 12px; color: #fff; }
.arrow { color: #fff; font-size: 20px; }
.asset-card { background: #fff; margin: -20px 15px 15px; border-radius: 12px; padding: 20px; display: flex; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.asset-item { flex: 1; text-align: center; }
.asset-value { font-size: 20px; font-weight: bold; color: #333; display: block; }
.asset-label { font-size: 12px; color: #999; display: block; margin-top: 4px; }
.menu-section { background: #fff; margin: 0 15px 15px; border-radius: 12px; overflow: hidden; }
.menu-item { display: flex; align-items: center; padding: 15px 16px; border-bottom: 1px solid #f5f5f5; }
.menu-item:last-child { border-bottom: none; }
.menu-icon { font-size: 20px; margin-right: 12px; }
.menu-text { flex: 1; font-size: 15px; color: #333; }
.menu-arrow { color: #ccc; font-size: 16px; }
</style>
