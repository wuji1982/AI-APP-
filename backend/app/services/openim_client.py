"""
OpenIM API 客户端封装
文档: https://docs.openim.io/restapi/apis/overview
"""
import httpx
import logging
import hashlib
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)


class OpenIMClient:
    """OpenIM REST API客户端"""

    def __init__(self):
        self.api_url = settings.OPENIM_API_URL
        self.admin_url = settings.OPENIM_ADMIN_URL
        self.secret = settings.OPENIM_SECRET
        self.admin_token = settings.OPENIM_ADMIN_TOKEN
        self.timeout = 30.0

    def _generate_token(self) -> str:
        """生成操作Token"""
        current_time = datetime.now().timestamp()
        sign_str = f"{self.secret}{int(current_time)}"
        return hashlib.md5(sign_str.encode()).hexdigest()

    def _headers(self, operation_id: str = "system") -> Dict[str, str]:
        """请求头"""
        return {
            "operationID": operation_id,
            "Content-Type": "application/json",
            "token": self.admin_token or self._generate_token()
        }

    async def _request(
        self,
        method: str,
        url: str,
        operation_id: str = "system",
        **kwargs
    ) -> Dict[str, Any]:
        """发送HTTP请求"""
        headers = self._headers(operation_id)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            result = response.json()
            
            if result.get("errCode") != 0:
                logger.error(f"OpenIM API错误: {result}")
                raise Exception(result.get("errMsg", "OpenIM API错误"))
            
            return result

    # ========== 用户管理 ==========

    async def register_user(
        self,
        user_id: str,
        name: str,
        face_url: str = "",
        phone: str = ""
    ) -> Dict:
        """注册IM用户"""
        return await self._request(
            "POST",
            f"{self.admin_url}/user/user_register",
            operation_id=f"register_{user_id}",
            json={
                "users": [{
                    "userID": user_id,
                    "name": name,
                    "faceURL": face_url,
                    "ex": json.dumps({"phone": phone})
                }]
            }
        )

    async def update_user_info(self, user_id: str, **kwargs) -> Dict:
        """更新用户信息"""
        data = {"userID": user_id}
        if "name" in kwargs:
            data["name"] = kwargs["name"]
        if "face_url" in kwargs:
            data["faceURL"] = kwargs["face_url"]
        
        return await self._request(
            "POST",
            f"{self.admin_url}/user/update_user_info",
            operation_id=f"update_{user_id}",
            json=data
        )

    async def get_user_info(self, user_id: str) -> Dict:
        """获取用户信息"""
        result = await self._request(
            "POST",
            f"{self.admin_url}/user/get_users_info",
            operation_id=f"get_{user_id}",
            json={"userIDs": [user_id]}
        )
        users = result.get("data", {}).get("usersInfo", [])
        return users[0] if users else {}

    # ========== 好友管理 ==========

    async def add_friend(self, from_id: str, to_id: str, req_msg: str = "") -> Dict:
        """发起好友申请"""
        return await self._request(
            "POST",
            f"{self.api_url}/friend/add_friend",
            operation_id=f"add_friend_{from_id}_{to_id}",
            json={
                "fromUserID": from_id,
                "toUserID": to_id,
                "reqMsg": req_msg
            }
        )

    async def process_friend_application(
        self,
        user_id: str,
        friend_user_id: str,
        handle_result: int  # 1=同意, -1=拒绝
    ) -> Dict:
        """处理好友申请"""
        return await self._request(
            "POST",
            f"{self.api_url}/friend/process_friend_application",
            operation_id=f"process_friend_{user_id}",
            json={
                "userID": user_id,
                "fromUserID": friend_user_id,
                "handleResult": handle_result
            }
        )

    async def get_friend_list(self, user_id: str) -> List[Dict]:
        """获取好友列表"""
        result = await self._request(
            "POST",
            f"{self.api_url}/friend/get_friend_list",
            operation_id=f"get_friends_{user_id}",
            json={"userID": user_id}
        )
        return result.get("data", [])

    async def delete_friend(self, user_id: str, friend_id: str) -> Dict:
        """删除好友"""
        return await self._request(
            "POST",
            f"{self.api_url}/friend/delete_friend",
            operation_id=f"del_friend_{user_id}",
            json={
                "ownerUserID": user_id,
                "friendUserIDs": [friend_id]
            }
        )

    async def add_black(self, user_id: str, black_id: str) -> Dict:
        """添加黑名单"""
        return await self._request(
            "POST",
            f"{self.api_url}/friend/add_black",
            operation_id=f"add_black_{user_id}",
            json={
                "userID": user_id,
                "blackUserID": black_id
            }
        )

    # ========== 群组管理 ==========

    async def create_group(
        self,
        group_id: str,
        group_name: str,
        owner_id: str,
        member_ids: List[str],
        group_type: int = 1,  # 1=普通群, 2=超级群
        introduction: str = ""
    ) -> Dict:
        """创建群组"""
        members = [{"userID": uid, "roleLevel": 1} for uid in member_ids]
        # 群主角色为2
        for m in members:
            if m["userID"] == owner_id:
                m["roleLevel"] = 2
        
        return await self._request(
            "POST",
            f"{self.api_url}/group/create_group",
            operation_id=f"create_group_{group_id}",
            json={
                "groupID": group_id,
                "groupName": group_name,
                "introduction": introduction,
                "groupType": group_type,
                "memberUserIDs": member_ids,
                "ownerUserID": owner_id
            }
        )

    async def invite_user_to_group(
        self,
        group_id: str,
        inviter_id: str,
        user_ids: List[str],
        reason: str = ""
    ) -> Dict:
        """邀请用户加入群组"""
        return await self._request(
            "POST",
            f"{self.api_url}/group/invite_user_to_group",
            operation_id=f"invite_group_{group_id}",
            json={
                "groupID": group_id,
                "inviterUserID": inviter_id,
                "invitedUserIDs": user_ids,
                "reason": reason
            }
        )

    async def kick_user_from_group(
        self,
        group_id: str,
        kicker_id: str,
        user_ids: List[str],
        reason: str = ""
    ) -> Dict:
        """踢出群组"""
        return await self._request(
            "POST",
            f"{self.api_url}/group/kick_group_member",
            operation_id=f"kick_group_{group_id}",
            json={
                "groupID": group_id,
                "kickedUserIDs": user_ids,
                "reason": reason
            }
        )

    async def get_group_members(self, group_id: str) -> List[Dict]:
        """获取群成员列表"""
        result = await self._request(
            "POST",
            f"{self.api_url}/group/get_group_member_list",
            operation_id=f"get_members_{group_id}",
            json={"groupID": group_id}
        )
        return result.get("data", [])

    async def dismiss_group(self, group_id: str) -> Dict:
        """解散群组"""
        return await self._request(
            "POST",
            f"{self.api_url}/group/dismiss_group",
            operation_id=f"dismiss_group_{group_id}",
            json={"groupID": group_id}
        )

    # ========== 消息管理 ==========

    async def send_message(
        self,
        send_id: str,
        recv_id: str,
        content: str,
        content_type: int = 101,  # 101=文本
        sender_platform_id: int = 1
    ) -> Dict:
        """发送单聊消息"""
        return await self._request(
            "POST",
            f"{self.api_url}/msg/send_msg",
            operation_id=f"send_msg_{send_id}",
            json={
                "sendID": send_id,
                "recvID": recv_id,
                "contentType": content_type,
                "content": json.dumps({"content": content}),
                "senderPlatformID": sender_platform_id
            }
        )

    async def send_group_message(
        self,
        send_id: str,
        group_id: str,
        content: str,
        content_type: int = 101
    ) -> Dict:
        """发送群聊消息"""
        return await self._request(
            "POST",
            f"{self.api_url}/msg/send_group_msg",
            operation_id=f"send_group_msg_{group_id}",
            json={
                "sendID": send_id,
                "groupID": group_id,
                "contentType": content_type,
                "content": json.dumps({"content": content})
            }
        )

    async def send_business_notification(
        self,
        send_id: str,
        recv_id: str,
        notification: str
    ) -> Dict:
        """发送业务通知（系统消息）"""
        return await self._request(
            "POST",
            f"{self.api_url}/msg/business_notification",
            operation_id=f"notify_{recv_id}",
            json={
                "sendID": send_id,
                "recvID": recv_id,
                "contentType": 1701,  # 通知类型
                "content": json.dumps({"detailNotification": notification})
            }
        )

    # ========== 用户Token管理 ==========

    async def get_user_token(self, user_id: str) -> str:
        """获取用户IM Token"""
        result = await self._request(
            "POST",
            f"{self.admin_url}/auth/user_token",
            operation_id=f"token_{user_id}",
            json={
                "userID": user_id,
                "platform": 5  # H5
            }
        )
        return result.get("data", {}).get("token", "")

    # ========== 推送管理 ==========

    async def push_message(
        self,
        user_ids: List[str],
        title: str,
        content: str,
        ext: Optional[Dict] = None
    ) -> Dict:
        """离线推送消息"""
        return await self._request(
            "POST",
            f"{self.admin_url}/push/push_msg",
            operation_id=f"push_{len(user_ids)}",
            json={
                "userIDList": user_ids,
                "offlinePushInfo": {
                    "title": title,
                    "desc": content,
                    "ex": json.dumps(ext or {})
                }
            }
        )


# 全局客户端实例
openim_client = OpenIMClient()
