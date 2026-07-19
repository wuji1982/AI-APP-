/**
 * OpenIM JSSDK 封装
 * 用于H5端的即时通讯SDK封装
 * 使用动态导入避免 Vite 预构建超时
 */

// 动态加载 SDK，避免阻塞页面
let _sdkModule = null
async function _loadSDKModule() {
  if (!_sdkModule) {
    try {
      _sdkModule = await import('@openim/client-sdk')
    } catch (e) {
      console.warn('[IM SDK] 加载失败，IM功能不可用:', e)
      _sdkModule = { getSDK: () => null, CbEvents: {} }
    }
  }
  return _sdkModule
}

// OpenIM 服务器配置（从环境变量或默认值获取）
const IM_CONFIG = {
  wsAddr: 'ws://localhost:10001',
  apiAddr: 'http://localhost:10002',
  platformID: 5, // 5 = H5
}

let IMSDK = null
let _isLogin = false
let _listeners = new Map()
let _CbEvents = {}

/**
 * 获取SDK实例（单例）
 */
export async function getIMSDK() {
  if (!IMSDK) {
    const mod = await _loadSDKModule()
    _CbEvents = mod.CbEvents || {}
    if (mod.getSDK) {
      IMSDK = mod.getSDK()
    }
  }
  return IMSDK
}

/**
 * 获取事件常量（异步）
 */
export async function getCbEvents() {
  await _loadSDKModule()
  return _CbEvents
}

/**
 * 生成唯一操作ID
 */
export function uuid() {
  return `${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
}

/**
 * 登录IM
 * @param {string} userID - 用户ID
 * @param {string} token - IM Token（从后端获取）
 * @returns {Promise<boolean>}
 */
export async function imLogin(userID, token) {
  const sdk = await getIMSDK()
  if (!sdk) return false
  try {
    await sdk.login({
      userID,
      token,
      wsAddr: IM_CONFIG.wsAddr,
      apiAddr: IM_CONFIG.apiAddr,
      platformID: IM_CONFIG.platformID,
    }, uuid())
    _isLogin = true
    console.log('[IM] 登录成功:', userID)
    return true
  } catch (e) {
    console.warn('[IM] 登录失败:', e)
    _isLogin = false
    return false
  }
}

/**
 * 登出IM
 */
export async function imLogout() {
  if (!_isLogin) return
  const sdk = await getIMSDK()
  if (!sdk) return
  try {
    await sdk.logout(uuid())
    _isLogin = false
    console.log('[IM] 已登出')
  } catch (e) {
    console.warn('[IM] 登出异常:', e)
  }
}

/**
 * 订阅IM事件
 * @param {CbEvents} event - 事件名
 * @param {Function} handler - 处理函数
 */
export async function imOn(event, handler) {
  const sdk = await getIMSDK()
  if (!sdk) return
  sdk.on(event, handler)
  if (!_listeners.has(event)) {
    _listeners.set(event, [])
  }
  _listeners.get(event).push(handler)
}

/**
 * 取消订阅IM事件
 */
export async function imOff(event, handler) {
  const sdk = await getIMSDK()
  if (!sdk) return
  sdk.off(event, handler)
  const handlers = _listeners.get(event)
  if (handlers) {
    const idx = handlers.indexOf(handler)
    if (idx > -1) handlers.splice(idx, 1)
  }
}

/**
 * 清除所有监听
 */
export async function imOffAll() {
  const sdk = await getIMSDK()
  if (!sdk) { _listeners.clear(); return }
  _listeners.forEach((handlers, event) => {
    handlers.forEach(h => sdk.off(event, h))
  })
  _listeners.clear()
}

// ========== 会话 API ==========

/**
 * 获取会话列表（分页）
 */
export async function getConversationList(offset = 0, count = 50) {
  const sdk = await getIMSDK()
  if (!sdk) return []
  const res = await sdk.getConversationListSplit({ offset, count }, uuid())
  return res.data || []
}

/**
 * 获取总未读数
 */
export async function getTotalUnreadCount() {
  const sdk = await getIMSDK()
  if (!sdk) return 0
  const res = await sdk.getTotalUnreadMsgCount(uuid())
  return res.data || 0
}

/**
 * 标记会话已读
 */
export async function markConversationRead(conversationID) {
  const sdk = await getIMSDK()
  await sdk.markConversationMessageAsRead(conversationID, uuid())
}

/**
 * 删除会话
 */
export async function deleteConversation(conversationID) {
  const sdk = await getIMSDK()
  if (!sdk) return
  await sdk.deleteConversationAndDeleteAllMsg(conversationID, uuid())
}

// ========== 好友 API ==========

/**
 * 获取好友列表（分页）
 */
export async function getFriendList(offset = 0, count = 100) {
  const sdk = await getIMSDK()
  if (!sdk) return []
  const res = await sdk.getFriendListPage({ offset, count }, uuid())
  return res.data || []
}

/**
 * 获取好友申请列表（收到的）
 */
export async function getFriendApplicationsReceived(offset = 0, count = 20) {
  const sdk = await getIMSDK()
  if (!sdk) return []
  const res = await sdk.getFriendApplicationListAsRecipient({ offset, count }, uuid())
  return res.data || []
}

/**
 * 获取好友申请列表（发出的）
 */
export async function getFriendApplicationsSent(offset = 0, count = 20) {
  const sdk = await getIMSDK()
  if (!sdk) return []
  const res = await sdk.getFriendApplicationListAsApplicant({ offset, count }, uuid())
  return res.data || []
}

/**
 * 发起好友申请
 */
export async function addFriend(toUserID, reqMsg = '') {
  const sdk = await getIMSDK()
  if (!sdk) return
  await sdk.addFriend({ toUserID, reqMsg }, uuid())
}

/**
 * 接受好友申请
 */
export async function acceptFriendApplication(toUserID, handleMsg = '') {
  const sdk = await getIMSDK()
  if (!sdk) return
  await sdk.acceptFriendApplication({ toUserID, handleMsg }, uuid())
}

/**
 * 拒绝好友申请
 */
export async function refuseFriendApplication(toUserID, handleMsg = '') {
  const sdk = await getIMSDK()
  if (!sdk) return
  await sdk.refuseFriendApplication({ toUserID, handleMsg }, uuid())
}

/**
 * 删除好友
 */
export async function deleteFriend(friendUserID) {
  const sdk = await getIMSDK()
  if (!sdk) return
  await sdk.deleteFriend(friendUserID, uuid())
}

/**
 * 设置好友备注
 */
export async function updateFriendRemark(friendUserIDs, remark) {
  const sdk = await getIMSDK()
  if (!sdk) return
  await sdk.updateFriends({ friendUserIDs, remark }, uuid())
}

/**
 * 获取黑名单列表
 */
export async function getBlackList(offset = 0, count = 100) {
  const sdk = await getIMSDK()
  if (!sdk) return []
  const res = await sdk.getBlackList({ offset, count }, uuid())
  return res.data || []
}

/**
 * 加入黑名单
 */
export async function addBlack(toUserID) {
  const sdk = await getIMSDK()
  if (!sdk) return
  await sdk.addBlack({ toUserID }, uuid())
}

// ========== 消息 API ==========

/**
 * 创建文本消息
 */
export async function createTextMessage(text) {
  const sdk = await getIMSDK()
  if (!sdk) return null
  const res = await sdk.createTextMessage(text, uuid())
  return res.data
}

/**
 * 创建图片消息
 */
export async function createImageMessage(sourcePicture, bigPicture, snapshotPicture, sourcePath) {
  const sdk = await getIMSDK()
  if (!sdk) return null
  const res = await sdk.createImageMessageByURL({
    sourcePicture, bigPicture, snapshotPicture, sourcePath
  }, uuid())
  return res.data
}

/**
 * 发送消息（单聊/群聊）
 * @param {string} recvID - 接收者ID（单聊）
 * @param {string} groupID - 群组ID（群聊）
 * @param {MessageItem} message - 消息对象
 */
export async function sendMessage(recvID, groupID, message) {
  const sdk = await getIMSDK()
  if (!sdk) return null
  const res = await sdk.sendMessage({ recvID, groupID, message }, uuid())
  return res.data
}

/**
 * 获取历史消息
 */
export async function getHistoryMessages(conversationID, count = 20, startClientMsgID = '') {
  const sdk = await getIMSDK()
  const res = await sdk.getAdvancedHistoryMessageList({
    conversationID,
    count,
    startClientMsgID,
    viewType: 0,
  }, uuid())
  return res.data
}

/**
 * 删除消息
 */
export async function deleteMessage(conversationID, clientMsgID) {
  const sdk = await getIMSDK()
  await sdk.deleteMessage({ conversationID, clientMsgID }, uuid())
}

/**
 * 撤回消息
 */
export async function revokeMessage(conversationID, clientMsgID) {
  const sdk = await getIMSDK()
  await sdk.revokeMessage({ conversationID, clientMsgID }, uuid())
}

// ========== 群组 API ==========

/**
 * 获取已加入的群组列表
 */
export async function getJoinedGroupList(offset = 0, count = 100) {
  const sdk = await getIMSDK()
  const res = await sdk.getJoinedGroupListPage({ offset, count }, uuid())
  return res.data || []
}

/**
 * 获取群成员列表
 */
export async function getGroupMembers(groupID) {
  const sdk = await getIMSDK()
  const res = await sdk.getGroupMemberList({ groupID, filter: 0, offset: 0, count: 200 }, uuid())
  return res.data || []
}

// ========== 用户 API ==========

/**
 * 获取当前登录用户信息
 */
export async function getSelfUserInfo() {
  const sdk = await getIMSDK()
  const res = await sdk.getSelfUserInfo(uuid())
  return res.data
}

/**
 * 搜索用户
 */
export async function getUsersInfo(userIDs) {
  const sdk = await getIMSDK()
  const res = await sdk.getUsersInfo(userIDs, uuid())
  return res.data || []
}

// ========== 状态 ==========

export function isIMLogin() {
  return _isLogin
}

export const CbEvents = new Proxy({}, { get: (_, k) => _CbEvents[k] || k })
