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

## 目录结构

```
daily-notes/
├── pyproject.toml
├── README.md
├── src/daily_notes/
│   ├── __init__.py
│   ├── cli.py                        # Click group 入口
│   ├── commands/
│   │   ├── decorators.py             # Click 装饰器工厂（vault_option, json_output, ensure_init）
│   │   ├── setup.py / add.py / ingest.py / review.py
│   │   └── list_cmd.py / search.py / link.py
│   └── core/
│       ├── config.py                 # 配置读写
│       ├── vault.py                  # 文件路径管理
│       ├── frontmatter.py            # front matter 解析/生成
│       └── id.py                     # id 生成（YYYYMMDD-短哈希）
└── tests/
```

```
# 根目录
skills/
  └── daily-notes/      # Claude Code Skill（SKILL.md 入口，供 npx skills 安装）
.agents/skills/
  └── daily-notes/      # 项目级 skill 安装位置，供 pi 等 agent 自动发现
```

## 代码规范

1. **装饰器工厂**：所有需要 `--vault` 选项和 init 检查的命令，必须使用 `commands/decorators.py` 中的 `@vault_option()`、`@ensure_init()`、`@json_output()`，不重复写样板代码
2. **装饰器顺序**：`@click.option(...)` → `@vault_option()` → `@ensure_init()` → `def cmd(vault):`
3. **错误处理**：未初始化用 `raise SystemExit(1)` + 提示运行 `setup`；找不到资源用 `raise SystemExit(1)` + 提示可用项
4. **文件编码**：统一 UTF-8
5. **禁止 Emoji**：代码中不包含任何 Emoji 表情
6. **id 格式**：`YYYYMMDD-<6位短哈希>`（`core/id.py` 的 `generate_date_id()`）

## 数据模型

### Front Matter 通用字段
- `id`: string（唯一标识）
- `type`: source / atomic / review
- `created`: datetime（ISO 8601）
- `tags`: list[string]

### Source 特有字段
- `source_type`: article / video / github / paper / fleeting
- `url`（cited 专有）
- `title` / `summary`（cited 专有）
- `body`（cited source 的原文摘录全文，通过 `add --body` 写入 markdown 正文）
- `content`（fleeting 存入 body，避免与 frontmatter.Post.content 冲突）

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
- 不提交：`__pycache__/`、`*.pyc`、`.venv/`、`uv.lock`、`test-vault/`、`*.stackdump`

## 测试规范

- 使用 `uv run pytest` 运行
- TDD：先写失败测试 → 运行确认失败 → 实现 → 运行确认通过
- 测试文件命名 `test_<module>.py`
- fixture `tmp_vault` 在 `tests/conftest.py` 中定义

## 已知问题

- Windows 控制台显示中文可能乱码（代码页问题），不影响功能。文件本身是 UTF-8 编码
- `frontmatter.Post` 的 `content` 键是保留的（表示正文 body），不要把 metadata 存入此键
