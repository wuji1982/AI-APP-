"""
用户智能体API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.services.user_agent_service import user_agent_service
from app.utils.auth import get_current_user_id

router = APIRouter(prefix="/agent", tags=["用户智能体"])


# ========== 请求/响应模型 ==========

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    conversation_id: str
    sources: list = []


class KnowledgeRequest(BaseModel):
    title: str
    content: str


# ========== API端点 ==========

@router.get("/status")
async def get_agent_status(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取用户智能体状态"""
    agent = await user_agent_service.get_user_agent(db, user_id)
    if not agent:
        return {
            "has_agent": False,
            "message": "智能体尚未创建"
        }
    return {
        "has_agent": True,
        "agent_name": agent.agent_name,
        "total_chats": agent.total_chats,
        "last_chat_at": agent.last_chat_at,
        "created_at": agent.created_at
    }


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """与智能体对话"""
    try:
        result = await user_agent_service.chat(
            db=db,
            user_id=user_id,
            message=request.message,
            conversation_id=request.conversation_id
        )
        return ChatResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """与智能体流式对话"""
    from fastapi.responses import StreamingResponse
    
    async def generate():
        try:
            async for chunk in user_agent_service.chat_stream(
                db=db,
                user_id=user_id,
                message=request.message,
                conversation_id=request.conversation_id
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/conversations")
async def get_conversations(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取历史对话列表"""
    conversations = await user_agent_service.get_conversations(db, user_id)
    return {"conversations": conversations}


@router.post("/knowledge")
async def add_knowledge(
    request: KnowledgeRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """添加用户私有知识"""
    try:
        result = await user_agent_service.add_personal_knowledge(
            db=db,
            user_id=user_id,
            title=request.title,
            content=request.content
        )
        return {"success": True, "document": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/config")
async def get_agent_config(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取智能体配置"""
    agent = await user_agent_service.get_user_agent(db, user_id)
    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")
    
    return {
        "agent_name": agent.agent_name,
        "system_prompt": agent.system_prompt,
        "is_active": agent.is_active,
        "enable_notifications": True  # 从config表读取
    }
