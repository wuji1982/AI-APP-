"""
AI Agent 基类
基于LangGraph实现Agent状态机
"""
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """AI Agent基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.state: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"agent.{name}")

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行Agent核心逻辑"""
        pass

    @abstractmethod
    async def should_continue(self, context: Dict[str, Any]) -> bool:
        """判断是否需要继续执行"""
        pass

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """运行Agent完整流程"""
        self.logger.info(f"[{self.name}] 开始执行, context={context}")
        try:
            result = await self.execute(context)
            self.logger.info(f"[{self.name}] 执行完成")
            return {"agent": self.name, "status": "success", "result": result}
        except Exception as e:
            self.logger.error(f"[{self.name}] 执行失败: {e}")
            return {"agent": self.name, "status": "error", "error": str(e)}

    def update_state(self, key: str, value: Any):
        self.state[key] = value

    def get_state(self, key: str, default=None):
        return self.state.get(key, default)
