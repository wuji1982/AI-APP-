<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <h2>AI共享商城</h2>
        <span>管理后台</span>
      </div>
      <el-menu :default-active="activeMenu" router class="sidebar-menu">
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据看板</span>
        </el-menu-item>
        <el-menu-item index="/group-buy">
          <el-icon><ShoppingCart /></el-icon>
          <span>拼团管理</span>
        </el-menu-item>
        <el-menu-item index="/products">
          <el-icon><Goods /></el-icon>
          <span>商品管理</span>
        </el-menu-item>
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/stores">
          <el-icon><Shop /></el-icon>
          <span>门店管理</span>
        </el-menu-item>
        <el-menu-item index="/settlement">
          <el-icon><Money /></el-icon>
          <span>分润结算</span>
        </el-menu-item>
        <el-menu-item index="/risk">
          <el-icon><Warning /></el-icon>
          <span>风控中心</span>
        </el-menu-item>
        <el-menu-item index="/agents">
          <el-icon><Cpu /></el-icon>
          <span>AI Agent</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">管理员</span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { DataAnalysis, ShoppingCart, Goods, User, Shop, Money, Warning, Cpu } from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.layout-container { height: 100vh; }
.sidebar { background: #1d1e1f; color: #fff; }
.logo { padding: 20px; text-align: center; border-bottom: 1px solid #333; }
.logo h2 { margin: 0; font-size: 18px; color: #409eff; }
.logo span { font-size: 12px; color: #999; }
.sidebar-menu { border-right: none; background: #1d1e1f; }
.sidebar-menu .el-menu-item { color: #ccc; }
.sidebar-menu .el-menu-item.is-active { color: #409eff; background: #263445; }
.header { background: #fff; border-bottom: 1px solid #eee; display: flex; align-items: center; justify-content: flex-end; }
.user-info { cursor: pointer; font-size: 14px; }
.main-content { background: #f5f7fa; }
</style>
