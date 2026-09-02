# CLI 命令详情

本文件是命令参数参考手册。典型工作流程（识别意图 → 路由到命令）见 SKILL.md 的"意图路由"一节。

## add
```bash
daily-notes add <content> [--url URL] [--type TYPE] [--title TITLE] [--summary SUMMARY] [--body BODY] [--tag TAG...]
```
有 `--url` → cited Source，无 `--url` → fleeting Source。
`--body` 用于保存 cited source 的原文全文（摘录），无 `--body` 时正文为空。

## ingest
```bash
daily-notes ingest --source <id> [--content TEXT] [--title TITLE] [--tag TAG...]
```
从 Source 创建 Atomic Note（只建壳，正文由用户填写）。同一 source 可多次 ingest（一对多），CLI 会提示该 source 已被引用，但不阻断。

## link
```bash
daily-notes link <source_id> <target_id> <reason>
```
在两条 Atomic Note 之间建立双向链接，并分别在正文追加 `## 相关笔记` / `## 反向链接` 引用。

## daily
```bash
daily-notes daily [--json]
```
列出待消化的 Source（尚未被任何 Atomic 引用，且未归档 / 未过期）。按 id 升序，最老的积压排最前。

## weekly
```bash
daily-notes weekly [--json]
```
列出待连接的 Atomic（尚无出链，且未过期）。`backlinks` 不计入。

## monthly
```bash
daily-notes monthly [--json]
```
按标签聚类展示全部 Atomic（多标签笔记出现在每个分组；未打标签归入"未打标签"）。同时内嵌待连接队列（不含过期项）。

## stale
```bash
daily-notes stale [--json]
```
列出全部过期内容（`status: stale`），作为复核入口。

## show
```bash
daily-notes show <id> [--json]
```
查看单条笔记全部字段（含 sources / links / backlinks / stale_note）与正文。

## mark
```bash
daily-notes mark <id> <stale|archived|active> [--note TEXT]
```
统一设置笔记状态：
- `stale`：标记过期，`--note` 可写原因（可选）
- `archived`：仅限 Source，放弃消化、移出 `daily` 队列
- `active`：清除 `status` 与 `stale_note`，恢复活跃

## list / search
```bash
daily-notes list [--type TYPE] [--tag TAG] [--json]
daily-notes search <query> [--json]
```

## 高频 / 复核命令速查
- `daily`：待消化 Source
- `weekly`：待连接 Atomic
- `monthly`：标签聚类 + 待连接队列
- `stale`：全部过期内容（复核入口）
- `show <id>`：单条笔记全字段
- `mark <id> <stale|archived|active>`：标记过期 / 归档 / 恢复

所有列表命令均支持 `--json`，输出 JSON 供 LLM 消费。
