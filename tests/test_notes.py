from pathlib import Path
import frontmatter
from daily_notes.core.notes import iter_notes, find_note, collect_source_refs
from daily_notes.core.vault import ensure_month_dirs


def _write(vault, rel: str, meta: dict, body: str = "") -> Path:
    p = vault / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    post = frontmatter.Post(body)
    for k, v in meta.items():
        post[k] = v
    p.write_text(frontmatter.dumps(post), encoding="utf-8")
    return p


def test_iter_notes_filters_by_type(tmp_path):
    ensure_month_dirs(tmp_path, 2026, 8)
    _write(tmp_path, "202608/00-Source/cited/20260801-aaaaaa.md",
           {"id": "20260801-aaaaaa", "type": "source"})
    _write(tmp_path, "202608/10-Atomic/20260802-bbbbbb.md",
           {"id": "20260802-bbbbbb", "type": "atomic"})
    assert [n.id_ for n in iter_notes(tmp_path, note_type="atomic")] == ["20260802-bbbbbb"]
    assert len(list(iter_notes(tmp_path))) == 2


def test_iter_notes_skips_unparsable_files(tmp_path):
    """front matter 解析失败时跳过并警告，不中断（沿用原设计 §10）."""
    ensure_month_dirs(tmp_path, 2026, 8)
    _write(tmp_path, "202608/10-Atomic/20260802-bbbbbb.md",
           {"id": "20260802-bbbbbb", "type": "atomic"})
    (tmp_path / "202608" / "10-Atomic" / "broken.md").write_text(
        "---\nkey: [unclosed\n---\nbody", encoding="utf-8")
    assert [n.id_ for n in iter_notes(tmp_path)] == ["20260802-bbbbbb"]


def test_find_note(tmp_path):
    ensure_month_dirs(tmp_path, 2026, 8)
    _write(tmp_path, "202608/10-Atomic/20260802-bbbbbb.md",
           {"id": "20260802-bbbbbb", "type": "atomic"})
    assert find_note(tmp_path, "20260802-bbbbbb") is not None
    assert find_note(tmp_path, "99999999-ffffff") is None


def test_note_ref_title_falls_back_to_body(tmp_path):
    """cited 取 title 字段；无 title 时取正文首行截断 40 字."""
    ensure_month_dirs(tmp_path, 2026, 8)
    _write(tmp_path, "202608/00-Source/fleeting/20260803-cccccc.md",
           {"id": "20260803-cccccc", "type": "source"},
           body="控制权的归属决定了同步与异步的本质差异" + "续" * 40)
    note = find_note(tmp_path, "20260803-cccccc")
    assert len(note.title) <= 43
    assert note.title.startswith("控制权的归属")


def test_note_ref_exposes_status(tmp_path):
    ensure_month_dirs(tmp_path, 2026, 8)
    _write(tmp_path, "202608/10-Atomic/20260802-bbbbbb.md",
           {"id": "20260802-bbbbbb", "type": "atomic", "status": "stale"})
    _write(tmp_path, "202608/10-Atomic/20260803-dddddd.md",
           {"id": "20260803-dddddd", "type": "atomic"})
    assert find_note(tmp_path, "20260802-bbbbbb").is_stale is True
    assert find_note(tmp_path, "20260803-dddddd").is_stale is False
    assert find_note(tmp_path, "20260803-dddddd").status == ""


def test_collect_source_refs(tmp_path):
    """已消化状态是派生的：由 atomic 的 sources 反查."""
    ensure_month_dirs(tmp_path, 2026, 8)
    _write(tmp_path, "202608/00-Source/cited/20260801-aaaaaa.md",
           {"id": "20260801-aaaaaa", "type": "source"})
    _write(tmp_path, "202608/10-Atomic/20260802-bbbbbb.md",
           {"id": "20260802-bbbbbb", "type": "atomic", "sources": ["20260801-aaaaaa"]})
    _write(tmp_path, "202608/10-Atomic/20260803-dddddd.md",
           {"id": "20260803-dddddd", "type": "atomic", "sources": ["20260801-aaaaaa"]})
    refs = collect_source_refs(tmp_path)
    assert sorted(refs["20260801-aaaaaa"]) == ["20260802-bbbbbb", "20260803-dddddd"]
    assert "20260809-zzzzzz" not in refs
