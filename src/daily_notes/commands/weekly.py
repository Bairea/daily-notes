"""weekly 子命令."""
import json
import click
from daily_notes.commands.decorators import vault_option, json_output, ensure_init
from daily_notes.core.notes import iter_notes


def collect_unlinked(vault) -> list[dict]:
    """待连接的 atomic：无出链且未过期（backlinks 不计入）."""
    items = []
    for note in iter_notes(vault, note_type="atomic"):
        if note.post.get("links"):
            continue
        if note.is_stale:
            continue
        items.append({
            "id": note.id_,
            "title": note.title,
            "tags": note.tags,
            "path": note.rel_path,
        })
    items.sort(key=lambda x: x["id"])
    return items


@click.command()
@json_output()
@vault_option()
@ensure_init()
def weekly(as_json: bool, vault):
    """列出待连接的 Atomic（尚未建立出链，且未过期）."""
    items = collect_unlinked(vault)
    if as_json:
        click.echo(json.dumps(items, ensure_ascii=False, indent=2))
    elif not items:
        click.echo("没有待连接的 atomic。")
    else:
        click.echo(f"# 待连接 Atomic ({len(items)})")
        for it in items:
            tags = f"  [{', '.join(it['tags'])}]" if it["tags"] else ""
            click.echo(f"- [{it['id']}] {it['title']}{tags}")
