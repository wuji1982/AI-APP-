"""
地图服务API - 门店定位/附近门店/物流追踪/地理编码
仅提供后端API接口，不涉及前端UI
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import math

from app.database import get_db
from app.models.store import Store, StoreStatus

router = APIRouter()


# ========== 请求/响应模型 ==========

class NearbyStoresRequest(BaseModel):
    latitude: float  # 纬度
    longitude: float  # 经度
    radius: float = 5000  # 搜索半径(米), 默认5km
    limit: int = 10


class StoreLocationInfo(BaseModel):
    id: int
    store_no: str
    name: str
    address: str
    province: str
    city: str
    district: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    distance: Optional[float] = None  # 距离(米)
    status: str


class LogisticsTrackPoint(BaseModel):
    """物流追踪点"""
    id: int
    order_no: str
    latitude: float
    longitude: float
    location_name: str  # 位置描述
    status: str  # picked_up / in_transit / delivering / delivered
    description: str
    recorded_at: datetime


class LogisticsTraceCreate(BaseModel):
    order_no: str
    latitude: float
    longitude: float
    location_name: str
    status: str = "in_transit"
    description: str = ""


class GeocodeResult(BaseModel):
    address: str
    latitude: float
    longitude: float
    formatted_address: str


# ========== 辅助函数 ==========

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    计算两个经纬度坐标之间的距离(米)
    使用Haversine公式
    """
    R = 6371000  # 地球半径(米)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# 门店模拟坐标(实际项目中应从数据库读取或调用地图API)
STORE_COORDINATES = {
    "ST001": (42.5095, 123.4370),  # 法库
    "ST002": (41.7968, 123.4497),  # 沈阳沈河
    "ST003": (38.9140, 121.6146),  # 大连中山
    "ST004": (43.8868, 125.3245),  # 长春朝阳
    "ST005": (45.7500, 126.6500),  # 哈尔滨南岗
}


# ========== 门店定位接口 ==========

@router.get("/store/nearby", summary="附近门店")
async def get_nearby_stores(
    latitude: float = Query(..., description="纬度"),
    longitude: float = Query(..., description="经度"),
    radius: float = Query(5000, description="搜索半径(米)"),
    limit: int = Query(10, description="返回数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    根据用户当前位置查找附近门店
    返回按距离排序的门店列表，包含距离信息
    """
    result = await db.execute(
        select(Store).where(Store.status == StoreStatus.ACTIVE)
    )
    stores = result.scalars().all()

    store_list = []
    for store in stores:
        coords = STORE_COORDINATES.get(store.store_no)
        if not coords:
            continue

        distance = haversine_distance(latitude, longitude, coords[0], coords[1])
        if distance <= radius:
            store_list.append({
                "id": store.id,
                "store_no": store.store_no,
                "name": store.name,
                "address": f"{store.province}{store.city}{store.district}{store.address or ''}",
                "province": store.province,
                "city": store.city,
                "district": store.district,
                "latitude": coords[0],
                "longitude": coords[1],
                "contact_name": store.contact_name,
                "contact_phone": store.contact_phone,
                "distance": round(distance, 1),
                "status": store.status.value if store.status else "active",
            })

    # 按距离排序
    store_list.sort(key=lambda x: x["distance"])
    store_list = store_list[:limit]

    return {
        "code": 0,
        "message": "success",
        "data": {
            "center": {"latitude": latitude, "longitude": longitude},
            "radius": radius,
            "stores": store_list,
            "total": len(store_list)
        }
    }


@router.get("/store/{store_id}/location", summary="门店位置详情")
async def get_store_location(
    store_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定门店的位置信息(经纬度、地址、导航信息)
    """
    result = await db.execute(select(Store).where(Store.id == store_id))
    store = result.scalar_one_or_none()
    if not store:
        raise HTTPException(status_code=404, detail="门店不存在")

    coords = STORE_COORDINATES.get(store.store_no, (0, 0))

    return {
        "code": 0,
        "message": "success",
        "data": {
            "id": store.id,
            "store_no": store.store_no,
            "name": store.name,
            "address": f"{store.province}{store.city}{store.district}{store.address or ''}",
            "latitude": coords[0],
            "longitude": coords[1],
            "contact_name": store.contact_name,
            "contact_phone": store.contact_phone,
            "status": store.status.value if store.status else "active",
            # 导航信息
            "navigation": {
                "scheme": f"geo:{coords[0]},{coords[1]}?q={store.name}",
                "apple_maps": f"http://maps.apple.com/?daddr={coords[0]},{coords[1]}",
                "amap": f"https://uri.amap.com/marker?position={coords[1]},{coords[0]}&name={store.name}",
                "baidu_maps": f"https://api.map.baidu.com/marker?location={coords[0]},{coords[1]}&title={store.name}",
            }
        }
    }


@router.get("/store/all-locations", summary="所有门店位置(地图标注)")
async def get_all_store_locations(
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有营业中门店的位置信息，用于地图标注
    """
    result = await db.execute(
        select(Store).where(Store.status == StoreStatus.ACTIVE)
    )
    stores = result.scalars().all()

    markers = []
    for store in stores:
        coords = STORE_COORDINATES.get(store.store_no)
        if not coords:
            continue
        markers.append({
            "id": store.id,
            "store_no": store.store_no,
            "name": store.name,
            "latitude": coords[0],
            "longitude": coords[1],
            "address": f"{store.city}{store.district}",
            "status": store.status.value if store.status else "active",
        })

    return {
        "code": 0,
        "message": "success",
        "data": {
            "markers": markers,
            "total": len(markers)
        }
    }


# ========== 物流追踪接口 ==========

# 模拟物流追踪数据(实际项目中应存储在数据库)
_logistics_traces: dict = {}


@router.get("/logistics/track/{order_no}", summary="物流追踪")
async def track_logistics(
    order_no: str,
    db: AsyncSession = Depends(get_db)
):
    """
    查询订单物流追踪信息
    返回物流轨迹列表(按时间倒序)
    """
    # 检查数据库中的订单
    from app.models.product import Order
    result = await db.execute(
        select(Order).where(Order.order_no == order_no)
    )
    order = result.scalar_one_or_none()

    # 返回模拟物流轨迹(实际项目中从物流API或数据库获取)
    if order_no in _logistics_traces:
        traces = _logistics_traces[order_no]
    else:
        # 生成模拟物流轨迹
        traces = _generate_mock_traces(order_no, order)

    return {
        "code": 0,
        "message": "success",
        "data": {
            "order_no": order_no,
            "status": traces[0]["status"] if traces else "unknown",
            "carrier": "顺丰速运",
            "tracking_no": f"SF{order_no[-8:]}",
            "estimated_delivery": "预计3天内送达",
            "traces": traces,
            "total": len(traces)
        }
    }


@router.post("/logistics/trace", summary="添加物流追踪点")
async def add_logistics_trace(
    data: LogisticsTraceCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    添加一条物流追踪记录(管理端/物流回调使用)
    """
    if data.order_no not in _logistics_traces:
        _logistics_traces[data.order_no] = []

    trace = {
        "id": len(_logistics_traces[data.order_no]) + 1,
        "order_no": data.order_no,
        "latitude": data.latitude,
        "longitude": data.longitude,
        "location_name": data.location_name,
        "status": data.status,
        "description": data.description or f"快件到达 {data.location_name}",
        "recorded_at": datetime.utcnow().isoformat(),
    }
    _logistics_traces[data.order_no].insert(0, trace)

    return {
        "code": 0,
        "message": "success",
        "data": trace
    }


def _generate_mock_traces(order_no: str, order=None) -> list:
    """生成模拟物流轨迹"""
    from datetime import timedelta
    now = datetime.utcnow()
    traces = [
        {
            "id": 4,
            "order_no": order_no,
            "latitude": 41.7968,
            "longitude": 123.4497,
            "location_name": "沈阳转运中心",
            "status": "delivering",
            "description": "快件正在派送中，快递员: 张师傅 138xxxx5678",
            "recorded_at": now.isoformat(),
        },
        {
            "id": 3,
            "order_no": order_no,
            "latitude": 41.8034,
            "longitude": 123.4218,
            "location_name": "沈阳集散中心",
            "status": "in_transit",
            "description": "快件已到达沈阳集散中心",
            "recorded_at": (now - timedelta(hours=3)).isoformat(),
        },
        {
            "id": 2,
            "order_no": order_no,
            "latitude": 42.5095,
            "longitude": 123.4370,
            "location_name": "法库发货仓",
            "status": "in_transit",
            "description": "快件已从法库发货仓发出",
            "recorded_at": (now - timedelta(hours=8)).isoformat(),
        },
        {
            "id": 1,
            "order_no": order_no,
            "latitude": 42.5095,
            "longitude": 123.4370,
            "location_name": "法库发货仓",
            "status": "picked_up",
            "description": "商家已发货，快递公司已揽收",
            "recorded_at": (now - timedelta(hours=12)).isoformat(),
        },
    ]
    return traces


# ========== 地理编码接口(模拟) ==========

@router.get("/geocode", summary="地址转坐标(地理编码)")
async def geocode_address(
    address: str = Query(..., description="地址文本"),
    city: str = Query("", description="城市名称(可选)"),
):
    """
    将地址文本转换为经纬度坐标
    注意: 当前为模拟实现，生产环境应对接高德/百度/腾讯地图API
    """
    # 模拟地理编码结果
    mock_results = {
        "法库": {"latitude": 42.5095, "longitude": 123.4370},
        "沈阳": {"latitude": 41.7968, "longitude": 123.4497},
        "大连": {"latitude": 38.9140, "longitude": 121.6146},
        "长春": {"latitude": 43.8868, "longitude": 125.3245},
        "哈尔滨": {"latitude": 45.7500, "longitude": 126.6500},
        "北京": {"latitude": 39.9042, "longitude": 116.4074},
        "上海": {"latitude": 31.2304, "longitude": 121.4737},
        "广州": {"latitude": 23.1291, "longitude": 113.2644},
        "深圳": {"latitude": 22.5431, "longitude": 114.0579},
    }

    # 模糊匹配
    result = None
    matched_city = ""
    for city_name, coords in mock_results.items():
        if city_name in address or (city and city_name in city):
            result = coords
            matched_city = city_name
            break

    if not result:
        # 默认返回北京坐标
        result = {"latitude": 39.9042, "longitude": 116.4074}
        matched_city = "未知"

    return {
        "code": 0,
        "message": "success",
        "data": {
            "address": address,
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "formatted_address": f"{matched_city} {address}",
            "source": "mock",
            "note": "模拟数据，生产环境请对接真实地图API"
        }
    }


@router.get("/reverse-geocode", summary="坐标转地址(逆地理编码)")
async def reverse_geocode(
    latitude: float = Query(..., description="纬度"),
    longitude: float = Query(..., description="经度"),
):
    """
    将经纬度坐标转换为地址文本
    注意: 当前为模拟实现，生产环境应对接高德/百度/腾讯地图API
    """
    # 模拟逆地理编码
    # 根据坐标范围粗略判断城市
    city_map = [
        ((42.0, 43.0, 123.0, 124.0), "辽宁省沈阳市法库县"),
        ((41.5, 42.0, 123.0, 124.0), "辽宁省沈阳市"),
        ((38.5, 39.5, 121.0, 122.0), "辽宁省大连市"),
        ((43.5, 44.5, 125.0, 126.0), "吉林省长春市"),
        ((45.5, 46.0, 126.0, 127.0), "黑龙江省哈尔滨市"),
        ((39.5, 40.5, 116.0, 117.0), "北京市"),
        ((31.0, 31.5, 121.0, 122.0), "上海市"),
        ((23.0, 23.5, 113.0, 114.0), "广东省广州市"),
    ]

    address = "未知地区"
    for (lat_min, lat_max, lon_min, lon_max), city_name in city_map:
        if lat_min <= latitude <= lat_max and lon_min <= longitude <= lon_max:
            address = city_name
            break

    return {
        "code": 0,
        "message": "success",
        "data": {
            "latitude": latitude,
            "longitude": longitude,
            "address": address,
            "formatted_address": f"{address}(经度:{longitude:.4f}, 纬度:{latitude:.4f})",
            "source": "mock",
            "note": "模拟数据，生产环境请对接真实地图API"
        }
    }


@router.get("/distance", summary="距离计算")
async def calculate_distance(
    from_lat: float = Query(..., description="起点纬度"),
    from_lng: float = Query(..., description="起点经度"),
    to_lat: float = Query(..., description="终点纬度"),
    to_lng: float = Query(..., description="终点经度"),
):
    """
    计算两点之间的直线距离和预估行车距离
    """
    straight_distance = haversine_distance(from_lat, from_lng, to_lat, to_lng)
    # 行车距离约为直线距离的1.3倍(经验系数)
    driving_distance = straight_distance * 1.3
    # 预估行车时间(平均时速40km/h)
    driving_time_minutes = round(driving_distance / (40000 / 60))

    return {
        "code": 0,
        "message": "success",
        "data": {
            "from": {"latitude": from_lat, "longitude": from_lng},
            "to": {"latitude": to_lat, "longitude": to_lng},
            "straight_distance": round(straight_distance, 1),  # 米
            "driving_distance": round(driving_distance, 1),  # 米
            "estimated_driving_time": driving_time_minutes,  # 分钟
            "note": "直线距离为精确计算，行车距离为估算值"
        }
    }
