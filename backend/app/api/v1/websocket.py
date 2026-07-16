"""
WebSocket路由
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.ws.manager import manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: int = Query(None)):
    """WebSocket连接端点"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # 处理客户端消息
            import json
            try:
                msg = json.loads(data)
                action = msg.get("action")
                
                if action == "subscribe":
                    channel = msg.get("channel")
                    if channel:
                        await manager.subscribe_channel(websocket, channel)
                        await websocket.send_text(json.dumps({
                            "type": "subscribed",
                            "channel": channel
                        }))
                
                elif action == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                    
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
