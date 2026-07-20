# src/daily_notes/commands/link.py
"""link 子命令."""
import click
import frontmatter
from daily_notes.commands.decorators import vault_option, ensure_init
from daily_notes.core.vault import list_all_months, get_month_dir


def _find_note_by_id(vault, id_: str):
    """在知识库中查找指定 id 的笔记."""
    months = list_all_months(vault)
    for year, month in months:
        month_dir = get_month_dir(vault, year, month)
        if not month_dir.exists():
            continue
        for md_file in month_dir.rglob("*.md"):
            if md_file.stem == id_:
                return md_file
    return None


@click.command()
@click.argument("source_id")
@click.argument("target_id")
@click.argument("reason")
@vault_option()
@ensure_init()
def link(source_id: str, target_id: str, reason: str, vault):
    """在两个 Atomic Note 之间建立链接.

    SOURCE_ID 是源笔记 id，TARGET_ID 是目标笔记 id。
    """
    source_path = _find_note_by_id(vault, source_id)
    if not source_path:
        click.echo(f"错误：未找到笔记 '{source_id}'。", err=True)
        raise SystemExit(1)

    target_path = _find_note_by_id(vault, target_id)
    if not target_path:
        click.echo(f"错误：未找到笔记 '{target_id}'。", err=True)
        raise SystemExit(1)

    # 更新 source：添加出链
    source_post = frontmatter.loads(source_path.read_text(encoding="utf-8"))
    if "links" not in source_post:
        source_post["links"] = []
    source_post["links"].append({"target": target_id, "reason": reason})
    # 正文追加 Obsidian 文件引用
    link_text = f"\n- [{reason}]({target_id}.md)\n"
    if "## 相关笔记" not in source_post.content:
        source_post.content = source_post.content.rstrip() + "\n## 相关笔记\n" + link_text
    else:
        source_post.content = source_post.content.rstrip() + link_text
    source_path.write_text(frontmatter.dumps(source_post), encoding="utf-8")

    # 更新 target：添加 backlink
    target_post = frontmatter.loads(target_path.read_text(encoding="utf-8"))
    if "backlinks" not in target_post:
        target_post["backlinks"] = []
    target_post["backlinks"].append({"source": source_id, "reason": reason})
    backlink_text = f"\n- [{reason}]({source_id}.md)\n"
    if "## 反向链接" not in target_post.content:
        target_post.content = target_post.content.rstrip() + "\n## 反向链接\n" + backlink_text
    else:
        target_post.content = target_post.content.rstrip() + backlink_text
    target_path.write_text(frontmatter.dumps(target_post), encoding="utf-8")

    click.echo(f"已链接: {source_id} -> {target_id}")
