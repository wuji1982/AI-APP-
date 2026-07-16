/**
 * IM即时通讯状态管理
 * 管理IM连接状态、会话列表、好友列表、消息等
 */
import { defineStore } from 'pinia'
import {
  imLogin, imLogout, imOn, imOffAll, isIMLogin,
  getConversationList, getTotalUnreadCount, markConversationRead, deleteConversation,
  getFriendList, getFriendApplicationsReceived, addFriend, acceptFriendApplication,
  refuseFriendApplication, deleteFriend, updateFriendRemark, addBlack, getBlackList,
  createTextMessage, sendMessage, getHistoryMessages, deleteMessage,
  getJoinedGroupList, getGroupMembers, getSelfUserInfo,
  CbEvents,
} from '@/utils/im-sdk'

export const useIMStore = defineStore('im', {
  state: () => ({
    // 连接状态
    connected: false,
    connecting: false,
    loginStatus: false, // IM SDK登录状态
    currentUserID: '',

    // 会话列表
    conversations: [],
    totalUnread: 0,

    // 好友
    friends: [],
    friendApplications: [], // 收到的好友申请
    blackList: [],

    // 群组
    joinedGroups: [],

    // 当前聊天消息
    currentMessages: [],
    currentConversationID: '',
    hasMoreMessages: true,

    // 用户信息
    selfInfo: null,

    // 降级标记（OpenIM未部署时使用mock数据）
    useMock: false,
  }),

  getters: {
    // 未读会话数
    unreadConversations: (state) => state.conversations.filter(c => c.unreadCount > 0),

    // 好友总数
    friendCount: (state) => state.friends.length,

    // 待处理好友申请数
    pendingFriendRequests: (state) => state.friendApplications.filter(a => a.handleResult === 0).length,
  },

  actions: {
    // ========== 连接管理 ==========

    /**
     * 登录IM
     */
    async login(userID, token) {
      this.currentUserID = userID
      this.connecting = true

      try {
        const success = await imLogin(userID, token)
        if (success) {
          this.loginStatus = true
          this.useMock = false
          this._setupListeners()
          // 加载初始数据
          await this._loadInitialData()
        } else {
          // SDK登录失败，降级到mock模式
          console.warn('[IM Store] SDK登录失败，启用mock模式')
          this.useMock = true
          this._loadMockData()
        }
      } catch (e) {
        console.warn('[IM Store] 登录异常，启用mock模式:', e)
        this.useMock = true
        this._loadMockData()
      } finally {
        this.connecting = false
      }
    },

    /**
     * 登出IM
     */
    async logout() {
      imOffAll()
      await imLogout()
      this.$reset()
    },

    /**
     * 设置SDK事件监听
     */
    _setupListeners() {
      // 连接成功
      imOn(CbEvents.OnConnectSuccess, () => {
        this.connected = true
        console.log('[IM] 连接成功')
      })

      // 连接中
      imOn(CbEvents.OnConnecting, () => {
        this.connecting = true
      })

      // 连接失败
      imOn(CbEvents.OnConnectFailed, (data) => {
        this.connected = false
        this.connecting = false
        console.warn('[IM] 连接失败:', data)
      })

      // 被踢下线
      imOn(CbEvents.OnKickedOffline, () => {
        this.connected = false
        this.loginStatus = false
        uni.showToast({ title: '您已被踢下线', icon: 'none' })
      })

      // Token过期
      imOn(CbEvents.OnUserTokenExpired, () => {
        this.connected = false
        this.loginStatus = false
        uni.showToast({ title: 'Token已过期，请重新登录', icon: 'none' })
      })

      // 新会话
      imOn(CbEvents.OnNewConversation, (data) => {
        const newConvs = data || []
        this.conversations = [...newConvs, ...this.conversations]
      })

      // 会话更新
      imOn(CbEvents.OnConversationChanged, (data) => {
        const changedConvs = data || []
        changedConvs.forEach(updated => {
          const idx = this.conversations.findIndex(c => c.conversationID === updated.conversationID)
          if (idx > -1) {
            this.conversations[idx] = updated
          } else {
            this.conversations.unshift(updated)
          }
        })
      })

      // 收到新消息
      imOn(CbEvents.OnRecvNewMessage, (data) => {
        const msg = data
        if (msg && this.currentConversationID) {
          // 如果当前正在查看该会话，追加消息
          const convID = msg.groupID
            ? `sg_${msg.groupID}`
            : `c2c_${msg.sendID === this.currentUserID ? msg.recvID : msg.sendID}`
          if (convID === this.currentConversationID) {
            this.currentMessages.push(msg)
          }
        }
        // 刷新未读数
        this.refreshUnreadCount()
      })

      // 总未读数变化
      imOn(CbEvents.OnTotalUnreadMessageCountChanged, (count) => {
        this.totalUnread = count || 0
      })

      // 好友申请
      imOn(CbEvents.OnFriendApplicationAdded, (data) => {
        this.friendApplications.unshift(data)
      })

      // 好友申请被接受
      imOn(CbEvents.OnFriendApplicationAccepted, () => {
        this.refreshFriends()
      })

      // 新好友
      imOn(CbEvents.OnFriendAdded, (data) => {
        this.friends.push(data)
      })

      // 好友删除
      imOn(CbEvents.OnFriendDeleted, (data) => {
        this.friends = this.friends.filter(f => f.userID !== data.userID)
      })

      // 新群组
      imOn(CbEvents.OnJoinedGroupAdded, (data) => {
        this.joinedGroups.push(data)
      })
    },

    // ========== 数据加载 ==========

    async _loadInitialData() {
      try {
        const [convs, friends, apps, groups, selfInfo] = await Promise.allSettled([
          getConversationList(0, 50),
          getFriendList(0, 200),
          getFriendApplicationsReceived(0, 20),
          getJoinedGroupList(0, 50),
          getSelfUserInfo(),
        ])
        if (convs.status === 'fulfilled') this.conversations = convs.value
        if (friends.status === 'fulfilled') this.friends = friends.value
        if (apps.status === 'fulfilled') this.friendApplications = apps.value
        if (groups.status === 'fulfilled') this.joinedGroups = groups.value
        if (selfInfo.status === 'fulfilled') this.selfInfo = selfInfo.value
        await this.refreshUnreadCount()
      } catch (e) {
        console.warn('[IM Store] 加载初始数据失败:', e)
      }
    },

    _loadMockData() {
      // OpenIM未部署时的mock数据
      this.conversations = [
        { conversationID: 'c2c_1', conversationType: 1, userID: '1', showName: '张三', faceURL: '', unreadCount: 3, latestMsg: '好的，明天见', latestMsgSendTime: Date.now() - 3600000 },
        { conversationID: 'sg_group_buy_1001', conversationType: 3, groupID: 'group_buy_1001', showName: '精酿啤酒拼团 #1001', faceURL: '', unreadCount: 5, latestMsg: '恭喜大家拼团成功！', latestMsgSendTime: Date.now() },
        { conversationID: 'c2c_2', conversationType: 1, userID: '2', showName: '李四', faceURL: '', unreadCount: 0, latestMsg: '消费券还有吗？', latestMsgSendTime: Date.now() - 86400000 },
      ]
      this.friends = [
        { userID: '1', nickname: '张三', faceURL: '', remark: '' },
        { userID: '2', nickname: '李四', faceURL: '', remark: '同事' },
        { userID: '3', nickname: '王五', faceURL: '', remark: '' },
      ]
      this.friendApplications = [
        { fromUserID: '6', fromNickname: '赵六', fromFaceURL: '', reqMsg: '我是您推荐的好友', handleResult: 0 },
      ]
      this.totalUnread = 8
    },

    // ========== 会话操作 ==========

    async refreshConversations() {
      if (this.useMock) return
      try {
        this.conversations = await getConversationList(0, 50)
      } catch (e) {
        console.warn('[IM Store] 刷新会话列表失败:', e)
      }
    },

    async refreshUnreadCount() {
      if (this.useMock) {
        this.totalUnread = this.conversations.reduce((sum, c) => sum + (c.unreadCount || 0), 0)
        return
      }
      try {
        this.totalUnread = await getTotalUnreadCount()
      } catch (e) {
        console.warn('[IM Store] 获取未读数失败:', e)
      }
    },

    async markAsRead(conversationID) {
      if (this.useMock) {
        const conv = this.conversations.find(c => c.conversationID === conversationID)
        if (conv) conv.unreadCount = 0
        return
      }
      try {
        await markConversationRead(conversationID)
      } catch (e) {
        console.warn('[IM Store] 标记已读失败:', e)
      }
    },

    async removeConversation(conversationID) {
      if (this.useMock) {
        this.conversations = this.conversations.filter(c => c.conversationID !== conversationID)
        return
      }
      try {
        await deleteConversation(conversationID)
        this.conversations = this.conversations.filter(c => c.conversationID !== conversationID)
      } catch (e) {
        console.warn('[IM Store] 删除会话失败:', e)
      }
    },

    // ========== 好友操作 ==========

    async refreshFriends() {
      if (this.useMock) return
      try {
        this.friends = await getFriendList(0, 200)
      } catch (e) {
        console.warn('[IM Store] 刷新好友列表失败:', e)
      }
    },

    async refreshFriendApplications() {
      if (this.useMock) return
      try {
        this.friendApplications = await getFriendApplicationsReceived(0, 20)
      } catch (e) {
        console.warn('[IM Store] 刷新好友申请失败:', e)
      }
    },

    async sendFriendRequest(toUserID, reqMsg = '') {
      if (this.useMock) {
        uni.showToast({ title: '好友申请已发送(mock)', icon: 'success' })
        return
      }
      await addFriend(toUserID, reqMsg)
    },

    async handleFriendApplication(toUserID, accept, handleMsg = '') {
      if (this.useMock) {
        this.friendApplications = this.friendApplications.filter(a => a.fromUserID !== toUserID)
        return
      }
      if (accept) {
        await acceptFriendApplication(toUserID, handleMsg)
      } else {
        await refuseFriendApplication(toUserID, handleMsg)
      }
    },

    async removeFriend(friendUserID) {
      if (this.useMock) {
        this.friends = this.friends.filter(f => f.userID !== friendUserID)
        return
      }
      await deleteFriend(friendUserID)
      this.friends = this.friends.filter(f => f.userID !== friendUserID)
    },

    async setFriendRemark(friendUserIDs, remark) {
      if (this.useMock) {
        const f = this.friends.find(f => friendUserIDs.includes(f.userID))
        if (f) f.remark = remark
        return
      }
      await updateFriendRemark(friendUserIDs, remark)
    },

    async blockUser(toUserID) {
      if (this.useMock) {
        this.friends = this.friends.filter(f => f.userID !== toUserID)
        return
      }
      await addBlack(toUserID)
      this.friends = this.friends.filter(f => f.userID !== toUserID)
    },

    // ========== 消息操作 ==========

    async loadMessages(conversationID, startClientMsgID = '') {
      this.currentConversationID = conversationID
      if (this.useMock) {
        // mock模式下返回模拟消息
        this.currentMessages = [
          { clientMsgID: '1', content: '你好！', sendID: '1', senderNickname: '对方', senderFaceUrl: '', sendTime: Date.now() - 3600000, contentType: 101, sessionType: 1 },
          { clientMsgID: '2', content: '你好，有什么事吗？', sendID: this.currentUserID || 'self', senderNickname: '我', senderFaceUrl: '', sendTime: Date.now() - 3500000, contentType: 101, sessionType: 1 },
        ]
        return this.currentMessages
      }
      try {
        const result = await getHistoryMessages(conversationID, 20, startClientMsgID)
        if (startClientMsgID) {
          this.currentMessages = [...(result.messageList || []), ...this.currentMessages]
        } else {
          this.currentMessages = result.messageList || []
        }
        this.hasMoreMessages = !result.isEnd
        return this.currentMessages
      } catch (e) {
        console.warn('[IM Store] 加载消息失败:', e)
        return []
      }
    },

    async sendTextMessage(recvID, groupID, text) {
      if (this.useMock) {
        const msg = {
          clientMsgID: `mock_${Date.now()}`,
          content: text,
          sendID: this.currentUserID || 'self',
          senderNickname: '我',
          senderFaceUrl: '',
          sendTime: Date.now(),
          contentType: 101,
          sessionType: groupID ? 3 : 1,
          recvID: recvID || '',
          groupID: groupID || '',
        }
        this.currentMessages.push(msg)
        return msg
      }
      const message = await createTextMessage(text)
      const sent = await sendMessage(recvID || '', groupID || '', message)
      this.currentMessages.push(sent)
      return sent
    },

    async removeMessage(conversationID, clientMsgID) {
      if (this.useMock) {
        this.currentMessages = this.currentMessages.filter(m => m.clientMsgID !== clientMsgID)
        return
      }
      await deleteMessage(conversationID, clientMsgID)
      this.currentMessages = this.currentMessages.filter(m => m.clientMsgID !== clientMsgID)
    },

    clearCurrentChat() {
      this.currentConversationID = ''
      this.currentMessages = []
      this.hasMoreMessages = true
    },
  },
})
