# 功能测试报告与 Bug 修复

> 日期：2026-08-31
> 方法：委派子代理运行 daily-notes CLI 全部命令，验证实际行为

## 1. 测试范围

通过子代理对以下命令做了端到端功能测试：
setup、add（cited/fleeting/--date/--body）、list（--type/--tag/--since/--json）、search（query/--tag）、ingest（--date）、link、review、daily/weekly/monthly、未初始化错误处理。

## 2. 发现的 Bug

| # | Bug | 严重度 | 文件 | 状态 |
|---|-----|--------|------|------|
| 1 | setup 首次运行误报"已存在配置" | 低 | setup.py | 已修复 |
| 2 | list --since 过滤完全失效 | 高 | list_cmd.py | 已修复 |
| 3 | list --tag 过滤完全失效 | 高 | list_cmd.py | 已修复 |
| 4 | search 无 --tag 选项 | 中 | search.py | 已修复 |
| 5 | link 用位置参数而非 --source/--target | 中 | link.py | 设计选择，不改 |
| 6 | add/ingest --date 非法日期抛未捕获异常 | 中 | add.py, ingest.py | 已修复 |

## 3. 修复详情

### Bug 1：setup 误报"已存在配置"
- **原因**：[setup.py](file:///d:/Desktopfile/chores/daily_notes/src/daily_notes/commands/setup.py) 在 `save_config` 之后才调用 `is_initialized`，永远返回 True
- **修复**：在 `save_config` 之前先检查 `is_initialized`，保存原始状态

### Bug 2：list --since 过滤失效
- **原因**：[list_cmd.py](file:///d:/Desktopfile/chores/daily_notes/src/daily_notes/commands/list_cmd.py) 接受 `--since` 参数但函数体从未引用
- **修复**：用笔记 id 的前 8 位（YYYYMMDD）与 since 日期比较，早于 since 的跳过

### Bug 3：list --tag 过滤失效
- **原因**：同上，`--tag` 参数被接受但从未用于过滤
- **修复**：加载每条笔记的 frontmatter，检查 `tags` 列表是否包含目标 tag

### Bug 4：search 无 --tag 选项
- **原因**：[search.py](file:///d:/Desktopfile/chores/daily_notes/src/daily_notes/commands/search.py) 只有 query 位置参数，无 --tag
- **修复**：添加 `--tag` 可选选项，query 改为可选。两者可组合使用，至少提供一个

### Bug 6：--date 非法日期抛异常
- **原因**：[add.py](file:///d:/Desktopfile/chores/daily_notes/src/daily_notes/commands/add.py) 和 [ingest.py](file:///d:/Desktopfile/chores/daily_notes/src/daily_notes/commands/ingest.py) 直接调用 `datetime.strptime` 未捕获 ValueError
- **修复**：用 try/except 包裹，捕获后输出"错误：日期格式无效，应为 YYYY-MM-DD"并 `raise SystemExit(1)`

## 4. 不修改项

### Bug 5：link 用位置参数
- `link SOURCE_ID TARGET_ID REASON` 是位置参数接口，功能完全正常（links/backlinks、Obsidian 文件引用都正确写入）
- 这是 CLI 设计选择，不是 bug。文档中应明确说明用位置参数调用

## 5. 测试结果

修复后新增 4 个测试（test_list_filter_by_tag、test_list_filter_by_since、test_add_invalid_date、test_search_by_tag），全部通过。

```
45 passed in 0.80s
```

## 6. 电脑控制 URL 获取状态

第一批次尝试用电脑控制点击微信文章获取完整 URL，但微信进程在操作过程中意外关闭（pid 消失）。需要重试。
