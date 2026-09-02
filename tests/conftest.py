import re
from pathlib import Path

import pytest
from click.testing import CliRunner

from daily_notes.cli import main

NOTE_ID_PATTERN = re.compile(r"(\d{8}-[0-9a-f]{6})")


@pytest.fixture
def tmp_vault(tmp_path):
    """创建临时知识库目录结构."""
    vault = tmp_path / "vault"
    vault.mkdir()
    config_dir = vault / ".daily-notes"
    config_dir.mkdir()
    return vault


def _extract_id(output: str) -> str:
    """从命令输出中提取笔记 id.

    不用 result.output.strip() 直接当路径：ingest 的警告会混入
    stdout，取决于 Click 版本与 CliRunner 的 stderr 合并策略。
    """
    m = NOTE_ID_PATTERN.search(output)
    assert m, f"输出中找不到笔记 id：{output}"
    return m.group(1)


class NotesHelper:
    """封装命令调用，返回笔记 id 而非原始输出."""

    def __init__(self):
        self.runner = CliRunner()

    def setup(self, vault) -> "NotesHelper":
        result = self.runner.invoke(main, ["setup", "--vault", str(vault)])
        assert result.exit_code == 0, result.output
        return self

    def add_source(self, vault, title="源材料", **opts) -> str:
        """添加 cited source，返回 id。opts 支持 tag 等选项，值可为 list."""
        args = ["add", "小结", "--url", "https://example.com",
                "--title", title, "--vault", str(vault)]
        for key, value in opts.items():
            for item in (value if isinstance(value, list) else [value]):
                args += [f"--{key}", item]
        return _extract_id(self._run(args).output)

    def add_fleeting(self, vault, content: str) -> str:
        return _extract_id(self._run(
            ["add", content, "--vault", str(vault)]).output)

    def ingest(self, vault, source_id: str, title="原子笔记", **opts) -> str:
        args = ["ingest", "--source", source_id, "--title", title,
                "--vault", str(vault)]
        for key, value in opts.items():
            for item in (value if isinstance(value, list) else [value]):
                args += [f"--{key}", item]
        return _extract_id(self._run(args).output)

    def mark(self, vault, note_id: str, state: str, note_text: str | None = None):
        args = ["mark", note_id, state, "--vault", str(vault)]
        if note_text is not None:
            args += ["--note", note_text]
        self._run(args)

    def link(self, vault, source_id: str, target_id: str, reason: str):
        self._run(["link", source_id, target_id, reason, "--vault", str(vault)])

    def run(self, *args, vault=None, stdin=None):
        """执行任意命令，返回 result（不校验退出码，供断言失败场景用）."""
        cmd = list(args) + ["--vault", str(vault)]
        return self.runner.invoke(main, cmd, input=stdin)

    def run_ok(self, *args, vault=None, stdin=None):
        """执行命令并断言成功，返回 result."""
        result = self.run(*args, vault=vault, stdin=stdin)
        assert result.exit_code == 0, f"命令失败 {args}：{result.output}"
        return result

    def _run(self, args):
        result = self.runner.invoke(main, args)
        assert result.exit_code == 0, f"命令失败 {args}：{result.output}"
        return result


@pytest.fixture
def notes():
    return NotesHelper()
