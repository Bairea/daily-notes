import json


def test_stale_lists_stale_sources_and_atomics(tmp_vault, notes):
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "过期材料")
    a1 = notes.ingest(tmp_vault, src, title="过期笔记")
    notes.mark(tmp_vault, src, "stale", note_text="数据已过时")
    notes.mark(tmp_vault, a1, "stale", note_text="被新版取代")

    result = notes.run_ok("stale", vault=tmp_vault)
    assert "过期材料" in result.output
    assert "数据已过时" in result.output
    assert "过期笔记" in result.output
    assert "被新版取代" in result.output


def test_stale_excludes_normal_notes(tmp_vault, notes):
    notes.setup(tmp_vault)
    notes.add_source(tmp_vault, "正常材料")
    result = notes.run_ok("stale", vault=tmp_vault)
    assert "正常材料" not in result.output


def test_stale_excludes_archived(tmp_vault, notes):
    """archived 是「不打算处理」，stale 是「需要复核」，两者不混."""
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "归档材料")
    notes.mark(tmp_vault, src, "archived")
    result = notes.run_ok("stale", vault=tmp_vault)
    assert "归档材料" not in result.output


def test_stale_empty_message(tmp_vault, notes):
    notes.setup(tmp_vault)
    result = notes.run_ok("stale", vault=tmp_vault)
    assert "没有" in result.output


def test_stale_json_shape(tmp_vault, notes):
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "过期材料")
    notes.mark(tmp_vault, src, "stale", note_text="过时")
    data = json.loads(notes.run_ok("stale", "--json", vault=tmp_vault).output)
    assert data[0]["stale_note"] == "过时"
    assert data[0]["type"] == "source"
