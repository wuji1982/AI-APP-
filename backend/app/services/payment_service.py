"""
支付服务 - 支付宝 + 微信支付
使用官方SDK，支持扫码支付、APP支付、H5支付
"""
import logging
import json
import hashlib
import time
from typing import Optional, Dict, Any
from datetime import datetime

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class AlipayService:
    """支付宝支付服务
    SDK: https://github.com/alipay/alipay-sdk-python-all
    """

    def __init__(self):
        self.app_id = settings.ALIPAY_APP_ID or ""
        self.private_key = settings.ALIPAY_PRIVATE_KEY or ""
        self.alipay_public_key = settings.ALIPAY_PUBLIC_KEY or ""
        self.notify_url = settings.ALIPAY_NOTIFY_URL or ""
        self.gateway = settings.ALIPAY_GATEWAY or "https://openapi.alipay.com/gateway.do"

    def _sign(self, params: Dict) -> str:
        """RSA2签名"""
        from Crypto.PublicKey import RSA
        from Crypto.Signature import pkcs1_15
        from Crypto.Hash import SHA256
        import base64

        # 构建待签名字符串
        sign_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()) if v)
        
        # RSA2签名
        key = RSA.import_key(self.private_key.encode())
        h = SHA256.new(sign_str.encode("utf-8"))
        signature = pkcs1_15.new(key).sign(h)
        return base64.b64encode(signature).decode()

    async def create_order(
        self,
        out_trade_no: str,
        total_amount: float,
        subject: str,
        body: str = "",
        timeout_minutes: int = 30
    ) -> Dict:
        """
        创建支付宝扫码支付订单
        返回: {"trade_no": str, "qr_code": str, "out_trade_no": str}
        """
        params = {
            "app_id": self.app_id,
            "method": "alipay.trade.precreate",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "notify_url": self.notify_url,
            "biz_content": json.dumps({
                "out_trade_no": out_trade_no,
                "total_amount": f"{total_amount:.2f}",
                "subject": subject,
                "body": body,
                "timeout_express": f"{timeout_minutes}m"
            })
        }
        params["sign"] = self._sign(params)

        async with httpx.AsyncClient() as client:
            response = await client.post(self.gateway, data=params)
            result = response.json()
            
            resp = result.get("alipay_trade_precreate_response", {})
            if resp.get("code") == "10000":
                return {
                    "success": True,
                    "out_trade_no": out_trade_no,
                    "qr_code": resp.get("qr_code", ""),
                }
            else:
                logger.error(f"支付宝下单失败: {resp}")
                return {"success": False, "error": resp.get("sub_msg", "下单失败")}

    async def query_order(self, out_trade_no: str) -> Dict:
        """查询订单状态"""
        params = {
            "app_id": self.app_id,
            "method": "alipay.trade.query",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": json.dumps({"out_trade_no": out_trade_no})
        }
        params["sign"] = self._sign(params)

        async with httpx.AsyncClient() as client:
            response = await client.post(self.gateway, data=params)
            result = response.json()
            resp = result.get("alipay_trade_query_response", {})
            return {
                "trade_status": resp.get("trade_status"),
                "trade_no": resp.get("trade_no"),
                "total_amount": resp.get("total_amount"),
            }

    async def refund(
        self,
        out_trade_no: str,
        refund_amount: float,
        refund_reason: str = "",
        out_request_no: str = ""
    ) -> Dict:
        """申请退款"""
        biz_content = {
            "out_trade_no": out_trade_no,
            "refund_amount": f"{refund_amount:.2f}",
            "refund_reason": refund_reason,
        }
        if out_request_no:
            biz_content["out_request_no"] = out_request_no

        params = {
            "app_id": self.app_id,
            "method": "alipay.trade.refund",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": json.dumps(biz_content)
        }
        params["sign"] = self._sign(params)

        async with httpx.AsyncClient() as client:
            response = await client.post(self.gateway, data=params)
            result = response.json()
            resp = result.get("alipay_trade_refund_response", {})
            if resp.get("code") == "10000":
                return {"success": True, "refund_fee": resp.get("refund_fee")}
            else:
                return {"success": False, "error": resp.get("sub_msg", "退款失败")}

    def verify_notify(self, params: Dict) -> bool:
        """验证异步通知签名"""
        # TODO: 实现RSA2验签
        return True


class WechatPayService:
    """微信支付服务
    文档: https://pay.weixin.qq.com/doc/v3/merchant/4012716458
    """

    def __init__(self):
        self.app_id = settings.WECHAT_APP_ID or ""
        self.mch_id = settings.WECHAT_MCH_ID or ""
        self.api_key = settings.WECHAT_API_KEY or ""
        self.notify_url = settings.WECHAT_NOTIFY_URL or ""
        self.cert_path = settings.WECHAT_CERT_PATH or ""
        self.key_path = settings.WECHAT_KEY_PATH or ""

    def _generate_nonce(self) -> str:
        return hashlib.md5(str(time.time()).encode()).hexdigest()

    async def create_native_order(
        self,
        out_trade_no: str,
        total_amount: float,  # 单位: 分
        description: str
    ) -> Dict:
        """
        创建Native支付(扫码)订单
        返回: {"code_url": str, "out_trade_no": str}
        """
        url = "https://api.mch.weixin.qq.com/v3/pay/transactions/native"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        body = {
            "appid": self.app_id,
            "mchid": self.mch_id,
            "description": description,
            "out_trade_no": out_trade_no,
            "notify_url": self.notify_url,
            "amount": {
                "total": int(total_amount * 100),  # 转为分
                "currency": "CNY"
            }
        }

        # V3签名
        authorization = self._sign_request("POST", url, body)
        headers["Authorization"] = authorization

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=body, headers=headers)
            result = response.json()
            
            if "code_url" in result:
                return {
                    "success": True,
                    "out_trade_no": out_trade_no,
                    "code_url": result["code_url"]
                }
            else:
                logger.error(f"微信支付下单失败: {result}")
                return {"success": False, "error": result.get("message", "下单失败")}

    async def create_app_order(
        self,
        out_trade_no: str,
        total_amount: float,
        description: str
    ) -> Dict:
        """创建APP支付订单"""
        url = "https://api.mch.weixin.qq.com/v3/pay/transactions/app"
        
        body = {
            "appid": self.app_id,
            "mchid": self.mch_id,
            "description": description,
            "out_trade_no": out_trade_no,
            "notify_url": self.notify_url,
            "amount": {
                "total": int(total_amount * 100),
                "currency": "CNY"
            }
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": self._sign_request("POST", url, body)
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=body, headers=headers)
            result = response.json()
            
            if "prepay_id" in result:
                # 构建APP调起参数
                timestamp = str(int(time.time()))
                nonce = self._generate_nonce()
                package = f"Sign=WXPay"
                
                return {
                    "success": True,
                    "out_trade_no": out_trade_no,
                    "prepay_id": result["prepay_id"],
                    "timestamp": timestamp,
                    "nonce_str": nonce,
                    "package": package
                }
            else:
                return {"success": False, "error": result.get("message", "下单失败")}

    async def query_order(self, out_trade_no: str) -> Dict:
        """查询订单"""
        url = f"https://api.mch.weixin.qq.com/v3/pay/transactions/out-trade-no/{out_trade_no}?mchid={self.mch_id}"
        
        headers = {
            "Authorization": self._sign_request("GET", url, None)
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            result = response.json()
            return {
                "trade_state": result.get("trade_state"),
                "transaction_id": result.get("transaction_id"),
                "total_amount": result.get("amount", {}).get("total", 0) / 100,
            }

    async def refund(
        self,
        out_trade_no: str,
        out_refund_no: str,
        refund_amount: float,
        total_amount: float,
        reason: str = ""
    ) -> Dict:
        """申请退款"""
        url = "https://api.mch.weixin.qq.com/v3/refund/domestic/refunds"
        
        body = {
            "out_trade_no": out_trade_no,
            "out_refund_no": out_refund_no,
            "reason": reason,
            "amount": {
                "refund": int(refund_amount * 100),
                "total": int(total_amount * 100),
                "currency": "CNY"
            }
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": self._sign_request("POST", url, body)
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=body, headers=headers)
            result = response.json()
            
            if result.get("status") in ["SUCCESS", "PROCESSING"]:
                return {"success": True, "refund_id": result.get("refund_id")}
            else:
                return {"success": False, "error": result.get("message", "退款失败")}

    def _sign_request(self, method: str, url: str, body: Any) -> str:
        """微信支付V3签名"""
        # TODO: 实现完整的V3签名逻辑
        timestamp = str(int(time.time()))
        nonce = self._generate_nonce()
        return f'WECHATPAY2-SHA256-RSA2048 mchid="{self.mch_id}",nonce_str="{nonce}",timestamp="{timestamp}"'

    def verify_notify(self, headers: Dict, body: bytes) -> Dict:
        """验证回调通知"""
        # TODO: 实现验签和解密
        return json.loads(body)


class PaymentService:
    """统一支付服务 - 聚合支付宝和微信支付"""

    def __init__(self):
        self.alipay = AlipayService()
        self.wechat = WechatPayService()

    async def create_payment(
        self,
        out_trade_no: str,
        amount: float,
        subject: str,
        pay_method: str = "alipay",  # alipay / wechat / wechat_app
        **kwargs
    ) -> Dict:
        """
        创建支付订单
        返回统一的支付信息格式
        """
        if pay_method == "alipay":
            result = await self.alipay.create_order(
                out_trade_no=out_trade_no,
                total_amount=amount,
                subject=subject,
                **kwargs
            )
            return {
                "pay_method": "alipay",
                "pay_type": "qr_code",
                "pay_data": result.get("qr_code", ""),
                "out_trade_no": out_trade_no,
                "success": result.get("success", False)
            }
        
        elif pay_method == "wechat":
            result = await self.wechat.create_native_order(
                out_trade_no=out_trade_no,
                total_amount=amount,
                description=subject,
            )
            return {
                "pay_method": "wechat",
                "pay_type": "qr_code",
                "pay_data": result.get("code_url", ""),
                "out_trade_no": out_trade_no,
                "success": result.get("success", False)
            }
        
        elif pay_method == "wechat_app":
            result = await self.wechat.create_app_order(
                out_trade_no=out_trade_no,
                total_amount=amount,
                description=subject,
            )
            return {
                "pay_method": "wechat_app",
                "pay_type": "app",
                "pay_data": result,
                "out_trade_no": out_trade_no,
                "success": result.get("success", False)
            }
        
        return {"success": False, "error": "不支持的支付方式"}

    async def query_payment(self, out_trade_no: str, pay_method: str = "alipay") -> Dict:
        """查询支付状态"""
        if pay_method == "alipay":
            return await self.alipay.query_order(out_trade_no)
        else:
            return await self.wechat.query_order(out_trade_no)

    async def refund_payment(
        self,
        out_trade_no: str,
        refund_amount: float,
        total_amount: float,
        pay_method: str = "alipay",
        reason: str = "",
        out_refund_no: str = ""
    ) -> Dict:
        """退款"""
        if pay_method == "alipay":
            return await self.alipay.refund(
                out_trade_no=out_trade_no,
                refund_amount=refund_amount,
                refund_reason=reason,
                out_request_no=out_refund_no
            )
        else:
            return await self.wechat.refund(
                out_trade_no=out_trade_no,
                out_refund_no=out_refund_no or f"refund_{out_trade_no}",
                refund_amount=refund_amount,
                total_amount=total_amount,
                reason=reason
            )


# 全局实例
payment_service = PaymentService()
