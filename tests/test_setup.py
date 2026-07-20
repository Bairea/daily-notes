# tests/test_setup.py
from click.testing import CliRunner
from daily_notes.cli import main
from daily_notes.core.config import load_config, is_initialized
from daily_notes.core.vault import ensure_month_dirs


def test_setup_creates_config(tmp_vault):
    runner = CliRunner()
    result = runner.invoke(main, ["setup", "--vault", str(tmp_vault)])
    assert result.exit_code == 0
    assert is_initialized(tmp_vault)
    config = load_config(tmp_vault)
    assert config.vault_path == str(tmp_vault)


def test_setup_creates_dirs(tmp_vault):
    runner = CliRunner()
    runner.invoke(main, ["setup", "--vault", str(tmp_vault)])
    import datetime
    now = datetime.datetime.now()
    month_dir = tmp_vault / f"{now.year}{now.month:02d}"
    assert (month_dir / "10-Atomic").is_dir()
