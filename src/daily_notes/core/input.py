"""命令输入处理."""
import sys
import click


def resolve_text(value: str, option_name: str) -> str:
    """解析文本参数：值为 '-' 时从 stdin 读取，否则原样返回.

    兑现原设计 §8.2「content 来自参数或 stdin」的承诺。
    参数值仍支持直接传入，两种方式并存。
    """
    if value != "-":
        return value
    if sys.stdin.isatty():
        click.echo(
            f"错误：--{option_name} 为 '-' 时需要从标准输入读取内容。",
            err=True,
        )
        click.echo(
            f"用法：--{option_name} - < file.md"
            f"  或  cat file.md | daily-notes ... --{option_name} -",
            err=True,
        )
        raise SystemExit(1)
    return sys.stdin.read()
