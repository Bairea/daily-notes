"""ingest 子命令."""
from datetime import datetime
import click
from daily_notes.commands.decorators import vault_option, ensure_init
from daily_notes.core.input import resolve_text
from daily_notes.core.vault import get_current_month_dir, get_atomic_dir
from daily_notes.core.id import generate_date_id
from daily_notes.core.frontmatter import create_atomic_frontmatter, serialize_note
from daily_notes.core.notes import find_note, collect_source_refs


@click.command()
@click.option("--source", required=True, help="Source 笔记 id")
@click.option("--content", default="", help="Atomic 正文内容")
@click.option("--title", default="", help="Atomic 标题")
@click.option("--date", "content_date", default=None,
              help="内容日期(YYYY-MM-DD)，默认用操作日期")
@click.option("--tag", multiple=True, help="标签")
@vault_option()
@ensure_init()
def ingest(source: str, content: str, title: str, content_date: str,
           tag: tuple[str, ...], vault):
    """从 Source 创建 Atomic Note.

    --date 指定内容日期，atomic note 将存入该日期所在年月目录。
    """
    content = resolve_text(content, "content")
    source_note = find_note(vault, source)
    if not source_note:
        click.echo(f"错误：未找到 Source '{source}'。", err=True)
        raise SystemExit(1)

    refs = collect_source_refs(vault)
    if source in refs:
        click.echo(
            f"警告：该 source 已被 {len(refs[source])} 条 atomic 引用", err=True)
        for atomic_id in refs[source]:
            ref = find_note(vault, atomic_id)
            click.echo(f"  - {atomic_id}  {ref.title if ref else ''}", err=True)

    dt = None
    if content_date:
        try:
            dt = datetime.strptime(content_date, "%Y-%m-%d")
        except ValueError:
            click.echo("错误：日期格式无效，应为 YYYY-MM-DD", err=True)
            raise SystemExit(1)
    id_ = generate_date_id(dt)
    month_dir = get_current_month_dir(vault, dt)
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
