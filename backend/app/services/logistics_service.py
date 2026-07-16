"""
物流查询服务 - 快递100 API
文档: https://api.kuaidi100.com/document/
支持400+快递公司实时查询
"""
import logging
import hashlib
from typing import Optional, Dict, List, Any
from datetime import datetime

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class LogisticsService:
    """快递100物流查询服务"""

    def __init__(self):
        self.key = settings.KUAIDI100_KEY or ""
        self.customer = settings.KUAIDI100_CUSTOMER or ""
        self.callback_url = settings.KUAIDI100_CALLBACK or ""
        self.base_url = "https://poll.kuaidi100.com/poll"

    def _sign(self, method: str, param: str, timestamp: str) -> str:
        """签名"""
        sign_str = f"{param}{timestamp}{self.key}{self.customer}"
        return hashlib.md5(sign_str.encode()).hexdigest().upper()

    async def query_track(
        self,
        company: str,
        number: str
    ) -> Dict:
        """
        实时查询物流轨迹
        company: 快递公司编码 (如: yuantong, shunfeng, zhongtong)
        number: 快递单号
        """
        param = {
            "com": company,
            "num": number,
            "customer": self.customer,
            "resultv2": 1  # 返回完整信息
        }
        
        import json
        param_str = json.dumps(param, separators=(",", ":"))
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/query.do",
                data={
                    "schema": "json",
                    "param": param_str,
                    "sign": self._sign("query", param_str, timestamp),
                    "key": self.key,
                    "t": timestamp
                }
            )
            result = response.json()
            
            if result.get("status") == "200":
                return {
                    "success": True,
                    "company": company,
                    "number": number,
                    "state": self._parse_state(result.get("state")),
                    "traces": result.get("data", [])
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "查询失败")
                }

    async def subscribe(
        self,
        company: str,
        number: str,
        phone: str = "",
        callback_url: str = ""
    ) -> Dict:
        """
        订阅物流推送
        快递状态变化时自动回调通知
        """
        import json
        param = {
            "company": company,
            "number": number,
            "key": self.key,
            "parameters": {
                "callbackurl": callback_url or self.callback_url,
                "phone": phone
            }
        }
        param_str = json.dumps(param, separators=(",", ":"))

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/",
                data={
                    "schema": "json",
                    "param": param_str
                }
            )
            result = response.json()
            return {
                "success": result.get("result") is True,
                "message": result.get("message", "")
            }

    async def auto_detect(self, number: str) -> List[Dict]:
        """
        智能识别快递公司
        根据单号自动判断是哪家快递
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.kuaidi100.com/autonumber/auto",
                params={"num": number}
            )
            result = response.json()
            return [
                {"code": item.get("comCode"), "name": self._company_name(item.get("comCode"))}
                for item in result
            ]

    async def create_electronic_order(
        self,
        company: str,
        sender_name: str,
        sender_phone: str,
        sender_address: Dict,
        receiver_name: str,
        receiver_phone: str,
        receiver_address: Dict,
        cargo: str = "",
        weight: float = 1.0,
        remark: str = ""
    ) -> Dict:
        """
        创建电子面单
        用于商家发货
        """
        import json
        param = {
            "kuaidicom": company,
            "recManName": receiver_name,
            "recManMobile": receiver_phone,
            "recManPrintAddr": f"{receiver_address.get('province', '')}{receiver_address.get('city', '')}{receiver_address.get('district', '')}{receiver_address.get('detail', '')}",
            "sendManName": sender_name,
            "sendManMobile": sender_phone,
            "sendManPrintAddr": f"{sender_address.get('province', '')}{sender_address.get('city', '')}{sender_address.get('district', '')}{sender_address.get('detail', '')}",
            "cargo": cargo,
            "weight": weight,
            "remark": remark,
            "payment": "SHIPPER",  # 寄付
            "serviceType": ""
        }

        param_str = json.dumps(param, separators=(",", ":"))
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        sign = hashlib.md5(f"{param_str}{timestamp}{self.key}{self.customer}".encode()).hexdigest().upper()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://order.kuaidi100.com/order/borddorder.do",
                data={
                    "method": "order",
                    "key": self.key,
                    "customer": self.customer,
                    "sign": sign,
                    "t": timestamp,
                    "param": param_str
                }
            )
            result = response.json()
            if result.get("result") == True:
                return {
                    "success": True,
                    "tracking_number": result.get("kuaidinum"),
                    "label": result.get("label", ""),  # 面单HTML
                }
            else:
                return {"success": False, "error": result.get("message", "下单失败")}

    def _parse_state(self, state: str) -> str:
        """解析物流状态"""
        state_map = {
            "0": "在途",
            "1": "揽收",
            "2": "疑难",
            "3": "签收",
            "4": "退签",
            "5": "派件",
            "6": "退回",
            "7": "转投",
            "10": "待清关",
            "11": "清关中",
            "12": "已清关",
            "13": "清关异常",
            "14": "收件人拒件"
        }
        return state_map.get(state, "未知")

    def _company_name(self, code: str) -> str:
        """快递公司编码转名称"""
        companies = {
            "yuantong": "圆通速递",
            "shunfeng": "顺丰速运",
            "zhongtong": "中通快递",
            "yunda": "韵达快递",
            "shentong": "申通快递",
            "jd": "京东物流",
            "ems": "EMS",
            "youzhengguonei": "邮政快递包裹",
            "debangkuaidi": "德邦快递",
            "annengwuliu": "安能物流",
            "zhaijisong": "宅急送",
            "tiantian": "天天快递",
        }
        return companies.get(code, code)


# 常用快递公司
EXPRESS_COMPANIES = [
    {"code": "shunfeng", "name": "顺丰速运"},
    {"code": "zhongtong", "name": "中通快递"},
    {"code": "yuantong", "name": "圆通速递"},
    {"code": "yunda", "name": "韵达快递"},
    {"code": "shentong", "name": "申通快递"},
    {"code": "jd", "name": "京东物流"},
    {"code": "ems", "name": "EMS"},
    {"code": "debangkuaidi", "name": "德邦快递"},
]


# 全局实例
logistics_service = LogisticsService()
