# Daily Notes

帮助自己持续学习（而非持续记笔记）的工具。

设计灵感来自 Zettelkasten（链接即知识）和 LLM Wiki（快速得到结构），通过周期性回顾建立知识之间的跨领域连接。

## 安装

```bash
uv pip install -e .
```

## 快速开始

```bash
# 1. 初始化知识库（默认当前目录，或指定 --vault）
daily-notes setup --vault ./my-vault

# 2. 添加一条阅读记录（有链接 -> cited source）
daily-notes add "Python asyncio 事件循环解析" \
  --url "https://example.com/python-async" \
  --type article \
  --title "Python Asyncio 深度解析" \
  --tag python --tag async

# 3. 或记录一个空想（无链接 -> fleeting note）
daily-notes add "异步和同步的本质区别在于控制权的归属"

# 4. 每日：检查哪些 source 可以产出 atomic note
daily-notes daily --vault ./my-vault

# 5. 每周：在 atomic notes 之间发现新链接
daily-notes weekly --vault ./my-vault

# 6. 每月：查漏补缺，发现 pattern
daily-notes monthly --vault ./my-vault
```

## 命令参考

| 命令 | 说明 |
|------|------|
| `setup [--vault PATH]` | 初始化知识库配置和目录结构 |
| `add CONTENT [--url URL] [--type TYPE] [--title TITLE] [--body BODY] [--tag TAG...]` | 添加 Source |
| `ingest --source ID [--content TEXT] [--title TITLE] [--tag TAG...]` | 从 Source 创建 Atomic Note |
| `daily [--json]` | 列出待消化的 Source（尚未产出 Atomic） |
| `weekly [--json]` | 列出待连接的 Atomic（尚无出链） |
| `monthly [--json]` | 按标签聚类展示 Atomic，并内嵌待连接队列 |
| `stale [--json]` | 列出所有过期内容（status: stale），复核入口 |
| `show ID [--json]` | 查看单条笔记全部字段与正文 |
| `mark ID <stale\|archived\|active> [--note TEXT]` | 标记过期 / 归档 / 恢复活跃 |
| `list [--type TYPE] [--tag TAG] [--json]` | 列出笔记 |
| `search QUERY [--json]` | 搜索笔记（标题/标签/内容） |
| `link SOURCE_ID TARGET_ID REASON` | 建立双向链接 |

## 知识库结构

```
my-vault/
├── .daily-notes/
│   └── config.yaml
├── 202607/                          # 按年月组织
│   ├── 00-Source/
│   │   ├── cited/                   # 有引用的原始材料
│   │   └── fleeting/                # 空想观点
│   └── 10-Atomic/                   # 原子笔记（核心知识单元）
└── 202608/
    └── ...
```

## 两类知识对象

- **Source**：原始材料，包括 cited（article/video/github）和 fleeting（空想）
- **Atomic Note**：永久笔记，一个知识单元，至少一个 Link，每个 Link 都有连接说明

## 知识过期机制

知识会过时。某些内容（过时的技术、被推翻的结论）不应被删除，而应被标记、暂停、复核：

- `mark <id> stale --note "为什么过期"`：标记笔记为过期。过期笔记立即退出 `daily` / `weekly` 待办队列，但仍出现在 `monthly` 聚类、`list`、`search` 中（带 `[过期]` 标记），不会被遗忘。
- `stale`：列出全部过期内容，作为复核入口。
- `mark <id> active`：复核后恢复活跃，自动回到原队列。
- `mark <id> archived`：对放弃消化的 Source 使用，彻底移出 `daily` 队列（仅限 source）。

CLI 只负责输出候选与结构化读写；判断"是否过期、是否恢复"由人（或 agent 会话）决定。

## 与 Claude Code 集成

将 skill 安装到 Claude Code：

```bash
# 方式一：从本仓库复制
cp -r skills/daily-notes ~/.claude/skills/

# 方式二：通过 npx skills 安装
npx skills add <owner>/<repo> -s daily-notes
```

然后在 Claude Code 中输入 `/daily-notes` 即可触发。

Skill 采用渐进式披露：主文件仅包含引用，详细内容在 `checklist.md` 和 `commands.md` 中按需加载。

## 与 Obsidian 集成

知识库中的 `.md` 文件使用标准 YAML front matter + `[title](id.md)` 格式的文件引用，可直接用 Obsidian 打开 `my-vault/` 目录查看和编辑。

## 测试

```bash
uv run pytest
```

## v1 边界

明确不做：多用户/协作、移动端、语义搜索/embedding、Web UI/Dashboard。
