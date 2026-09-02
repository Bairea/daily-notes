"""Click CLI 入口."""
import click
from daily_notes import __version__
from daily_notes.commands.setup import setup
from daily_notes.commands.add import add
from daily_notes.commands.list_cmd import list_cmd
from daily_notes.commands.search import search
from daily_notes.commands.ingest import ingest
from daily_notes.commands.link import link
from daily_notes.commands.show import show
from daily_notes.commands.mark import mark
from daily_notes.commands.daily import daily
from daily_notes.commands.weekly import weekly
from daily_notes.commands.monthly import monthly
from daily_notes.commands.stale import stale


@click.group()
@click.version_option(version=__version__)
def main():
    """Daily Notes - 帮助持续学习的笔记整理工具."""
    pass


# 注册顺序决定 --help 中的排列：高频命令在前
main.add_command(daily)
main.add_command(weekly)
main.add_command(monthly)
main.add_command(stale)
main.add_command(add)
main.add_command(ingest)
main.add_command(link)
main.add_command(show)
main.add_command(mark)
main.add_command(list_cmd)
main.add_command(search)
main.add_command(setup)
