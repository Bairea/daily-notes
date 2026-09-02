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


def test_ingest_with_content_date(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    month_dir = get_current_month_dir(tmp_vault)
    cited_dir, _ = get_source_dir(month_dir)
    source_id = generate_date_id()
    fm = create_source_frontmatter(id_=source_id, source_type="article", summary="test")
    (cited_dir / f"{source_id}.md").write_text(serialize_note(fm), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, [
        "ingest", "--source", source_id,
        "--content", "atomic content",
        "--date", "2026-08-05",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0
    assert "202608" in result.output


def test_ingest_missing_source(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, [
        "ingest", "--source", "nonexistent-id",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code != 0


def test_ingest_content_from_stdin(tmp_vault, notes):
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "源材料")
    notes.run_ok(
        "ingest", "--source", src, "--title", "原子",
        "--content", "-", vault=tmp_vault, stdin="第一段。\n\n第二段。\n",
    )
    from daily_notes.core.notes import find_note
    from daily_notes.core.vault import get_current_month_dir, get_atomic_dir
    atomic = list(get_atomic_dir(get_current_month_dir(tmp_vault)).glob("*.md"))[0]
    assert "第一段。" in find_note(tmp_vault, atomic.stem).post.content


def test_ingest_warns_on_already_referenced_source(tmp_vault, notes):
    """不阻止重复 ingest（一对多是设计），但输出提示."""
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "源材料")
    notes.ingest(tmp_vault, src, title="甲")
    result = notes.run("ingest", "--source", src, "--title", "乙",
                       vault=tmp_vault)
    assert result.exit_code == 0
    assert "已被" in result.output
    assert "甲" in result.output


def test_ingest_still_creates_when_referenced(tmp_vault, notes):
    """提示归提示，创建照常."""
    notes.setup(tmp_vault)
    src = notes.add_source(tmp_vault, "源材料")
    notes.ingest(tmp_vault, src, title="甲")
    notes.ingest(tmp_vault, src, title="乙")
    from daily_notes.core.vault import get_current_month_dir, get_atomic_dir
    atomic_dir = get_atomic_dir(get_current_month_dir(tmp_vault))
    assert len(list(atomic_dir.glob("*.md"))) == 2
