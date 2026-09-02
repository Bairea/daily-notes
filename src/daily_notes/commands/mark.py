"""mark 子命令."""
import click
from daily_notes.commands.decorators import vault_option, ensure_init
from daily_notes.commands.show import echo_not_found
from daily_notes.core.notes import find_note


@click.command()
@click.argument("note_id")
@click.argument("state", type=click.Choice(["stale", "archived", "active"]))
@click.option("--note", "note_text", default="",
              help="备注，state=stale 时写入 stale_note")
@vault_option()
@ensure_init()
def mark(note_id: str, state: str, note_text: str, vault):
    """修改笔记状态: stale(过期) / archived(归档) / active(恢复正常)."""
    note = find_note(vault, note_id)
    if note is None:
        echo_not_found(note_id, vault)
        raise SystemExit(1)

    if state == "archived" and note.type != "source":
        click.echo(f"错误：archived 仅适用于 source 笔记，"
                   f"'{note_id}' 是 {note.type}。", err=True)
        raise SystemExit(1)

    if state == "active":
        note.post.metadata.pop("status", None)
        note.post.metadata.pop("stale_note", None)
        click.echo(f"已恢复: {note_id} -> active")
    else:
        note.post["status"] = state
        # --note 仅绑定 stale（spec §5.4）；archived 不接受 stale_note
        if note_text and state == "stale":
            note.post["stale_note"] = note_text
        click.echo(f"已标记: {note_id} -> {state}")

    note.save()
