"""add 子命令."""
import click
from daily_notes.commands.decorators import vault_option, ensure_init
from daily_notes.core.vault import get_current_month_dir, get_source_dir
from daily_notes.core.id import generate_date_id
from daily_notes.core.frontmatter import (
    create_source_frontmatter,
    serialize_note,
)


@click.command()
@click.argument("content")
@click.option("--url", default="", help="来源 URL")
@click.option("--type", "source_type", default="article", help="来源类型")
@click.option("--title", default="", help="标题")
@click.option("--summary", default="", help="小结")
@click.option("--body", default="", help="正文全文（cited source 的原文摘录）")
@click.option("--tag", multiple=True, help="标签（可重复）")
@vault_option()
@ensure_init()
def add(content: str, url: str, source_type: str, title: str, summary: str,
        body: str, tag: tuple[str, ...], vault):
    """添加一条 Source 笔记.

    CONTENT 是内容描述（小结或空想内容）。
    有 --url 时为 cited source，可通过 --body 保存原文全文。
    """
    id_ = generate_date_id()
    month_dir = get_current_month_dir(vault)
    cited_dir, fleeting_dir = get_source_dir(month_dir)

    if url:
        # cited source
        fm = create_source_frontmatter(
            id_=id_,
            source_type=source_type,
            title=title or content[:50],
            url=url,
            tags=list(tag),
            summary=summary or content,
        )
        target_dir = cited_dir
        body_content = body
    else:
        # fleeting source
        fm = create_source_frontmatter(
            id_=id_,
            source_type="fleeting",
            tags=list(tag),
        )
        target_dir = fleeting_dir
        body_content = content

    text = serialize_note(fm, body_content)
    file_path = target_dir / f"{id_}.md"
    file_path.write_text(text, encoding="utf-8")
    click.echo(str(file_path))
