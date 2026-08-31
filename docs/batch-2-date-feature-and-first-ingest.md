# 批次2：--date 功能实现与第一批 ingest

> 日期：2026-08-31
> 目标：实现按内容日期存放的功能，并 ingest 第一批微信 daily 群消息（8月5-10日）

## 1. 完成内容

### 1.1 `--date` 功能（TDD）

按内容日期存放而非操作日期。改动 4 个文件：

- [id.py](file:///d:/Desktopfile/chores/daily_notes/src/daily_notes/core/id.py)：`generate_date_id(date=None)` 接受 datetime 对象或 `YYYY-MM-DD` 字符串，用该日期生成 id 前缀
- [vault.py](file:///d:/Desktopfile/chores/daily_notes/src/daily_notes/core/vault.py)：`get_current_month_dir(vault, dt=None)` 接受可选日期，按该日期所在年月创建/获取目录
- [add.py](file:///d:/Desktopfile/chores/daily_notes/src/daily_notes/commands/add.py)：新增 `--date` 选项，解析后传入 id 生成和目录选择
- [ingest.py](file:///d:/Desktopfile/chores/daily_notes/src/daily_notes/commands/ingest.py)：同上

TDD 流程：先写 4 个失败测试（test_id 2个 + test_add 1个 + test_ingest 1个）→ 确认失败 → 实现 → 41 个测试全通过。

顺带修复了 `test_add_cited_with_body` 的硬编码月份 bug（`202607` → 动态 `datetime.now().strftime("%Y%m")`）。

### 1.2 第一批 ingest（8月5-10日）

使用 `--date` 将 7 条消息 ingest 到 `test-vault/202608`：

| source id | 日期 | 类型 | 内容 |
|-----------|------|------|------|
| 20260805-44c576 | 08-05 | cited | 6个月估值翻10倍，被OpenAI点名 |
| 20260805-b73ace | 08-05 | cited | 我是24届应届生，6月放弃考研 |
| 20260805-0e3b52 | 08-05 | fleeting | agent vs chat 形态判断 |
| 20260808-ac9993 | 08-08 | cited | 我用Cursor写了2年代码（深度测评） |
| 20260808-bd50ba | 08-08 | cited | 我是怎样把微信好友月入3K的 |
| 20260810-5943d4 | 08-10 | cited | 我用Claude Code两个月后（深度测评） |
| 20260810-babe43 | 08-10 | fleeting | AI编程工具正确打开方式 |

验证：`daily-notes list --type source` 正确列出 202608 目录下的 7 条新笔记。

## 2. 关键设计决策

- **日期只影响 id 和目录**：`--date` 改变 id 的日期前缀和存放的年月目录，`created` frontmatter 字段仍为操作时间（语义正确）
- **日期格式**：`YYYY-MM-DD`（ISO 标准，Click 解析方便）
- **URL 占位**：电脑控制只采集到域名（如 mp.weixin.qq.com），暂用域名作 URL，后续批次可补充完整链接
- **fleeting source 用途**：将群聊中有洞察的文字消息作为 fleeting source ingest，保留原文

## 3. 测试集处理进度

- 已处理：8月5-10日的 5 篇链接文章 + 2 条洞察（消息 #4, #5, #7, #8, #12, #17, #22, #25-#28）
- 待处理：8月11-31日的 19 篇链接文章 + 其他文字消息

详见 [wechat-daily-testset.md](file:///d:/Desktopfile/chores/daily_notes/docs/wechat-daily-testset.md) 的批次处理日志。

## 4. 已知局限与后续 TODO

- URL 仅有域名，未采集完整文章链接
- `list --since` 的日期过滤行为需验证（本次列出全部，可能未按 since 过滤）
- 后续批次继续 ingest 8月11-31日剩余消息
