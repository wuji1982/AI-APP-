<template>
  <div class="products-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>商品管理</span>
          <el-button type="primary" @click="showAddDialog">添加商品</el-button>
        </div>
      </template>

      <el-table :data="products" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="商品名称" />
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag>{{ categoryLabels[row.category] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="selling_price" label="售价" width="100">
          <template #default="{ row }">¥{{ row.selling_price }}</template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="100" />
        <el-table-column prop="sales_count" label="销量" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'on_sale' ? 'success' : 'info'">
              {{ row.status === 'on_sale' ? '在售' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="editProduct(row)">编辑</el-button>
            <el-button size="small" :type="row.status === 'on_sale' ? 'danger' : 'success'" @click="toggleStatus(row)">
              {{ row.status === 'on_sale' ? '下架' : '上架' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const products = ref([])
const categoryLabels = { food: '吃', drink: '喝', use: '用', wear: '穿' }

const loadProducts = async () => {
  // TODO: 调用API
  products.value = [
    { id: 1, name: '法库啤酒6瓶装', category: 'drink', selling_price: 288, stock: 100, sales_count: 45, status: 'on_sale' }
  ]
}

const showAddDialog = () => {
  ElMessage.info('添加商品功能开发中')
}

const editProduct = (product) => {
  ElMessage.info(`编辑商品 ${product.name}`)
}

const toggleStatus = (product) => {
  ElMessage.info(`切换商品状态 ${product.name}`)
}

onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
.products-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
