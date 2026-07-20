"""ID 生成模块.格式: YYYYMMDD-<6位短哈希>."""
import secrets
from datetime import datetime


def generate_date_id() -> str:
    """生成基于当前时间的唯一 id."""
    date_part = datetime.now().strftime("%Y%m%d")
    hash_part = secrets.token_hex(3)  # 6 hex chars
    return f"{date_part}-{hash_part}"


def parse_id(id_str: str) -> datetime:
    """从 id 解析出日期."""
    date_part = id_str.split("-")[0]
    return datetime.strptime(date_part, "%Y%m%d")
