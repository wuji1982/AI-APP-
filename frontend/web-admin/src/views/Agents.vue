<template>
  <div class="agents-page">
    <!-- Agent 状态概览 -->
    <el-row :gutter="20" class="agent-row">
      <el-col :span="6" v-for="agent in agents" :key="agent.name">
        <el-card shadow="hover" class="agent-card">
          <div class="agent-header">
            <div class="agent-icon">{{ agent.icon }}</div>
            <div class="agent-info">
              <div class="agent-name">{{ agent.label }}</div>
              <div class="agent-status">
                <el-tag :type="agent.status === 'running' ? 'success' : agent.status === 'error' ? 'danger' : 'info'" size="small">
                  {{ statusLabels[agent.status] }}
                </el-tag>
              </div>
            </div>
          </div>
          <div class="agent-stats">
            <div class="stat-row">
              <span class="stat-label">今日执行次数</span>
              <span class="stat-value">{{ agent.today_executions || 0 }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">成功率</span>
              <span class="stat-value">{{ agent.success_rate || 0 }}%</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">最后执行</span>
              <span class="stat-value">{{ agent.last_execution || '从未' }}</span>
            </div>
          </div>
          <div class="agent-actions">
            <el-button size="small" type="primary" @click="runAgent(agent)" :disabled="agent.status === 'running'">手动执行</el-button>
            <el-button size="small" @click="viewLogs(agent)">日志</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 执行日志 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Agent 执行日志</span>
          <div>
            <el-select v-model="filterAgent" placeholder="Agent筛选" clearable @change="loadLogs">
              <el-option label="全部" value="" />
              <el-option v-for="agent in agents" :key="agent.name" :label="agent.label" :value="agent.name" />
            </el-select>
            <el-button type="primary" @click="runAllAgents" style="margin-left: 10px">全部执行</el-button>
          </div>
        </div>
      </template>

      <el-table :data="logs" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="agent_name" label="Agent" width="120">
          <template #default="{ row }">
            <el-tag>{{ agentLabel(row.agent_name) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="动作" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : row.status === 'failed' ? 'danger' : 'warning'">
              {{ row.status === 'success' ? '成功' : row.status === 'failed' ? '失败' : '执行中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="100">
          <template #default="{ row }">{{ row.duration }}ms</template>
        </el-table-column>
        <el-table-column prop="result" label="结果" show-overflow-tooltip />
        <el-table-column prop="created_at" label="执行时间" width="180" />
      </el-table>

      <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" @current-change="loadLogs" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAgentStatus, runAgentApi, getAgentLogs } from '@/api'

const agents = ref([
  { name: 'group_buy', label: '拼团调度Agent', icon: '🎯', status: 'idle', today_executions: 0, success_rate: 0, last_execution: null },
  { name: 'settlement', label: '分账结算Agent', icon: '💰', status: 'idle', today_executions: 0, success_rate: 0, last_execution: null },
  { name: 'rights', label: '权益核算Agent', icon: '📊', status: 'idle', today_executions: 0, success_rate: 0, last_execution: null },
  { name: 'dividend', label: '分红结算Agent', icon: '💎', status: 'idle', today_executions: 0, success_rate: 0, last_execution: null },
  { name: 'user_ops', label: '用户运营Agent', icon: '👥', status: 'idle', today_executions: 0, success_rate: 0, last_execution: null },
  { name: 'team', label: '团队管理Agent', icon: '🏪', status: 'idle', today_executions: 0, success_rate: 0, last_execution: null },
  { name: 'risk', label: '风控Agent', icon: '🛡️', status: 'idle', today_executions: 0, success_rate: 0, last_execution: null }
])

const logs = ref([])
const filterAgent = ref('')
const page = ref(1)
const total = ref(0)

const statusLabels = {
  running: '运行中',
  idle: '空闲',
  error: '异常'
}

const agentLabel = (name) => {
  const agent = agents.value.find(a => a.name === name)
  return agent ? agent.label : name
}

const loadAgentStatus = async () => {
  try {
    const res = await getAgentStatus()
    agents.value.forEach(agent => {
      const status = res[agent.name]
      if (status) {
        Object.assign(agent, status)
      }
    })
  } catch (e) {
    console.error('加载Agent状态失败', e)
  }
}

const loadLogs = async () => {
  try {
    const res = await getAgentLogs({ page: page.value, agent_name: filterAgent.value })
    logs.value = res.items || []
    total.value = res.total || 0
  } catch (e) {
    ElMessage.error('加载日志失败')
  }
}

const runAgent = async (agent) => {
  try {
    await ElMessageBox.confirm(`确定手动执行 ${agent.label} 吗？`, '提示', { type: 'warning' })
    agent.status = 'running'
    await runAgentApi(agent.name)
    ElMessage.success('执行成功')
    loadAgentStatus()
    loadLogs()
  } catch (e) {
    if (e !== 'cancel') {
      agent.status = 'error'
      ElMessage.error('执行失败')
    }
  }
}

const runAllAgents = async () => {
  try {
    await ElMessageBox.confirm('确定执行所有Agent吗？', '提示', { type: 'warning' })
    agents.value.forEach(a => a.status = 'running')
    for (const agent of agents.value) {
      await runAgentApi(agent.name)
    }
    ElMessage.success('全部执行成功')
    loadAgentStatus()
    loadLogs()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('执行失败')
  }
}

const viewLogs = (agent) => {
  filterAgent.value = agent.name
  loadLogs()
}

onMounted(() => {
  loadAgentStatus()
  loadLogs()
})
</script>

<style scoped>
.agents-page { padding: 20px; }
.agent-row { margin-bottom: 20px; }
.agent-card { height: 100%; }
.agent-header { display: flex; align-items: center; margin-bottom: 15px; }
.agent-icon { font-size: 36px; margin-right: 15px; }
.agent-info { flex: 1; }
.agent-name { font-size: 16px; font-weight: bold; margin-bottom: 5px; }
.agent-stats { margin-bottom: 15px; }
.stat-row { display: flex; justify-content: space-between; padding: 5px 0; font-size: 13px; }
.stat-label { color: #999; }
.stat-value { color: #333; font-weight: 500; }
.agent-actions { display: flex; gap: 10px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
<template><div><el-card><template #header>AI Agent����</template><p>7��Agent״̬���/�ֶ�����/��־�鿴</p></el-card></div></template>
