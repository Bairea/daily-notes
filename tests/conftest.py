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
