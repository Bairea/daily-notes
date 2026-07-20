"""Click 装饰器工厂函数 — 减少各命令中的重复代码."""
from functools import wraps
from pathlib import Path
import click
from daily_notes.core.config import load_config, ConfigError


def vault_option():
    """添加 --vault 选项并将字符串转为 Path 注入函数参数."""
    def decorator(f):
        @click.option("--vault", "vault_path", default=None, help="知识库路径")
        @wraps(f)
        def wrapper(vault_path, *args, **kwargs):
            vault = Path(vault_path).resolve() if vault_path else Path.cwd().resolve()
            return f(vault=vault, *args, **kwargs)
        return wrapper
    return decorator


def json_output():
    """添加 --json/--no-json 选项."""
    def decorator(f):
        @click.option("--json/--no-json", "as_json", default=False,
                      help="输出 JSON 格式")
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapper
    return decorator


def ensure_init():
    """确保知识库已初始化，未初始化则报错退出."""
    def decorator(f):
        @wraps(f)
        def wrapper(vault, *args, **kwargs):
            try:
                load_config(vault)
            except ConfigError:
                click.echo("错误：知识库未初始化。请先运行 'daily-notes setup'。", err=True)
                raise SystemExit(1)
            return f(vault=vault, *args, **kwargs)
        return wrapper
    return decorator
