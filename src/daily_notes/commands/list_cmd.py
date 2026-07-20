"""list 子命令."""
import json
import click
from daily_notes.commands.decorators import vault_option, json_output, ensure_init
from daily_notes.core.vault import list_notes, list_all_months


@click.command("list")
@click.option("--type", "note_type", type=click.Choice(["source", "atomic", "review"]),
              default="source")
@click.option("--tag", default=None, help="按标签过滤")
@click.option("--since", default=None, help="起始日期 YYYY-MM-DD")
@json_output()
@vault_option()
@ensure_init()
def list_cmd(note_type: str, tag: str | None, since: str | None,
             as_json: bool, vault):
    """列出笔记."""
    months = list_all_months(vault)
    items = []
    for year, month in months:
        for note in list_notes(vault, year, month, note_type):
            items.append({
                "id": note.id_,
                "type": note.type,
                "path": str(note.path.relative_to(vault)),
            })

    if as_json:
        click.echo(json.dumps(items, ensure_ascii=False, indent=2))
    else:
        for item in items:
            click.echo(f"{item['id']}  {item['path']}")
