<template>
  <view class="login-page">
    <view class="login-header">
      <text class="app-name">AI星木商城</text>
      <text class="app-slogan">共享商城 · 拼团生态</text>
    </view>

    <view class="login-form">
      <!-- 登录/注册切换 -->
      <view class="tab-switch">
        <text :class="{ active: mode === 'login' }" @click="mode = 'login'">登录</text>
        <text :class="{ active: mode === 'register' }" @click="mode = 'register'">注册</text>
      </view>

      <!-- 手机号 -->
      <view class="form-item">
        <input type="number" v-model="form.phone" placeholder="请输入手机号" maxlength="11" />
      </view>

      <!-- 密码 -->
      <view class="form-item">
        <input type="password" v-model="form.password" placeholder="请输入密码" />
      </view>

      <!-- 确认密码（注册时） -->
      <view class="form-item" v-if="mode === 'register'">
        <input type="password" v-model="form.confirm_password" placeholder="请确认密码" />
      </view>

      <!-- 邀请码（注册时） -->
      <view class="form-item" v-if="mode === 'register'">
        <input type="text" v-model="form.invite_code" placeholder="邀请码（选填）" />
      </view>

      <!-- 验证码 -->
      <view class="form-item code-item">
        <input type="number" v-model="form.code" placeholder="验证码" maxlength="6" />
        <button class="code-btn" :disabled="countdown > 0" @click="sendCode">
          {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
        </button>
      </view>

      <!-- 登录按钮 -->
      <button class="submit-btn" @click="handleSubmit">
        {{ mode === 'login' ? '登录' : '注册' }}
      </button>

      <!-- 其他登录方式 -->
      <view class="other-login">
        <text class="other-text">其他登录方式</text>
        <view class="other-icons">
          <text class="icon-btn">微信</text>
          <text class="icon-btn">Apple</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { login, register } from '../../api/index'
import { useIMStore } from '@/stores/im'

export default {
  data() {
    return {
      mode: 'login',
      form: {
        phone: '',
        password: '',
        confirm_password: '',
        invite_code: '',
        code: ''
      },
      countdown: 0,
      timer: null
    }
  },
  onLoad(options) {
    if (options.invite_code) {
      this.form.invite_code = options.invite_code
      this.mode = 'register'
    }
  },
  methods: {
    async sendCode() {
      if (!this.form.phone || this.form.phone.length !== 11) {
        uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
        return
      }
      uni.showToast({ title: '验证码已发送', icon: 'success' })
      this.countdown = 60
      this.timer = setInterval(() => {
        this.countdown--
        if (this.countdown <= 0) {
          clearInterval(this.timer)
        }
      }, 1000)
    },
    async handleSubmit() {
      if (!this.form.phone || this.form.phone.length !== 11) {
        uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
        return
      }
      if (!this.form.password) {
        uni.showToast({ title: '请输入密码', icon: 'none' })
        return
      }
      if (this.mode === 'register' && this.form.password !== this.form.confirm_password) {
        uni.showToast({ title: '两次密码不一致', icon: 'none' })
        return
      }

      try {
        if (this.mode === 'login') {
          const res = await login({
            phone: this.form.phone,
            password: this.form.password
          })
          uni.setStorageSync('token', res.access_token)
          uni.setStorageSync('user_id', res.user_id)

          // 尝试登录IM
          if (res.im_token) {
            uni.setStorageSync('im_token', res.im_token)
            try {
              const imStore = useIMStore()
              await imStore.login(String(res.user_id), res.im_token)
            } catch (e) {
              console.warn('IM登录失败:', e)
            }
          }

          uni.showToast({ title: '登录成功', icon: 'success' })
          setTimeout(() => {
            uni.switchTab({ url: '/pages/index/index' })
          }, 1500)
        } else {
          const res = await register({
            phone: this.form.phone,
            password: this.form.password,
            invite_code: this.form.invite_code,
            code: this.form.code
          })
          uni.setStorageSync('token', res.access_token)
          uni.setStorageSync('user_id', res.user_id)
          if (res.im_token) {
            uni.setStorageSync('im_token', res.im_token)
          }
          uni.showToast({ title: '注册成功', icon: 'success' })
          setTimeout(() => {
            this.mode = 'login'
          }, 1500)
        }
      } catch (e) {
        uni.showToast({ title: e.message || '操作失败', icon: 'none' })
      }
    }
  }
}
</script>

<style scoped>
.login-page { background: #fff; min-height: 100vh; padding: 0 30px; }
.login-header { text-align: center; padding: 80px 0 40px; }
.app-name { font-size: 32px; font-weight: bold; color: #409eff; display: block; }
.app-slogan { font-size: 14px; color: #999; display: block; margin-top: 8px; }
.tab-switch { display: flex; justify-content: center; gap: 40px; margin-bottom: 30px; }
.tab-switch text { font-size: 18px; color: #999; padding-bottom: 8px; }
.tab-switch text.active { color: #409eff; font-weight: bold; border-bottom: 2px solid #409eff; }
.form-item { margin-bottom: 20px; }
.form-item input { border: 1px solid #eee; border-radius: 8px; padding: 14px 16px; font-size: 15px; }
.code-item { display: flex; gap: 10px; }
.code-item input { flex: 1; }
.code-btn { background: #409eff; color: #fff; border: none; border-radius: 8px; padding: 0 20px; font-size: 14px; white-space: nowrap; }
.code-btn[disabled] { background: #ccc; }
.submit-btn { background: linear-gradient(135deg, #409eff, #67c23a); color: #fff; border: none; border-radius: 25px; padding: 14px 0; font-size: 16px; font-weight: bold; margin-top: 30px; }
.other-login { text-align: center; margin-top: 50px; }
.other-text { font-size: 13px; color: #999; display: block; margin-bottom: 20px; }
.other-icons { display: flex; justify-content: center; gap: 30px; }
.icon-btn { font-size: 14px; color: #666; padding: 10px 20px; border: 1px solid #eee; border-radius: 20px; }
</style>
