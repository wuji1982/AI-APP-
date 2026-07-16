<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">今日销售额</div>
            <div class="stat-value">¥{{ stats.today_sales || '0.00' }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">今日订单</div>
            <div class="stat-value">{{ stats.today_orders || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">团队人数</div>
            <div class="stat-value">{{ stats.team_count || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">本月分润</div>
            <div class="stat-value">¥{{ stats.monthly_profit || '0.00' }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-card class="action-card">
      <template #header>
        <span>快捷操作</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-button type="primary" size="large" @click="$router.push('/products')">商品管理</el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="success" size="large" @click="$router.push('/orders')">订单管理</el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="warning" size="large" @click="$router.push('/team')">团队管理</el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="info" size="large" @click="$router.push('/settlement')">分润结算</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 最近订单 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>最近订单</span>
          <el-button type="primary" text @click="$router.push('/orders')">查看全部</el-button>
        </div>
      </template>
      <el-table :data="recentOrders" stripe>
        <el-table-column prop="order_no" label="订单号" />
        <el-table-column prop="product_name" label="商品" />
        <el-table-column prop="amount" label="金额">
          <template #default="{ row }">¥{{ row.amount }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'warning'">
              {{ row.status === 'completed' ? '已完成' : '处理中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const stats = ref({})
const recentOrders = ref([])

const loadStats = async () => {
  // TODO: 调用API加载数据
  stats.value = {
    today_sales: '12580.00',
    today_orders: 45,
    team_count: 128,
    monthly_profit: '3560.50'
  }
}

const loadRecentOrders = async () => {
  // TODO: 调用API加载数据
  recentOrders.value = [
    { order_no: 'GB20240315001', product_name: '法库啤酒6瓶装', amount: '288.00', status: 'completed', created_at: '2024-03-15 14:30' },
    { order_no: 'GB20240315002', product_name: '法库啤酒12瓶装', amount: '1440.00', status: 'pending', created_at: '2024-03-15 15:20' }
  ]
}

onMounted(() => {
  loadStats()
  loadRecentOrders()
})
</script>

<style scoped>
.dashboard { padding: 20px; }
.stat-row { margin-bottom: 20px; }
.stat-item { text-align: center; }
.stat-label { font-size: 14px; color: #999; margin-bottom: 8px; }
.stat-value { font-size: 24px; font-weight: bold; color: #333; }
.action-card { margin-bottom: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
