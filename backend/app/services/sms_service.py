"""
短信验证码服务
支持: 阿里云短信 / 腾讯云短信 / 模拟模式
"""
import logging
import random
import string
from datetime import datetime, timedelta
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """短信验证码服务"""

    CODE_LENGTH = 6
    CODE_EXPIRE_MINUTES = 5
    SEND_INTERVAL_SECONDS = 60  # 发送间隔

    def __init__(self):
        self.provider = settings.SMS_PROVIDER or "mock"  # mock / aliyun / tencent

    async def send_code(self, phone: str, scene: str = "login") -> dict:
        """
        发送验证码
        scene: login / register / pay_verify / reset_pwd
        """
        # 生成验证码
        code = "".join(random.choices(string.digits, k=self.CODE_LENGTH))

        # 存入Redis(5分钟过期)
        from app.database import redis_client
        redis = await redis_client()

        # 检查发送频率
        rate_key = f"sms:rate:{phone}:{scene}"
        if await redis.exists(rate_key):
            return {"success": False, "error": f"发送太频繁，请{self.SEND_INTERVAL_SECONDS}秒后重试"}

        # 存储验证码
        code_key = f"sms:code:{phone}:{scene}"
        await redis.setex(code_key, self.CODE_EXPIRE_MINUTES * 60, code)
        await redis.setex(rate_key, self.SEND_INTERVAL_SECONDS, "1")

        # 发送短信
        if self.provider == "mock":
            logger.info(f"[模拟短信] {phone} 验证码: {code} (场景: {scene})")
            return {"success": True, "message": "验证码已发送(模拟模式)", "code": code}

        elif self.provider == "aliyun":
            return await self._send_aliyun(phone, code, scene)

        elif self.provider == "tencent":
            return await self._send_tencent(phone, code, scene)

        return {"success": False, "error": "未知的短信服务商"}

    async def verify_code(self, phone: str, code: str, scene: str = "login") -> bool:
        """验证验证码"""
        from app.database import redis_client
        redis = await redis_client()

        code_key = f"sms:code:{phone}:{scene}"
        stored_code = await redis.get(code_key)

        if not stored_code:
            return False
        if stored_code != code:
            return False

        # 验证成功后删除
        await redis.delete(code_key)
        return True

    async def _send_aliyun(self, phone: str, code: str, scene: str) -> dict:
        """阿里云短信"""
        # TODO: 实现阿里云短信SDK调用
        # pip install alibabacloud-dysmsapi20170525
        logger.info(f"[阿里云短信] {phone} 验证码: {code}")
        return {"success": True, "message": "验证码已发送"}

    async def _send_tencent(self, phone: str, code: str, scene: str) -> dict:
        """腾讯云短信"""
        # TODO: 实现腾讯云短信SDK调用
        # pip install tencentcloud-sdk-python
        logger.info(f"[腾讯云短信] {phone} 验证码: {code}")
        return {"success": True, "message": "验证码已发送"}


# 全局实例
sms_service = SMSService()
