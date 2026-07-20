# src/daily_notes/commands/setup.py
"""setup 子命令."""
import click
from datetime import datetime
from pathlib import Path
from daily_notes.core.config import save_config, Config, is_initialized
from daily_notes.core.vault import ensure_month_dirs


@click.command()
@click.option("--vault", "vault_path", default=".", envvar="DAILY_NOTES_VAULT")
def setup(vault_path: str):
    """初始化知识库配置和目录结构."""
    vault = Path(vault_path).resolve()
    vault.mkdir(parents=True, exist_ok=True)
    config = Config(vault_path=str(vault))
    save_config(vault, config)
    now = datetime.now()
    ensure_month_dirs(vault, now.year, now.month)
    click.echo(f"知识库已初始化: {vault}")
    if is_initialized(vault):
        click.echo("提示：知识库已存在配置，无需重复初始化。")
