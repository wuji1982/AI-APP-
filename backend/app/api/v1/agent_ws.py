"""
用户智能体 WebSocket 对话端点
支持实时流式对话
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import json
import logging

from app.database import get_db
from app.services.user_agent_service import user_agent_service
from app.ws.manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/agent")
async def agent_websocket(
    websocket: WebSocket,
    user_id: int = Query(..., description="用户ID")
):
    """
    用户智能体WebSocket对话端点
    
    客户端消息格式:
    {
        "action": "chat",
        "message": "用户消息",
        "conversation_id": "可选的对话ID"
    }
    
    服务端响应格式:
    {
        "type": "agent_response",
        "content": "AI回复内容",
        "conversation_id": "对话ID",
        "sources": []
    }
    """
    # 连接到WebSocket管理器
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                msg = json.loads(data)
                action = msg.get("action")
                
                if action == "chat":
                    # 处理对话请求
                    message = msg.get("message", "")
                    conversation_id = msg.get("conversation_id")
                    
                    if not message:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "消息不能为空"
                        }))
                        continue
                    
                    # 获取数据库会话
                    async for db in get_db():
                        try:
                            # 调用智能体服务
                            result = await user_agent_service.chat(
                                db=db,
                                user_id=user_id,
                                message=message,
                                conversation_id=conversation_id
                            )
                            
                            # 发送响应
                            await websocket.send_text(json.dumps({
                                "type": "agent_response",
                                "content": result["answer"],
                                "conversation_id": result["conversation_id"],
                                "sources": result.get("sources", [])
                            }))
                            
                            # 通过频道广播（可选）
                            await manager.send_to_channel(
                                f"agent_{user_id}",
                                {
                                    "type": "chat_history",
                                    "user_message": message,
                                    "agent_response": result["answer"]
                                }
                            )
                            
                        except ValueError as e:
                            await websocket.send_text(json.dumps({
                                "type": "error",
                                "message": str(e)
                            }))
                        except Exception as e:
                            logger.error(f"智能体对话错误: {e}")
                            await websocket.send_text(json.dumps({
                                "type": "error",
                                "message": "智能体处理失败，请稍后重试"
                            }))
                        break
                
                elif action == "subscribe":
                    # 订阅用户智能体频道
                    channel = f"agent_{user_id}"
                    await manager.subscribe_channel(websocket, channel)
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "channel": channel
                    }))
                
                elif action == "get_status":
                    # 获取智能体状态
                    async for db in get_db():
                        agent = await user_agent_service.get_user_agent(db, user_id)
                        if agent:
                            await websocket.send_text(json.dumps({
                                "type": "agent_status",
                                "has_agent": True,
                                "agent_name": agent.agent_name,
                                "total_chats": agent.total_chats,
                                "is_active": agent.is_active
                            }))
                        else:
                            await websocket.send_text(json.dumps({
                                "type": "agent_status",
                                "has_agent": False,
                                "message": "智能体尚未创建"
                            }))
                        break
                
                elif action == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                    
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "无效的JSON格式"
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"用户 {user_id} 智能体WebSocket断开")


@router.websocket("/ws/agent/stream")
async def agent_stream_websocket(
    websocket: WebSocket,
    user_id: int = Query(..., description="用户ID")
):
    """
    用户智能体流式对话WebSocket端点
    支持逐字输出效果
    """
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                msg = json.loads(data)
                action = msg.get("action")
                
                if action == "chat_stream":
                    message = msg.get("message", "")
                    conversation_id = msg.get("conversation_id")
                    
                    if not message:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "消息不能为空"
                        }))
                        continue
                    
                    # 发送开始标记
                    await websocket.send_text(json.dumps({
                        "type": "stream_start"
                    }))
                    
                    async for db in get_db():
                        try:
                            full_response = ""
                            async for chunk in user_agent_service.chat_stream(
                                db=db,
                                user_id=user_id,
                                message=message,
                                conversation_id=conversation_id
                            ):
                                # 解析chunk
                                try:
                                    chunk_data = json.loads(chunk)
                                    content = chunk_data.get("answer", "")
                                    if content:
                                        full_response += content
                                        await websocket.send_text(json.dumps({
                                            "type": "stream_chunk",
                                            "content": content
                                        }))
                                except:
                                    pass
                            
                            # 发送完成标记
                            await websocket.send_text(json.dumps({
                                "type": "stream_end",
                                "full_content": full_response
                            }))
                            
                        except Exception as e:
                            await websocket.send_text(json.dumps({
                                "type": "error",
                                "message": str(e)
                            }))
                        break
                
                elif action == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                    
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
