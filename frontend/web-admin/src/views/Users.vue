<template>
  <div class="users-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-input v-model="searchKeyword" placeholder="搜索手机号/昵称" style="width: 250px" clearable @change="loadUsers">
            <template #append>
              <el-button @click="loadUsers">搜索</el-button>
            </template>
          </el-input>
        </div>
      </template>

      <el-table :data="users" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="nickname" label="昵称" />
        <el-table-column prop="agent_level" label="代理级别" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.agent_level" :type="levelTag(row.agent_level)">
              {{ levelLabels[row.agent_level] || row.agent_level }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="balance" label="余额" width="100">
          <template #default="{ row }">¥{{ row.balance || 0 }}</template>
        </el-table-column>
        <el-table-column prop="contribution_value" label="贡献值" width="100">
          <template #default="{ row }">{{ row.contribution_value || 0 }}</template>
        </el-table-column>
        <el-table-column prop="points" label="积分" width="100">
          <template #default="{ row }">{{ row.points || 0 }}</template>
        </el-table-column>
        <el-table-column prop="coupon_balance" label="消费券" width="100">
          <template #default="{ row }">{{ row.coupon_balance || 0 }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180" />
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
            <el-button size="small" :type="row.status === 'active' ? 'danger' : 'success'" @click="toggleStatus(row)">
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" layout="total, sizes, prev, pager, next" @size-change="loadUsers" @current-change="loadUsers" />
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="dialogVisible" title="用户详情" width="700px">
      <div v-if="currentUser">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户ID">{{ currentUser.id }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ currentUser.phone }}</el-descriptions-item>
          <el-descriptions-item label="昵称">{{ currentUser.nickname }}</el-descriptions-item>
          <el-descriptions-item label="代理级别">{{ levelLabels[currentUser.agent_level] || '普通用户' }}</el-descriptions-item>
          <el-descriptions-item label="余额">¥{{ currentUser.balance }}</el-descriptions-item>
          <el-descriptions-item label="贡献值">{{ currentUser.contribution_value }}</el-descriptions-item>
          <el-descriptions-item label="积分">{{ currentUser.points }}</el-descriptions-item>
          <el-descriptions-item label="消费券">{{ currentUser.coupon_balance }}</el-descriptions-item>
          <el-descriptions-item label="推荐人">{{ currentUser.referrer_id || '无' }}</el-descriptions-item>
          <el-descriptions-item label="邀请码">{{ currentUser.invite_code }}</el-descriptions-item>
          <el-descriptions-item label="注册时间">{{ currentUser.created_at }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ currentUser.status === 'active' ? '正常' : '禁用' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUsers, toggleUserStatus } from '@/api'

const users = ref([])
const searchKeyword = ref('')
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const currentUser = ref(null)

const levelLabels = {
  province: '省级代理',
  city: '市级代理',
  district: '区县代理',
  store: '门店'
}

const levelTag = (level) => {
  const map = { province: 'danger', city: 'warning', district: '', store: 'success' }
  return map[level] || ''
}

const loadUsers = async () => {
  try {
    const res = await getUsers({ page: page.value, size: pageSize.value, keyword: searchKeyword.value })
    users.value = res.items || []
    total.value = res.total || 0
  } catch (e) {
    ElMessage.error('加载用户失败')
  }
}

const viewDetail = (user) => {
  currentUser.value = user
  dialogVisible.value = true
}

const toggleStatus = async (user) => {
  const action = user.status === 'active' ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确定${action}用户 ${user.phone} 吗？`, '提示', { type: 'warning' })
    await toggleUserStatus(user.id)
    ElMessage.success(`${action}成功`)
    loadUsers()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(`${action}失败`)
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.users-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
<template><div><el-card><template #header>�û�����</template><p>�û��б�/��ɫ����/�Ƽ���ϵ</p></el-card></div></template>
