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
    # 验证正文被写入文件
    files = list((tmp_vault / "202607" / "00-Source" / "cited").glob("*.md"))
    # 过滤掉可能的其他测试文件
    cited_files = [f for f in files if f.name != "20260720-345299.md"]
    assert len(cited_files) >= 1
    body = cited_files[-1].read_text(encoding="utf-8")
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


def test_add_requires_init(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["add", "test", "--vault", str(tmp_path)])
    assert result.exit_code != 0
    assert "setup" in result.output.lower()
