<template>
  <div class="risk-page">
    <!-- 风控概览 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">今日风控拦截</div>
            <div class="stat-value danger">{{ riskStats.today_blocks || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">黑名单用户</div>
            <div class="stat-value">{{ riskStats.blacklist_count || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">高风险用户</div>
            <div class="stat-value warning">{{ riskStats.high_risk_count || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">平均风险评分</div>
            <div class="stat-value">{{ riskStats.avg_risk_score || 0 }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 风控日志 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>风控日志</span>
          <div>
            <el-select v-model="filterRule" placeholder="规则筛选" clearable @change="loadLogs">
              <el-option label="全部" value="" />
              <el-option label="单ID限购" value="order_limit" />
              <el-option label="黑名单" value="blacklist" />
              <el-option label="风险评分" value="risk_score" />
              <el-option label="异常行为" value="abnormal_behavior" />
            </el-select>
            <el-button type="danger" @click="showBlacklistDialog" style="margin-left: 10px">黑名单管理</el-button>
          </div>
        </div>
      </template>

      <el-table :data="logs" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user_id" label="用户ID" width="100" />
        <el-table-column prop="rule_type" label="触发规则" width="120">
          <template #default="{ row }">
            <el-tag :type="ruleTag(row.rule_type)">{{ ruleLabels[row.rule_type] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="动作" width="100">
          <template #default="{ row }">
            <el-tag :type="row.action === 'block' ? 'danger' : 'warning'">
              {{ row.action === 'block' ? '拦截' : '警告' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="risk_score" label="风险评分" width="100">
          <template #default="{ row }">
            <span :class="{ 'text-danger': row.risk_score > 70, 'text-warning': row.risk_score > 50 }">
              {{ row.risk_score }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="detail" label="详情" show-overflow-tooltip />
        <el-table-column prop="created_at" label="触发时间" width="180" />
      </el-table>

      <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" @current-change="loadLogs" />
    </el-card>

    <!-- 黑名单弹窗 -->
    <el-dialog v-model="blacklistDialogVisible" title="黑名单管理" width="700px">
      <el-button type="primary" @click="addToBlacklist" style="margin-bottom: 15px">添加黑名单</el-button>
      <el-table :data="blacklist" stripe>
        <el-table-column prop="user_id" label="用户ID" width="100" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="reason" label="原因" />
        <el-table-column prop="created_at" label="加入时间" width="180" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="removeFromBlacklist(row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRiskLogs, getRiskStats, getBlacklist, addToBlacklistApi, removeFromBlacklistApi } from '@/api'

const riskStats = ref({})
const logs = ref([])
const filterRule = ref('')
const page = ref(1)
const total = ref(0)
const blacklistDialogVisible = ref(false)
const blacklist = ref([])

const ruleLabels = {
  order_limit: '单ID限购',
  blacklist: '黑名单',
  risk_score: '风险评分',
  abnormal_behavior: '异常行为'
}

const ruleTag = (rule) => {
  const map = { order_limit: 'warning', blacklist: 'danger', risk_score: '', abnormal_behavior: 'info' }
  return map[rule] || ''
}

const loadStats = async () => {
  try {
    const res = await getRiskStats()
    riskStats.value = res
  } catch (e) {
    console.error('加载统计失败', e)
  }
}

const loadLogs = async () => {
  try {
    const res = await getRiskLogs({ page: page.value, rule_type: filterRule.value })
    logs.value = res.items || []
    total.value = res.total || 0
  } catch (e) {
    ElMessage.error('加载风控日志失败')
  }
}

const showBlacklistDialog = async () => {
  blacklistDialogVisible.value = true
  try {
    const res = await getBlacklist()
    blacklist.value = res.items || []
  } catch (e) {
    ElMessage.error('加载黑名单失败')
  }
}

const addToBlacklist = async () => {
  try {
    const { value } = await ElMessageBox.prompt('请输入用户ID', '添加黑名单', {
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    await addToBlacklistApi(value)
    ElMessage.success('添加成功')
    showBlacklistDialog()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('添加失败')
  }
}

const removeFromBlacklist = async (item) => {
  try {
    await ElMessageBox.confirm(`确定移除用户 ${item.phone} 吗？`, '提示', { type: 'warning' })
    await removeFromBlacklistApi(item.user_id)
    ElMessage.success('移除成功')
    showBlacklistDialog()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('移除失败')
  }
}

onMounted(() => {
  loadStats()
  loadLogs()
})
</script>

<style scoped>
.risk-page { padding: 20px; }
.stat-row { margin-bottom: 20px; }
.stat-item { text-align: center; }
.stat-label { font-size: 14px; color: #999; margin-bottom: 8px; }
.stat-value { font-size: 24px; font-weight: bold; color: #333; }
.stat-value.danger { color: #f56c6c; }
.stat-value.warning { color: #e6a23c; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.text-danger { color: #f56c6c; font-weight: bold; }
.text-warning { color: #e6a23c; font-weight: bold; }
</style>
<template><div><el-card><template #header>�������</template><p>�����־/������/�쳣���</p></el-card></div></template>
