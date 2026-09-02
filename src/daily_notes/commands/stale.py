"""stale 子命令."""
import json
import click
from daily_notes.commands.decorators import vault_option, json_output, ensure_init
from daily_notes.core.notes import iter_notes


@click.command()
@json_output()
@vault_option()
@ensure_init()
def stale(as_json: bool, vault):
    """列出全部过期内容（status: stale），作为复核入口.

    标记过期 = 暂停一切、先复核。复核后执行 `mark <id> active`
    即自动回到原队列。
    """
    items = []
    for note in iter_notes(vault):
        if not note.is_stale:
            continue
        items.append({
            "id": note.id_,
            "type": note.type,
            "title": note.title,
            "stale_note": note.post.get("stale_note", ""),
            "path": note.rel_path,
        })
    items.sort(key=lambda x: x["id"])

    if as_json:
        click.echo(json.dumps(items, ensure_ascii=False, indent=2))
    elif not items:
        click.echo("没有过期的内容。")
    else:
        click.echo(f"# 过期内容 ({len(items)})")
        for it in items:
            note_text = f"  {it['stale_note']}" if it["stale_note"] else ""
            click.echo(f"- [{it['id']}] {it['title']}  [{it['type']}]{note_text}")
