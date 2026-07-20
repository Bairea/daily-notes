# src/daily_notes/commands/review.py
"""review 子命令."""
import json
import click
import frontmatter
from datetime import datetime, timedelta
from daily_notes.commands.decorators import vault_option, json_output, ensure_init
from daily_notes.core.vault import (
    list_all_months, get_month_dir, get_source_dir, get_atomic_dir,
)


def _collect_candidates(vault, period: str) -> dict:
    """根据时间范围收集候选笔记."""
    now = datetime.now()
    if period == "day":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif period == "week":
        start = now - timedelta(days=7)
        end = now
    elif period == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    else:
        start = now - timedelta(days=1)
        end = now

    candidates = {
        "period": period,
        "sources": [],
        "atomics": [],
    }

    months = list_all_months(vault)
    for year, month in months:
        month_dir = get_month_dir(vault, year, month)
        if not month_dir.exists():
            continue
        cited_dir, fleeting_dir = get_source_dir(month_dir)
        for md_file in sorted(cited_dir.glob("*.md")):
            post = frontmatter.loads(md_file.read_text(encoding="utf-8"))
            note_time = datetime.fromisoformat(post["created"])
            if start <= note_time <= end:
                candidates["sources"].append({
                    "id": post["id"],
                    "type": post.get("source_type", "article"),
                    "summary": post.get("summary", ""),
                    "path": str(md_file.relative_to(vault)),
                })
        for md_file in sorted(fleeting_dir.glob("*.md")):
            post = frontmatter.loads(md_file.read_text(encoding="utf-8"))
            note_time = datetime.fromisoformat(post["created"])
            if start <= note_time <= end:
                candidates["sources"].append({
                    "id": post["id"],
                    "type": "fleeting",
                    "summary": post.content.strip(),
                    "path": str(md_file.relative_to(vault)),
                })
        atomic_dir = get_atomic_dir(month_dir)
        for md_file in sorted(atomic_dir.glob("*.md")):
            post = frontmatter.loads(md_file.read_text(encoding="utf-8"))
            note_time = datetime.fromisoformat(post["created"])
            if start <= note_time <= end:
                candidates["atomics"].append({
                    "id": post["id"],
                    "title": post.get("title", ""),
                    "tags": post.get("tags", []),
                    "path": str(md_file.relative_to(vault)),
                })
    return candidates


@click.command()
@click.option("--period", type=click.Choice(["day", "week", "month"]), required=True)
@click.option("--focus", type=click.Choice(["ingest", "link", "pattern"]),
              multiple=True, required=True)
@json_output()
@vault_option()
@ensure_init()
def review(period: str, focus: tuple[str, ...], as_json: bool, vault):
    """列出指定时间范围内的候选笔记."""
    candidates = _collect_candidates(vault, period)
    if as_json:
        click.echo(json.dumps(candidates, ensure_ascii=False, indent=2))
    else:
        click.echo(f"# Review: {period}")
        click.echo(f"## Sources ({len(candidates['sources'])})")
        for s in candidates["sources"]:
            click.echo(f"- [{s['id']}] {s['summary'][:60]}")
        click.echo(f"## Atomics ({len(candidates['atomics'])})")
        for a in candidates["atomics"]:
            click.echo(f"- [{a['id']}] {a.get('title', '')}")
