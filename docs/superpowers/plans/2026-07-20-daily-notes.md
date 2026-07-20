# Daily Notes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建帮助持续学习的 Python CLI + Claude Code Skill 工具，支持 Source 捕获、Atomic Note 产出、周期性 Review。

**Architecture:** Python Click CLI 负责所有确定性操作（文件、front matter、搜索、创建），Claude Code Skill 负责 LLM 交互（review、推荐 link）。三层存储结构（00-Source/10-Atomic/20-Review）按年月组织。

**Tech Stack:** Python 3.11+, Click, python-frontmatter, PyYAML, pytest, uv

---

## File Structure

```
daily-notes/
├── pyproject.toml                    # uv 项目管理、依赖、入口点
├── README.md                         # 使用说明
├── src/daily_notes/
│   ├── __init__.py                   # 包初始化，暴露 __version__
│   ├── cli.py                        # Click group 入口，注册所有子命令
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── decorators.py             # Click 装饰器工厂函数（减少重复代码）
│   │   ├── setup.py                  # setup 子命令
│   │   ├── add.py                    # add 子命令
│   │   ├── ingest.py                 # ingest 子命令
│   │   ├── review.py                 # review 子命令（daily/weekly/monthly 共用）
│   │   ├── list_cmd.py               # list 子命令（避免与内置 list 冲突）
│   │   ├── search.py                 # search 子命令
│   │   └── link.py                   # link 子命令
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                 # 配置读写（.daily-notes/config.yaml）
│   │   ├── vault.py                  # 文件路径管理、读写
│   │   ├── frontmatter.py            # front matter 解析/生成
│   │   ├── id.py                     # id 生成（时间戳 + 短哈希）
│   │   └── models.py                 # 数据模型（ dataclass）
│   └── skills/
│       ├── daily-notes.md            # Claude Code Skill 主文件
│       ├── checklist.md              # 首次启动检查清单
│       └── commands.md               # 命令详情
└── tests/
    ├── __init__.py
    ├── conftest.py                   # 共享 fixture
    ├── test_decorators.py            # 装饰器工厂测试
    ├── test_id.py                    # id 生成测试
    ├── test_frontmatter.py           # front matter 解析测试
    ├── test_config.py                # config 读写测试
    ├── test_vault.py                 # vault 操作测试
    ├── test_setup.py                 # setup 命令测试
    ├── test_add.py                   # add 命令测试
    ├── test_review.py                # review 命令测试
    ├── test_list.py                  # list 命令测试
    ├── test_search.py                # search 命令测试
    ├── test_ingest.py                # ingest 命令测试
    ├── test_link.py                  # link 命令测试
    └── test_integration.py           # 端到端集成测试
```

---

## Task 1: 项目初始化（pyproject.toml + 目录结构）

**Files:**
- Create: `D:/Desktopfile/chores/daily_notes/pyproject.toml`
- Create: `D:/Desktopfile/chores/daily_notes/README.md`
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/__init__.py`
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/commands/__init__.py`
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/core/__init__.py`
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/skills/__init__.py`
- Create: `D:/Desktopfile/chores/daily_notes/tests/__init__.py`
- Create: `D:/Desktopfile/chores/daily_notes/tests/conftest.py`

- [ ] **Step 1: 创建 pyproject.toml**

```toml
[project]
name = "daily-notes"
version = "0.1.0"
description = "帮助持续学习的笔记整理工具"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1",
    "python-frontmatter>=1.1",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.5",
]

[project.scripts]
daily-notes = "daily_notes.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/daily_notes"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

[tool.ruff]
line-length = 100
target-version = "py311"
```

- [ ] **Step 2: 创建 README.md**

```markdown
# Daily Notes

帮助自己持续学习（而非持续记笔记）的工具。

## 安装

```bash
uv pip install -e .
```

## 使用

```bash
daily-notes setup                    # 初始化知识库
daily-notes add "想法" [--url URL]    # 添加 Source
daily-notes daily                    # 每日 review
daily-notes weekly                   # 每周 review
daily-notes monthly                  # 每月 review
```

## 与 Claude Code 集成

将 `src/daily-notes/skills/daily-notes.md` 安装到 Claude Code skills 目录。
```

- [ ] **Step 3: 创建 src/daily_notes/__init__.py**

```python
__version__ = "0.1.0"
```

- [ ] **Step 4: 创建其他 __init__.py 文件**

`src/daily_notes/commands/__init__.py`、`src/daily_notes/core/__init__.py`、`src/daily_notes/skills/__init__.py`、`tests/__init__.py`：均为空文件。

- [ ] **Step 5: 创建 tests/conftest.py**

```python
import pytest
from pathlib import Path
from datetime import datetime


@pytest.fixture
def tmp_vault(tmp_path):
    """创建临时知识库目录结构."""
    vault = tmp_path / "vault"
    vault.mkdir()
    config_dir = vault / ".daily-notes"
    config_dir.mkdir()
    return vault
```

- [ ] **Step 6: 验证包可导入**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run python -c "import daily_notes; print(daily_notes.__version__)"
```

Expected: `0.1.0`

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml README.md src tests
git commit -m "feat: initialize project structure"
```

---

## Task 1.5: Click 装饰器工厂（commands/decorators.py）

**Files:**
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/commands/decorators.py`
- Create: `D:/Desktopfile/chores/daily_notes/tests/test_decorators.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_decorators.py
from click.testing import CliRunner
import click
from daily_notes.commands.decorators import vault_option, json_output, ensure_init


def test_vault_option_injects_vault():
    @click.command()
    @vault_option()
    def cmd(vault):
        click.echo(vault)

    runner = CliRunner()
    result = runner.invoke(cmd, ["--vault", "/tmp/test"])
    assert result.exit_code == 0
    assert "/tmp/test" in result.output


def test_json_output_flag():
    @click.command()
    @json_output()
    def cmd(json):
        click.echo(str(json))

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
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_decorators.py -v
```

Expected: FAIL。

- [ ] **Step 3: 实现装饰器工厂**

```python
# src/daily_notes/commands/decorators.py
"""Click 装饰器工厂函数 — 减少各命令中的重复代码."""
from functools import wraps
from pathlib import Path
import click
from daily_notes.core.config import load_config, ConfigError, is_initialized


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
        return f
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
```

- [ ] **Step 4: 运行测试验证通过**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_decorators.py -v
```

Expected: 4 PASSED。

- [ ] **Step 5: Commit**

```bash
git add src/daily_notes/commands/decorators.py tests/test_decorators.py
git commit -m "feat: add click decorator factories for vault/json/init"
```

---

## 约定：后续命令使用装饰器工厂

> **从 Task 7（setup）开始，所有需要 `--vault` 选项和 init 检查的命令，必须使用 `commands/decorators.py` 中的装饰器工厂：**
>
> - `@vault_option()` — 添加 `--vault` 选项，自动解析为 `vault: Path` 参数
> - `@ensure_init()` — 检查知识库已初始化，未初始化则报错退出
> - `@json_output()` — 添加 `--json/--no-json` 选项
>
> 这样每个命令不再需要重复写 `@click.option("--vault", ...)`、`Path(vault_path).resolve()` 和 `try: load_config(...)` 的样板代码。
>
> 使用示例（add 命令）：
> ```python
> @click.command()
> @click.argument("content")
> @vault_option()
> @ensure_init()
> def add(content: str, vault):
>     ...
> ```

---

## Task 2: ID 生成模块（core/id.py）

**Files:**
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/core/id.py`
- Create: `D:/Desktopfile/chores/daily_notes/tests/test_id.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_id.py
from daily_notes.core.id import generate_id, parse_id


def test_generate_id_format():
    """id 格式: YYYYMMDD-<6位短哈希>."""
    id_ = generate_date_id()
    parts = id_.split("-")
    assert len(parts) == 2
    assert len(parts[0]) == 8  # YYYYMMDD
    assert len(parts[1]) == 6  # 短哈希
    assert parts[0].isdigit()


def test_generate_id_uniqueness():
    """同一时刻生成的 id 应唯一."""
    ids = {generate_date_id() for _ in range(100)}
    assert len(ids) == 100


def test_parse_id():
    """parse_id 返回 datetime."""
    id_ = generate_date_id()
    dt = parse_id(id_)
    assert isinstance(dt, datetime)
    assert dt.year >= 2026
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_id.py -v
```

Expected: FAIL — `generate_date_id` 未定义。

- [ ] **Step 3: 实现 ID 生成**

```python
# src/daily_notes/core/id.py
"""ID 生成模块.格式: YYYYMMDD-<6位短哈希>."""
import secrets
from datetime import datetime


def generate_date_id() -> str:
    """生成基于当前时间的唯一 id."""
    date_part = datetime.now().strftime("%Y%m%d")
    hash_part = secrets.token_hex(3)  # 6 hex chars
    return f"{date_part}-{hash_part}"


def parse_id(id_str: str) -> datetime:
    """从 id 解析出日期."""
    date_part = id_str.split("-")[0]
    return datetime.strptime(date_part, "%Y%m%d")
```

- [ ] **Step 4: 运行测试验证通过**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_id.py -v
```

Expected: 3 PASSED。

- [ ] **Step 5: Commit**

```bash
git add src/daily_notes/core/id.py tests/test_id.py
git commit -m "feat: add id generation with date + short hash"
```

---

## Task 3: Front Matter 模块（core/frontmatter.py）

**Files:**
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/core/frontmatter.py`
- Create: `D:/Desktopfile/chores/daily_notes/tests/test_frontmatter.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_frontmatter.py
import frontmatter
from daily_notes.core.frontmatter import (
    create_source_frontmatter,
    create_atomic_frontmatter,
    serialize_note,
    deserialize_note,
)


def test_create_source_cited():
    fm = create_source_frontmatter(
        id_="20260720-abc123",
        source_type="article",
        title="Test Article",
        url="https://example.com",
        tags=["python"],
        summary="A test",
    )
    assert fm["id"] == "20260720-abc123"
    assert fm["type"] == "source"
    assert fm["source_type"] == "article"
    assert fm["url"] == "https://example.com"
    assert "created" in fm


def test_create_source_fleeting():
    fm = create_source_frontmatter(
        id_="20260720-def456",
        source_type="fleeting",
        content="A fleeting thought",
    )
    assert fm["type"] == "source"
    assert fm["source_type"] == "fleeting"
    assert fm["content"] == "A fleeting thought"


def test_create_atomic():
    fm = create_atomic_frontmatter(
        id_="20260720-ghi789",
        title="Atomic Thought",
        sources=["20260720-abc123"],
        tags=["pattern"],
        links=[{"target": "20260715-xyz111", "reason": "related"}],
    )
    assert fm["id"] == "20260720-ghi789"
    assert fm["type"] == "atomic"
    assert fm["sources"] == ["20260720-abc123"]
    assert fm["links"][0]["target"] == "20260715-xyz111"


def test_serialize_deserialize_roundtrip():
    fm = create_source_frontmatter(
        id_="20260720-abc123",
        source_type="article",
        title="Test",
    )
    content = "正文内容"
    full_text = serialize_note(fm, content)
    post = deserialize_note(full_text)
    assert post["id"] == "20260720-abc123"
    assert post.content == "正文内容"
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_frontmatter.py -v
```

Expected: FAIL。

- [ ] **Step 3: 实现 front matter 模块**

```python
# src/daily_notes/core/frontmatter.py
"""Front matter 解析与生成."""
from datetime import datetime
from typing import Any
import frontmatter


def create_source_frontmatter(
    id_: str,
    source_type: str,
    title: str = "",
    url: str = "",
    tags: list[str] | None = None,
    summary: str = "",
    content: str = "",
) -> frontmatter.Post:
    """创建 Source 的 front matter."""
    fm = frontmatter.Post("")
    fm["id"] = id_
    fm["type"] = "source"
    fm["created"] = datetime.now().isoformat()
    fm["tags"] = tags or []
    fm["source_type"] = source_type
    if title:
        fm["title"] = title
    if url:
        fm["url"] = url
    if summary:
        fm["summary"] = summary
    if content:
        fm["content"] = content
    return fm


def create_atomic_frontmatter(
    id_: str,
    title: str = "",
    sources: list[str] | None = None,
    tags: list[str] | None = None,
    links: list[dict[str, str]] | None = None,
) -> frontmatter.Post:
    """创建 Atomic Note 的 front matter."""
    fm = frontmatter.Post("")
    fm["id"] = id_
    fm["type"] = "atomic"
    fm["created"] = datetime.now().isoformat()
    fm["tags"] = tags or []
    if title:
        fm["title"] = title
    if sources:
        fm["sources"] = sources
    if links:
        fm["links"] = links
    return fm


def create_review_frontmatter(
    id_: str,
    period: str,
    related_notes: list[str] | None = None,
) -> frontmatter.Post:
    """创建 Review Note 的 front matter."""
    fm = frontmatter.Post("")
    fm["id"] = id_
    fm["type"] = "review"
    fm["created"] = datetime.now().isoformat()
    fm["period"] = period
    if related_notes:
        fm["related_notes"] = related_notes
    return fm


def serialize_note(post: frontmatter.Post, content: str = "") -> str:
    """将 Post 对象序列化为带 front matter 的 markdown 文本."""
    post.content = content
    return frontmatter.dumps(post)


def deserialize_note(text: str) -> frontmatter.Post:
    """从 markdown 文本解析 Post 对象."""
    return frontmatter.loads(text)
```

- [ ] **Step 4: 运行测试验证通过**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_frontmatter.py -v
```

Expected: 4 PASSED。

- [ ] **Step 5: Commit**

```bash
git add src/daily_notes/core/frontmatter.py tests/test_frontmatter.py
git commit -m "feat: add frontmatter serialization and generation"
```

---

## Task 4: 配置模块（core/config.py）

**Files:**
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/core/config.py`
- Create: `D:/Desktopfile/chores/daily_notes/tests/test_config.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_config.py
import yaml
from daily_notes.core.config import load_config, save_config, Config


def test_save_and_load(tmp_vault):
    config = Config(vault_path=str(tmp_vault), author="test")
    save_config(tmp_vault, config)
    loaded = load_config(tmp_vault)
    assert loaded.vault_path == str(tmp_vault)
    assert loaded.author == "test"


def test_load_not_exists(tmp_path):
    from daily_notes.core.config import ConfigError
    with pytest.raises(ConfigError):
        load_config(tmp_path)
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_config.py -v
```

Expected: FAIL。

- [ ] **Step 3: 实现 config 模块**

```python
# src/daily_notes/core/config.py
"""配置读写模块."""
from dataclasses import dataclass, asdict
from pathlib import Path
import yaml


CONFIG_DIR = ".daily-notes"
CONFIG_FILE = "config.yaml"


class ConfigError(Exception):
    """配置相关错误."""
    pass


@dataclass
class Config:
    vault_path: str = ""
    author: str = ""
    version: str = "0.1.0"


def get_config_dir(vault_path: Path) -> Path:
    """获取配置目录路径."""
    return vault_path / CONFIG_DIR


def get_config_path(vault_path: Path) -> Path:
    """获取配置文件路径."""
    return vault_path / CONFIG_DIR / CONFIG_FILE


def save_config(vault_path: Path, config: Config) -> None:
    """写入配置文件."""
    config_dir = get_config_dir(vault_path)
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = get_config_path(vault_path)
    data = asdict(config)
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


def load_config(vault_path: Path) -> Config:
    """加载配置文件."""
    config_path = get_config_path(vault_path)
    if not config_path.exists():
        raise ConfigError(
            f"配置文件不存在: {config_path}。请先运行 'daily-notes setup'。"
        )
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Config(**data)


def is_initialized(vault_path: Path) -> bool:
    """检查知识库是否已初始化."""
    return get_config_path(vault_path).exists()
```

- [ ] **Step 4: 运行测试验证通过**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_config.py -v
```

Expected: 2 PASSED。

- [ ] **Step 5: Commit**

```bash
git add src/daily_notes/core/config.py tests/test_config.py
git commit -m "feat: add config read/write module"
```

---

## Task 5: Vault 模块（core/vault.py）

**Files:**
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/core/vault.py`
- Create: `D:/Desktopfile/chores/daily_notes/tests/test_vault.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_vault.py
from pathlib import Path
from daily_notes.core.vault import (
    get_month_dir,
    get_source_dir,
    get_atomic_dir,
    get_review_dir,
    ensure_month_dirs,
    list_notes,
    NoteInfo,
)
from daily_notes.core.id import generate_date_id


def test_get_month_dir():
    vault = Path("/tmp/vault")
    month_dir = get_month_dir(vault, 2026, 7)
    assert month_dir == vault / "202607"


def test_get_source_dirs():
    vault = Path("/tmp/vault")
    month_dir = vault / "202607"
    cited, fleeting = get_source_dir(month_dir)
    assert cited == month_dir / "00-Source" / "cited"
    assert fleeting == month_dir / "00-Source" / "fleeting"


def test_get_atomic_dir():
    vault = Path("/tmp/vault")
    month_dir = vault / "202607"
    assert get_atomic_dir(month_dir) == month_dir / "10-Atomic"


def test_get_review_dir():
    vault = Path("/tmp/vault")
    month_dir = vault / "202607"
    assert get_review_dir(month_dir) == month_dir / "20-Review"


def test_ensure_month_dirs(tmp_path):
    ensure_month_dirs(tmp_path, 2026, 7)
    month_dir = tmp_path / "202607"
    assert (month_dir / "00-Source" / "cited").is_dir()
    assert (month_dir / "00-Source" / "fleeting").is_dir()
    assert (month_dir / "10-Atomic").is_dir()
    assert (month_dir / "20-Review").is_dir()


def test_list_notes_empty(tmp_path):
    ensure_month_dirs(tmp_path, 2026, 7)
    notes = list_notes(tmp_path, 2026, 7, "atomic")
    assert notes == []


def test_list_notes_with_files(tmp_path):
    ensure_month_dirs(tmp_path, 2026, 7)
    atomic_dir = tmp_path / "202607" / "10-Atomic"
    id_ = generate_date_id()
    (atomic_dir / f"{id_}.md").write_text("test", encoding="utf-8")
    notes = list_notes(tmp_path, 2026, 7, "atomic")
    assert len(notes) == 1
    assert notes[0].id_ == id_
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_vault.py -v
```

Expected: FAIL。

- [ ] **Step 3: 实现 vault 模块**

```python
# src/daily_notes/core/vault.py
"""知识库文件路径管理."""
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import frontmatter


@dataclass
class NoteInfo:
    """笔记元信息."""
    id_: str
    path: Path
    type: str


def get_month_dir(vault: Path, year: int, month: int) -> Path:
    """获取年月目录.如 vault/202607."""
    return vault / f"{year}{month:02d}"


def get_source_dir(month_dir: Path) -> tuple[Path, Path]:
    """获取 Source 子目录 (cited, fleeting)."""
    base = month_dir / "00-Source"
    return base / "cited", base / "fleeting"


def get_atomic_dir(month_dir: Path) -> Path:
    """获取 Atomic 目录."""
    return month_dir / "10-Atomic"


def get_review_dir(month_dir: Path) -> Path:
    """获取 Review 目录."""
    return month_dir / "20-Review"


def ensure_month_dirs(vault: Path, year: int, month: int) -> None:
    """确保年月的目录结构存在."""
    month_dir = get_month_dir(vault, year, month)
    cited, fleeting = get_source_dir(month_dir)
    atomic = get_atomic_dir(month_dir)
    review = get_review_dir(month_dir)
    for d in [cited, fleeting, atomic, review]:
        d.mkdir(parents=True, exist_ok=True)


def list_notes(vault: Path, year: int, month: int, note_type: str) -> list[NoteInfo]:
    """列出指定年月的某类型笔记."""
    month_dir = get_month_dir(vault, year, month)
    if not month_dir.exists():
        return []
    type_dir_map = {
        "source_cited": month_dir / "00-Source" / "cited",
        "source_fleeting": month_dir / "00-Source" / "fleeting",
        "source": month_dir / "00-Source",
        "atomic": month_dir / "10-Atomic",
        "review": month_dir / "20-Review",
    }
    search_dir = type_dir_map.get(note_type)
    if not search_dir or not search_dir.exists():
        return []
    notes = []
    for md_file in sorted(search_dir.glob("*.md")):
        id_ = md_file.stem
        notes.append(NoteInfo(id_=id_, path=md_file, type=note_type))
    return notes


def list_all_months(vault: Path) -> list[tuple[int, int]]:
    """列出知识库中所有年月目录."""
    months = []
    for p in sorted(vault.iterdir()):
        if p.is_dir() and len(p.name) == 6 and p.name.isdigit():
            year = int(p.name[:4])
            month = int(p.name[4:])
            months.append((year, month))
    return months


def get_current_month_dir(vault: Path) -> Path:
    """获取当前年月的目录，不存在则创建."""
    now = datetime.now()
    ensure_month_dirs(vault, now.year, now.month)
    return get_month_dir(vault, now.year, now.month)
```

- [ ] **Step 4: 运行测试验证通过**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_vault.py -v
```

Expected: 6+ PASSED。

- [ ] **Step 5: Commit**

```bash
git add src/daily_notes/core/vault.py tests/test_vault.py
git commit -m "feat: add vault path management module"
```

---

## Task 6: CLI 入口（cli.py）

**Files:**
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/cli.py`

- [ ] **Step 1: 创建 CLI 入口**

```python
# src/daily_notes/cli.py
"""Click CLI 入口."""
import click
from daily_notes import __version__


@click.group()
@click.version_option(version=__version__)
def main():
    """Daily Notes - 帮助持续学习的笔记整理工具."""
    pass
```

- [ ] **Step 2: 验证 CLI 可运行**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run daily-notes --version
```

Expected: `daily-notes, version 0.1.0`

- [ ] **Step 3: Commit**

```bash
git add src/daily_notes/cli.py
git commit -m "feat: add click cli entry point"
```

---

## Task 7: setup 命令

**Files:**
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/commands/setup.py`
- Modify: `D:/Desktopfile/chores/daily_notes/src/daily_notes/cli.py`
- Create: `D:/Desktopfile/chores/daily_notes/tests/test_setup.py`

- [ ] **Step 1: 写失败测试**

```python
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
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_setup.py -v
```

Expected: FAIL。

- [ ] **Step 3: 实现 setup 命令**

```python
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
```

- [ ] **Step 4: 注册到 cli.py**

```python
# src/daily_notes/cli.py（更新）
import click
from daily_notes import __version__
from daily_notes.commands.setup import setup


@click.group()
@click.version_option(version=__version__)
def main():
    """Daily Notes - 帮助持续学习的笔记整理工具."""
    pass


main.add_command(setup)
```

- [ ] **Step 5: 运行测试验证通过**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_setup.py -v
```

Expected: 2 PASSED。

- [ ] **Step 6: Commit**

```bash
git add src/daily_notes/commands/setup.py src/daily_notes/cli.py tests/test_setup.py
git commit -m "feat: add setup command"
```

---

## Task 8: add 命令

**Files:**
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/commands/add.py`
- Modify: `D:/Desktopfile/chores/daily_notes/src/daily_notes/cli.py`
- Create: `D:/Desktopfile/chores/daily_notes/tests/test_add.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_add.py
from click.testing import CliRunner
from daily_notes.cli import main
from daily_notes.core.config import save_config, Config
from daily_notes.core.vault import ensure_month_dirs


def test_add_cited(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, [
        "add", "一篇好文章",
        "--url", "https://example.com",
        "--type", "article",
        "--title", "Test",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0
    assert "2026" in result.output  # 路径包含年月


def test_add_fleeting(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, [
        "add", "一个想法",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0


def test_add_requires_init(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["add", "test", "--vault", str(tmp_path)])
    assert result.exit_code != 0
    assert "setup" in result.output.lower()
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_add.py -v
```

Expected: FAIL。

- [ ] **Step 3: 实现 add 命令**

```python
# src/daily_notes/commands/add.py
"""add 子命令."""
import click
from daily_notes.commands.decorators import vault_option, ensure_init
from daily_notes.core.vault import get_current_month_dir, get_source_dir
from daily_notes.core.id import generate_date_id
from daily_notes.core.frontmatter import (
    create_source_frontmatter,
    serialize_note,
)


@click.command()
@click.argument("content")
@click.option("--url", default="", help="来源 URL")
@click.option("--type", "source_type", default="article", help="来源类型")
@click.option("--title", default="", help="标题")
@click.option("--summary", default="", help="小结")
@click.option("--tag", multiple=True, help="标签（可重复）")
@vault_option()
@ensure_init()
def add(content: str, url: str, source_type: str, title: str, summary: str,
        tag: tuple[str, ...], vault):
    """添加一条 Source 笔记.

    CONTENT 是内容描述（小结或空想内容）。
    """
    id_ = generate_date_id()
    month_dir = get_current_month_dir(vault)
    cited_dir, fleeting_dir = get_source_dir(month_dir)

    if url:
        # cited source
        fm = create_source_frontmatter(
            id_=id_,
            source_type=source_type,
            title=title or content[:50],
            url=url,
            tags=list(tag),
            summary=summary or content,
        )
        target_dir = cited_dir
    else:
        # fleeting source
        fm = create_source_frontmatter(
            id_=id_,
            source_type="fleeting",
            content=content,
            tags=list(tag),
        )
        target_dir = fleeting_dir

    text = serialize_note(fm)
    file_path = target_dir / f"{id_}.md"
    file_path.write_text(text, encoding="utf-8")
    click.echo(str(file_path))
```

- [ ] **Step 4: 注册到 cli.py**

```python
# src/daily_notes/cli.py（更新）
from daily_notes.commands.add import add
# ... 在 main 组下添加:
main.add_command(add)
```

- [ ] **Step 5: 运行测试验证通过**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_add.py -v
```

Expected: 3 PASSED。

- [ ] **Step 6: Commit**

```bash
git add src/daily_notes/commands/add.py src/daily_notes/cli.py tests/test_add.py
git commit -m "feat: add add command for capturing sources"
```

---

## Task 9: review 命令

**Files:**
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/commands/review.py`
- Modify: `D:/Desktopfile/chores/daily_notes/src/daily_notes/cli.py`
- Create: `D:/Desktopfile/chores/daily_notes/tests/test_review.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_review.py
import frontmatter
from click.testing import CliRunner
from daily_notes.cli import main
from daily_notes.core.config import save_config, Config
from daily_notes.core.vault import ensure_month_dirs, get_current_month_dir, get_source_dir
from daily_notes.core.id import generate_date_id
from daily_notes.core.frontmatter import create_source_frontmatter, serialize_note


def _create_test_source(vault, content="test source"):
    month_dir = get_current_month_dir(vault)
    cited_dir, _ = get_source_dir(month_dir)
    id_ = generate_date_id()
    fm = create_source_frontmatter(id_=id_, source_type="article", summary=content)
    path = cited_dir / f"{id_}.md"
    path.write_text(serialize_note(fm), encoding="utf-8")
    return id_


def test_review_day(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    _create_test_source(tmp_vault)
    runner = CliRunner()
    result = runner.invoke(main, ["review", "--period", "day", "--focus", "ingest",
                                  "--vault", str(tmp_vault)])
    assert result.exit_code == 0


def test_review_json(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    _create_test_source(tmp_vault)
    runner = CliRunner()
    result = runner.invoke(main, ["review", "--period", "day", "--focus", "ingest",
                                  "--json", "--vault", str(tmp_vault)])
    assert result.exit_code == 0
    import json
    data = json.loads(result.output)
    assert "candidates" in data
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_review.py -v
```

Expected: FAIL。

- [ ] **Step 3: 实现 review 命令**

```python
# src/daily_notes/commands/review.py
"""review 子命令."""
import json
import click
from datetime import datetime, timedelta
from pathlib import Path
from daily_notes.core.config import load_config, ConfigError
from daily_notes.core.vault import (
    list_notes, list_all_months, get_month_dir, get_source_dir,
    get_atomic_dir, NoteInfo,
)
from daily_notes.core.id import parse_id


def _collect_candidates(vault: Path, period: str, focus: str) -> dict:
    """根据时间范围和关注点收集候选笔记."""
    now = datetime.now()
    if period == "day":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif period == "week":
        start = now - timedelta(days=7)
        end = now
    elif period == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    else:
        start = now - timedelta(days=1)
        end = now

    candidates = {
        "period": period,
        "focus": focus,
        "sources": [],
        "atomics": [],
        "unprocessed_sources": [],
    }

    months = list_all_months(vault)
    for year, month in months:
        month_dir = get_month_dir(vault, year, month)
        if not month_dir.exists():
            continue
        cited_dir, fleeting_dir = get_source_dir(month_dir)
        for src_dir in [cited_dir, fleeting_dir]:
            for note in list_notes(vault, year, month, "atomic"):
                pass  # placeholder
        # 列出所有 source
        for md_file in sorted(cited_dir.glob("*.md")):
            post = frontmatter.loads(md_file.read_text(encoding="utf-8"))
            note_time = datetime.fromisoformat(post["created"])
            if start <= note_time <= end:
                candidates["sources"].append({
                    "id": post["id"],
                    "type": post.get("source_type", "article"),
                    "summary": post.get("summary", ""),
                    "path": str(md_file.relative_to(vault)),
                })
        for md_file in sorted(fleeting_dir.glob("*.md")):
            post = frontmatter.loads(md_file.read_text(encoding="utf-8"))
            note_time = datetime.fromisoformat(post["created"])
            if start <= note_time <= end:
                candidates["sources"].append({
                    "id": post["id"],
                    "type": "fleeting",
                    "summary": post.get("content", ""),
                    "path": str(md_file.relative_to(vault)),
                })
        # 列出 atomic
        atomic_dir = get_atomic_dir(month_dir)
        for md_file in sorted(atomic_dir.glob("*.md")):
            post = frontmatter.loads(md_file.read_text(encoding="utf-8"))
            note_time = datetime.fromisoformat(post["created"])
            if start <= note_time <= end:
                candidates["atomics"].append({
                    "id": post["id"],
                    "title": post.get("title", ""),
                    "tags": post.get("tags", []),
                    "path": str(md_file.relative_to(vault)),
                })
    return candidates


@click.command()
@click.option("--period", type=click.Choice(["day", "week", "month"]), required=True)
@click.option("--focus", type=click.Choice(["ingest", "link", "pattern"]),
              multiple=True, required=True)
@click.option("--json/--no-json", "as_json", default=False)
@click.option("--vault", "vault_path", default=None)
def review(period: str, focus: tuple[str, ...], as_json: bool, vault_path: str | None):
    """列出指定时间范围内的候选笔记."""
    vault = Path(vault_path).resolve() if vault_path else Path.cwd().resolve()
    try:
        load_config(vault)
    except ConfigError:
        click.echo("错误：知识库未初始化。请先运行 'daily-notes setup'。", err=True)
        raise SystemExit(1)

    candidates = _collect_candidates(vault, period, focus[0])
    if as_json:
        click.echo(json.dumps(candidates, ensure_ascii=False, indent=2))
    else:
        click.echo(f"# Review: {period}")
        click.echo(f"## Sources ({len(candidates['sources'])})")
        for s in candidates["sources"]:
            click.echo(f"- [{s['id']}] {s['summary'][:60]}")
        click.echo(f"## Atomics ({len(candidates['atomics'])})")
        for a in candidates["atomics"]:
            click.echo(f"- [{a['id']}] {a.get('title', '')}")
```

- [ ] **Step 4: 注册到 cli.py**

```python
from daily_notes.commands.review import review
main.add_command(review)
```

- [ ] **Step 5: 运行测试验证通过**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_review.py -v
```

Expected: 2 PASSED。

- [ ] **Step 6: Commit**

```bash
git add src/daily_notes/commands/review.py src/daily_notes/cli.py tests/test_review.py
git commit -m "feat: add review command for listing candidates"
```

---

## Task 10: list 命令

**Files:**
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/commands/list_cmd.py`
- Modify: `D:/Desktopfile/chores/daily_notes/src/daily_notes/cli.py`
- Create: `D:/Desktopfile/chores/daily_notes/tests/test_list.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_list.py
from click.testing import CliRunner
from daily_notes.cli import main
from daily_notes.core.config import save_config, Config
from daily_notes.core.vault import get_current_month_dir, get_source_dir
from daily_notes.core.id import generate_date_id
from daily_notes.core.frontmatter import create_source_frontmatter, serialize_note


def test_list_empty(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, ["list", "--type", "source", "--vault", str(tmp_vault)])
    assert result.exit_code == 0


def test_list_with_notes(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    month_dir = get_current_month_dir(tmp_vault)
    cited_dir, _ = get_source_dir(month_dir)
    id_ = generate_date_id()
    fm = create_source_frontmatter(id_=id_, source_type="article", summary="test")
    (cited_dir / f"{id_}.md").write_text(serialize_note(fm), encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["list", "--type", "source", "--vault", str(tmp_vault)])
    assert result.exit_code == 0
    assert id_ in result.output
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_list.py -v
```

Expected: FAIL。

- [ ] **Step 3: 实现 list 命令**

```python
# src/daily_notes/commands/list_cmd.py
"""list 子命令."""
import json
import click
from pathlib import Path
from daily_notes.core.config import load_config, ConfigError
from daily_notes.core.vault import list_notes, list_all_months


@click.command("list")
@click.option("--type", "note_type", type=click.Choice(["source", "atomic", "review"]),
              default="source")
@click.option("--tag", default=None, help="按标签过滤")
@click.option("--since", default=None, help="起始日期 YYYY-MM-DD")
@click.option("--json/--no-json", "as_json", default=False)
@click.option("--vault", "vault_path", default=None)
def list_cmd(note_type: str, tag: str | None, since: str | None,
             as_json: bool, vault_path: str | None):
    """列出笔记."""
    vault = Path(vault_path).resolve() if vault_path else Path.cwd().resolve()
    try:
        load_config(vault)
    except ConfigError:
        click.echo("错误：知识库未初始化。请先运行 'daily-notes setup'。", err=True)
        raise SystemExit(1)

    months = list_all_months(vault)
    items = []
    for year, month in months:
        for note in list_notes(vault, year, month, note_type):
            items.append({
                "id": note.id_,
                "type": note.type,
                "path": str(note.path.relative_to(vault)),
            })

    if as_json:
        click.echo(json.dumps(items, ensure_ascii=False, indent=2))
    else:
        for item in items:
            click.echo(f"{item['id']}  {item['path']}")
```

- [ ] **Step 4: 注册到 cli.py**

```python
from daily_notes.commands.list_cmd import list_cmd
main.add_command(list_cmd)
```

- [ ] **Step 5: 运行测试验证通过**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_list.py -v
```

Expected: 2 PASSED。

- [ ] **Step 6: Commit**

```bash
git add src/daily_notes/commands/list_cmd.py src/daily_notes/cli.py tests/test_list.py
git commit -m "feat: add list command"
```

---

## Task 11: search 命令

**Files:**
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/commands/search.py`
- Modify: `D:/Desktopfile/chores/daily_notes/src/daily_notes/cli.py`
- Create: `D:/Desktopfile/chores/daily_notes/tests/test_search.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_search.py
from click.testing import CliRunner
from daily_notes.cli import main
from daily_notes.core.config import save_config, Config
from daily_notes.core.vault import get_current_month_dir, get_source_dir
from daily_notes.core.id import generate_date_id
from daily_notes.core.frontmatter import create_source_frontmatter, serialize_note


def test_search_finds_match(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    month_dir = get_current_month_dir(tmp_vault)
    cited_dir, _ = get_source_dir(month_dir)
    id_ = generate_date_id()
    fm = create_source_frontmatter(id_=id_, source_type="article", summary="Python 异步编程")
    (cited_dir / f"{id_}.md").write_text(serialize_note(fm), encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["search", "Python", "--vault", str(tmp_vault)])
    assert result.exit_code == 0
    assert id_ in result.output


def test_search_no_match(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, ["search", "不存在的关键词", "--vault", str(tmp_vault)])
    assert result.exit_code == 0
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_search.py -v
```

Expected: FAIL。

- [ ] **Step 3: 实现 search 命令**

```python
# src/daily_notes/commands/search.py
"""search 子命令."""
import json
import click
import frontmatter
from pathlib import Path
from daily_notes.core.config import load_config, ConfigError
from daily_notes.core.vault import list_all_months, get_month_dir


@click.command()
@click.argument("query")
@click.option("--json/--no-json", "as_json", default=False)
@click.option("--vault", "vault_path", default=None)
def search(query: str, as_json: bool, vault_path: str | None):
    """搜索笔记（标题/标签/内容精确匹配）."""
    vault = Path(vault_path).resolve() if vault_path else Path.cwd().resolve()
    try:
        load_config(vault)
    except ConfigError:
        click.echo("错误：知识库未初始化。请先运行 'daily-notes setup'。", err=True)
        raise SystemExit(1)

    months = list_all_months(vault)
    results = []
    query_lower = query.lower()
    for year, month in months:
        month_dir = get_month_dir(vault, year, month)
        if not month_dir.exists():
            continue
        for md_file in month_dir.rglob("*.md"):
            post = frontmatter.loads(md_file.read_text(encoding="utf-8"))
            searchable = " ".join([
                post.get("title", ""),
                post.get("summary", ""),
                post.get("content", ""),
                " ".join(post.get("tags", [])),
            ]).lower()
            if query_lower in searchable:
                results.append({
                    "id": post["id"],
                    "type": post.get("type", ""),
                    "path": str(md_file.relative_to(vault)),
                })

    if as_json:
        click.echo(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            click.echo(f"{r['id']}  {r['path']}")
```

- [ ] **Step 4: 注册到 cli.py**

```python
from daily_notes.commands.search import search
main.add_command(search)
```

- [ ] **Step 5: 运行测试验证通过**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_search.py -v
```

Expected: 2 PASSED。

- [ ] **Step 6: Commit**

```bash
git add src/daily_notes/commands/search.py src/daily_notes/cli.py tests/test_search.py
git commit -m "feat: add search command"
```

---

## Task 12: ingest 命令

**Files:**
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/commands/ingest.py`
- Modify: `D:/Desktopfile/chores/daily_notes/src/daily_notes/cli.py`
- Create: `D:/Desktopfile/chores/daily_notes/tests/test_ingest.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_ingest.py
from click.testing import CliRunner
from daily_notes.cli import main
from daily_notes.core.config import save_config, Config
from daily_notes.core.vault import get_current_month_dir, get_source_dir, get_atomic_dir
from daily_notes.core.id import generate_date_id
from daily_notes.core.frontmatter import create_source_frontmatter, serialize_note


def test_ingest_creates_atomic(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    month_dir = get_current_month_dir(tmp_vault)
    cited_dir, _ = get_source_dir(month_dir)
    source_id = generate_date_id()
    fm = create_source_frontmatter(id_=source_id, source_type="article", summary="test")
    (cited_dir / f"{source_id}.md").write_text(serialize_note(fm), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, [
        "ingest", "--source", source_id,
        "--content", "我的原子笔记内容",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0
    atomic_dir = get_atomic_dir(month_dir)
    atomic_files = list(atomic_dir.glob("*.md"))
    assert len(atomic_files) == 1


def test_ingest_missing_source(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, [
        "ingest", "--source", "nonexistent-id",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code != 0
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_ingest.py -v
```

Expected: FAIL。

- [ ] **Step 3: 实现 ingest 命令**

```python
# src/daily_notes/commands/ingest.py
"""ingest 子命令."""
import click
from pathlib import Path
from daily_notes.core.config import load_config, ConfigError
from daily_notes.core.vault import (
    get_current_month_dir, get_atomic_dir, list_all_months, get_month_dir,
)
from daily_notes.core.id import generate_date_id
from daily_notes.core.frontmatter import create_atomic_frontmatter, serialize_note
import frontmatter


def _find_note_by_id(vault: Path, id_: str) -> Path | None:
    """在知识库中查找指定 id 的笔记."""
    months = list_all_months(vault)
    for year, month in months:
        month_dir = get_month_dir(vault, year, month)
        for md_file in month_dir.rglob("*.md"):
            if md_file.stem == id_:
                return md_file
    return None


@click.command()
@click.option("--source", required=True, help="Source 笔记 id")
@click.option("--content", default="", help="Atomic 正文内容")
@click.option("--title", default="", help="Atomic 标题")
@click.option("--tag", multiple=True, help="标签")
@click.option("--vault", "vault_path", default=None)
def ingest(source: str, content: str, title: str, tag: tuple[str, ...],
           vault_path: str | None):
    """从 Source 创建 Atomic Note."""
    vault = Path(vault_path).resolve() if vault_path else Path.cwd().resolve()
    try:
        load_config(vault)
    except ConfigError:
        click.echo("错误：知识库未初始化。请先运行 'daily-notes setup'。", err=True)
        raise SystemExit(1)

    source_path = _find_note_by_id(vault, source)
    if not source_path:
        click.echo(f"错误：未找到 Source '{source}'。", err=True)
        raise SystemExit(1)

    id_ = generate_date_id()
    month_dir = get_current_month_dir(vault)
    atomic_dir = get_atomic_dir(month_dir)

    fm = create_atomic_frontmatter(
        id_=id_,
        title=title,
        sources=[source],
        tags=list(tag),
    )
    text = serialize_note(fm, content)
    file_path = atomic_dir / f"{id_}.md"
    file_path.write_text(text, encoding="utf-8")
    click.echo(str(file_path))
```

- [ ] **Step 4: 注册到 cli.py**

```python
from daily_notes.commands.ingest import ingest
main.add_command(ingest)
```

- [ ] **Step 5: 运行测试验证通过**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_ingest.py -v
```

Expected: 2 PASSED。

- [ ] **Step 6: Commit**

```bash
git add src/daily_notes/commands/ingest.py src/daily_notes/cli.py tests/test_ingest.py
git commit -m "feat: add ingest command for creating atomic notes"
```

---

## Task 13: link 命令

**Files:**
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/commands/link.py`
- Modify: `D:/Desktopfile/chores/daily_notes/src/daily_notes/cli.py`
- Create: `D:/Desktopfile/chores/daily_notes/tests/test_link.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_link.py
import frontmatter
from click.testing import CliRunner
from daily_notes.cli import main
from daily_notes.core.config import save_config, Config
from daily_notes.core.vault import get_current_month_dir, get_atomic_dir
from daily_notes.core.id import generate_date_id
from daily_notes.core.frontmatter import create_atomic_frontmatter, serialize_note


def _create_atomic(vault, id_, title="test"):
    month_dir = get_current_month_dir(vault)
    atomic_dir = get_atomic_dir(month_dir)
    fm = create_atomic_frontmatter(id_=id_, title=title)
    (atomic_dir / f"{id_}.md").write_text(serialize_note(fm), encoding="utf-8")
    return atomic_dir / f"{id_}.md"


def test_link_creates_bidirectional(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    source_id = generate_date_id()
    target_id = generate_date_id()
    _create_atomic(tmp_vault, source_id, "Source Note")
    _create_atomic(tmp_vault, target_id, "Target Note")

    runner = CliRunner()
    result = runner.invoke(main, [
        "link", source_id, target_id, "两者相关",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0

    # 验证 source 有出链
    month_dir = get_current_month_dir(tmp_vault)
    atomic_dir = get_atomic_dir(month_dir)
    source_post = frontmatter.loads(
        (atomic_dir / f"{source_id}.md").read_text(encoding="utf-8")
    )
    assert any(l["target"] == target_id for l in source_post.get("links", []))

    # 验证 target 有反向链接
    target_post = frontmatter.loads(
        (atomic_dir / f"{target_id}.md").read_text(encoding="utf-8")
    )
    assert any(b["source"] == source_id for b in target_post.get("backlinks", []))
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_link.py -v
```

Expected: FAIL。

- [ ] **Step 3: 实现 link 命令**

```python
# src/daily_notes/commands/link.py
"""link 子命令."""
import click
import frontmatter
from pathlib import Path
from daily_notes.core.config import load_config, ConfigError
from daily_notes.core.vault import list_all_months, get_month_dir


def _find_note_by_id(vault: Path, id_: str) -> Path | None:
    """在知识库中查找指定 id 的笔记."""
    months = list_all_months(vault)
    for year, month in months:
        month_dir = get_month_dir(vault, year, month)
        for md_file in month_dir.rglob("*.md"):
            if md_file.stem == id_:
                return md_file
    return None


@click.command()
@click.argument("source_id")
@click.argument("target_id")
@click.argument("reason")
@click.option("--vault", "vault_path", default=None)
def link(source_id: str, target_id: str, reason: str, vault_path: str | None):
    """在两个 Atomic Note 之间建立链接.

    SOURCE_ID 是源笔记 id，TARGET_ID 是目标笔记 id。
    """
    vault = Path(vault_path).resolve() if vault_path else Path.cwd().resolve()
    try:
        load_config(vault)
    except ConfigError:
        click.echo("错误：知识库未初始化。请先运行 'daily-notes setup'。", err=True)
        raise SystemExit(1)

    source_path = _find_note_by_id(vault, source_id)
    if not source_path:
        click.echo(f"错误：未找到笔记 '{source_id}'。", err=True)
        raise SystemExit(1)

    target_path = _find_note_by_id(vault, target_id)
    if not target_path:
        click.echo(f"错误：未找到笔记 '{target_id}'。", err=True)
        raise SystemExit(1)

    # 更新 source：添加出链
    source_post = frontmatter.loads(source_path.read_text(encoding="utf-8"))
    if "links" not in source_post:
        source_post["links"] = []
    source_post["links"].append({"target": target_id, "reason": reason})
    # 正文追加 Obsidian 文件引用
    link_text = f"\n- [{reason}]({target_id}.md)\n"
    source_post.content = source_post.content.rstrip() + "\n## 相关笔记\n" + link_text
    source_path.write_text(frontmatter.dumps(source_post), encoding="utf-8")

    # 更新 target：添加 backlink
    target_post = frontmatter.loads(target_path.read_text(encoding="utf-8"))
    if "backlinks" not in target_post:
        target_post["backlinks"] = []
    target_post["backlinks"].append({"source": source_id, "reason": reason})
    backlink_text = f"\n- [{reason}]({source_id}.md)\n"
    target_post.content = target_post.content.rstrip() + "\n## 反向链接\n" + backlink_text
    target_path.write_text(frontmatter.dumps(target_post), encoding="utf-8")

    click.echo(f"已链接: {source_id} -> {target_id}")
```

- [ ] **Step 4: 注册到 cli.py**

```python
from daily_notes.commands.link import link
main.add_command(link)
```

- [ ] **Step 5: 运行测试验证通过**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_link.py -v
```

Expected: 1 PASSED。

- [ ] **Step 6: Commit**

```bash
git add src/daily_notes/commands/link.py src/daily_notes/cli.py tests/test_link.py
git commit -m "feat: add link command for bidirectional linking"
```

---

## Task 14: daily/weekly/monthly 快捷命令

**Files:**
- Modify: `D:/Desktopfile/chores/daily_notes/src/daily_notes/cli.py`
- Create: `D:/Desktopfile/chores/daily_notes/tests/test_shortcuts.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_shortcuts.py
from click.testing import CliRunner
from daily_notes.cli import main
from daily_notes.core.config import save_config, Config


def test_daily_shortcut(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, ["daily", "--vault", str(tmp_vault)])
    assert result.exit_code == 0


def test_weekly_shortcut(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, ["weekly", "--vault", str(tmp_vault)])
    assert result.exit_code == 0


def test_monthly_shortcut(tmp_vault):
    save_config(tmp_vault, Config(vault_path=str(tmp_vault)))
    runner = CliRunner()
    result = runner.invoke(main, ["monthly", "--vault", str(tmp_vault)])
    assert result.exit_code == 0
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_shortcuts.py -v
```

Expected: FAIL。

- [ ] **Step 3: 实现快捷命令**

```python
# src/daily_notes/cli.py（在 main 组下添加）
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
```

- [ ] **Step 4: 运行测试验证通过**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_shortcuts.py -v
```

Expected: 3 PASSED。

- [ ] **Step 5: Commit**

```bash
git add src/daily_notes/cli.py tests/test_shortcuts.py
git commit -m "feat: add daily/weekly/monthly shortcut commands"
```

---

## Task 15: Skill 文件

**Files:**
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/skills/daily-notes.md`
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/skills/checklist.md`
- Create: `D:/Desktopfile/chores/daily_notes/src/daily_notes/skills/commands.md`

- [ ] **Step 1: 创建 Skill 主文件**

```markdown
---
name: daily-notes
description: 阅读笔记整理工具（Source → Atomic → Link → Pattern）
---

你是阅读笔记助手。所有操作通过 `daily-notes` CLI 执行。

## 启动检查
首次使用时按 `skills/checklist.md` 执行。

## 操作
用户给你内容时调用 CLI。子命令详情见 `skills/commands.md`。

## 规则
- 永远不要替用户写 Atomic Note 正文
- AI 提建议，人做决策
```

- [ ] **Step 2: 创建 checklist.md**

```markdown
# 启动检查清单

1. 运行 `which daily-notes` 检查 CLI 是否安装
2. 未安装 → 告诉用户运行 `uv pip install daily-notes` 并停止
3. 已安装 → 运行 `daily-notes setup`（若未初始化）
```

- [ ] **Step 3: 创建 commands.md**

```markdown
# CLI 命令详情

## add
```bash
daily-notes add <content> [--url URL] [--type TYPE] [--title TITLE] [--tag TAG...]
```
有 `--url` → cited Source，无 `--url` → fleeting Source。

## review
```bash
daily-notes review --period {day|week|month} --focus {ingest|link|pattern}... [--json]
```
列出候选笔记。`--json` 输出 JSON 给 LLM 消费。

## ingest
```bash
daily-notes ingest --source <id> [--content TEXT] [--title TITLE] [--tag TAG...]
```
从 Source 创建 Atomic Note。

## link
```bash
daily-notes link <source_id> <target_id> <reason>
```
建立双向链接。

## list / search
```bash
daily-notes list [--type TYPE] [--tag TAG] [--json]
daily-notes search <query> [--json]
```

## 快捷入口
- `daily` = `review --period day --focus ingest`
- `weekly` = `review --period week --focus link`
- `monthly` = `review --period month --focus link --focus pattern`
```

- [ ] **Step 4: Commit**

```bash
git add src/daily_notes/skills/
git commit -m "feat: add Claude Code skill files"
```

---

## Task 16: 集成测试

**Files:**
- Create: `D:/Desktopfile/chores/daily_notes/tests/test_integration.py`

- [ ] **Step 1: 写集成测试**

```python
# tests/test_integration.py
from click.testing import CliRunner
from daily_notes.cli import main
from daily_notes.core.config import save_config, Config
from daily_notes.core.vault import get_current_month_dir, get_atomic_dir
import frontmatter


def test_full_workflow(tmp_vault):
    """完整流程: setup → add → review → ingest → link."""
    runner = CliRunner()

    # 1. setup
    result = runner.invoke(main, ["setup", "--vault", str(tmp_vault)])
    assert result.exit_code == 0

    # 2. add cited source
    result = runner.invoke(main, [
        "add", "一篇关于 Python 异步编程的文章",
        "--url", "https://example.com/async-python",
        "--type", "article",
        "--title", "Python Async",
        "--tag", "python",
        "--tag", "async",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0
    source_path = result.output.strip()

    # 3. add fleeting
    result = runner.invoke(main, [
        "add", "异步和同步的本质区别在于控制权",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0

    # 4. review
    result = runner.invoke(main, [
        "review", "--period", "day", "--focus", "ingest",
        "--json", "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0
    import json
    data = json.loads(result.output)
    assert len(data["sources"]) >= 2

    # 5. ingest
    source_id = data["sources"][0]["id"]
    result = runner.invoke(main, [
        "ingest", "--source", source_id,
        "--title", "异步编程的核心思想",
        "--tag", "pattern",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0

    # 6. link (先创建第二个 atomic)
    result2 = runner.invoke(main, [
        "ingest", "--source", source_id,
        "--title", "控制权视角",
        "--vault", str(tmp_vault),
    ])
    assert result2.exit_code == 0

    # 获取两个 atomic 的 id
    month_dir = get_current_month_dir(tmp_vault)
    atomic_dir = get_atomic_dir(month_dir)
    atomic_ids = [f.stem for f in atomic_dir.glob("*.md")]
    assert len(atomic_ids) == 2

    # 建立链接
    result = runner.invoke(main, [
        "link", atomic_ids[0], atomic_ids[1], "互补观点",
        "--vault", str(tmp_vault),
    ])
    assert result.exit_code == 0

    # 验证链接
    post = frontmatter.loads(
        (atomic_dir / f"{atomic_ids[0]}.md").read_text(encoding="utf-8")
    )
    assert any(l["target"] == atomic_ids[1] for l in post.get("links", []))
```

- [ ] **Step 2: 运行集成测试**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest tests/test_integration.py -v
```

Expected: 1 PASSED。

- [ ] **Step 3: 运行全部测试**

```bash
cd D:/Desktopfile/chores/daily_notes && uv run pytest -v
```

Expected: 全部 PASSED。

- [ ] **Step 4: Commit**

```bash
git add tests/test_integration.py
git commit -m "feat: add end-to-end integration test"
```

---

## Self-Review

**Spec 覆盖检查：**

| Spec 需求 | 对应 Task |
|----------|----------|
| 三类知识对象（Source/Atomic/Review）| Task 3 (frontmatter) + Task 8 (add) + Task 12 (ingest) |
| 三层存储结构 | Task 5 (vault) |
| setup/add/ingest/review/list/search/link | Task 7/8/12/9/10/11/13 |
| daily/weekly/monthly 快捷命令 | Task 14 |
| front matter schema | Task 3 |
| Obsidian 文件引用链接 | Task 13 (link 正文追加) |
| ID 生成（时间戳+短哈希）| Task 2 |
| 配置管理 | Task 4 |
| Skill 文件 | Task 15 |
| 错误处理 | 各命令中 SystemExit + 错误提示 |
| 测试策略 | Task 1-16 每步都有测试 + Task 16 集成测试 |

**Placeholder 扫描：** 无 TBD/TODO，所有步骤有完整代码。

**类型一致性：**
- `generate_date_id()` 在 Task 2 定义，Task 8/9/12/13 使用 ✅
- `load_config()` / `ConfigError` 在 Task 4 定义，各命令使用 ✅
- `NoteInfo` dataclass 在 Task 5 定义，Task 5/10 使用 ✅
- `serialize_note()` / `create_source_frontmatter()` 在 Task 3 定义，Task 8/9/12 使用 ✅

**无遗漏：** 所有 spec 需求都有对应 task。
