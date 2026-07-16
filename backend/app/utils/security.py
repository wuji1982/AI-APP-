"""
密码加密与验证服务
使用 bcrypt 进行密码哈希
"""
import hashlib
import secrets
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """密码加密"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def generate_invite_code(length: int = 8) -> str:
    """生成邀请码"""
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_order_no(prefix: str = "GB") -> str:
    """生成订单号"""
    import datetime
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    random_str = secrets.token_hex(3).upper()
    return f"{prefix}{timestamp}{random_str}"
