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


def test_generate_id_with_date_obj():
    """generate_date_id 接受 datetime 指定日期前缀."""
    dt = datetime(2026, 8, 5)
    id_ = generate_date_id(dt)
    assert id_.startswith("20260805-")
    parts = id_.split("-")
    assert len(parts[1]) == 6


def test_generate_id_with_date_str():
    """generate_date_id 接受 YYYY-MM-DD 字符串."""
    id_ = generate_date_id("2026-08-05")
    assert id_.startswith("20260805-")
