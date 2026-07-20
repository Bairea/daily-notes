from datetime import datetime

from daily_notes.core.id import generate_date_id, parse_id


def test_generate_id_format():
    """id 格式: YYYYMMDD-<6位短哈希>."""
    id_ = generate_date_id()
    parts = id_.split("-")
    assert len(parts) == 2
    assert len(parts[0]) == 8  # YYYYMMDD
    assert len(parts[1]) == 6  # 短哈希
    assert parts[0].isdigit()


def test_generate_id_uniqueness():
    """同一时刻生成的 id 应唯一."""
    ids = {generate_date_id() for _ in range(100)}
    assert len(ids) == 100


def test_parse_id():
    """parse_id 返回 datetime."""
    id_ = generate_date_id()
    dt = parse_id(id_)
    assert isinstance(dt, datetime)
    assert dt.year >= 2026
