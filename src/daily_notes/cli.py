# src/daily_notes/cli.py（更新）
"""Click CLI 入口."""
import click
from daily_notes import __version__
from daily_notes.commands.setup import setup
from daily_notes.commands.add import add


@click.group()
@click.version_option(version=__version__)
def main():
    """Daily Notes - 帮助持续学习的笔记整理工具."""
    pass


main.add_command(setup)
main.add_command(add)
