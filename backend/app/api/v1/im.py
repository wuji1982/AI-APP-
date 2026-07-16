"""
IM即时通讯API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pydantic import BaseModel

from app.database import get_db
from app.services.im_service import im_service
from app.services.openim_client import openim_client
from app.utils.auth import get_current_user_id

router = APIRouter(prefix="/im", tags=["即时通讯"])


# ========== 请求/响应模型 ==========

class AddFriendRequest(BaseModel):
    to_user_id: int
    message: str = ""


class ProcessFriendRequest(BaseModel):
    from_user_id: int
    action: str  # "accept" or "reject"


class CreateGroupRequest(BaseModel):
    name: str
    member_ids: List[int]
    group_type: str = "normal"  # normal/team/store


class SendMessageRequest(BaseModel):
    to_user_id: int
    content: str
    content_type: int = 101


class SendGroupMessageRequest(BaseModel):
    group_id: str
    content: str
    content_type: int = 101


# ========== 好友管理 ==========

@router.get("/friends")
async def get_friend_list(
    user_id: int = Depends(get_current_user_id)
):
    """获取好友列表"""
    friends = await im_service.get_user_friends(user_id)
    return {"friends": friends, "total": len(friends)}


@router.post("/friends/add")
async def add_friend(
    request: AddFriendRequest,
    user_id: int = Depends(get_current_user_id)
):
    """发起好友申请"""
    try:
        result = await openim_client.add_friend(
            from_id=str(user_id),
            to_id=str(request.to_user_id),
            req_msg=request.message
        )
        return {"success": True, "message": "好友申请已发送"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/friends/process")
async def process_friend_application(
    request: ProcessFriendRequest,
    user_id: int = Depends(get_current_user_id)
):
    """处理好友申请"""
    handle_result = 1 if request.action == "accept" else -1
    try:
        await openim_client.process_friend_application(
            user_id=str(user_id),
            friend_user_id=str(request.from_user_id),
            handle_result=handle_result
        )
        action_text = "已同意" if handle_result == 1 else "已拒绝"
        return {"success": True, "message": f"好友申请{action_text}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/friends/delete")
async def delete_friend(
    friend_id: int = Query(...),
    user_id: int = Depends(get_current_user_id)
):
    """删除好友"""
    try:
        await openim_client.delete_friend(str(user_id), str(friend_id))
        return {"success": True, "message": "已删除好友"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/friends/block")
async def block_user(
    user_to_block: int = Query(...),
    user_id: int = Depends(get_current_user_id)
):
    """拉黑用户"""
    try:
        await openim_client.add_black(str(user_id), str(user_to_block))
        return {"success": True, "message": "已拉黑该用户"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ========== 群组管理 ==========

@router.post("/groups/create")
async def create_group(
    request: CreateGroupRequest,
    user_id: int = Depends(get_current_user_id)
):
    """创建群组"""
    import time
    group_id = f"{request.group_type}_{user_id}_{int(time.time())}"
    
    try:
        result = await openim_client.create_group(
            group_id=group_id,
            group_name=request.name,
            owner_id=str(user_id),
            member_ids=[str(uid) for uid in request.member_ids]
        )
        return {
            "success": True,
            "group_id": group_id,
            "message": "群组创建成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/groups/{group_id}/invite")
async def invite_to_group(
    group_id: str,
    user_ids: List[int],
    user_id: int = Depends(get_current_user_id)
):
    """邀请用户加入群组"""
    try:
        await openim_client.invite_user_to_group(
            group_id=group_id,
            inviter_id=str(user_id),
            user_ids=[str(uid) for uid in user_ids]
        )
        return {"success": True, "message": "邀请已发送"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/groups/{group_id}/kick")
async def kick_from_group(
    group_id: str,
    user_ids: List[int],
    user_id: int = Depends(get_current_user_id)
):
    """踢出群成员"""
    try:
        await openim_client.kick_user_from_group(
            group_id=group_id,
            kicker_id=str(user_id),
            user_ids=[str(uid) for uid in user_ids]
        )
        return {"success": True, "message": "已踢出群成员"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/groups/{group_id}/members")
async def get_group_members(group_id: str):
    """获取群成员列表"""
    try:
        members = await openim_client.get_group_members(group_id)
        return {"members": members, "total": len(members)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/groups/{group_id}")
async def dismiss_group(
    group_id: str,
    user_id: int = Depends(get_current_user_id)
):
    """解散群组"""
    try:
        await openim_client.dismiss_group(group_id)
        return {"success": True, "message": "群组已解散"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ========== 消息发送 ==========

@router.post("/messages/send")
async def send_message(
    request: SendMessageRequest,
    user_id: int = Depends(get_current_user_id)
):
    """发送单聊消息"""
    try:
        result = await openim_client.send_message(
            send_id=str(user_id),
            recv_id=str(request.to_user_id),
            content=request.content,
            content_type=request.content_type
        )
        return {"success": True, "message": "消息已发送"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/messages/send-group")
async def send_group_message(
    request: SendGroupMessageRequest,
    user_id: int = Depends(get_current_user_id)
):
    """发送群聊消息"""
    try:
        result = await openim_client.send_group_message(
            send_id=str(user_id),
            group_id=request.group_id,
            content=request.content,
            content_type=request.content_type
        )
        return {"success": True, "message": "消息已发送"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ========== 用户信息 ==========

@router.get("/user/info/{target_user_id}")
async def get_user_info(target_user_id: int):
    """获取用户IM信息"""
    try:
        info = await openim_client.get_user_info(str(target_user_id))
        return info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
