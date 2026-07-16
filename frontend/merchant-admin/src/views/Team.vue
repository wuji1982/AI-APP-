<template>
  <div class="team-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>团队管理</span>
          <el-button type="primary" @click="inviteMember">邀请成员</el-button>
        </div>
      </template>

      <el-table :data="teamMembers" stripe>
        <el-table-column prop="user_id" label="用户ID" width="100" />
        <el-table-column prop="nickname" label="昵称" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="level" label="层级" width="100">
          <template #default="{ row }">
            <el-tag :type="levelTag(row.level)">{{ levelLabels[row.level] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_orders" label="订单数" width="100" />
        <el-table-column prop="total_amount" label="贡献金额" width="120">
          <template #default="{ row }">¥{{ row.total_amount }}</template>
        </el-table-column>
        <el-table-column prop="joined_at" label="加入时间" width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const teamMembers = ref([])
const levelLabels = { direct: '直属', indirect_1: '间接1层', indirect_2: '间接2层' }
const levelTag = (level) => {
  const map = { direct: 'danger', indirect_1: 'warning', indirect_2: '' }
  return map[level] || ''
}

const loadTeam = async () => {
  // TODO: 调用API
  teamMembers.value = [
    { user_id: 1001, nickname: '张三', phone: '138****1234', level: 'direct', total_orders: 15, total_amount: '4320.00', joined_at: '2024-01-15' }
  ]
}

const inviteMember = () => {
  ElMessage.info('邀请成员功能开发中')
}

onMounted(() => {
  loadTeam()
})
</script>

<style scoped>
.team-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
