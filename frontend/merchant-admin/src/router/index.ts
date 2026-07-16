import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', component: () => import('@/views/Dashboard.vue'), meta: { title: '数据概览' } },
      { path: 'products', component: () => import('@/views/Products.vue'), meta: { title: '商品管理' } },
      { path: 'orders', component: () => import('@/views/Orders.vue'), meta: { title: '订单管理' } },
      { path: 'team', component: () => import('@/views/Team.vue'), meta: { title: '团队管理' } },
      { path: 'settlement', component: () => import('@/views/Settlement.vue'), meta: { title: '分润结算' } },
      { path: 'settings', component: () => import('@/views/Settings.vue'), meta: { title: '门店设置' } }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
