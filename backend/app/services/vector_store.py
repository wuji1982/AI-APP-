"""
pgvector 向量存储集成
使用PostgreSQL的pgvector扩展存储用户智能体的向量数据
每个用户的向量数据通过namespace隔离
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """pgvector向量存储"""

    def __init__(self):
        self.dimension = settings.VECTOR_DIMENSION

    async def init_pgvector(self, db: AsyncSession) -> None:
        """初始化pgvector扩展和表结构"""
        # 创建pgvector扩展
        await db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        
        # 创建用户向量表
        await db.execute(text(f"""
            CREATE TABLE IF NOT EXISTS user_vectors (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                namespace VARCHAR(100) NOT NULL,
                content TEXT NOT NULL,
                embedding vector({self.dimension}),
                metadata JSONB DEFAULT '{{}}',
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        
        # 创建索引
        await db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_user_vectors_user_id 
            ON user_vectors(user_id)
        """))
        
        await db.execute(text(f"""
            CREATE INDEX IF NOT EXISTS idx_user_vectors_embedding 
            ON user_vectors 
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """))
        
        await db.commit()
        logger.info("pgvector初始化完成")

    async def add_vectors(
        self,
        db: AsyncSession,
        user_id: int,
        items: List[Dict[str, Any]]
    ) -> int:
        """
        添加向量数据
        items: [{"content": str, "embedding": List[float], "metadata": dict}]
        """
        count = 0
        for item in items:
            embedding_str = "[" + ",".join(str(x) for x in item["embedding"]) + "]"
            metadata = item.get("metadata", {})
            
            await db.execute(
                text("""
                    INSERT INTO user_vectors (user_id, namespace, content, embedding, metadata)
                    VALUES (:user_id, :namespace, :content, :embedding, :metadata)
                """),
                {
                    "user_id": user_id,
                    "namespace": f"user_{user_id}",
                    "content": item["content"],
                    "embedding": embedding_str,
                    "metadata": str(metadata).replace("'", '"')
                }
            )
            count += 1
        
        await db.commit()
        return count

    async def search(
        self,
        db: AsyncSession,
        user_id: int,
        query_embedding: List[float],
        top_k: int = 5,
        filter_namespace: Optional[str] = None
    ) -> List[Dict]:
        """
        向量相似度搜索
        返回最相似的top_k个结果
        """
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        
        sql = """
            SELECT id, content, metadata, 
                   1 - (embedding <=> :embedding) as similarity
            FROM user_vectors
            WHERE user_id = :user_id
        """
        params = {
            "user_id": user_id,
            "embedding": embedding_str
        }
        
        if filter_namespace:
            sql += " AND namespace = :namespace"
            params["namespace"] = filter_namespace
        
        sql += " ORDER BY embedding <=> :embedding LIMIT :top_k"
        params["top_k"] = top_k
        
        result = await db.execute(text(sql), params)
        rows = result.fetchall()
        
        return [
            {
                "id": row[0],
                "content": row[1],
                "metadata": row[2],
                "similarity": float(row[3])
            }
            for row in rows
        ]

    async def delete_user_vectors(
        self,
        db: AsyncSession,
        user_id: int,
        namespace: Optional[str] = None
    ) -> int:
        """删除用户向量数据"""
        if namespace:
            result = await db.execute(
                text("DELETE FROM user_vectors WHERE user_id = :user_id AND namespace = :namespace"),
                {"user_id": user_id, "namespace": namespace}
            )
        else:
            result = await db.execute(
                text("DELETE FROM user_vectors WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
        await db.commit()
        return result.rowcount


class EmbeddingService:
    """Embedding生成服务"""

    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.api_base = settings.LLM_API_BASE or "https://api.openai.com/v1"

    async def get_embedding(self, text: str) -> List[float]:
        """获取文本的embedding向量"""
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base}/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "input": text,
                    "model": "text-embedding-3-small"
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """批量获取embedding"""
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base}/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "input": texts,
                    "model": "text-embedding-3-small"
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]


# 全局实例
vector_store = VectorStore()
embedding_service = EmbeddingService()
