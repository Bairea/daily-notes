# tests/test_add.py
from click.testing import CliRunner
from daily_notes.cli import main
from daily_notes.core.config import save_config, Config
from daily_notes.core.vault import ensure_month_dirs


def test_add_cited(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, [
        "add", "一篇好文章",
        "--url", "https://example.com",
        "--type", "article",
        "--title", "Test",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0
    assert "2026" in result.output  # 路径包含年月


def test_add_cited_with_body(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, [
        "add", "小结",
        "--url", "https://example.com",
        "--type", "article",
        "--title", "Test",
        "--body", "这是文章的全文内容。\n第二段。",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0
    # 验证正文被写入文件（用动态月份，避免跨月测试失败）
    from datetime import datetime
    month_str = datetime.now().strftime("%Y%m")
    files = list((tmp_vault / month_str / "00-Source" / "cited").glob("*.md"))
    assert len(files) >= 1
    body = files[-1].read_text(encoding="utf-8")
    assert "这是文章的全文内容。" in body
    assert "第二段。" in body


def test_add_fleeting(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, [
        "add", "一个想法",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0


def test_add_with_content_date(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, [
        "add", "一篇好文章",
        "--url", "https://example.com",
        "--title", "Test",
        "--date", "2026-08-05",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0
    assert "202608" in result.output


def test_add_invalid_date(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, [
        "add", "test", "--url", "https://example.com",
        "--date", "not-a-date", "--vault", str(tmp_vault),
    ])
    assert result.exit_code != 0
    assert "YYYY-MM-DD" in result.output


def test_add_requires_init(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["add", "test", "--vault", str(tmp_path)])
    assert result.exit_code != 0
    assert "setup" in result.output.lower()


def test_add_body_from_stdin(tmp_vault, notes):
    notes.setup(tmp_vault)
    result = notes.run(
        "add", "小结", "--url", "https://example.com", "--title", "长文",
        "--body", "-", vault=tmp_vault,
        stdin="第一段：核心结论。\n\n第二段：包含「中文引号」。\n",
    )
    assert result.exit_code == 0
    from daily_notes.core.notes import iter_notes
    note = list(iter_notes(tmp_vault))[0]
    assert "第一段：核心结论。" in note.post.content
    assert "第二段：包含「中文引号」。" in note.post.content


def test_add_body_dash_is_not_literal(tmp_vault, notes):
    """'-' 是 stdin 标记，不应作为字面内容写入."""
    notes.setup(tmp_vault)
    notes.run_ok(
        "add", "小结", "--url", "https://example.com", "--title", "长文",
        "--body", "-", vault=tmp_vault, stdin="真实内容",
    )
    from daily_notes.core.notes import iter_notes
    note = list(iter_notes(tmp_vault))[0]
    assert note.post.content.strip() == "真实内容"
