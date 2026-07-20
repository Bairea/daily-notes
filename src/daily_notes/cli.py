# src/daily_notes/cli.py（更新）
"""Click CLI 入口."""
import click
from daily_notes import __version__
from daily_notes.commands.setup import setup
from daily_notes.commands.add import add
from daily_notes.commands.review import review
from daily_notes.commands.list_cmd import list_cmd
from daily_notes.commands.search import search
from daily_notes.commands.ingest import ingest
from daily_notes.commands.link import link


@click.group()
@click.version_option(version=__version__)
def main():
    """Daily Notes - 帮助持续学习的笔记整理工具."""
    pass


main.add_command(setup)
main.add_command(add)
main.add_command(review)
main.add_command(list_cmd)
main.add_command(search)
main.add_command(ingest)
main.add_command(link)


@click.command()
@click.option("--vault", "vault_path", default=None)
@click.pass_context
def daily(ctx, vault_path):
    """每日 review（关注 ingest）."""
    ctx.invoke(review, period="day", focus=("ingest",), as_json=False, vault_path=vault_path)


@click.command()
@click.option("--vault", "vault_path", default=None)
@click.pass_context
def weekly(ctx, vault_path):
    """每周 review（关注 link）."""
    ctx.invoke(review, period="week", focus=("link",), as_json=False, vault_path=vault_path)


@click.command()
@click.option("--vault", "vault_path", default=None)
@click.pass_context
def monthly(ctx, vault_path):
    """每月 review（关注 pattern）."""
    ctx.invoke(review, period="month", focus=("link", "pattern"), as_json=False, vault_path=vault_path)


main.add_command(daily)
main.add_command(weekly)
main.add_command(monthly)
