<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">今日拼团场次</div>
            <div class="stat-value">{{ stats.todaySessions }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">今日交易金额</div>
            <div class="stat-value">¥{{ stats.todayAmount?.toLocaleString() }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">全网总贡献值</div>
            <div class="stat-value">{{ stats.totalContrib?.toLocaleString() }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">积分池剩余</div>
            <div class="stat-value">{{ stats.pointsRemaining?.toLocaleString() }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header><span>拼团场次实时状态</span></template>
          <el-table :data="sessions" stripe>
            <el-table-column prop="session_no" label="场次编号" />
            <el-table-column prop="level" label="级别">
              <template #default="{ row }">
                <el-tag :type="row.level === 'svip' ? 'danger' : row.level === 'senior' ? 'warning' : 'info'">
                  {{ row.level }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="current_players" label="当前人数" />
            <el-table-column prop="total_players" label="总人数" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : row.status === 'full' ? 'danger' : 'info'">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span>AI Agent 运行状态</span></template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="拼团调度Agent"><el-tag type="success">运行中</el-tag></el-descriptions-item>
            <el-descriptions-item label="智能分账Agent"><el-tag type="success">运行中</el-tag></el-descriptions-item>
            <el-descriptions-item label="权益核算Agent"><el-tag type="success">运行中</el-tag></el-descriptions-item>
            <el-descriptions-item label="分红结算Agent"><el-tag type="success">运行中</el-tag></el-descriptions-item>
            <el-descriptions-item label="用户运营Agent"><el-tag type="success">运行中</el-tag></el-descriptions-item>
            <el-descriptions-item label="团队管理Agent"><el-tag type="success">运行中</el-tag></el-descriptions-item>
            <el-descriptions-item label="智能风控Agent"><el-tag type="success">运行中</el-tag></el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getActiveSessions } from '../api/groupBuy'

const stats = ref({
  todaySessions: 0,
  todayAmount: 0,
  totalContrib: 0,
  pointsRemaining: 12000000,
})
const sessions = ref([])

onMounted(async () => {
  try {
    const res = await getActiveSessions()
    sessions.value = res.items || []
    stats.value.todaySessions = sessions.value.length
  } catch (e) {
    console.error('加载数据失败', e)
  }
})
</script>

<style scoped>
.stat-cards .el-card { text-align: center; }
.stat-label { font-size: 14px; color: #999; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: bold; color: #303133; }
</style>
