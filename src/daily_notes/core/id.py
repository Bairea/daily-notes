"""ID 生成模块.格式: YYYYMMDD-<6位短哈希>."""
import secrets
from datetime import datetime, date as date_cls


def generate_date_id(date=None) -> str:
    """生成基于时间的唯一 id.

    date 为 None 时用当前时间；传入 datetime 或 YYYY-MM-DD 字符串时用该日期。
    """
    if date is None:
        dt = datetime.now()
    elif isinstance(date, str):
        dt = datetime.strptime(date, "%Y-%m-%d")
    elif isinstance(date, (datetime, date_cls)):
        dt = date
    else:
        dt = datetime.now()
    date_part = dt.strftime("%Y%m%d")
    hash_part = secrets.token_hex(3)  # 6 hex chars
    return f"{date_part}-{hash_part}"


def parse_id(id_str: str) -> datetime:
    """从 id 解析出日期."""
    date_part = id_str.split("-")[0]
    return datetime.strptime(date_part, "%Y%m%d")
