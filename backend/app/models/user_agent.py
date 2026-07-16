"""
用户智能体数据模型
每个用户拥有独立的AI智能体实例
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class UserAgent(Base):
    """用户智能体配置"""
    __tablename__ = "user_agents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    # Dify配置
    dify_app_id = Column(String(100), comment="Dify应用ID")
    dify_api_key = Column(String(200), comment="Dify应用API Key")
    dify_dataset_id = Column(String(100), comment="Dify知识库ID")
    
    # 智能体配置
    agent_name = Column(String(100), comment="智能体名称")
    agent_avatar = Column(String(500), comment="智能体头像")
    system_prompt = Column(Text, comment="系统提示词")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否激活")
    total_chats = Column(Integer, default=0, comment="总对话次数")
    last_chat_at = Column(DateTime, comment="最后对话时间")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class UserAgentMemory(Base):
    """用户智能体对话记忆"""
    __tablename__ = "user_agent_memories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey("user_agents.id"), nullable=False, index=True)
    
    # 对话内容
    role = Column(String(20), nullable=False, comment="角色: user/assistant/system")
    content = Column(Text, nullable=False, comment="对话内容")
    
    # 元数据
    conversation_id = Column(String(100), comment="Dify对话ID")
    tokens_used = Column(Integer, default=0, comment="消耗token数")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())


class AgentKnowledgeSource(Base):
    """智能体知识来源"""
    __tablename__ = "agent_knowledge_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey("user_agents.id"), nullable=False, index=True)
    
    # 知识来源
    source_type = Column(String(50), nullable=False, comment="来源类型: platform/personal/order/contribution")
    title = Column(String(200), nullable=False, comment="知识标题")
    content = Column(Text, nullable=False, comment="知识内容")
    
    # Dify文档ID
    dify_document_id = Column(String(100), comment="Dify文档ID")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class UserAgentConfig(Base):
    """用户智能体个性化配置"""
    __tablename__ = "user_agent_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey("user_agents.id"), unique=True, nullable=False)
    
    # 个性化配置
    response_style = Column(String(50), default="friendly", comment="回复风格: friendly/professional/concise")
    language = Column(String(20), default="zh-CN", comment="语言")
    enable_notifications = Column(Boolean, default=True, comment="是否启用主动通知")
    notification_types = Column(String(500), comment="通知类型: group_buy,coupon,dividend,team")
    
    # 偏好设置
    preferred_topics = Column(String(500), comment="关注话题: 收益分析,拼团策略,团队管理")
    auto_summary = Column(Boolean, default=True, comment="是否自动生成对话摘要")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
