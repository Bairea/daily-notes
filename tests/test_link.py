# tests/test_link.py
import frontmatter
from click.testing import CliRunner
from daily_notes.cli import main
from daily_notes.core.config import save_config, Config
from daily_notes.core.vault import get_current_month_dir, get_atomic_dir
from daily_notes.core.id import generate_date_id
from daily_notes.core.frontmatter import create_atomic_frontmatter, serialize_note


def _create_atomic(vault, id_, title="test"):
    month_dir = get_current_month_dir(vault)
    atomic_dir = get_atomic_dir(month_dir)
    fm = create_atomic_frontmatter(id_=id_, title=title)
    (atomic_dir / f"{id_}.md").write_text(serialize_note(fm), encoding="utf-8")
    return atomic_dir / f"{id_}.md"


def test_link_creates_bidirectional(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    source_id = generate_date_id()
    target_id = generate_date_id()
    _create_atomic(tmp_vault, source_id, "Source Note")
    _create_atomic(tmp_vault, target_id, "Target Note")

    runner = CliRunner()
    result = runner.invoke(main, [
        "link", source_id, target_id, "两者相关",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0

    # 验证 source 有出链
    month_dir = get_current_month_dir(tmp_vault)
    atomic_dir = get_atomic_dir(month_dir)
    source_post = frontmatter.loads(
        (atomic_dir / f"{source_id}.md").read_text(encoding="utf-8")
    )
    assert any(l["target"] == target_id for l in source_post.get("links", []))

    # 验证 target 有反向链接
    target_post = frontmatter.loads(
        (atomic_dir / f"{target_id}.md").read_text(encoding="utf-8")
    )
    assert any(b["source"] == source_id for b in target_post.get("backlinks", []))
