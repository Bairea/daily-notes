# tests/test_integration.py
import json

from tests.conftest import NotesHelper


def test_full_workflow(tmp_vault, notes: NotesHelper):
    """完整学习闭环: add -> daily -> ingest -> weekly -> link -> mark stale -> stale -> active -> search."""
    notes.setup(tmp_vault)

    # 1. add 两条 source（一条 cited，一条 fleeting）
    s1 = notes.add_source(tmp_vault, "Python Async 文章", tag="python")
    s2 = notes.add_fleeting(tmp_vault, "fleeting 灵感：异步本质")

    # 2. daily 应列出两条待消化 source
    daily = notes.run_ok("daily", "--json", vault=tmp_vault)
    daily_items = json.loads(daily.output)
    assert len(daily_items) == 2
    assert {it["id"] for it in daily_items} == {s1, s2}

    # 3. 从 s1 ingest 第一条 atomic（a1）
    a1 = notes.ingest(tmp_vault, s1, title="Async Core", tag="pattern")

    # 4. daily 中 s1 应消失（已引用），仅剩 s2
    daily_items = json.loads(notes.run_ok("daily", "--json", vault=tmp_vault).output)
    assert len(daily_items) == 1
    assert daily_items[0]["id"] == s2

    # 5. 从同一 source 再 ingest 一条（a2，一对多，触发已引用警告但不阻断）
    a2 = notes.ingest(tmp_vault, s1, title="Control Flow")

    # 6. weekly 应列出两条未连接的 atomic
    weekly_items = json.loads(notes.run_ok("weekly", "--json", vault=tmp_vault).output)
    assert len(weekly_items) == 2
    assert {it["id"] for it in weekly_items} == {a1, a2}

    # 7. 连接 a1 -> a2
    notes.link(tmp_vault, a1, a2, "互补视角")

    # 8. weekly 中 a1 应因已出链而退出队列，仅剩 a2
    weekly_items = json.loads(notes.run_ok("weekly", "--json", vault=tmp_vault).output)
    assert len(weekly_items) == 1
    assert weekly_items[0]["id"] == a2

    # 9. show a1 应暴露出链到 a2
    shown = json.loads(notes.run_ok("show", a1, "--json", vault=tmp_vault).output)
    assert any(l["target"] == a2 for l in shown["links"])

    # 10. 标记 a1 过期并附带说明
    notes.mark(tmp_vault, a1, "stale", note_text="假设已过时，需复核")

    # 11. stale 列表应仅含 a1，且带 stale_note
    stale_items = json.loads(notes.run_ok("stale", "--json", vault=tmp_vault).output)
    assert len(stale_items) == 1
    assert stale_items[0]["id"] == a1
    assert stale_items[0]["stale_note"] == "假设已过时，需复核"

    # 12. weekly 仍只含 a2（a1 既已连接又已过期，均被排除）
    weekly_items = json.loads(notes.run_ok("weekly", "--json", vault=tmp_vault).output)
    assert len(weekly_items) == 1
    assert weekly_items[0]["id"] == a2

    # 13. 复核后标记 a1 回到 active，stale 列表清空
    notes.mark(tmp_vault, a1, "active")
    stale_items = json.loads(notes.run_ok("stale", "--json", vault=tmp_vault).output)
    assert stale_items == []

    # 14. search 能按标题命中 a1
    found = json.loads(notes.run_ok("search", "Async Core", "--json", vault=tmp_vault).output)
    assert any(r["id"] == a1 for r in found)
