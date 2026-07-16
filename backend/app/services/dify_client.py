"""
Dify API 客户端封装
用于管理用户知识库、Agent实例
文档: https://docs.dify.ai/getting-started/readme
"""
import httpx
import logging
from typing import Optional, Dict, Any, List
from app.config import settings

logger = logging.getLogger(__name__)


class DifyClient:
    """Dify API客户端"""

    def __init__(self):
        self.base_url = settings.DIFY_API_URL or "http://localhost/v1"
        self.api_key = settings.DIFY_API_KEY or ""
        self.timeout = 30.0

    async def _request(
        self,
        method: str,
        endpoint: str,
        api_key: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {api_key or self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()

    # ========== 知识库(Dataset)管理 ==========
    
    async def create_dataset(self, name: str, description: str = "") -> Dict:
        """创建知识库"""
        return await self._request(
            "POST",
            "/datasets",
            json={
                "name": name,
                "description": description,
                "indexing_technique": "high_quality",
                "permission": "only_me"
            }
        )

    async def delete_dataset(self, dataset_id: str) -> None:
        """删除知识库"""
        await self._request("DELETE", f"/datasets/{dataset_id}")

    async def upload_document(
        self,
        dataset_id: str,
        name: str,
        text: str,
        process_rule: Optional[Dict] = None
    ) -> Dict:
        """上传文档到知识库"""
        if process_rule is None:
            process_rule = {
                "mode": "automatic",
                "rules": {}
            }
        
        return await self._request(
            "POST",
            f"/datasets/{dataset_id}/document/create_by_text",
            json={
                "name": name,
                "text": text,
                "indexing_technique": "high_quality",
                "process_rule": process_rule
            }
        )

    async def list_documents(self, dataset_id: str) -> List[Dict]:
        """列出知识库文档"""
        result = await self._request("GET", f"/datasets/{dataset_id}/documents")
        return result.get("data", [])

    # ========== Agent/Chat 对话 ==========

    async def chat(
        self,
        api_key: str,
        query: str,
        user: str,
        conversation_id: Optional[str] = None,
        files: Optional[List[Dict]] = None,
        inputs: Optional[Dict] = None
    ) -> Dict:
        """发送对话消息"""
        payload = {
            "inputs": inputs or {},
            "query": query,
            "user": user,
            "response_mode": "blocking"
        }
        if conversation_id:
            payload["conversation_id"] = conversation_id
        if files:
            payload["files"] = files
        
        return await self._request("POST", "/chat-messages", api_key=api_key, json=payload)

    async def chat_stream(
        self,
        api_key: str,
        query: str,
        user: str,
        conversation_id: Optional[str] = None
    ):
        """流式对话（返回异步生成器）"""
        url = f"{self.base_url}/chat-messages"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": {},
            "query": query,
            "user": user,
            "response_mode": "streaming"
        }
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        yield line[6:]

    async def get_conversations(self, api_key: str, user: str) -> List[Dict]:
        """获取对话列表"""
        result = await self._request(
            "GET",
            "/conversations",
            api_key=api_key,
            params={"user": user}
        )
        return result.get("data", [])

    async def delete_conversation(self, api_key: str, conversation_id: str, user: str) -> None:
        """删除对话"""
        await self._request(
            "DELETE",
            f"/conversations/{conversation_id}",
            api_key=api_key,
            params={"user": user}
        )

    # ========== 应用(App)管理 ==========

    async def create_app(
        self,
        name: str,
        mode: str = "chat",
        description: str = ""
    ) -> Dict:
        """创建应用"""
        return await self._request(
            "POST",
            "/apps",
            json={
                "name": name,
                "mode": mode,
                "description": description
            }
        )

    async def get_app_info(self, api_key: str) -> Dict:
        """获取应用信息"""
        return await self._request("GET", "/info", api_key=api_key)


# 全局客户端实例
dify_client = DifyClient()
