<template>
  <div class="settlement-page">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">今日分润总额</div>
            <div class="stat-value">¥{{ stats.daily_total || '0.00' }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">本月分润总额</div>
            <div class="stat-value">¥{{ stats.monthly_total || '0.00' }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">待结算金额</div>
            <div class="stat-value warning">¥{{ stats.pending_amount || '0.00' }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">已结算金额</div>
            <div class="stat-value success">¥{{ stats.settled_amount || '0.00' }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分润记录 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>分润结算记录</span>
          <div>
            <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" @change="loadSettlements" />
            <el-select v-model="filterType" placeholder="类型筛选" clearable @change="loadSettlements" style="margin-left: 10px">
              <el-option label="全部" value="" />
              <el-option label="拼团分润" value="group_buy" />
              <el-option label="门店分红" value="store_dividend" />
              <el-option label="代理分润" value="agent_commission" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table :data="settlements" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="settlement_no" label="结算单号" width="180" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="typeTag(row.type)">{{ typeLabels[row.type] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="user_id" label="用户ID" width="100" />
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">
            <span class="amount">¥{{ row.amount }}</span>
          </template>
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

      <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" @current-change="loadSettlements" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSettlements, getSettlementStats } from '@/api'

const stats = ref({})
const settlements = ref([])
const dateRange = ref([])
const filterType = ref('')
const page = ref(1)
const total = ref(0)

const typeLabels = {
  group_buy: '拼团分润',
  store_dividend: '门店分红',
  agent_commission: '代理分润'
}

const typeTag = (type) => {
  const map = { group_buy: '', store_dividend: 'success', agent_commission: 'warning' }
  return map[type] || ''
}

const loadStats = async () => {
  try {
    const res = await getSettlementStats()
    stats.value = res
  } catch (e) {
    console.error('加载统计失败', e)
  }
}

const loadSettlements = async () => {
  try {
    const params = { page: page.value, type: filterType.value }
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0].toISOString().split('T')[0]
      params.end_date = dateRange.value[1].toISOString().split('T')[0]
    }
    const res = await getSettlements(params)
    settlements.value = res.items || []
    total.value = res.total || 0
  } catch (e) {
    ElMessage.error('加载分润记录失败')
  }
}

onMounted(() => {
  loadStats()
  loadSettlements()
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
.card-header { display: flex; justify-content: space-between; align-items: center; }
.amount { color: #f56c6c; font-weight: bold; }
</style>
<template><div><el-card><template #header>�������</template><p>�����¼/��������/�ŵ���ݷֺ�</p></el-card></div></template>
