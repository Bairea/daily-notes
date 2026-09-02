import json


def test_monthly_clusters_by_tag(tmp_vault, notes):
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "源材料")
    notes.ingest(tmp_vault, src, title="甲", tag="pattern")
    notes.ingest(tmp_vault, src, title="乙", tag="pattern")
    notes.ingest(tmp_vault, src, title="丙", tag="cli")
    result = notes.run_ok("monthly", vault=tmp_vault)
    assert "## pattern" in result.output
    assert "## cli" in result.output
    # 组内数量降序：pattern(2) 排在 cli(1) 之前
    assert result.output.index("## pattern") < result.output.index("## cli")


def test_monthly_untagged_group(tmp_vault, notes):
    """未打标签的归入「未打标签」组，把还没归类的笔记显式暴露出来."""
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "源材料")
    notes.ingest(tmp_vault, src, title="无标签笔记")
    result = notes.run_ok("monthly", vault=tmp_vault)
    assert "未打标签" in result.output
    assert "无标签笔记" in result.output


def test_monthly_multi_tag_note_appears_in_each_group(tmp_vault, notes):
    """多 tag 的笔记出现在其每一个 tag 分组下（tag 是多维分类）."""
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "源材料")
    notes.ingest(tmp_vault, src, title="跨领域笔记", tag=["pattern", "cli"])
    result = notes.run_ok("monthly", vault=tmp_vault)
    assert result.output.index("## cli") < result.output.index("跨领域笔记")
    assert "跨领域笔记" in result.output.split("## pattern")[1]


def test_monthly_cluster_shows_stale_but_queue_excludes(tmp_vault, notes):
    """聚类是展示视角（列出并标记）；待连接清单是建设性队列（排除）."""
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "源材料")
    a1 = notes.ingest(tmp_vault, src, title="过期笔记", tag="pattern")
    notes.mark(tmp_vault, a1, "stale")
    result = notes.run_ok("monthly", vault=tmp_vault)
    assert "[过期]" in result.output
    tail = result.output.split("# 待连接")[1]
    assert "过期笔记" not in tail


def test_monthly_includes_unlinked_queue(tmp_vault, notes):
    """monthly 内嵌待连接清单，使其可作为独立的全景复查命令."""
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "源材料")
    notes.ingest(tmp_vault, src, title="孤立笔记", tag="pattern")
    result = notes.run_ok("monthly", vault=tmp_vault)
    assert "# 待连接 Atomic" in result.output
    assert "孤立笔记" in result.output.split("# 待连接")[1]


def test_monthly_json_shape(tmp_vault, notes):
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "源材料")
    notes.ingest(tmp_vault, src, title="甲", tag="pattern")
    data = json.loads(notes.run_ok("monthly", "--json", vault=tmp_vault).output)
    assert "clusters" in data and "unlinked" in data
    assert data["clusters"][0]["tag"] == "pattern"
