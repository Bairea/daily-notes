from pathlib import Path
from daily_notes.core.vault import (
    get_month_dir,
    get_source_dir,
    get_atomic_dir,
    get_review_dir,
    ensure_month_dirs,
    list_notes,
    NoteInfo,
)
from daily_notes.core.id import generate_date_id


def test_get_month_dir():
    vault = Path("/tmp/vault")
    month_dir = get_month_dir(vault, 2026, 7)
    assert month_dir == vault / "202607"


def test_get_source_dirs():
    vault = Path("/tmp/vault")
    month_dir = vault / "202607"
    cited, fleeting = get_source_dir(month_dir)
    assert cited == month_dir / "00-Source" / "cited"
    assert fleeting == month_dir / "00-Source" / "fleeting"


def test_get_atomic_dir():
    vault = Path("/tmp/vault")
    month_dir = vault / "202607"
    assert get_atomic_dir(month_dir) == month_dir / "10-Atomic"


def test_get_review_dir():
    vault = Path("/tmp/vault")
    month_dir = vault / "202607"
    assert get_review_dir(month_dir) == month_dir / "20-Review"


def test_ensure_month_dirs(tmp_path):
    ensure_month_dirs(tmp_path, 2026, 7)
    month_dir = tmp_path / "202607"
    assert (month_dir / "00-Source" / "cited").is_dir()
    assert (month_dir / "00-Source" / "fleeting").is_dir()
    assert (month_dir / "10-Atomic").is_dir()
    assert (month_dir / "20-Review").is_dir()


def test_list_notes_empty(tmp_path):
    ensure_month_dirs(tmp_path, 2026, 7)
    notes = list_notes(tmp_path, 2026, 7, "atomic")
    assert notes == []


def test_list_notes_with_files(tmp_path):
    ensure_month_dirs(tmp_path, 2026, 7)
    atomic_dir = tmp_path / "202607" / "10-Atomic"
    id_ = generate_date_id()
    (atomic_dir / f"{id_}.md").write_text("test", encoding="utf-8")
    notes = list_notes(tmp_path, 2026, 7, "atomic")
    assert len(notes) == 1
    assert notes[0].id_ == id_
