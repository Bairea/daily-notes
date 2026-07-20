"""知识库文件路径管理."""
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class NoteInfo:
    """笔记元信息."""
    id_: str
    path: Path
    type: str


def get_month_dir(vault: Path, year: int, month: int) -> Path:
    """获取年月目录.如 vault/202607."""
    return vault / f"{year}{month:02d}"


def get_source_dir(month_dir: Path) -> tuple[Path, Path]:
    """获取 Source 子目录 (cited, fleeting)."""
    base = month_dir / "00-Source"
    return base / "cited", base / "fleeting"


def get_atomic_dir(month_dir: Path) -> Path:
    """获取 Atomic 目录."""
    return month_dir / "10-Atomic"


def get_review_dir(month_dir: Path) -> Path:
    """获取 Review 目录."""
    return month_dir / "20-Review"


def ensure_month_dirs(vault: Path, year: int, month: int) -> None:
    """确保年月的目录结构存在."""
    month_dir = get_month_dir(vault, year, month)
    cited, fleeting = get_source_dir(month_dir)
    atomic = get_atomic_dir(month_dir)
    review = get_review_dir(month_dir)
    for d in [cited, fleeting, atomic, review]:
        d.mkdir(parents=True, exist_ok=True)


def list_notes(vault: Path, year: int, month: int, note_type: str) -> list[NoteInfo]:
    """列出指定年月的某类型笔记."""
    month_dir = get_month_dir(vault, year, month)
    if not month_dir.exists():
        return []
    type_dir_map = {
        "source_cited": month_dir / "00-Source" / "cited",
        "source_fleeting": month_dir / "00-Source" / "fleeting",
        "source": month_dir / "00-Source",
        "atomic": month_dir / "10-Atomic",
        "review": month_dir / "20-Review",
    }
    search_dir = type_dir_map.get(note_type)
    if not search_dir or not search_dir.exists():
        return []
    notes = []
    for md_file in sorted(search_dir.rglob("*.md")):
        id_ = md_file.stem
        notes.append(NoteInfo(id_=id_, path=md_file, type=note_type))
    return notes


def list_all_months(vault: Path) -> list[tuple[int, int]]:
    """列出知识库中所有年月目录."""
    months = []
    for p in sorted(vault.iterdir()):
        if p.is_dir() and len(p.name) == 6 and p.name.isdigit():
            year = int(p.name[:4])
            month = int(p.name[4:])
            months.append((year, month))
    return months


def get_current_month_dir(vault: Path) -> Path:
    """获取当前年月的目录，不存在则创建."""
    now = datetime.now()
    ensure_month_dirs(vault, now.year, now.month)
    return get_month_dir(vault, now.year, now.month)
