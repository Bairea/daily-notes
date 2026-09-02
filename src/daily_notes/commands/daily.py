"""daily 子命令."""
import json
import click
from daily_notes.commands.decorators import vault_option, json_output, ensure_init
from daily_notes.core.notes import iter_notes, collect_source_refs


@click.command()
@json_output()
@vault_option()
@ensure_init()
def daily(as_json: bool, vault):
    """列出待消化的 Source（尚未产出 Atomic，且未归档、未过期）.

    按状态过滤，与创建时间无关。按 id 升序输出，最老的积压排最前
    （id 格式为 YYYYMMDD-<hash>，见原设计 §6.4）。
    """
    refs = collect_source_refs(vault)
    items = []
    for note in iter_notes(vault, note_type="source"):
        if note.id_ in refs:
            continue
        if note.status in ("archived", "stale"):
            continue
        items.append({
            "id": note.id_,
            "source_type": note.post.get("source_type", ""),
            "title": note.title,
            "tags": note.tags,
            "path": note.rel_path,
        })
    items.sort(key=lambda x: x["id"])

    if as_json:
        click.echo(json.dumps(items, ensure_ascii=False, indent=2))
    elif not items:
        click.echo("没有待消化的 source。")
    else:
        click.echo(f"# 待消化 Source ({len(items)})")
        for it in items:
            date = f"{it['id'][:4]}-{it['id'][4:6]}-{it['id'][6:8]}"
            click.echo(f"- [{it['id']}] {it['title']}  ({date}, {it['source_type']})")
