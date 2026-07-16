/**
 * uni-app API 请求封装
 */
const BASE_URL = '/api/v1'

const request = (options) => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.header
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          uni.removeStorageSync('token')
          uni.navigateTo({ url: '/pages/login/index' })
          reject(new Error('未登录'))
        } else {
          reject(new Error(res.data?.detail || '请求失败'))
        }
      },
      fail: (err) => reject(err)
    })
  })
}

// 认证
export const login = (data) => request({ url: '/auth/login', method: 'POST', data })
export const register = (data) => request({ url: '/auth/register', method: 'POST', data })

// 拼团
export const getSessions = (level) => request({ url: '/group-buy/sessions', data: { level } })
export const joinGroupBuy = (sessionId) => request({ url: '/group-buy/join', method: 'POST', data: { session_id: sessionId } })
export const getMyOrders = (page = 1, size = 20) => request({ url: `/group-buy/orders?page=${page}&size=${size}` })

// 商品
export const getProducts = (params = {}) => request({ url: '/product/list', data: params })
export const getProductDetail = (id) => request({ url: `/product/${id}` })
export const searchProducts = (params = {}) => request({ url: '/product/search', data: params })
export const getRecommended = (size = 10) => request({ url: `/product/recommended?size=${size}` })

// 购物车
export const getCart = () => request({ url: '/cart/list' })
export const addToCart = (data) => request({ url: '/cart/add', method: 'POST', data })
export const updateCart = (itemId, quantity) => request({ url: `/cart/${itemId}`, method: 'PUT', data: { quantity } })
export const removeCartItem = (itemId) => request({ url: `/cart/${itemId}`, method: 'DELETE' })
export const selectCartItems = (itemIds) => request({ url: '/cart/select', method: 'POST', data: itemIds })
export const selectAllCart = (selected = true) => request({ url: `/cart/select-all?selected=${selected}`, method: 'POST' })

// 收货地址
export const getAddresses = () => request({ url: '/address/list' })
export const createAddress = (data) => request({ url: '/address', method: 'POST', data })
export const updateAddress = (id, data) => request({ url: `/address/${id}`, method: 'PUT', data })
export const deleteAddress = (id) => request({ url: `/address/${id}`, method: 'DELETE' })
export const setDefaultAddress = (id) => request({ url: `/address/${id}/default`, method: 'POST' })

// 收藏
export const addFavorite = (productId) => request({ url: `/favorite/${productId}`, method: 'POST' })
export const removeFavorite = (productId) => request({ url: `/favorite/${productId}`, method: 'DELETE' })
export const checkFavorite = (productId) => request({ url: `/favorite/check/${productId}` })

// 订单
export const createOrder = (data) => request({ url: '/order/create', method: 'POST', data })
export const getOrderList = (params = {}) => request({ url: '/order/list', data: params })
export const getOrderDetail = (orderId) => request({ url: `/order/${orderId}` })
export const cancelOrder = (orderId) => request({ url: `/order/${orderId}/cancel`, method: 'POST' })
export const confirmReceive = (orderId) => request({ url: `/order/${orderId}/confirm`, method: 'POST' })

// 评价
export const getProductReviews = (productId, page = 1) => request({ url: `/review/product/${productId}?page=${page}` })
export const createReview = (data) => request({ url: '/review', method: 'POST', data })

// 用户
export const getUserInfo = () => request({ url: '/user/me' })
export const getWallet = () => request({ url: '/user/wallet' })

// 贡献值
export const getMyContributions = () => request({ url: '/contribution/my' })

// 积分
export const getPointsPool = () => request({ url: '/points/pool' })
export const convertPoints = (amount) => request({ url: '/points/convert', method: 'POST', data: { points_amount: amount } })

// 消费券
export const getMyCoupons = () => request({ url: '/coupon/my' })

// 门店
export const getStoreRanking = (yearMonth) => request({ url: `/store/ranking?year_month=${yearMonth}` })
export const getMyTeam = (level) => request({ url: `/store/team?level=${level}` })

// Banner/公告
export const getBanners = (position = 'home') => request({ url: `/banner/list?position=${position}` })
export const getAnnouncements = (page = 1) => request({ url: `/announcement/list?page=${page}` })

export default request
