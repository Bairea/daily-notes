from daily_notes.core.notes import find_note


def test_mark_stale_with_note(tmp_vault, notes):
    notes.setup(tmp_vault)
    note_id = notes.add_source(tmp_vault, "异步深析")
    notes.mark(tmp_vault, note_id, "stale", note_text="被新版取代")
    note = find_note(tmp_vault, note_id)
    assert note.post["status"] == "stale"
    assert note.post["stale_note"] == "被新版取代"


def test_mark_active_clears_status_and_note(tmp_vault, notes):
    notes.setup(tmp_vault)
    note_id = notes.add_source(tmp_vault, "异步深析")
    notes.mark(tmp_vault, note_id, "stale", note_text="待复核")
    notes.mark(tmp_vault, note_id, "active")
    note = find_note(tmp_vault, note_id)
    assert "status" not in note.post
    assert "stale_note" not in note.post


def test_mark_active_on_plain_note_is_noop(tmp_vault, notes):
    """active 作用于无状态的笔记时不报错."""
    notes.setup(tmp_vault)
    note_id = notes.add_source(tmp_vault, "异步深析")
    result = notes.run("mark", note_id, "active", vault=tmp_vault)
    assert result.exit_code == 0


def test_mark_archived_rejects_atomic(tmp_vault, notes):
    """archived 仅适用于 source；目标是 atomic 时报错."""
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "源材料")
    atomic_id = notes.ingest(tmp_vault, src, title="原子")
    result = notes.run("mark", atomic_id, "archived", vault=tmp_vault)
    assert result.exit_code == 1
    assert "source" in result.output


def test_mark_archived_accepts_source(tmp_vault, notes):
    notes.setup(tmp_vault)
    note_id = notes.add_source(tmp_vault, "源材料")
    notes.mark(tmp_vault, note_id, "archived")
    assert find_note(tmp_vault, note_id).post["status"] == "archived"


def test_mark_archived_with_note_does_not_write_stale_note(tmp_vault, notes):
    """--note 仅绑定 stale；archived + --note 不得产出 stale_note（spec §5.4）."""
    notes.setup(tmp_vault)
    note_id = notes.add_source(tmp_vault, "源材料")
    result = notes.run("mark", note_id, "archived", "--note", "放弃",
                       vault=tmp_vault)
    assert result.exit_code == 0
    note = find_note(tmp_vault, note_id)
    assert note.post["status"] == "archived"
    assert "stale_note" not in note.post


def test_mark_idempotent(tmp_vault, notes):
    notes.setup(tmp_vault)
    note_id = notes.add_source(tmp_vault, "异步深析")
    notes.mark(tmp_vault, note_id, "stale")
    notes.mark(tmp_vault, note_id, "stale")
    assert find_note(tmp_vault, note_id).post["status"] == "stale"


def test_mark_preserves_body(tmp_vault, notes):
    """状态变更不得破坏正文."""
    notes.setup(tmp_vault)
    note_id = notes.add_source(tmp_vault, "异步深析", body="原文内容不可丢")
    notes.mark(tmp_vault, note_id, "stale", note_text="过期")
    assert "原文内容不可丢" in find_note(tmp_vault, note_id).post.content


def test_mark_missing_id_exits_with_error(tmp_vault, notes):
    notes.setup(tmp_vault)
    result = notes.run("mark", "99999999-ffffff", "stale", vault=tmp_vault)
    assert result.exit_code == 1
    assert "未找到" in result.output
