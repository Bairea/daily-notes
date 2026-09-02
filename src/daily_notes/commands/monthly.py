"""monthly 子命令."""
import json
from collections import defaultdict

import click

from daily_notes.commands.decorators import vault_option, json_output, ensure_init
from daily_notes.commands.weekly import collect_unlinked
from daily_notes.core.notes import iter_notes

UNTAGGED = "未打标签"


@click.command()
@json_output()
@vault_option()
@ensure_init()
def monthly(as_json: bool, vault):
    """按 tag 聚类展示全部 Atomic，并附待连接清单.

    聚类是「展示」视角：过期内容仍列出并加 [过期] 标记（不隐藏历史）。
    待连接清单是「建设性队列」：排除过期内容（不在过期基础上继续建设）。
    """
    atomics = list(iter_notes(vault, note_type="atomic"))
    groups: dict[str, list[dict]] = defaultdict(list)
    for note in atomics:
        entry = {
            "id": note.id_,
            "title": note.title,
            "stale": note.is_stale,
            "path": note.rel_path,
        }
        if note.tags:
            for t in note.tags:
                groups[t].append(entry)
        else:
            groups[UNTAGGED].append(entry)

    clusters = []
    for tag, entries in groups.items():
        entries.sort(key=lambda x: x["id"])
        clusters.append({"tag": tag, "notes": entries})
    # 组内数量降序；数量相同时按 tag 名升序，保证输出稳定
    clusters.sort(key=lambda c: (-len(c["notes"]), c["tag"]))

    unlinked = collect_unlinked(vault)

    if as_json:
        click.echo(json.dumps({"clusters": clusters, "unlinked": unlinked},
                              ensure_ascii=False, indent=2))
        return

    click.echo(f"# 主题聚类 ({len(clusters)} 个主题 / {len(atomics)} 条 atomic)")
    for c in clusters:
        click.echo(f"## {c['tag']} ({len(c['notes'])})")
        for n in c["notes"]:
            marker = "  [过期]" if n["stale"] else ""
            click.echo(f"- [{n['id']}] {n['title']}{marker}")
    click.echo("")
    click.echo(f"# 待连接 Atomic ({len(unlinked)})")
    if not unlinked:
        click.echo("没有待连接的 atomic。")
    for it in unlinked:
        tags = f"  [{', '.join(it['tags'])}]" if it["tags"] else ""
        click.echo(f"- [{it['id']}] {it['title']}{tags}")
