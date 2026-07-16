<template>
  <div class="stores-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>门店管理</span>
          <div>
            <el-select v-model="filterCity" placeholder="城市筛选" clearable @change="loadStores">
              <el-option label="全部" value="" />
              <el-option v-for="city in cities" :key="city" :label="city" :value="city" />
            </el-select>
            <el-button type="primary" @click="showAddDialog" style="margin-left: 10px">添加门店</el-button>
          </div>
        </div>
      </template>

      <el-table :data="stores" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="门店名称" />
        <el-table-column prop="province" label="省" width="100" />
        <el-table-column prop="city" label="市" width="100" />
        <el-table-column prop="district" label="区县" width="120" />
        <el-table-column prop="owner_id" label="店主ID" width="100" />
        <el-table-column prop="team_count" label="团队人数" width="100">
          <template #default="{ row }">{{ row.team_count || 0 }}</template>
        </el-table-column>
        <el-table-column prop="monthly_sales" label="月销售额" width="120">
          <template #default="{ row }">¥{{ row.monthly_sales || 0 }}</template>
        </el-table-column>
        <el-table-column prop="dividend_rate" label="分红比例" width="100">
          <template #default="{ row }">
            <el-tag type="success">{{ row.dividend_rate || 0 }}%</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '营业中' : '已关闭' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewTeam(row)">团队</el-button>
            <el-button size="small" type="primary" @click="editStore(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 团队弹窗 -->
    <el-dialog v-model="teamDialogVisible" title="门店团队" width="800px">
      <el-table :data="teamMembers" stripe>
        <el-table-column prop="user_id" label="用户ID" width="100" />
        <el-table-column prop="nickname" label="昵称" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="level" label="层级" width="100">
          <template #default="{ row }">
            <el-tag :type="levelTag(row.level)">{{ levelLabels[row.level] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="joined_at" label="加入时间" width="180" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getStores, getStoreTeam } from '@/api'

const stores = ref([])
const filterCity = ref('')
const cities = ref(['北京', '上海', '广州', '深圳', '杭州'])
const teamDialogVisible = ref(false)
const teamMembers = ref([])

const levelLabels = {
  direct: '直属',
  indirect_1: '间接1层',
  indirect_2: '间接2层',
  indirect_3: '间接3层'
}

const levelTag = (level) => {
  const map = { direct: 'danger', indirect_1: 'warning', indirect_2: '', indirect_3: 'info' }
  return map[level] || ''
}

const loadStores = async () => {
  try {
    const res = await getStores({ city: filterCity.value })
    stores.value = res.items || []
  } catch (e) {
    ElMessage.error('加载门店失败')
  }
}

const viewTeam = async (store) => {
  try {
    const res = await getStoreTeam(store.id)
    teamMembers.value = res.members || []
    teamDialogVisible.value = true
  } catch (e) {
    ElMessage.error('加载团队失败')
  }
}

const showAddDialog = () => {
  ElMessage.info('添加门店功能开发中')
}

const editStore = (store) => {
  ElMessage.info(`编辑门店 ${store.name}`)
}

onMounted(() => {
  loadStores()
})
</script>

<style scoped>
.stores-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
<template><div><el-card><template #header>�ŵ����</template><p>�ŵ��б�/���/ҵ��ͳ��</p></el-card></div></template>
