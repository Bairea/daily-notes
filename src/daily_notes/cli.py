"""Click CLI 入口."""
import click
from daily_notes import __version__


@click.group()
@click.version_option(version=__version__)
def main():
    """Daily Notes - 帮助持续学习的笔记整理工具."""
    pass
