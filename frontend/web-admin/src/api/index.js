import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

// 请求拦截器: 自动附加Token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ========== 认证 ==========
export const login = (data) => api.post('/auth/login', data)
export const register = (data) => api.post('/auth/register', data)

// ========== 拼团 ==========
export const getActiveSessions = (level) => api.get('/group-buy/sessions', { params: { level } })
export const joinGroupBuy = (sessionId) => api.post('/group-buy/join', { session_id: sessionId })
export const getMyOrders = (page, size) => api.get('/group-buy/orders', { params: { page, size } })

// ========== 商品 ==========
export const getProducts = (params) => api.get('/product/list', { params })

// ========== 用户 ==========
export const getUserInfo = () => api.get('/user/me')
export const getWallet = () => api.get('/user/wallet')

// ========== 贡献值 ==========
export const getMyContributions = () => api.get('/contribution/my')
export const getTotalContrib = () => api.get('/contribution/total')

// ========== 积分 ==========
export const getPointsPool = () => api.get('/points/pool')
export const convertPoints = (amount) => api.post('/points/convert', { points_amount: amount })

// ========== 消费券 ==========
export const getMyCoupons = () => api.get('/coupon/my')

// ========== 门店 ==========
export const getStoreList = (params) => api.get('/store/list', { params })
export const getStoreRanking = (yearMonth) => api.get('/store/ranking', { params: { year_month: yearMonth } })
export const getMyTeam = (level) => api.get('/store/team', { params: { level } })

// ========== 管理后台 ==========
export const adminCreateSessions = (date) => api.post('/admin/group-buy/create-sessions', null, { params: { date } })
export const adminSettleSession = (sessionId) => api.post(`/admin/group-buy/settle/${sessionId}`)
export const adminWeeklyDividend = () => api.post('/admin/dividend/weekly')
export const adminRiskLogs = (page, size) => api.get('/admin/risk/logs', { params: { page, size } })

// ========== 拼团管理 (web-admin专用) ==========
export const createDailySessions = () => api.post('/admin/group-buy/create-sessions')
export const settleSession = (sessionId) => api.post(`/admin/group-buy/settle/${sessionId}`)
export const getSessions = (params) => api.get('/group-buy/sessions', { params })

// ========== 用户管理 ==========
export const getUsers = (params) => api.get('/admin/users', { params })
export const toggleUserStatus = (userId) => api.post(`/admin/users/${userId}/toggle-status`)

// ========== 门店管理 ==========
export const getStores = (params) => api.get('/store/list', { params })
export const getStoreTeam = (storeId) => api.get(`/store/${storeId}/team`)

// ========== 分润结算 ==========
export const getSettlements = (params) => api.get('/admin/settlements', { params })
export const getSettlementStats = () => api.get('/admin/settlements/stats')

// ========== 风控管理 ==========
export const getRiskLogs = (params) => api.get('/admin/risk/logs', { params })
export const getRiskStats = () => api.get('/admin/risk/stats')
export const getBlacklist = () => api.get('/admin/risk/blacklist')
export const addToBlacklistApi = (userId) => api.post('/admin/risk/blacklist', { user_id: userId })
export const removeFromBlacklistApi = (userId) => api.delete(`/admin/risk/blacklist/${userId}`)

// ========== Agent管理 ==========
export const getAgentStatus = () => api.get('/admin/agents/status')
export const runAgentApi = (agentName) => api.post(`/admin/agents/${agentName}/run`)
export const getAgentLogs = (params) => api.get('/admin/agents/logs', { params })

export default api
