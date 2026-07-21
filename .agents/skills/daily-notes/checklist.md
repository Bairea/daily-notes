# 启动检查清单

按顺序执行，不要跳过。

## 1. 检查 CLI 是否安装

```bash
# macOS / Linux
which daily-notes

# Windows
where daily-notes
```

- **已安装** → 继续
- **未安装** → 直接从仓库安装：

```bash
uv pip install git+https://github.com/Bairea/daily-notes.git
```

安装完成后重新检查 `which daily-notes` / `where daily-notes`，确认可用后继续

## 2. 检查 vault 是否已初始化

检查当前目录（或用户指定的 `--vault` 路径）下是否存在 `.daily-notes/config.yaml`。

- **已初始化** → 告诉用户 vault 位置，建议下一步（如 `daily-notes daily` 查看今日候选项），继续执行用户任务
- **未初始化** → 运行 `daily-notes setup [--vault <path>]`（幂等，重复运行安全），然后告诉用户已就绪，建议下一步

## 3. 注意事项

- 如果用户从未指定 `--vault`，默认使用当前工作目录
- 不要假设 vault 路径，不确定时问用户
