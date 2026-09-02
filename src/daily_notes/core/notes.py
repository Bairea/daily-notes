"""笔记查询层 — 跨命令共享的遍历、定位与派生状态计算."""
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import click
import frontmatter

from daily_notes.core.vault import list_all_months, get_month_dir

TITLE_TRUNCATE = 40


@dataclass
class NoteRef:
    """一条笔记：物理位置 + 解析后的 front matter 与正文."""

    id_: str
    path: Path
    post: frontmatter.Post
    rel_path: str = ""

    @property
    def type(self) -> str:
        return self.post.get("type", "")

    @property
    def status(self) -> str:
        """状态标记：stale / archived，缺省返回空字符串."""
        return self.post.get("status", "")

    @property
    def tags(self) -> list[str]:
        return self.post.get("tags", [])

    @property
    def is_stale(self) -> bool:
        return self.status == "stale"

    @property
    def title(self) -> str:
        """展示用标题：优先 title 字段，否则取正文首行."""
        t = self.post.get("title", "")
        if t:
            return t
        lines = self.post.content.strip().splitlines()
        if not lines:
            return ""
        line = lines[0].strip()
        return line[:TITLE_TRUNCATE] + ("..." if len(line) > TITLE_TRUNCATE else "")

    def save(self) -> None:
        """将 front matter 与正文写回原文件."""
        self.path.write_text(frontmatter.dumps(self.post), encoding="utf-8")


def iter_notes(vault: Path, note_type: str | None = None) -> Iterator[NoteRef]:
    """遍历全库笔记，按路径升序。front matter 解析失败则跳过并警告."""
    for year, month in list_all_months(vault):
        month_dir = get_month_dir(vault, year, month)
        if not month_dir.exists():
            continue
        for md_file in sorted(month_dir.rglob("*.md")):
            try:
                post = frontmatter.loads(md_file.read_text(encoding="utf-8"))
            except Exception:
                click.echo(f"警告：无法解析 {md_file}，已跳过。", err=True)
                continue
            if note_type and post.get("type", "") != note_type:
                continue
            yield NoteRef(
                id_=md_file.stem,
                path=md_file,
                post=post,
                rel_path=str(md_file.relative_to(vault)),
            )


def find_note(vault: Path, id_: str) -> NoteRef | None:
    """按 id 定位单条笔记，未找到返回 None."""
    for note in iter_notes(vault):
        if note.id_ == id_:
            return note
    return None


def collect_source_refs(vault: Path) -> dict[str, list[str]]:
    """派生「哪些 source 已被消化」：返回 {source_id: [atomic_id, ...]}.

    这是已消化状态的唯一真相源，不落盘存储。删除 atomic 后
    对应 source 自动回到待消化队列。
    """
    refs: dict[str, list[str]] = {}
    for note in iter_notes(vault, note_type="atomic"):
        for source_id in note.post.get("sources", []):
            refs.setdefault(source_id, []).append(note.id_)
    return refs
