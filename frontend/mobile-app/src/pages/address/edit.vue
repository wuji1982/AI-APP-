<template>
  <view class="edit-page">
    <view class="form-card">
      <view class="form-item">
        <text class="label">收货人</text>
        <input v-model="form.receiver_name" placeholder="请输入收货人姓名" />
      </view>
      <view class="form-item">
        <text class="label">手机号</text>
        <input v-model="form.receiver_phone" placeholder="请输入手机号" type="number" maxlength="11" />
      </view>
      <view class="form-item">
        <text class="label">省份</text>
        <input v-model="form.province" placeholder="请输入省份" />
      </view>
      <view class="form-item">
        <text class="label">城市</text>
        <input v-model="form.city" placeholder="请输入城市" />
      </view>
      <view class="form-item">
        <text class="label">区/县</text>
        <input v-model="form.district" placeholder="请输入区县" />
      </view>
      <view class="form-item">
        <text class="label">详细地址</text>
        <input v-model="form.detail" placeholder="请输入详细地址" />
      </view>
      <view class="form-item switch-item">
        <text class="label">设为默认地址</text>
        <switch :checked="form.is_default" @change="form.is_default = $event.detail.value" color="#409eff" />
      </view>
    </view>

    <button class="save-btn" @click="saveAddress">保存</button>
  </view>
</template>

<script>
import { createAddress, updateAddress, getAddresses } from '../../api/index'

export default {
  data() {
    return {
      addressId: null,
      form: {
        receiver_name: '',
        receiver_phone: '',
        province: '',
        city: '',
        district: '',
        detail: '',
        is_default: false
      }
    }
  },
  async onLoad(options) {
    if (options.id) {
      this.addressId = parseInt(options.id)
      await this.loadAddress(this.addressId)
    }
  },
  methods: {
    async loadAddress(id) {
      try {
        const res = await getAddresses()
        const addr = (res.items || []).find(a => a.id === id)
        if (addr) {
          this.form = {
            receiver_name: addr.receiver_name,
            receiver_phone: addr.receiver_phone,
            province: addr.province,
            city: addr.city,
            district: addr.district,
            detail: addr.detail,
            is_default: addr.is_default
          }
        }
      } catch(e) {}
    },
    validate() {
      if (!this.form.receiver_name) { uni.showToast({ title: '请输入收货人', icon: 'none' }); return false }
      if (!this.form.receiver_phone || this.form.receiver_phone.length !== 11) { uni.showToast({ title: '请输入正确手机号', icon: 'none' }); return false }
      if (!this.form.province) { uni.showToast({ title: '请输入省份', icon: 'none' }); return false }
      if (!this.form.city) { uni.showToast({ title: '请输入城市', icon: 'none' }); return false }
      if (!this.form.district) { uni.showToast({ title: '请输入区县', icon: 'none' }); return false }
      if (!this.form.detail) { uni.showToast({ title: '请输入详细地址', icon: 'none' }); return false }
      return true
    },
    async saveAddress() {
      if (!this.validate()) return
      try {
        if (this.addressId) {
          await updateAddress(this.addressId, this.form)
          uni.showToast({ title: '修改成功', icon: 'success' })
        } else {
          await createAddress(this.form)
          uni.showToast({ title: '添加成功', icon: 'success' })
        }
        setTimeout(() => uni.navigateBack(), 1000)
      } catch(e) {
        uni.showToast({ title: e.message || '保存失败', icon: 'none' })
      }
    }
  }
}
</script>

<style scoped>
.edit-page { background: #f5f5f5; min-height: 100vh; padding: 15px; }
.form-card { background: #fff; border-radius: 12px; padding: 0 15px; }
.form-item { display: flex; align-items: center; padding: 14px 0; border-bottom: 1px solid #f5f5f5; }
.form-item:last-child { border-bottom: none; }
.label { width: 80px; font-size: 14px; color: #333; flex-shrink: 0; }
.form-item input { flex: 1; font-size: 14px; }
.switch-item { justify-content: space-between; }
.save-btn { margin-top: 30px; background: #409eff; color: #fff; border: none; border-radius: 25px; padding: 13px 0; font-size: 16px; font-weight: bold; }
</style>
