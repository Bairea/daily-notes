import json


def test_show_outputs_frontmatter_and_body(tmp_vault, notes):
    notes.setup(tmp_vault)
    note_id = notes.add_source(tmp_vault, "异步深析",
                               body="事件循环是核心调度器")
    result = notes.run_ok("show", note_id, vault=tmp_vault)
    assert "异步深析" in result.output
    assert "事件循环是核心调度器" in result.output


def test_show_json_keys_always_present(tmp_vault, notes):
    """--json 字段恒定存在（缺省为空值），避免 agent 判断键是否存在."""
    notes.setup(tmp_vault)
    note_id = notes.add_source(tmp_vault, "异步深析", body="事件循环")
    result = notes.run_ok("show", note_id, "--json", vault=tmp_vault)
    data = json.loads(result.output)
    for key in ["id", "type", "created", "tags", "status", "stale_note",
                "title", "url", "summary", "source_type",
                "sources", "links", "backlinks", "body", "path"]:
        assert key in data, f"缺少字段 {key}"
    assert data["id"] == note_id
    assert data["body"] == "事件循环"


def test_show_atomic_exposes_relations(tmp_vault, notes):
    """agent 判断「值不值得提炼」需要完整的 links/sources 结构."""
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "源材料")
    a1 = notes.ingest(tmp_vault, src, title="甲")
    a2 = notes.ingest(tmp_vault, src, title="乙")
    notes.link(tmp_vault, a1, a2, "互补视角")
    data = json.loads(notes.run_ok("show", a1, "--json", vault=tmp_vault).output)
    assert data["sources"] == [src]
    assert data["links"][0]["target"] == a2
    data2 = json.loads(notes.run_ok("show", a2, "--json", vault=tmp_vault).output)
    assert data2["backlinks"][0]["source"] == a1


def test_show_missing_id_exits_with_error(tmp_vault, notes):
    notes.setup(tmp_vault)
    result = notes.run("show", "99999999-ffffff", vault=tmp_vault)
    assert result.exit_code == 1
    assert "未找到" in result.output
