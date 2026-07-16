import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
      { path: 'group-buy', name: 'GroupBuy', component: () => import('../views/GroupBuy.vue') },
      { path: 'products', name: 'Products', component: () => import('../views/Products.vue') },
      { path: 'users', name: 'Users', component: () => import('../views/Users.vue') },
      { path: 'stores', name: 'Stores', component: () => import('../views/Stores.vue') },
      { path: 'settlement', name: 'Settlement', component: () => import('../views/Settlement.vue') },
      { path: 'risk', name: 'Risk', component: () => import('../views/Risk.vue') },
      { path: 'agents', name: 'Agents', component: () => import('../views/Agents.vue') },
    ]
  }
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
