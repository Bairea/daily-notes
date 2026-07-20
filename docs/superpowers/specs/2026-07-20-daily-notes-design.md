# Daily Notes 设计文档

> 帮助自己持续学习（而非持续记笔记）的 Python CLI + Claude Code Skill 工具。

---

## 1. 背景与目标

### 1.1 问题

阅读后产生的想法和感悟容易流失，缺乏系统化的沉淀和连接。现有的笔记工具要么太重（Notion），要么缺乏连接性（普通文件夹）。

### 1.2 设计灵感

- **Zettelkasten**：让知识自己产生新知识，链接即知识，通过链接自动聚集成领域（书由薄变厚）
- **LLM Wiki**：将资料整理成可查询可复用的 wiki，快速得到结构（书由厚变薄）
- **核心诉求**：通过周期性回顾找到与以前的联系（跨界的抽象联系），提高知识的连接性和利用率

### 1.3 核心目标

- 降低记录成本
- 提高回顾频率
- 增加知识之间的新连接
- 让思考能够不断演化

### 1.4 设计原则

> **AI 提建议，人做决策。**

AI 不负责写 Atomic Note，不替用户思考。AI 负责总结 Source、推荐 Link、发现重复、提供新视角。

---

## 2. 三类知识对象

### 2.1 Source（原始材料）

保存原始信息，作为 Evidence。

子类型：
- **cited**：有引用的材料（article、video、github、paper）
- **fleeting**：空想观点（无外部来源）

### 2.2 Atomic Note（永久笔记）

整个知识库真正的核心。

特点：
- 一个知识单元
- 用户手敲正文
- 至少一个 Link
- 每个 Link 都有连接说明
- 记录来源引用

### 2.3 Review Note（Review 输出）

记录思考过程：
- 新发现
- 新 Link
- 新 Pattern
- 新 Methodology

不是永久知识，而是思考过程。

---

## 3. 学习循环

```
Capture (add)
    ↓
Review Daily → Atomic (ingest)
    ↓
Review Weekly → New Links (link)
    ↓
Review Monthly → New Patterns
    ↓
继续学习
```

### 3.1 Daily

- 关注点：产出原子笔记
- 时间范围：当天
- 遍历未 ingest 的 Source，尝试产出 Atomic

### 3.2 Weekly

- 关注点：产出链接
- 时间范围：本周
- 在已有 Atomic 之间发现新链接

### 3.3 Monthly

- 关注点：查漏补缺 + 发现 pattern
- 时间范围：本月
- 回顾未产出 Atomic 的 Source，检查更多链接，发现方法论层面的 pattern

---

## 4. 技术架构

### 4.1 形态

- **Python CLI**：所有确定性操作（文件、front matter、搜索、创建、生命周期）
- **Claude Code Skill**：LLM 交互入口，一个 skill 多个子命令
- **Obsidian**：查看和编辑（文件兼容即可）

### 4.2 职责划分

| CLI 负责 | Skill 负责 |
|---------|-----------|
| 文件操作 | Prompt 管理 |
| Front Matter 读写 | Daily Review |
| 搜索 | Weekly Review |
| 创建 | Monthly Review |
| 生命周期管理 | 与用户对话 |
| 确定性操作 | 调用 CLI 执行 |

### 4.3 技术选型

| 组件 | 选择 | 理由 |
|------|------|------|
| CLI 框架 | Click | 成熟稳定，装饰器模式简洁 |
| Front matter 解析 | python-frontmatter | 标准 front matter 读写 |
| YAML 处理 | PyYAML | config 和 front matter 的 YAML |
| 依赖管理 | uv | 符合项目规范 |
| 测试 | pytest + Click CliRunner | 单元 + 集成测试 |

---

## 5. 项目结构

```
daily-notes/
├── pyproject.toml
├── README.md
├── src/daily_notes/
│   ├── __init__.py
│   ├── cli.py                  # Click group 入口，注册所有子命令
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── setup.py            # 初始化 .daily-notes/ 配置
│   │   ├── add.py              # 添加 Source（cited/fleeting）
│   │   ├── ingest.py           # Source → Atomic Note
│   │   ├── review.py           # 列出候选（daily/weekly/monthly 共用）
│   │   ├── list_cmd.py         # 列出笔记
│   │   ├── search.py           # 搜索笔记
│   │   └── link.py             # 手动建立链接
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # 配置读写（.daily-notes/config.yaml）
│   │   ├── vault.py            # 文件路径管理、读写
│   │   ├── frontmatter.py      # front matter 解析/生成
│   │   ├── id.py               # id 生成（时间戳 + 短哈希）
│   │   └── models.py           # 数据模型（dataclass）
│   └── skills/
│       ├── daily-notes.md      # Claude Code Skill 主文件
│       ├── checklist.md        # 首次启动检查清单（按需读取）
│       └── commands.md         # 命令详情（按需读取）
└── tests/
    ├── __init__.py
    ├── test_frontmatter.py
    ├── test_id.py
    └── test_vault.py
```

---

## 6. 数据模型

### 6.1 Front Matter Schema

#### Source (cited)

```yaml
id: "20260720-a1b2c3"
type: "source"
created: "2026-07-20T10:30:00+08:00"
tags: [python, cli]
source_type: "article"
url: "https://example.com/..."
title: "文章标题"
summary: "LLM 或用户写的小结"
```

#### Source (fleeting)

```yaml
id: "20260720-d4e5f6"
type: "source"
created: "2026-07-20T11:00:00+08:00"
tags: [idea]
source_type: "fleeting"
content: "用户手敲的空想内容"
```

#### Atomic Note

```yaml
id: "20260720-g7h8i9"
type: "atomic"
created: "2026-07-20T20:00:00+08:00"
tags: [abstraction, pattern]
title: "原子笔记标题"
sources: ["20260720-a1b2c3"]
links:
  - target: "20260715-x1y2z3"
    reason: "两者都讨论了抽象层级的演化"
  - target: "20260718-m4n5o6"
    reason: "方法论上的互补"
```

#### Review Note

```yaml
id: "20260720-j1k2l3"
type: "review"
created: "2026-07-20T21:00:00+08:00"
period: "daily"
related_notes: ["20260720-g7h8i9"]
```

### 6.2 通用字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 唯一标识，时间戳 + 短哈希 |
| type | string | source / atomic / review |
| created | datetime | 创建时间（ISO 8601） |
| tags | list[string] | 标签列表 |

### 6.3 链接在正文中的格式

使用 Obsidian 文件引用链接（非 wiki-link）：

```markdown
## 相关笔记
- [抽象层级的演化](20260715-x1y2z3.md)：两者都讨论了...
- [方法论互补](20260718-m4n5o6.md)：...
```

### 6.4 ID 生成规则

格式：`YYYYMMDD-<6位短哈希>`

示例：`20260720-a1b2c3`

- 时间戳部分保证按文件名排序即按创建时间排序
- 短哈希避免同一秒内创建的冲突
- 文件名即 id：`20260720-a1b2c3.md`

---

## 7. 目录结构

```
.vault/                          # 知识库根目录（setup 时指定）
├── .daily-notes/
│   ├── config.yaml              # 配置（vault 路径、作者等）
│   └── .gitkeep
├── 202607/                      # 按年月组织
│   ├── 00-Source/
│   │   ├── cited/
│   │   │   └── 20260720-a1b2c3.md
│   │   └── fleeting/
│   │       └── 20260720-d4e5f6.md
│   ├── 10-Atomic/
│   │   └── 20260720-g7h8i9.md
│   └── 20-Review/
│       └── 20260720-j1k2l3.md
├── 202608/
│   └── ...
└── ...
```

### 路径规则

- `add` 自动算出当前年月的路径
- `review --period week` 读取最近 7 天的所有年月目录
- `review --period month` 读取当前年月的所有目录

---

## 8. 命令设计

### 8.1 命令总览

| 命令 | 类型 | 说明 |
|------|------|------|
| setup | 核心 | 初始化配置和目录结构 |
| add | 核心 | 添加 Source |
| ingest | 核心 | 创建 Atomic Note |
| review | 核心 | 列出候选项 |
| list | 辅助 | 列出笔记 |
| search | 辅助 | 搜索笔记 |
| link | 辅助 | 手动建立链接 |
| daily | 快捷 | = review --period day --focus ingest |
| weekly | 快捷 | = review --period week --focus link |
| monthly | 快捷 | = review --period month --focus pattern |

### 8.2 命令详情

#### setup

```bash
daily-notes setup [--vault PATH]
```

- 创建 `.daily-notes/config.yaml`
- 初始化目录结构（当前年月的 00-Source/10-Atomic/20-Review）
- 默认 vault 为当前工作目录

#### add

```bash
daily-notes add <content> [--url URL] [--type TYPE] [--title TITLE]
```

- 有 `--url` → cited Source（存入 00-Source/cited/）
- 无 `--url` → fleeting Source（存入 00-Source/fleeting/）
- 自动生成 id、created
- 输出新文件路径

#### ingest

```bash
daily-notes ingest --source <id> [--content TEXT]
```

- 从模板创建 Atomic 文件
- front matter 记录 source 引用
- content 来自参数或 stdin
- 输出新文件路径

#### review

```bash
daily-notes review --period {day|week|month} --focus {ingest|link|pattern}... [--json]
```

- 读取时间范围内的笔记
- `--focus` 可重复（如 `--focus link --pattern`）
- 输出候选项（markdown 或 JSON）
- daily/weekly/monthly 是 review 的快捷封装

#### list

```bash
daily-notes list [--type TYPE] [--tag TAG] [--since DATE] [--json]
```

- 列出符合条件的笔记
- 默认输出表格格式

#### search

```bash
daily-notes search <query> [--json]
```

- 标题/标签/内容精确搜索
- 输出匹配结果

#### link

```bash
daily-notes link <source_id> <target_id> <reason>
```

- 在 source Atomic 的 front matter（links 字段）和正文（Obsidian 文件引用）中插入出链
- 反向操作：在 target Atomic 的 front matter 中插入 backlink 字段（ source + reason），正文追加反向引用

### 8.3 全局选项

| 选项 | 说明 |
|------|------|
| `--json` | 输出 JSON 格式（给 Skill/LLM 消费） |
| `--vault PATH` | 指定知识库路径（覆盖 config） |
| `--pretty` | JSON 美化输出 |

---

## 9. Skill 设计

### 9.1 主文件

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

### 9.2 渐进式披露

Skill 本体只放标题和引用，实际内容按需读取：

- **skills/checklist.md**：首次启动时读取（检查 CLI 安装、运行 setup）
- **skills/commands.md**：需要了解命令细节时读取

### 9.3 调用方式

```
/daily-notes              → 交互模式，问用户想做什么
/daily-notes <content>    → 直接 add
/daily-notes daily        → 内部映射 review --period day --focus ingest
/daily-notes weekly       → 内部映射 review --period week --focus link
/daily-notes monthly      → 内部映射 review --period month --focus pattern
```

### 9.4 联网能力

联网能力通过 Claude Code 安装的其他 skill 实现。有则抓取全文再 add，无则只保存用户给的内容。CLI 不自己处理联网。

---

## 10. 错误处理

| 场景 | 处理方式 |
|------|------|
| CLI 未安装 | Skill 首次检查时引导安装 |
| vault 未初始化 | CLI 报错并提示运行 setup |
| front matter 解析失败 | CLI 跳过该文件，输出警告，不中断 |
| ingest 时 source 不存在 | CLI 报错，列出可用 source |
| link 时 target 不存在 | CLI 报错，列出可用 atomic |
| review 无候选 | CLI 输出友好提示 |
| id 冲突 | 追加额外随机字符 |

---

## 11. 测试策略

| 测试类型 | 覆盖内容 | 工具 |
|---------|---------|------|
| 单元测试 | front matter 解析/生成、id 生成、路径计算 | pytest |
| 单元测试 | config 读写、vault 文件操作 | pytest + tmp_path |
| 集成测试 | 完整 add → review → ingest 流程 | pytest + Click CliRunner |

---

## 12. v1 边界（明确不做）

- 多用户/协作
- 移动端支持
- 语义搜索/embedding
- Web UI / Dashboard

---

## 13. 关键决策记录

### 13.1 为什么用 Click 而非 Typer？

Click 更成熟稳定，装饰器模式可以写得很简洁。对于这个规模的 CLI（~10 个命令），Click 完全够用。

### 13.2 为什么 Source 不移动，而是复制引用？

Source 和 Atomic 是一对多关系。一个 Source 可能产出多个 Atomic，一个 Atomic 也可能引用多个 Source。保持 Source 不动，通过 front matter 的 sources 字段建立关联。

### 13.3 为什么用 Obsidian 文件引用而非 wiki-link？

用户明确偏好 `[xxx](xxx.md)` 格式的文件引用，而非 `[[xxx]]` wiki-link。文件引用在 Obsidian 以外的编辑器中也有更好的兼容性。

### 13.4 为什么 daily/weekly/monthly 是 review 的快捷封装？

三者的核心逻辑相同（读取时间范围 → 列出候选 → 推荐操作），只是时间窗口和关注点不同。封装为快捷命令减少重复代码，同时保持语义清晰。

---

## 14. 实现优先级

1. **P0**：core 模块（config、vault、frontmatter、id）+ setup + add
2. **P1**：review + list + search
3. **P2**：ingest + link
4. **P3**：Skill 文件 + daily/weekly/monthly 快捷命令
5. **P4**：测试覆盖
