"""
WebSocket 实时推送服务
用于拼团进度、Agent状态等实时通知
"""
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    GROUP_BUY_UPDATE = "group_buy_update"      # 拼团人数更新
    GROUP_BUY_RESULT = "group_buy_result"      # 拼团结果
    AGENT_STATUS = "agent_status"              # Agent状态变更
    NOTIFICATION = "notification"              # 通用通知
    PRICE_UPDATE = "price_update"              # 积分单价更新


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 全局连接
        self.active_connections: Set[WebSocket] = set()
        # 按用户ID分组的连接
        self.user_connections: Dict[int, Set[WebSocket]] = {}
        # 按频道分组的连接 (如 group_buy_1, agent_status)
        self.channel_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int = None):
        """接受并注册连接"""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(websocket)
        
        logger.info(f"WebSocket连接建立, 当前连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, user_id: int = None):
        """断开并移除连接"""
        self.active_connections.discard(websocket)
        
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # 从频道中移除
        for channel in list(self.channel_connections.keys()):
            self.channel_connections[channel].discard(websocket)
            if not self.channel_connections[channel]:
                del self.channel_connections[channel]
        
        logger.info(f"WebSocket连接断开, 当前连接数: {len(self.active_connections)}")

    async def subscribe_channel(self, websocket: WebSocket, channel: str):
        """订阅频道"""
        if channel not in self.channel_connections:
            self.channel_connections[channel] = set()
        self.channel_connections[channel].add(websocket)

    async def send_to_user(self, user_id: int, message: dict):
        """向指定用户发送消息"""
        if user_id in self.user_connections:
            data = json.dumps(message, ensure_ascii=False)
            for ws in self.user_connections[user_id]:
                try:
                    await ws.send_text(data)
                except Exception:
                    self.disconnect(ws, user_id)

    async def send_to_channel(self, channel: str, message: dict):
        """向频道内所有连接发送消息"""
        if channel in self.channel_connections:
            data = json.dumps(message, ensure_ascii=False)
            disconnected = set()
            for ws in self.channel_connections[channel]:
                try:
                    await ws.send_text(data)
                except Exception:
                    disconnected.add(ws)
            for ws in disconnected:
                self.disconnect(ws)

    async def broadcast(self, message: dict):
        """全局广播"""
        data = json.dumps(message, ensure_ascii=False)
        disconnected = set()
        for ws in self.active_connections:
            try:
                await ws.send_text(data)
            except Exception:
                disconnected.add(ws)
        for ws in disconnected:
            self.disconnect(ws)

    async def send_group_buy_update(self, session_id: int, current_players: int, total_players: int):
        """发送拼团人数更新"""
        await self.send_to_channel(f"group_buy_{session_id}", {
            "type": MessageType.GROUP_BUY_UPDATE,
            "data": {
                "session_id": session_id,
                "current_players": current_players,
                "total_players": total_players
            }
        })

    async def send_group_buy_result(self, session_id: int, winner_id: int, results: list):
        """发送拼团结果"""
        await self.send_to_channel(f"group_buy_{session_id}", {
            "type": MessageType.GROUP_BUY_RESULT,
            "data": {
                "session_id": session_id,
                "winner_id": winner_id,
                "results": results
            }
        })


# 全局实例
manager = ConnectionManager()
