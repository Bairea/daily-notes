# tests/test_list.py
from click.testing import CliRunner
from daily_notes.cli import main
from daily_notes.core.config import save_config, Config
from daily_notes.core.vault import (
    get_current_month_dir, get_source_dir, get_month_dir, ensure_month_dirs,
)
from daily_notes.core.id import generate_date_id
from daily_notes.core.frontmatter import create_source_frontmatter, serialize_note


def test_list_empty(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, ["list", "--type", "source", "--vault", str(tmp_vault)])
    assert result.exit_code == 0


def test_list_with_notes(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    month_dir = get_current_month_dir(tmp_vault)
    cited_dir, _ = get_source_dir(month_dir)
    id_ = generate_date_id()
    fm = create_source_frontmatter(id_=id_, source_type="article", summary="test")
    (cited_dir / f"{id_}.md").write_text(serialize_note(fm), encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["list", "--type", "source", "--vault", str(tmp_vault)])
    assert result.exit_code == 0
    assert id_ in result.output


def test_list_filter_by_tag(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    month_dir = get_current_month_dir(tmp_vault)
    cited_dir, _ = get_source_dir(month_dir)
    id1 = generate_date_id()
    fm1 = create_source_frontmatter(id_=id1, source_type="article",
                                    summary="alpha", tags=["alpha"])
    (cited_dir / f"{id1}.md").write_text(serialize_note(fm1), encoding="utf-8")
    id2 = generate_date_id()
    fm2 = create_source_frontmatter(id_=id2, source_type="article",
                                    summary="beta", tags=["beta"])
    (cited_dir / f"{id2}.md").write_text(serialize_note(fm2), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["list", "--type", "source", "--tag", "alpha",
                                  "--vault", str(tmp_vault)])
    assert result.exit_code == 0
    assert id1 in result.output
    assert id2 not in result.output


def test_list_filter_by_since(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    ensure_month_dirs(tmp_vault, 2026, 7)
    ensure_month_dirs(tmp_vault, 2026, 8)
    july_cited, _ = get_source_dir(get_month_dir(tmp_vault, 2026, 7))
    aug_cited, _ = get_source_dir(get_month_dir(tmp_vault, 2026, 8))
    id_july = "20260715-aaaaaa"
    fm1 = create_source_frontmatter(id_=id_july, source_type="article", summary="july")
    (july_cited / f"{id_july}.md").write_text(serialize_note(fm1), encoding="utf-8")
    id_aug = "20260815-bbbbbb"
    fm2 = create_source_frontmatter(id_=id_aug, source_type="article", summary="aug")
    (aug_cited / f"{id_aug}.md").write_text(serialize_note(fm2), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["list", "--type", "source", "--since", "2026-08-01",
                                  "--vault", str(tmp_vault)])
    assert result.exit_code == 0
    assert id_aug in result.output
    assert id_july not in result.output
