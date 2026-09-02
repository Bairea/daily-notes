import json


def test_weekly_lists_unlinked_atomics(tmp_vault, notes):
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "源材料")
    notes.ingest(tmp_vault, src, title="孤立笔记")
    result = notes.run_ok("weekly", vault=tmp_vault)
    assert "孤立笔记" in result.output


def test_weekly_excludes_linked_atomics(tmp_vault, notes):
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "源材料")
    a1 = notes.ingest(tmp_vault, src, title="甲")
    a2 = notes.ingest(tmp_vault, src, title="乙")
    notes.link(tmp_vault, a1, a2, "关联")
    result = notes.run_ok("weekly", vault=tmp_vault)
    assert "甲" not in result.output
    assert "乙" in result.output


def test_weekly_backlinks_do_not_count(tmp_vault, notes):
    """仅有反向链接、自身未主动连出的，仍视为待连接.

    与原设计 §2.2「每个 Atomic 至少一个 Link」的不变量一致：
    该不变量指的是主动建立的出链。
    """
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "源材料")
    a1 = notes.ingest(tmp_vault, src, title="甲")
    a2 = notes.ingest(tmp_vault, src, title="乙")
    notes.link(tmp_vault, a1, a2, "关联")
    result = notes.run_ok("weekly", vault=tmp_vault)
    assert "乙" in result.output


def test_weekly_excludes_stale(tmp_vault, notes):
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "源材料")
    a1 = notes.ingest(tmp_vault, src, title="过期笔记")
    notes.mark(tmp_vault, a1, "stale")
    result = notes.run_ok("weekly", vault=tmp_vault)
    assert "过期笔记" not in result.output


def test_weekly_empty_message(tmp_vault, notes):
    notes.setup(tmp_vault)
    result = notes.run_ok("weekly", vault=tmp_vault)
    assert "没有" in result.output


def test_weekly_json_shape(tmp_vault, notes):
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "源材料")
    notes.ingest(tmp_vault, src, title="甲", tag="pattern")
    data = json.loads(notes.run_ok("weekly", "--json", vault=tmp_vault).output)
    assert data[0]["title"] == "甲"
    assert data[0]["tags"] == ["pattern"]
