# tests/test_search.py
from click.testing import CliRunner
from daily_notes.cli import main
from daily_notes.core.config import save_config, Config
from daily_notes.core.vault import get_current_month_dir, get_source_dir
from daily_notes.core.id import generate_date_id
from daily_notes.core.frontmatter import create_source_frontmatter, serialize_note


def test_search_finds_match(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    month_dir = get_current_month_dir(tmp_vault)
    cited_dir, _ = get_source_dir(month_dir)
    id_ = generate_date_id()
    fm = create_source_frontmatter(id_=id_, source_type="article", summary="Python async programming")
    (cited_dir / f"{id_}.md").write_text(serialize_note(fm), encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["search", "Python", "--vault", str(tmp_vault)])
    assert result.exit_code == 0
    assert id_ in result.output


def test_search_no_match(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, ["search", "nonexistent keyword", "--vault", str(tmp_vault)])
    assert result.exit_code == 0


def test_search_by_tag(tmp_vault):
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
    result = runner.invoke(main, ["search", "--tag", "alpha", "--vault", str(tmp_vault)])
    assert result.exit_code == 0
    assert id1 in result.output
    assert id2 not in result.output


def test_search_matches_body(tmp_vault, notes):
    """--body 存入的原文全文必须可被搜索（当前为 0 命中）."""
    notes.setup(tmp_vault)
    note_id = notes.add_source(tmp_vault, "异步深析",
                               body="原文里有一个独一无二的词：紫水晶骑兵")
    result = notes.run_ok("search", "紫水晶骑兵", vault=tmp_vault)
    assert note_id in result.output


def test_search_matches_fleeting_body(tmp_vault, notes):
    """fleeting 的内容存在正文里，必须可被搜索."""
    notes.setup(tmp_vault)
    note_id = notes.add_fleeting(tmp_vault, "控制权的归属决定同步与异步")
    result = notes.run_ok("search", "控制权", vault=tmp_vault)
    assert note_id in result.output


def test_search_output_includes_title(tmp_vault, notes):
    """结果行须含标题：否则命中正文的 fleeting 只是一串看不出内容的 id."""
    notes.setup(tmp_vault)
    notes.add_source(tmp_vault, "异步深析")
    result = notes.run_ok("search", "异步深析", vault=tmp_vault)
    assert "异步深析" in result.output
