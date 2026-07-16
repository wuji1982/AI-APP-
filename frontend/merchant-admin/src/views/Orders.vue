<template>
  <div class="orders-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>订单管理</span>
          <div>
            <el-select v-model="filterStatus" placeholder="状态筛选" clearable @change="loadOrders">
              <el-option label="全部" value="" />
              <el-option label="待处理" value="pending" />
              <el-option label="已完成" value="completed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table :data="orders" stripe>
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="product_name" label="商品" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">¥{{ row.amount }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)">{{ statusLabels[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="下单时间" width="180" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" @current-change="loadOrders" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const orders = ref([])
const filterStatus = ref('')
const page = ref(1)
const total = ref(0)

const statusLabels = { pending: '待处理', completed: '已完成', cancelled: '已取消' }
const statusTag = (status) => {
  const map = { pending: 'warning', completed: 'success', cancelled: 'info' }
  return map[status] || ''
}

const loadOrders = async () => {
  // TODO: 调用API
  orders.value = [
    { order_no: 'GB20240315001', product_name: '法库啤酒6瓶装', quantity: 1, amount: '288.00', status: 'completed', created_at: '2024-03-15 14:30' }
  ]
}

const viewDetail = (order) => {
  ElMessage.info(`查看订单 ${order.order_no}`)
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.orders-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
