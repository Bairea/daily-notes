"""ingest 子命令."""
import click
from daily_notes.commands.decorators import vault_option, ensure_init
from daily_notes.core.vault import (
    get_current_month_dir, get_atomic_dir, list_all_months, get_month_dir,
)
from daily_notes.core.id import generate_date_id
from daily_notes.core.frontmatter import create_atomic_frontmatter, serialize_note


def _find_note_by_id(vault, id_: str):
    """在知识库中查找指定 id 的笔记."""
    months = list_all_months(vault)
    for year, month in months:
        month_dir = get_month_dir(vault, year, month)
        for md_file in month_dir.rglob("*.md"):
            if md_file.stem == id_:
                return md_file
    return None


@click.command()
@click.option("--source", required=True, help="Source 笔记 id")
@click.option("--content", default="", help="Atomic 正文内容")
@click.option("--title", default="", help="Atomic 标题")
@click.option("--tag", multiple=True, help="标签")
@vault_option()
@ensure_init()
def ingest(source: str, content: str, title: str, tag: tuple[str, ...], vault):
    """从 Source 创建 Atomic Note."""
    source_path = _find_note_by_id(vault, source)
    if not source_path:
        click.echo(f"错误：未找到 Source '{source}'。", err=True)
        raise SystemExit(1)

    id_ = generate_date_id()
    month_dir = get_current_month_dir(vault)
    atomic_dir = get_atomic_dir(month_dir)

    fm = create_atomic_frontmatter(
        id_=id_,
        title=title,
        sources=[source],
        tags=list(tag),
    )
    text = serialize_note(fm, content)
    file_path = atomic_dir / f"{id_}.md"
    file_path.write_text(text, encoding="utf-8")
    click.echo(str(file_path))
