from pathlib import Path
from click.testing import CliRunner
import click
from daily_notes.commands.decorators import vault_option, json_output, ensure_init


def test_vault_option_injects_vault():
    @click.command()
    @vault_option()
    def cmd(vault):
        click.echo(str(vault))

    runner = CliRunner()
    result = runner.invoke(cmd, ["--vault", "/tmp/test"])
    assert result.exit_code == 0
    assert str(Path("/tmp/test").resolve()) in result.output


def test_json_output_flag():
    @click.command()
    @json_output()
    def cmd(as_json):
        click.echo(str(as_json))

    runner = CliRunner()
    result = runner.invoke(cmd, ["--json"])
    assert "True" in result.output


def test_ensure_init_passes_when_initialized(tmp_vault):
    from daily_notes.core.config import save_config, Config
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))

    @click.command()
    @vault_option()
    @ensure_init()
    def cmd(vault):
        click.echo("ok")

    runner = CliRunner()
    result = runner.invoke(cmd, ["--vault", str(tmp_vault)])
    assert result.exit_code == 0
    assert "ok" in result.output


def test_ensure_init_blocks_when_not_initialized(tmp_path):
    @click.command()
    @vault_option()
    @ensure_init()
    def cmd(vault):
        click.echo("ok")

    runner = CliRunner()
    result = runner.invoke(cmd, ["--vault", str(tmp_path)])
    assert result.exit_code != 0
    assert "setup" in result.output.lower()
