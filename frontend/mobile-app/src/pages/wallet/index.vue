<template>
  <view class="wallet-page">
    <!-- 余额卡片 -->
    <view class="balance-card">
      <view class="balance-header">
        <text class="balance-label">余额(元)</text>
        <text class="balance-eye" @click="toggleHide">{{ showAmount ? '👁️' : '🙈' }}</text>
      </view>
      <text class="balance-amount">{{ showAmount ? formatNum(wallet.balance) : '****' }}</text>
      <view class="sub-assets">
        <view class="sub-item">
          <text class="sub-label">消费券</text>
          <text class="sub-value">{{ showAmount ? formatNum(wallet.coupon_balance) : '****' }}</text>
        </view>
        <view class="sub-item">
          <text class="sub-label">贡献值</text>
          <text class="sub-value">{{ showAmount ? formatNum(wallet.contribution_value) : '****' }}</text>
        </view>
        <view class="sub-item">
          <text class="sub-label">增值积分</text>
          <text class="sub-value">{{ showAmount ? formatNum(wallet.points) : '****' }}</text>
        </view>
      </view>
    </view>

    <!-- 快捷操作 -->
    <view class="quick-actions">
      <view class="action-btn" @click="showRechargeModal">
        <text class="action-icon">💳</text>
        <text class="action-text">充值</text>
      </view>
      <view class="action-btn" @click="showWithdrawModal">
        <text class="action-icon">💰</text>
        <text class="action-text">提现</text>
      </view>
      <view class="action-btn" @click="showConvertDialog">
        <text class="action-icon">🔄</text>
        <text class="action-text">积分兑换</text>
      </view>
      <view class="action-btn" @click="goTo('/pages/coupon/index')">
        <text class="action-icon">🎫</text>
        <text class="action-text">消费券</text>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="menu-section">
      <view class="menu-item" @click="goTo('/pages/order/index')">
        <text class="menu-icon">📋</text>
        <text class="menu-text">我的拼团订单</text>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @click="showPointsPool">
        <text class="menu-icon">📊</text>
        <text class="menu-text">积分池状态</text>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @click="goTo('/pages/contribution/index')">
        <text class="menu-icon">🎯</text>
        <text class="menu-text">贡献值明细</text>
        <text class="menu-arrow">›</text>
      </view>
    </view>

    <!-- 余额流水 -->
    <view class="logs-section">
      <view class="logs-header">
        <text class="logs-title">余额流水</text>
        <view class="logs-filter">
          <text class="filter-item" :class="{ active: logFilter === '' }" @click="filterLogs('')">全部</text>
          <text class="filter-item" :class="{ active: logFilter === 'balance' }" @click="filterLogs('balance')">余额</text>
          <text class="filter-item" :class="{ active: logFilter === 'contribution' }" @click="filterLogs('contribution')">贡献值</text>
          <text class="filter-item" :class="{ active: logFilter === 'points' }" @click="filterLogs('points')">积分</text>
          <text class="filter-item" :class="{ active: logFilter === 'coupon' }" @click="filterLogs('coupon')">消费券</text>
        </view>
      </view>

      <view class="logs-list">
        <view class="log-item" v-for="log in balanceLogs" :key="log.id">
          <view class="log-left">
            <text class="log-desc">{{ log.description || getLogDesc(log) }}</text>
            <text class="log-time">{{ formatTime(log.created_at) }}</text>
          </view>
          <view class="log-right">
            <text class="log-amount" :class="log.change_type === 'income' ? 'income' : 'expense'">
              {{ log.change_type === 'income' ? '+' : '-' }}{{ formatNum(log.amount) }}
            </text>
            <text class="log-balance">余额 ¥{{ formatNum(log.balance_after) }}</text>
          </view>
        </view>

        <view class="empty-logs" v-if="balanceLogs.length === 0 && !logsLoading">
          <text class="empty-icon">📝</text>
          <text class="empty-text">暂无流水记录</text>
        </view>

        <view class="load-more" v-if="logsLoading">
          <text>加载中...</text>
        </view>
        <view class="load-more" v-if="!logsLoading && logsNoMore && balanceLogs.length > 0">
          <text>— 没有更多了 —</text>
        </view>
      </view>
    </view>

    <!-- 充值弹窗 -->
    <view class="modal-mask" v-if="showRecharge" @click="showRecharge = false">
      <view class="modal-content" @click.stop>
        <text class="modal-title">余额充值</text>
        <view class="amount-input-wrap">
          <text class="amount-prefix">¥</text>
          <input class="amount-input" type="digit" v-model="rechargeAmount" placeholder="0.00" />
        </view>
        <view class="quick-amount">
          <text class="quick-item" @click="rechargeAmount = '100'">¥100</text>
          <text class="quick-item" @click="rechargeAmount = '500'">¥500</text>
          <text class="quick-item" @click="rechargeAmount = '1000'">¥1000</text>
          <text class="quick-item" @click="rechargeAmount = '5000'">¥5000</text>
        </view>
        <view class="modal-actions">
          <view class="modal-btn cancel" @click="showRecharge = false">取消</view>
          <view class="modal-btn confirm" @click="doRecharge">确认充值</view>
        </view>
      </view>
    </view>

    <!-- 提现弹窗 -->
    <view class="modal-mask" v-if="showWithdraw" @click="showWithdraw = false">
      <view class="modal-content" @click.stop>
        <text class="modal-title">余额提现</text>
        <text class="modal-hint">可提现余额: ¥{{ formatNum(wallet.balance) }}</text>
        <view class="amount-input-wrap">
          <text class="amount-prefix">¥</text>
          <input class="amount-input" type="digit" v-model="withdrawAmount" placeholder="0.00" />
        </view>
        <view class="modal-actions">
          <view class="modal-btn cancel" @click="showWithdraw = false">取消</view>
          <view class="modal-btn confirm" @click="doWithdraw">确认提现</view>
        </view>
      </view>
    </view>

    <!-- 积分池弹窗 -->
    <view class="modal-mask" v-if="showPool" @click="showPool = false">
      <view class="modal-content" @click.stop>
        <text class="modal-title">积分池状态</text>
        <view class="pool-info">
          <view class="pool-row"><text class="pool-label">总发行量</text><text class="pool-value">{{ poolInfo.total_supply?.toLocaleString() }}</text></view>
          <view class="pool-row"><text class="pool-label">已发放</text><text class="pool-value">{{ poolInfo.total_issued?.toLocaleString() }}</text></view>
          <view class="pool-row"><text class="pool-label">已通缩</text><text class="pool-value">{{ poolInfo.total_deflated?.toLocaleString() }}</text></view>
          <view class="pool-row"><text class="pool-label">当前单价</text><text class="pool-value">¥{{ poolInfo.current_unit_price?.toFixed(4) }}</text></view>
          <view class="pool-row"><text class="pool-label">剩余可发</text><text class="pool-value">{{ poolInfo.remaining?.toLocaleString() }}</text></view>
        </view>
        <view class="modal-footer" @click="showPool = false">关闭</view>
      </view>
    </view>
  </view>
</template>

<script>
import { getWallet, getWalletSummary, getBalanceLogs, getPointsPool, convertPoints, rechargeWallet, withdrawWallet } from '../../api/index'

export default {
  data() {
    return {
      wallet: {},
      summary: {},
      showAmount: true,
      balanceLogs: [],
      logFilter: '',
      logsLoading: false,
      logsNoMore: false,
      logsPage: 1,
      poolInfo: {},
      showPool: false,
      showRecharge: false,
      showWithdraw: false,
      rechargeAmount: '',
      withdrawAmount: '',
    }
  },
  onShow() {
    this.loadData()
  },
  onReachBottom() {
    this.loadLogs(true)
  },
  methods: {
    async loadData() {
      try {
        const [walletRes, summaryRes] = await Promise.all([
          getWallet().catch(() => ({})),
          getWalletSummary().catch(() => ({}))
        ])
        this.wallet = walletRes
        this.summary = summaryRes
        this.logsPage = 1
        this.logsNoMore = false
        this.balanceLogs = []
        this.loadLogs()
      } catch (e) {
        console.error('加载钱包数据失败', e)
      }
    },
    async loadLogs(append = false) {
      if (this.logsLoading || this.logsNoMore) return
      this.logsLoading = true
      try {
        const params = {
          asset_type: this.logFilter,
          page: this.logsPage,
          size: 20
        }
        const res = await getBalanceLogs(params)
        const items = res.items || []
        if (append) {
          if (items.length === 0) {
            this.logsNoMore = true
          } else {
            this.balanceLogs.push(...items)
          }
        } else {
          this.balanceLogs = items
          if (items.length < 20) this.logsNoMore = true
        }
      } catch (e) {
        console.error('加载流水失败', e)
      } finally {
        this.logsLoading = false
      }
    },
    filterLogs(type) {
      this.logFilter = type
      this.logsPage = 1
      this.logsNoMore = false
      this.balanceLogs = []
      this.loadLogs()
    },
    toggleHide() {
      this.showAmount = !this.showAmount
    },
    showRechargeModal() {
      this.rechargeAmount = ''
      this.showRecharge = true
    },
    showWithdrawModal() {
      this.withdrawAmount = ''
      this.showWithdraw = true
    },
    async doRecharge() {
      const amount = parseFloat(this.rechargeAmount)
      if (!amount || amount <= 0) {
        uni.showToast({ title: '请输入有效金额', icon: 'none' })
        return
      }
      try {
        const res = await rechargeWallet(amount, '余额充值')
        uni.showToast({ title: res.message || '充值成功', icon: 'success' })
        this.showRecharge = false
        this.loadData()
      } catch (e) {
        uni.showToast({ title: e.message || '充值失败', icon: 'none' })
      }
    },
    async doWithdraw() {
      const amount = parseFloat(this.withdrawAmount)
      if (!amount || amount <= 0) {
        uni.showToast({ title: '请输入有效金额', icon: 'none' })
        return
      }
      try {
        const res = await withdrawWallet(amount, '余额提现')
        uni.showToast({ title: res.message || '提现成功', icon: 'success' })
        this.showWithdraw = false
        this.loadData()
      } catch (e) {
        uni.showToast({ title: e.message || '提现失败', icon: 'none' })
      }
    },
    async showConvertDialog() {
      uni.showModal({
        title: '积分兑换消费券',
        editable: true,
        placeholderText: '请输入兑换积分数量',
        success: (res) => {
          if (res.confirm && res.content) {
            const points = parseFloat(res.content)
            if (isNaN(points) || points <= 0) {
              uni.showToast({ title: '请输入有效数量', icon: 'none' })
              return
            }
            convertPoints(points).then(() => {
              uni.showToast({ title: '兑换成功', icon: 'success' })
              this.loadData()
            }).catch(() => {
              uni.showToast({ title: '兑换失败', icon: 'none' })
            })
          }
        }
      })
    },
    async showPointsPool() {
      try {
        this.poolInfo = await getPointsPool()
        this.showPool = true
      } catch (e) {
        uni.showToast({ title: '加载失败', icon: 'none' })
      }
    },
    goTo(url) {
      uni.navigateTo({ url })
    },
    formatNum(val) {
      const num = parseFloat(val) || 0
      return num.toFixed(2)
    },
    formatTime(timeStr) {
      if (!timeStr) return ''
      const d = new Date(timeStr)
      const now = new Date()
      const diff = now - d
      if (diff < 60000) return '刚刚'
      if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
      return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
    },
    getLogDesc(log) {
      const typeMap = {
        'balance': '余额变动',
        'contribution': '贡献值变动',
        'points': '积分变动',
        'coupon': '消费券变动'
      }
      return typeMap[log.asset_type] || '资产变动'
    }
  }
}
</script>

<style scoped>
.wallet-page { background: #f5f5f5; min-height: 100vh; padding-bottom: 20px; }

/* 余额卡片 */
.balance-card { background: linear-gradient(135deg, #1a73e8, #4285f4, #669df6); padding: 28px 24px 20px; color: #fff; }
.balance-header { display: flex; justify-content: space-between; align-items: center; }
.balance-label { font-size: 14px; opacity: 0.8; }
.balance-eye { font-size: 20px; }
.balance-amount { font-size: 38px; font-weight: bold; display: block; margin: 8px 0 16px; letter-spacing: 1px; }
.sub-assets { display: flex; gap: 0; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.2); }
.sub-item { flex: 1; }
.sub-label { font-size: 11px; opacity: 0.7; display: block; }
.sub-value { font-size: 15px; font-weight: 500; display: block; margin-top: 4px; }

/* 快捷操作 */
.quick-actions { display: flex; background: #fff; margin: -12px 15px 15px; border-radius: 12px; padding: 18px 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.action-btn { flex: 1; display: flex; flex-direction: column; align-items: center; }
.action-icon { font-size: 26px; margin-bottom: 6px; }
.action-text { font-size: 12px; color: #333; }

/* 功能菜单 */
.menu-section { background: #fff; margin: 0 15px 15px; border-radius: 12px; overflow: hidden; }
.menu-item { display: flex; align-items: center; padding: 15px 16px; border-bottom: 1px solid #f5f5f5; }
.menu-item:last-child { border-bottom: none; }
.menu-icon { font-size: 20px; margin-right: 12px; }
.menu-text { flex: 1; font-size: 15px; color: #333; }
.menu-arrow { color: #ccc; font-size: 20px; }

/* 流水区域 */
.logs-section { background: #fff; margin: 0 15px 15px; border-radius: 12px; overflow: hidden; }
.logs-header { padding: 14px 16px 0; }
.logs-title { font-size: 16px; font-weight: 600; color: #333; display: block; margin-bottom: 10px; }
.logs-filter { display: flex; gap: 0; border-bottom: 1px solid #f0f0f0; }
.filter-item { padding: 8px 12px; font-size: 13px; color: #666; position: relative; }
.filter-item.active { color: #1a73e8; font-weight: 500; }
.filter-item.active::after { content: ''; position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 20px; height: 2px; background: #1a73e8; border-radius: 1px; }

.logs-list { padding: 0 16px; }
.log-item { display: flex; justify-content: space-between; align-items: center; padding: 14px 0; border-bottom: 1px solid #f8f8f8; }
.log-item:last-child { border-bottom: none; }
.log-left { flex: 1; }
.log-desc { font-size: 14px; color: #333; display: block; }
.log-time { font-size: 12px; color: #999; display: block; margin-top: 4px; }
.log-right { text-align: right; }
.log-amount { font-size: 15px; font-weight: 600; display: block; }
.log-amount.income { color: #4caf50; }
.log-amount.expense { color: #f44336; }
.log-balance { font-size: 11px; color: #999; display: block; margin-top: 2px; }

.empty-logs { text-align: center; padding: 40px 0; }
.empty-icon { font-size: 36px; display: block; }
.empty-text { font-size: 13px; color: #999; display: block; margin-top: 8px; }
.load-more { text-align: center; padding: 12px; color: #ccc; font-size: 12px; }

/* 弹窗 */
.modal-mask { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 999; }
.modal-content { background: #fff; border-radius: 16px; padding: 24px; width: 320px; }
.modal-title { font-size: 18px; font-weight: 600; color: #333; display: block; text-align: center; margin-bottom: 16px; }
.modal-hint { font-size: 13px; color: #999; display: block; text-align: center; margin-bottom: 12px; }
.amount-input-wrap { display: flex; align-items: center; background: #f5f5f5; border-radius: 8px; padding: 0 12px; height: 48px; margin-bottom: 12px; }
.amount-prefix { font-size: 20px; font-weight: bold; color: #333; margin-right: 8px; }
.amount-input { flex: 1; font-size: 24px; font-weight: bold; background: transparent; }
.quick-amount { display: flex; gap: 8px; margin-bottom: 16px; }
.quick-item { flex: 1; text-align: center; padding: 8px; background: #f5f5f5; border-radius: 6px; font-size: 13px; color: #666; }
.quick-item:active { background: #e0e0e0; }
.modal-actions { display: flex; gap: 12px; }
.modal-btn { flex: 1; height: 44px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 15px; }
.modal-btn.cancel { background: #f5f5f5; color: #666; }
.modal-btn.confirm { background: #1a73e8; color: #fff; }
.modal-footer { text-align: center; padding: 12px; margin-top: 12px; background: #f5f5f5; border-radius: 8px; font-size: 14px; color: #666; }

/* 积分池 */
.pool-info { padding: 8px 0; }
.pool-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f5f5f5; }
.pool-row:last-child { border-bottom: none; }
.pool-label { font-size: 14px; color: #666; }
.pool-value { font-size: 14px; color: #333; font-weight: 500; }
</style>
