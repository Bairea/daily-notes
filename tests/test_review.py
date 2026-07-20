# tests/test_review.py
import frontmatter
from click.testing import CliRunner
from daily_notes.cli import main
from daily_notes.core.config import save_config, Config
from daily_notes.core.vault import ensure_month_dirs, get_current_month_dir, get_source_dir
from daily_notes.core.id import generate_date_id
from daily_notes.core.frontmatter import create_source_frontmatter, serialize_note


def _create_test_source(vault, content="test source"):
    month_dir = get_current_month_dir(vault)
    cited_dir, _ = get_source_dir(month_dir)
    id_ = generate_date_id()
    fm = create_source_frontmatter(id_=id_, source_type="article", summary=content)
    path = cited_dir / f"{id_}.md"
    path.write_text(serialize_note(fm), encoding="utf-8")
    return id_


def test_review_day(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    _create_test_source(tmp_vault)
    runner = CliRunner()
    result = runner.invoke(main, ["review", "--period", "day", "--focus", "ingest",
                                  "--vault", str(tmp_vault)])
    assert result.exit_code == 0


def test_review_json(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    _create_test_source(tmp_vault)
    runner = CliRunner()
    result = runner.invoke(main, ["review", "--period", "day", "--focus", "ingest",
                                  "--json", "--vault", str(tmp_vault)])
    assert result.exit_code == 0
    import json
    data = json.loads(result.output)
    assert "sources" in data
