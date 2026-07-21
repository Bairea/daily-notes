# CLI 命令详情

本文件是命令参数参考手册。典型工作流程（识别意图 → 路由到命令）见 SKILL.md 的"意图路由"一节。

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
