import json


def test_daily_lists_unprocessed_sources(tmp_vault, notes):
    notes.setup(tmp_vault)
    notes.add_source(tmp_vault, "第一篇")
    result = notes.run_ok("daily", vault=tmp_vault)
    assert "第一篇" in result.output


def test_daily_excludes_ingested_sources(tmp_vault, notes):
    """已被引用的 source 不再出现在待办中（派生自 atomic 的 sources）."""
    notes.setup(tmp_vault)
    s1 = notes.add_source(tmp_vault, "被消化的")
    s2 = notes.add_source(tmp_vault, "未消化的")
    notes.ingest(tmp_vault, s1, title="A")
    result = notes.run_ok("daily", vault=tmp_vault)
    assert "被消化的" not in result.output
    assert "未消化的" in result.output


def test_daily_excludes_archived_and_stale(tmp_vault, notes):
    notes.setup(tmp_vault)
    s1 = notes.add_source(tmp_vault, "归档的")
    s2 = notes.add_source(tmp_vault, "过期的")
    s3 = notes.add_source(tmp_vault, "正常的")
    notes.mark(tmp_vault, s1, "archived")
    notes.mark(tmp_vault, s2, "stale")
    result = notes.run_ok("daily", vault=tmp_vault)
    assert "归档的" not in result.output
    assert "过期的" not in result.output
    assert "正常的" in result.output


def test_daily_includes_fleeting(tmp_vault, notes):
    notes.setup(tmp_vault)
    notes.add_fleeting(tmp_vault, "一个转瞬即逝的想法")
    result = notes.run_ok("daily", vault=tmp_vault)
    assert "一个转瞬即逝的想法" in result.output


def test_daily_returns_to_queue_when_atomic_deleted(tmp_vault, notes):
    """删除 atomic 后 source 自动回退为待办 —— 派生状态的直接收益."""
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "会被退回的")
    atomic_id = notes.ingest(tmp_vault, src, title="A")
    assert "会被退回的" not in notes.run_ok("daily", vault=tmp_vault).output
    from daily_notes.core.notes import find_note
    find_note(tmp_vault, atomic_id).path.unlink()
    assert "会被退回的" in notes.run_ok("daily", vault=tmp_vault).output


def test_daily_empty_has_friendly_message(tmp_vault, notes):
    notes.setup(tmp_vault)
    result = notes.run_ok("daily", vault=tmp_vault)
    assert "没有" in result.output


def test_daily_json_shape(tmp_vault, notes):
    notes.setup(tmp_vault)
    notes.add_source(tmp_vault, "第一篇", tag="pattern")
    data = json.loads(notes.run_ok("daily", "--json", vault=tmp_vault).output)
    assert isinstance(data, list)
    assert data[0]["title"] == "第一篇"
    assert data[0]["tags"] == ["pattern"]
    assert "path" in data[0] and "id" in data[0]
