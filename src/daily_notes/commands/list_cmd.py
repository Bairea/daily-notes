"""list 子命令."""
import json
import click
from daily_notes.commands.decorators import vault_option, json_output, ensure_init
from daily_notes.core.notes import iter_notes
from daily_notes.core.id import parse_id


@click.command("list")
@click.option("--type", "note_type", type=click.Choice(["source", "atomic"]),
              default="source")
@click.option("--tag", default=None, help="按标签过滤")
@click.option("--since", default=None, help="起始日期 YYYY-MM-DD")
@json_output()
@vault_option()
@ensure_init()
def list_cmd(note_type: str, tag: str | None, since: str | None,
             as_json: bool, vault):
    """列出笔记."""
    items = []
    for note in iter_notes(vault, note_type=note_type):
        if tag and tag not in note.tags:
            continue
        if since:
            try:
                parse_id(note.id_)
                since_date_str = since.replace("-", "")
                if note.id_[:8] < since_date_str:
                    continue
            except Exception:
                pass
        items.append({
            "id": note.id_,
            "type": note.type,
            "title": note.title,
            "stale": note.is_stale,
            "path": note.rel_path,
        })

    if as_json:
        click.echo(json.dumps(items, ensure_ascii=False, indent=2))
    else:
        for item in items:
            marker = "  [过期]" if item["stale"] else ""
            click.echo(f"{item['id']}  {item['path']}  {item['title']}{marker}")
