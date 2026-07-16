<template>
  <div class="settings-page">
    <el-card>
      <template #header>
        <span>门店设置</span>
      </template>

      <el-form :model="storeInfo" label-width="120px" style="max-width: 600px">
        <el-form-item label="门店名称">
          <el-input v-model="storeInfo.name" />
        </el-form-item>
        <el-form-item label="省份">
          <el-input v-model="storeInfo.province" />
        </el-form-item>
        <el-form-item label="城市">
          <el-input v-model="storeInfo.city" />
        </el-form-item>
        <el-form-item label="区县">
          <el-input v-model="storeInfo.district" />
        </el-form-item>
        <el-form-item label="详细地址">
          <el-input v-model="storeInfo.address" type="textarea" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="storeInfo.phone" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveSettings">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const storeInfo = ref({
  name: '',
  province: '',
  city: '',
  district: '',
  address: '',
  phone: ''
})

const loadSettings = async () => {
  // TODO: 调用API加载门店信息
  storeInfo.value = {
    name: '测试门店',
    province: '辽宁省',
    city: '沈阳市',
    district: '法库县',
    address: '测试地址',
    phone: '024-12345678'
  }
}

const saveSettings = () => {
  // TODO: 调用API保存
  ElMessage.success('保存成功')
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings-page { padding: 20px; }
</style>
