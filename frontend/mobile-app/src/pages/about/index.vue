<template>
  <view class="about-page">
    <view class="logo-section">
      <view class="logo-circle">
        <text class="logo-text">AI</text>
      </view>
      <text class="app-name">AI星木商城</text>
      <text class="version">v1.0.0</text>
    </view>

    <view class="info-card">
      <view class="info-item">
        <text class="info-label">平台简介</text>
        <text class="info-value">AI星木商城是基于 AI Agent 技术的共享电商平台，融合拼团生态、贡献值体系与智能推荐，为用户提供智能化购物体验。</text>
      </view>
      <view class="info-item">
        <text class="info-label">技术支持</text>
        <text class="info-value">LangGraph + Dify 多租户智能体架构</text>
      </view>
      <view class="info-item">
        <text class="info-label">联系方式</text>
        <text class="info-value">service@aixingmu.com</text>
      </view>
      <view class="info-item">
        <text class="info-label">官方网站</text>
        <text class="info-value">www.aixingmu.com</text>
      </view>
    </view>

    <view class="links-section">
      <view class="link-item" @click="openLink('user-agreement')">
        <text>用户协议</text>
        <text class="arrow">></text>
      </view>
      <view class="link-item" @click="openLink('privacy')">
        <text>隐私政策</text>
        <text class="arrow">></text>
      </view>
      <view class="link-item" @click="openLink('license')">
        <text>开源许可</text>
        <text class="arrow">></text>
      </view>
    </view>

    <text class="copyright">Copyright 2024 AI星木商城 All Rights Reserved</text>
  </view>
</template>

<script>
export default {
  methods: {
    openLink(type) {
      const titles = {
        'user-agreement': '用户协议',
        'privacy': '隐私政策',
        'license': '开源许可'
      }
      uni.showModal({
        title: titles[type] || '提示',
        content: '该页面内容正在完善中，敬请期待。',
        showCancel: false
      })
    }
  }
}
</script>

<style scoped>
.about-page { background: #f5f5f5; min-height: 100vh; }
.logo-section { text-align: center; padding: 50px 0 30px; background: #fff; }
.logo-circle { width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, #409eff, #67c23a); display: flex; align-items: center; justify-content: center; margin: 0 auto 15px; }
.logo-text { color: #fff; font-size: 28px; font-weight: bold; }
.app-name { font-size: 20px; font-weight: bold; color: #333; display: block; }
.version { font-size: 13px; color: #999; display: block; margin-top: 4px; }
.info-card { background: #fff; margin-top: 10px; padding: 15px; }
.info-item { padding: 12px 0; border-bottom: 1px solid #f5f5f5; }
.info-item:last-child { border-bottom: none; }
.info-label { font-size: 14px; color: #999; display: block; margin-bottom: 5px; }
.info-value { font-size: 14px; color: #333; line-height: 1.5; }
.links-section { background: #fff; margin-top: 10px; }
.link-item { display: flex; justify-content: space-between; align-items: center; padding: 15px; border-bottom: 1px solid #f5f5f5; font-size: 15px; color: #333; }
.link-item:last-child { border-bottom: none; }
.arrow { color: #ccc; }
.copyright { text-align: center; padding: 30px 15px; font-size: 12px; color: #ccc; display: block; }
</style>
