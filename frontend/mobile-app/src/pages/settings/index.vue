<template>
  <view class="settings-page">
    <view class="menu-section">
      <view class="menu-item" @click="goPage('/pages/address/index')">
        <text class="menu-icon">📍</text>
        <text class="menu-text">收货地址管理</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="changePassword">
        <text class="menu-icon">🔒</text>
        <text class="menu-text">修改密码</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="clearCache">
        <text class="menu-icon">🗑️</text>
        <text class="menu-text">清除缓存</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="goPage('/pages/about/index')">
        <text class="menu-icon">ℹ️</text>
        <text class="menu-text">关于我们</text>
        <text class="menu-arrow">></text>
      </view>
    </view>

    <button class="logout-btn" v-if="isLogged" @click="handleLogout">退出登录</button>
  </view>
</template>

<script>
export default {
  data() {
    return {
      isLogged: false
    }
  },
  onShow() {
    this.isLogged = !!uni.getStorageSync('token')
  },
  methods: {
    goPage(url) {
      uni.navigateTo({ url })
    },
    changePassword() {
      uni.showModal({
        title: '修改密码',
        content: '暂不支持在线修改密码，请联系客服处理',
        showCancel: false
      })
    },
    clearCache() {
      uni.showModal({
        title: '清除缓存',
        content: '确定清除本地缓存数据吗？（不会清除账号信息）',
        success: (res) => {
          if (res.confirm) {
            const token = uni.getStorageSync('token')
            const userInfo = uni.getStorageSync('user_info')
            uni.clearStorageSync()
            if (token) uni.setStorageSync('token', token)
            if (userInfo) uni.setStorageSync('user_info', userInfo)
            uni.showToast({ title: '缓存已清除', icon: 'success' })
          }
        }
      })
    },
    handleLogout() {
      uni.showModal({
        title: '退出登录',
        content: '确定退出登录吗？',
        success: (res) => {
          if (res.confirm) {
            uni.removeStorageSync('token')
            uni.removeStorageSync('user_info')
            uni.showToast({ title: '已退出', icon: 'success' })
            setTimeout(() => {
              uni.switchTab({ url: '/pages/mine/index' })
            }, 1000)
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.settings-page { background: #f5f5f5; min-height: 100vh; padding: 15px 0; }
.menu-section { background: #fff; margin: 0 15px 15px; border-radius: 12px; overflow: hidden; }
.menu-item { display: flex; align-items: center; padding: 15px 16px; border-bottom: 1px solid #f5f5f5; }
.menu-item:last-child { border-bottom: none; }
.menu-icon { font-size: 20px; margin-right: 12px; }
.menu-text { flex: 1; font-size: 15px; color: #333; }
.menu-arrow { color: #ccc; font-size: 16px; }
.logout-btn { margin: 30px 15px; background: #fff; color: #f56c6c; border: 1px solid #f56c6c; border-radius: 25px; padding: 12px 0; font-size: 15px; }
</style>
