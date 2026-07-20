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

# 4. 每日 review：检查哪些 source 可以产出 atomic note
daily-notes daily --vault ./my-vault

# 5. 每周 review：在 atomic notes 之间发现新链接
daily-notes weekly --vault ./my-vault

# 6. 每月 review：查漏补缺，发现 pattern
daily-notes monthly --vault ./my-vault
```

## 命令参考

| 命令 | 说明 |
|------|------|
| `setup [--vault PATH]` | 初始化知识库配置和目录结构 |
| `add CONTENT [--url URL] [--type TYPE] [--title TITLE] [--tag TAG...]` | 添加 Source |
| `ingest --source ID [--content TEXT] [--title TITLE] [--tag TAG...]` | 从 Source 创建 Atomic Note |
| `review --period {day,week,month} --focus {ingest,link,pattern}... [--json]` | 列出候选项 |
| `list [--type TYPE] [--tag TAG] [--json]` | 列出笔记 |
| `search QUERY [--json]` | 搜索笔记（标题/标签/内容） |
| `link SOURCE_ID TARGET_ID REASON` | 建立双向链接 |
| `daily` | = `review --period day --focus ingest` |
| `weekly` | = `review --period week --focus link` |
| `monthly` | = `review --period month --focus link --focus pattern` |

## 知识库结构

```
my-vault/
├── .daily-notes/
│   └── config.yaml
├── 202607/                          # 按年月组织
│   ├── 00-Source/
│   │   ├── cited/                   # 有引用的原始材料
│   │   └── fleeting/                # 空想观点
│   ├── 10-Atomic/                   # 原子笔记（核心知识单元）
│   └── 20-Review/                   # Review 输出
└── 202608/
    └── ...
```

## 三类知识对象

- **Source**：原始材料，包括 cited（article/video/github）和 fleeting（空想）
- **Atomic Note**：永久笔记，一个知识单元，至少一个 Link，每个 Link 都有连接说明
- **Review Note**：思考过程记录（新发现、新 Link、新 Pattern）

## 与 Claude Code 集成

将 skill 安装到 Claude Code：

```bash
cp -r src/daily_notes/skills/daily-notes ~/.claude/skills/
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
