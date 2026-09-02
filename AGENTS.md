# Daily Notes 项目规范

## 项目定位

帮助自己持续学习（而非持续记笔记）的 Python CLI + Claude Code Skill 工具。设计灵感来自 Zettelkasten 和 LLM Wiki。

核心原则：**AI 提建议，人做决策。** AI 不写 Atomic Note，不替用户思考。

## 技术栈

- Python 3.11+
- Click（CLI 框架）
- python-frontmatter（front matter 读写）
- PyYAML（config 和 front matter）
- uv（依赖管理）
- pytest（测试）
- hatchling（构建）
- ruff（lint）

## 目录结构

```
daily-notes/
├── pyproject.toml
├── README.md
├── src/daily_notes/
│   ├── __init__.py
│   ├── cli.py                        # Click group 入口（12 个命令）
│   ├── commands/
│   │   ├── decorators.py             # Click 装饰器工厂（vault_option, json_output, ensure_init）
│   │   ├── setup.py / add.py / ingest.py / link.py
│   │   ├── daily.py / weekly.py / monthly.py / stale.py
│   │   ├── show.py / mark.py
│   │   └── list_cmd.py / search.py
│   └── core/
│       ├── config.py                 # 配置读写
│       ├── vault.py                  # 文件路径管理
│       ├── frontmatter.py            # front matter 解析/生成
│       ├── id.py                     # id 生成（YYYYMMDD-短哈希）
│       ├── notes.py                  # 共享查询层：iter_notes / find_note / collect_source_refs / NoteRef
│       └── input.py                  # stdin 输入解析（resolve_text，支持 "-" 读标准输入）
└── tests/
```

```
# 根目录
skills/
  ├── daily-notes/           # Claude Code Skill（供 npx skills 安装）
  │   ├── SKILL.md           # 入口文件
  │   ├── checklist.md       # 启动检查清单
  │   └── commands.md        # 命令参考
  └── daily-notes-workspace/ # skill 迭代工作区
      └── iteration-1/
```

> `.agents/skills/daily-notes/` 是项目级 skill 安装位置（已加入 `.gitignore`），供 pi 等 agent 自动发现。

## 代码规范

1. **装饰器工厂**：所有需要 `--vault` 选项和 init 检查的命令，必须使用 `commands/decorators.py` 中的 `@vault_option()`、`@ensure_init()`、`@json_output()`，不重复写样板代码
2. **装饰器顺序**：`@click.option(...)` → `@vault_option()` → `@ensure_init()` → `def cmd(vault):`
3. **错误处理**：未初始化用 `raise SystemExit(1)` + 提示运行 `setup`；找不到资源统一复用 `commands/show.py` 的 `echo_not_found()`（`raise SystemExit(1)` + 列出可用 id），不得在各命令内联重复相同逻辑（mark/ingest/link 均已复用）
4. **文件编码**：统一 UTF-8
5. **禁止 Emoji**：代码中不包含任何 Emoji 表情
6. **id 格式**：`YYYYMMDD-<6位短哈希>`（`core/id.py` 的 `generate_date_id()`）

## 数据模型

### Front Matter 通用字段
- `id`: string（唯一标识）
- `type`: source / atomic
- `status`: 可选，active（缺省）/ stale（过期，待复核）/ archived（放弃消化，仅 source）
- `stale_note`: `status: stale` 时的可选说明（为什么过期）
- `created`: datetime（ISO 8601）
- `tags`: list[string]

### Source 特有字段
- `source_type`: article / video / github / paper / fleeting
- `url`（cited 专有）
- `title` / `summary`（cited 专有）
- `body`（cited source 的原文摘录全文，通过 `add --body` 写入 markdown 正文）
- `content`（fleeting 存入 body，避免与 frontmatter.Post.content 冲突）
- `date`（可选，通过 `add --date YYYY-MM-DD` 指定内容日期，笔记存入该日期所在年月目录）

### Atomic 特有字段
- `sources`: list[string]（引用的 source id）
- `links`: list[{target, reason}]（出链）
- `backlinks`: list[{source, reason}]（反向链接）

### 链接正文格式（Obsidian 文件引用）
```markdown
## 相关笔记
- [连接理由](target-id.md)
```

## Git 规范

- commit 信息遵循 Angular 规范：`<type>(<scope>): <summary>`，英文一句话
- 去掉 Co-Authored-By 等大模型信息
- 不提交：`__pycache__/`、`*.pyc`、`.venv/`、`uv.lock`、`test-vault/`、`*.stackdump`、`.agents/`

## 测试规范

- 使用 `uv run pytest` 运行
- TDD：先写失败测试 → 运行确认失败 → 实现 → 运行确认通过
- 测试文件命名 `test_<module>.py`
- fixture `tmp_vault`（临时知识库目录）与 `notes`（NotesHelper，封装命令调用并返回笔记 id）在 `tests/conftest.py` 中定义；断言失败场景用 `notes.run(...)` 直接拿 result
- ⚠️ 从输出提取 id 必须用 conftest 的 `NOTE_ID_PATTERN`（锚定结尾 `.md`）：ingest 对已引用 source 会先打印含裸 id 的警告，不锚定会误抓警告里的旧 id

## 高频命令

CLI 只输出候选列表与结构化 I/O；判断由人（或 agent 会话）完成。高频命令均为独立命令（不再是对 `review` 的封装）：
- `daily`：列出待消化的 Source（尚未产出 Atomic）
- `weekly`：列出待连接的 Atomic（尚无出链）
- `monthly`：按标签聚类展示 Atomic，并内嵌待连接队列
- `stale`：列出全部过期内容（status: stale），复核入口

## 知识过期机制

- 派生状态「已消化」由 `core/notes.py` 的 `collect_source_refs()` 实时计算（source 被任意 atomic 的 `sources` 引用即视为已消化），不落盘
- `mark <id> <stale|archived|active> [--note TEXT]` 统一设置状态：`stale` 标记过期、`archived` 放弃一条 source、`active` 清除 `status` 与 `stale_note` 恢复活跃；`--note` 仅当 `state=stale` 时写入 `stale_note`（archived 不接受）
- 过期笔记退出 `daily`/`weekly` 待办队列，但仍保留在 `monthly`/`list`/`search` 中（带 `[过期]` 标记），不会被遗忘
- 判断「是否过期、是否恢复」由人（或 agent 会话）决定，CLI 不自动判定

## 已知问题

- Windows 控制台显示中文可能乱码（代码页问题），不影响功能。文件本身是 UTF-8 编码
- `frontmatter.Post` 的 `content` 键是保留的（表示正文 body），不要把 metadata 存入此键
