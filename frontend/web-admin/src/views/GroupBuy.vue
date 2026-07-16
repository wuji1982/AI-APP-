<template>
  <div class="group-buy-page">
    <!-- 操作栏 -->
    <el-card class="action-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-button type="primary" @click="createSessions">创建今日场次</el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="success" @click="settleAll">批量结算</el-button>
        </el-col>
        <el-col :span="6">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" @change="loadSessions" />
        </el-col>
        <el-col :span="6">
          <el-select v-model="filterLevel" placeholder="级别筛选" clearable @change="loadSessions">
            <el-option label="全部" value="" />
            <el-option label="初级团" value="junior" />
            <el-option label="高级团" value="senior" />
            <el-option label="SVIP团" value="svip" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <!-- 场次列表 -->
    <el-card class="session-card">
      <template #header>
        <div class="card-header">
          <span>拼团场次</span>
          <el-tag type="info">共 {{ sessions.length }} 场</el-tag>
        </div>
      </template>
      <el-table :data="sessions" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="session_date" label="日期" width="120" />
        <el-table-column prop="start_time" label="开始时间" width="100">
          <template #default="{ row }">
            {{ formatTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="levelTag(row.level)">{{ levelLabels[row.level] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_price" label="金额" width="100">
          <template #default="{ row }">
            ¥{{ row.total_price }}
          </template>
        </el-table-column>
        <el-table-column prop="current_players" label="参团人数" width="120">
          <template #default="{ row }">
            <span :class="{ 'text-success': row.current_players >= 31 }">
              {{ row.current_players }}/{{ row.total_players }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)">{{ statusLabels[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="winner_id" label="拼中者" width="100">
          <template #default="{ row }">
            {{ row.winner_id || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
            <el-button size="small" type="primary" @click="settleSession(row)" :disabled="row.status !== 'full'">结算</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="dialogVisible" title="场次详情" width="800px">
      <div v-if="currentSession">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="场次ID">{{ currentSession.id }}</el-descriptions-item>
          <el-descriptions-item label="日期">{{ currentSession.session_date }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatTime(currentSession.start_time) }}</el-descriptions-item>
          <el-descriptions-item label="级别">{{ levelLabels[currentSession.level] }}</el-descriptions-item>
          <el-descriptions-item label="金额">¥{{ currentSession.total_price }}</el-descriptions-item>
          <el-descriptions-item label="参团人数">{{ currentSession.current_players }}/{{ currentSession.total_players }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ statusLabels[currentSession.status] }}</el-descriptions-item>
          <el-descriptions-item label="拼中者">{{ currentSession.winner_id || '待结算' }}</el-descriptions-item>
        </el-descriptions>

        <h4 style="margin-top: 20px">参团记录</h4>
        <el-table :data="currentSession.orders || []" stripe>
          <el-table-column prop="user_id" label="用户ID" width="100" />
          <el-table-column prop="order_no" label="订单号" />
          <el-table-column prop="status" label="状态">
            <template #default="{ row }">
              <el-tag :type="row.status === 'win' ? 'success' : row.status === 'lose' ? 'warning' : 'info'">
                {{ row.status === 'win' ? '拼中' : row.status === 'lose' ? '拼失败' : '待结算' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="参团时间" />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createDailySessions, settleSession as settleSessionApi, getSessions } from '@/api/groupBuy'

const sessions = ref([])
const dateRange = ref([])
const filterLevel = ref('')
const dialogVisible = ref(false)
const currentSession = ref(null)

const levelLabels = {
  junior: '初级团',
  senior: '高级团',
  svip: 'SVIP团'
}

const statusLabels = {
  pending: '待开始',
  ongoing: '进行中',
  full: '已满员',
  settled: '已结算',
  expired: '已过期'
}

const levelTag = (level) => {
  const map = { junior: '', senior: 'warning', svip: 'danger' }
  return map[level] || ''
}

const statusTag = (status) => {
  const map = { pending: 'info', ongoing: 'primary', full: 'warning', settled: 'success', expired: 'danger' }
  return map[status] || ''
}

const formatTime = (time) => {
  if (!time) return '-'
  return time.substring(11, 16)
}

const loadSessions = async () => {
  try {
    const params = {}
    if (filterLevel.value) params.level = filterLevel.value
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0].toISOString().split('T')[0]
      params.end_date = dateRange.value[1].toISOString().split('T')[0]
    }
    const res = await getSessions(params)
    sessions.value = res.items || []
  } catch (e) {
    ElMessage.error('加载场次失败')
  }
}

const createSessions = async () => {
  try {
    await ElMessageBox.confirm('确定创建今日所有拼团场次吗？', '提示', { type: 'warning' })
    await createDailySessions()
    ElMessage.success('场次创建成功')
    loadSessions()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('创建场次失败')
  }
}

const settleAll = async () => {
  try {
    await ElMessageBox.confirm('确定批量结算所有已满员场次吗？', '提示', { type: 'warning' })
    const fullSessions = sessions.value.filter(s => s.status === 'full')
    for (const session of fullSessions) {
      await settleSessionApi(session.id)
    }
    ElMessage.success(`已结算 ${fullSessions.length} 场`)
    loadSessions()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('批量结算失败')
  }
}

const settleSession = async (session) => {
  try {
    await ElMessageBox.confirm(`确定结算场次 ${session.id} 吗？`, '提示', { type: 'warning' })
    await settleSessionApi(session.id)
    ElMessage.success('结算成功')
    loadSessions()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('结算失败')
  }
}

const viewDetail = (session) => {
  currentSession.value = session
  dialogVisible.value = true
}

onMounted(() => {
  loadSessions()
})
</script>

<style scoped>
.group-buy-page { padding: 20px; }
.action-card { margin-bottom: 20px; }
.session-card { }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.text-success { color: #67c23a; font-weight: bold; }
</style>
