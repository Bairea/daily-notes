"""search 子命令."""
import json
import click
from daily_notes.commands.decorators import vault_option, json_output, ensure_init
from daily_notes.core.notes import iter_notes


@click.command()
@click.argument("query", required=False)
@click.option("--tag", default=None, help="按标签过滤")
@json_output()
@vault_option()
@ensure_init()
def search(query: str | None, tag: str | None, as_json: bool, vault):
    """搜索笔记（标题/标签/正文精确匹配）.

    QUERY 为关键词，可选。--tag 按标签过滤。两者可组合使用。
    """
    if not query and not tag:
        click.echo("错误：请提供搜索关键词或 --tag 选项。", err=True)
        raise SystemExit(1)

    query_lower = query.lower() if query else ""
    results = []
    for note in iter_notes(vault):
        if tag and tag not in note.tags:
            continue
        if query_lower:
            searchable = " ".join([
                note.post.get("title", ""),
                note.post.get("summary", ""),
                note.post.content,
                " ".join(note.tags),
            ]).lower()
            if query_lower not in searchable:
                continue
        results.append({
            "id": note.id_,
            "type": note.type,
            "title": note.title,
            "stale": note.is_stale,
            "path": note.rel_path,
        })

    if as_json:
        click.echo(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            marker = "  [过期]" if r["stale"] else ""
            click.echo(f"{r['id']}  {r['path']}  {r['title']}{marker}")
