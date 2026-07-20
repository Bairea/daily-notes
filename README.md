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
