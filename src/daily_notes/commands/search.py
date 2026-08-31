# src/daily_notes/commands/search.py
"""search 子命令."""
import json
import click
import frontmatter
from daily_notes.commands.decorators import vault_option, json_output, ensure_init
from daily_notes.core.vault import list_all_months, get_month_dir


@click.command()
@click.argument("query", required=False)
@click.option("--tag", default=None, help="按标签过滤")
@json_output()
@vault_option()
@ensure_init()
def search(query: str | None, tag: str | None, as_json: bool, vault):
    """搜索笔记（标题/标签/内容精确匹配）.

    QUERY 为关键词，可选。--tag 按标签过滤。两者可组合使用。
    """
    if not query and not tag:
        click.echo("错误：请提供搜索关键词或 --tag 选项。", err=True)
        raise SystemExit(1)
    months = list_all_months(vault)
    results = []
    query_lower = query.lower() if query else ""
    for year, month in months:
        month_dir = get_month_dir(vault, year, month)
        if not month_dir.exists():
            continue
        for md_file in month_dir.rglob("*.md"):
            post = frontmatter.loads(md_file.read_text(encoding="utf-8"))
            note_tags = post.get("tags", [])
            if tag and tag not in note_tags:
                continue
            if query_lower:
                searchable = " ".join([
                    post.get("title", ""),
                    post.get("summary", ""),
                    post.get("content", ""),
                    " ".join(note_tags),
                ]).lower()
                if query_lower not in searchable:
                    continue
            results.append({
                "id": post["id"],
                "type": post.get("type", ""),
                "path": str(md_file.relative_to(vault)),
            })

    if as_json:
        click.echo(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            click.echo(f"{r['id']}  {r['path']}")
