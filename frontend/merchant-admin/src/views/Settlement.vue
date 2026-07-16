<template>
  <div class="settlement-page">
    <el-row :gutter="20" class="stat-row">
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">本月分润</div>
            <div class="stat-value">¥{{ stats.monthly_profit || '0.00' }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">待结算</div>
            <div class="stat-value warning">¥{{ stats.pending_amount || '0.00' }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">已结算</div>
            <div class="stat-value success">¥{{ stats.settled_amount || '0.00' }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <template #header>
        <span>分润明细</span>
      </template>

      <el-table :data="settlements" stripe>
        <el-table-column prop="settlement_no" label="结算单号" width="180" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ typeLabels[row.type] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">¥{{ row.amount }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'warning'">
              {{ row.status === 'completed' ? '已完成' : '处理中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" show-overflow-tooltip />
        <el-table-column prop="created_at" label="结算时间" width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const stats = ref({})
const settlements = ref([])
const typeLabels = { group_buy: '拼团分润', team: '团队分润', store_dividend: '门店分红' }

const loadData = async () => {
  // TODO: 调用API
  stats.value = { monthly_profit: '3560.50', pending_amount: '1200.00', settled_amount: '2360.50' }
  settlements.value = [
    { settlement_no: 'ST20240315001', type: 'group_buy', amount: '28.80', status: 'completed', remark: '拼团分润', created_at: '2024-03-15 14:30' }
  ]
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.settlement-page { padding: 20px; }
.stat-row { margin-bottom: 20px; }
.stat-item { text-align: center; }
.stat-label { font-size: 14px; color: #999; margin-bottom: 8px; }
.stat-value { font-size: 24px; font-weight: bold; color: #333; }
.stat-value.warning { color: #e6a23c; }
.stat-value.success { color: #67c23a; }
</style>
