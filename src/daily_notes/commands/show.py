"""show 子命令."""
import json
import click
from daily_notes.commands.decorators import vault_option, json_output, ensure_init
from daily_notes.core.notes import find_note, iter_notes


@click.command()
@click.argument("note_id")
@json_output()
@vault_option()
@ensure_init()
def show(note_id: str, as_json: bool, vault):
    """显示单条笔记的完整 front matter 与正文."""
    note = find_note(vault, note_id)
    if note is None:
        echo_not_found(note_id, vault)
        raise SystemExit(1)

    if as_json:
        click.echo(json.dumps({
            "id": note.id_,
            "type": note.type,
            "created": note.post.get("created", ""),
            "tags": note.tags,
            "status": note.status,
            "stale_note": note.post.get("stale_note", ""),
            "title": note.post.get("title", ""),
            "url": note.post.get("url", ""),
            "summary": note.post.get("summary", ""),
            "source_type": note.post.get("source_type", ""),
            "sources": note.post.get("sources", []),
            "links": note.post.get("links", []),
            "backlinks": note.post.get("backlinks", []),
            "body": note.post.content,
            "path": note.rel_path,
        }, ensure_ascii=False, indent=2))
        return

    click.echo(f"# {note.title or note.id_}")
    click.echo(f"id: {note.id_}")
    click.echo(f"type: {note.type}")
    click.echo(f"created: {note.post.get('created', '')}")
    click.echo(f"tags: {', '.join(note.tags) or '(无)'}")
    if note.status:
        click.echo(f"status: {note.status}")
    if note.post.get("stale_note"):
        click.echo(f"stale_note: {note.post['stale_note']}")
    if note.post.get("url"):
        click.echo(f"url: {note.post['url']}")
    if note.post.get("sources"):
        click.echo(f"sources: {', '.join(note.post['sources'])}")
    if note.post.get("links"):
        click.echo("links:")
        for l in note.post["links"]:
            click.echo(f"  - {l.get('target', '')}  {l.get('reason', '')}")
    if note.post.get("backlinks"):
        click.echo("backlinks:")
        for b in note.post["backlinks"]:
            click.echo(f"  - {b.get('source', '')}  {b.get('reason', '')}")
    click.echo("")
    click.echo(note.post.content)


def echo_not_found(note_id: str, vault) -> None:
    """输出未找到提示并列出可用 id."""
    available = [n.id_ for n in iter_notes(vault)]
    click.echo(f"错误：未找到笔记 '{note_id}'。", err=True)
    if not available:
        click.echo("知识库中暂无笔记。", err=True)
        return
    click.echo("可用的笔记 id：", err=True)
    for id_ in available[:20]:
        click.echo(f"  - {id_}", err=True)
    if len(available) > 20:
        click.echo(f"  ...（共 {len(available)} 条）", err=True)
