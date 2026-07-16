<template>
  <view class="address-page">
    <!-- 地址列表 -->
    <view class="address-list" v-if="addresses.length > 0">
      <view class="address-card" v-for="addr in addresses" :key="addr.id" @click="selectAddress(addr)">
        <view class="addr-info">
          <view class="addr-top">
            <text class="addr-name">{{ addr.receiver_name }}</text>
            <text class="addr-phone">{{ addr.receiver_phone }}</text>
            <text class="default-tag" v-if="addr.is_default">默认</text>
          </view>
          <text class="addr-detail">{{ addr.province }}{{ addr.city }}{{ addr.district }} {{ addr.detail }}</text>
        </view>
        <view class="addr-actions">
          <view class="action-item" @click.stop="setDefault(addr)" v-if="!addr.is_default">
            <text>设为默认</text>
          </view>
          <view class="action-item" @click.stop="editAddress(addr)">
            <text>编辑</text>
          </view>
          <view class="action-item danger" @click.stop="deleteAddr(addr)">
            <text>删除</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <text class="empty-icon">📍</text>
      <text class="empty-text">暂无收货地址</text>
    </view>

    <!-- 新增地址按钮 -->
    <view class="add-btn-wrap">
      <button class="add-btn" @click="addAddress">+ 新增收货地址</button>
    </view>
  </view>
</template>

<script>
import { getAddresses, deleteAddress, setDefaultAddress } from '../../api/index'

export default {
  data() {
    return {
      addresses: [],
      isSelectMode: false  // 从结算页进入时为选择模式
    }
  },
  onLoad(options) {
    this.isSelectMode = options.select === '1'
  },
  onShow() {
    this.loadAddresses()
  },
  methods: {
    async loadAddresses() {
      const token = uni.getStorageSync('token')
      if (!token) { uni.navigateTo({ url: '/pages/login/index' }); return }
      try {
        const res = await getAddresses()
        this.addresses = res.items || []
      } catch(e) {
        uni.showToast({ title: '请先登录', icon: 'none' })
      }
    },
    selectAddress(addr) {
      if (this.isSelectMode) {
        // 返回结算页并传递地址
        const pages = getCurrentPages()
        const prevPage = pages[pages.length - 2]
        if (prevPage) {
          prevPage.$vm && prevPage.$vm.setSelectedAddress && prevPage.$vm.setSelectedAddress(addr)
        }
        uni.navigateBack()
      }
    },
    async setDefault(addr) {
      try {
        await setDefaultAddress(addr.id)
        uni.showToast({ title: '已设为默认', icon: 'success' })
        this.loadAddresses()
      } catch(e) {}
    },
    editAddress(addr) {
      uni.navigateTo({ url: `/pages/address/edit?id=${addr.id}` })
    },
    async deleteAddr(addr) {
      uni.showModal({
        title: '提示',
        content: '确定删除该地址吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await deleteAddress(addr.id)
              uni.showToast({ title: '已删除', icon: 'success' })
              this.loadAddresses()
            } catch(e) {}
          }
        }
      })
    },
    addAddress() {
      uni.navigateTo({ url: '/pages/address/edit' })
    }
  }
}
</script>

<style scoped>
.address-page { background: #f5f5f5; min-height: 100vh; padding-bottom: 80px; }
.address-list { padding: 10px; }
.address-card { background: #fff; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
.addr-top { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.addr-name { font-size: 16px; font-weight: bold; }
.addr-phone { font-size: 14px; color: #666; }
.default-tag { font-size: 11px; background: #409eff; color: #fff; padding: 1px 6px; border-radius: 3px; }
.addr-detail { font-size: 14px; color: #666; line-height: 1.5; }
.addr-actions { display: flex; justify-content: flex-end; gap: 20px; margin-top: 12px; padding-top: 10px; border-top: 1px solid #f5f5f5; }
.action-item text { font-size: 13px; color: #409eff; }
.action-item.danger text { color: #f56c6c; }
.empty-state { text-align: center; padding: 80px 0; }
.empty-icon { font-size: 60px; display: block; }
.empty-text { font-size: 15px; color: #999; display: block; margin-top: 15px; }
.add-btn-wrap { position: fixed; bottom: 0; left: 0; right: 0; padding: 12px 15px; background: #fff; box-shadow: 0 -2px 8px rgba(0,0,0,0.06); }
.add-btn { background: #409eff; color: #fff; border: none; border-radius: 25px; padding: 12px 0; font-size: 15px; font-weight: bold; }
</style>
