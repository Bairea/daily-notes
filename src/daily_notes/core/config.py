"""知识库配置管理 — 最小实现，供 decorators 使用."""
from dataclasses import dataclass, asdict
from pathlib import Path
import yaml


CONFIG_DIR = ".daily-notes"
CONFIG_FILE = "config.yaml"


class ConfigError(Exception):
    pass


@dataclass
class Config:
    vault_path: str = ""
    author: str = ""
    version: str = "0.1.0"


def get_config_path(vault_path: Path) -> Path:
    return vault_path / CONFIG_DIR / CONFIG_FILE


def save_config(vault_path: Path, config: Config) -> None:
    config_dir = vault_path / CONFIG_DIR
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = get_config_path(vault_path)
    data = asdict(config)
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


def load_config(vault_path: Path) -> Config:
    config_path = get_config_path(vault_path)
    if not config_path.exists():
        raise ConfigError(
            f"配置文件不存在: {config_path}。请先运行 'daily-notes setup'。"
        )
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Config(**data)


def is_initialized(vault_path: Path) -> bool:
    return get_config_path(vault_path).exists()
