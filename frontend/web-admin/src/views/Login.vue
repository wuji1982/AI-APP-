<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <h1>AI星木商城</h1>
        <p>管理后台</p>
      </div>
      <el-form :model="form" :rules="rules" ref="formRef" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="管理员账号" prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" size="large" show-password @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" style="width: 100%" @click="handleLogin" :loading="loading">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-footer">
        <text>AI Agent全量赋能 · 共享商城+拼团生态</text>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '@/api'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const form = ref({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await login(form.value)
    localStorage.setItem('token', res.data.access_token)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.login-card { width: 420px; padding: 40px; background: #fff; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
.login-header { text-align: center; margin-bottom: 30px; }
.login-header h1 { font-size: 28px; color: #333; margin: 0; }
.login-header p { font-size: 14px; color: #999; margin-top: 8px; }
.login-footer { text-align: center; margin-top: 20px; }
.login-footer text { font-size: 12px; color: #ccc; }
</style>
<template><div><el-card class="login-card"><h2>AI�����̳ǹ�����̨</h2><el-form><el-form-item label="�ֻ���"><el-input v-model="phone" placeholder="�������ֻ���"/></el-form-item><el-form-item label="����"><el-input v-model="password" type="password" placeholder="����������"/></el-form-item><el-button type="primary" style="width:100%">��¼</el-button></el-form></el-card></div></template>
