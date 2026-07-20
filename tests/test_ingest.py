# tests/test_ingest.py
from click.testing import CliRunner
from daily_notes.cli import main
from daily_notes.core.config import save_config, Config
from daily_notes.core.vault import get_current_month_dir, get_source_dir, get_atomic_dir
from daily_notes.core.id import generate_date_id
from daily_notes.core.frontmatter import create_source_frontmatter, serialize_note


def test_ingest_creates_atomic(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    month_dir = get_current_month_dir(tmp_vault)
    cited_dir, _ = get_source_dir(month_dir)
    source_id = generate_date_id()
    fm = create_source_frontmatter(id_=source_id, source_type="article", summary="test")
    (cited_dir / f"{source_id}.md").write_text(serialize_note(fm), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, [
        "ingest", "--source", source_id,
        "--content", "My atomic note content",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0
    atomic_dir = get_atomic_dir(month_dir)
    atomic_files = list(atomic_dir.glob("*.md"))
    assert len(atomic_files) == 1


def test_ingest_missing_source(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, [
        "ingest", "--source", "nonexistent-id",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code != 0
