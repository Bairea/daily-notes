# tests/test_shortcuts.py
from click.testing import CliRunner
from daily_notes.cli import main
from daily_notes.core.config import save_config, Config


def test_daily_shortcut(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, ["daily", "--vault", str(tmp_vault)])
    assert result.exit_code == 0


def test_weekly_shortcut(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, ["weekly", "--vault", str(tmp_vault)])
    assert result.exit_code == 0


def test_monthly_shortcut(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, ["monthly", "--vault", str(tmp_vault)])
    assert result.exit_code == 0
