# src/daily_notes/commands/search.py
"""search 子命令."""
import json
import click
import frontmatter
from daily_notes.commands.decorators import vault_option, json_output, ensure_init
from daily_notes.core.vault import list_all_months, get_month_dir


@click.command()
@click.argument("query")
@json_output()
@vault_option()
@ensure_init()
def search(query: str, as_json: bool, vault):
    """搜索笔记（标题/标签/内容精确匹配）."""
    months = list_all_months(vault)
    results = []
    query_lower = query.lower()
    for year, month in months:
        month_dir = get_month_dir(vault, year, month)
        if not month_dir.exists():
            continue
        for md_file in month_dir.rglob("*.md"):
            post = frontmatter.loads(md_file.read_text(encoding="utf-8"))
            searchable = " ".join([
                post.get("title", ""),
                post.get("summary", ""),
                post.get("content", ""),
                " ".join(post.get("tags", [])),
            ]).lower()
            if query_lower in searchable:
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
