# 电脑控制流程参考文档

> 本文档记录通过 MCP `mcp_Computer_Use` 服务器控制 Windows 桌面应用（以微信为例）的完整流程，供后续批次迭代参考。

## 1. 核心发现

桌面控制能力不在 agent 的直接工具列表中，而是通过 **MCP 服务器 `mcp_Computer_Use`** 提供。必须用 `run_mcp` 工具调用。

调用模板：

```
run_mcp(
  server_name = "mcp_Computer_Use",
  tool_name   = "<工具名>",
  args        = { ... }   // 所有参数放在 args 对象里
)
```

> 注意：`run_mcp` 的所有工具参数必须放在 `args` 字段内，不能作为顶层字段传递。

## 2. 可用工具清单

| 工具名 | 作用 | 关键参数 |
|--------|------|----------|
| `list_apps` | 列出运行中/已安装的应用，返回 pid 和 app_id | `{"includeWindowIds": true}` |
| `launch_app` | 启动应用，返回 pid | `{"app": "<app_id>"}` |
| `get_app_state` | 获取应用截图 + UI 无障碍树 | `{"pid": <数字>, "max_depths": 25, "disableDiff": true}` |
| `click` | 点击元素（坐标或 element_id） | `{"pid": <数字>, "element_id": "0", "x": <数字>, "y": <数字>}` |
| `scroll` | 滚动元素 | `{"pid": <数字>, "element_id": "<id>", "direction": "up"/"down", "pages": 2}` |
| `type_text` | 输入文字 | `{"pid": <数字>, "text": "<内容>"}` |
| `press_key` | 按键 | `{"pid": <数字>, "key": "<键名>"}` |
| `set_value` | 设置控件值 | `{"pid": <数字>, "element_id": "<id>", "value": "<值>"}` |
| `drag` | 拖拽 | `{"pid": <数字>, "from": {...}, "to": {...}}` |
| `select_text` | 选择文本 | `{"pid": <数字>, "element_id": "<id>"}` |
| `perform_action` | 执行动作（Press/Confirm 等） | `{"pid": <数字>, "element_id": "<id>", "action": "<动作>"}` |

## 3. 标准工作流（以微信为例）

### 步骤 1：定位目标应用

```
run_mcp("mcp_Computer_Use", "list_apps", {"includeWindowIds": true})
```

从返回结果中找到目标应用的 `pid`。例如微信：

```
微信 [pid=16436, app_id={6D809377-...}\Tencent\Weixin\Weixin.exe]
```

> pid 每次开机后会变化，不能硬编码，每次都要重新 `list_apps` 获取。

如果应用未运行，用 `launch_app` 启动：

```
run_mcp("mcp_Computer_Use", "launch_app", {"app": "<app_id>"})
```

### 步骤 2：获取应用状态（截图 + UI 树）

```
run_mcp("mcp_Computer_Use", "get_app_state", {
  "pid": 16436,
  "max_depths": 25,
  "disableDiff": true
})
```

返回内容包含：
- `<ui_tree>`：无障碍 UI 树，每个元素一行，格式为 `role "label" (traits) [actions] val=value id=ID`
- `image-uri`：截图文件路径（`file:///...` 格式）
- 坐标系：相对于应用窗口的像素坐标

### 步骤 3：查看截图（视觉判断）

`get_app_state` 返回的截图保存在本地文件，路径形如：

```
file:///c%3A/Users/.../screenshots/win-sdk-xxxx.jpg
```

用 `Read` 工具读取该路径即可看到截图内容（agent 的视觉能力会解析图片）。

> 关键：由于微信使用自定义 UI 框架，无障碍树很浅（往往只能看到 `pane`），**必须依赖截图视觉判断元素位置**，再用 `click` 的 `x/y` 坐标点击。

### 步骤 4：交互操作

点击聊天列表中的某个群：

```
run_mcp("mcp_Computer_Use", "click", {
  "pid": 16436,
  "element_id": "0",   // element_id 必填，无具体 id 时传 "0"
  "x": 120,            // 从截图中读出的坐标
  "y": 300
})
```

搜索群聊：点击搜索框 → 输入文字 → 点击结果

```
run_mcp("mcp_Computer_Use", "click", {"pid": 16436, "element_id": "0", "x": <搜索框x>, "y": <搜索框y>})
run_mcp("mcp_Computer_Use", "type_text", {"pid": 16436, "text": "daily"})
# 再次 get_app_state 截图，找到搜索结果坐标后点击
```

### 步骤 5：滚动查看历史消息

```
run_mcp("mcp_Computer_Use", "scroll", {
  "pid": 16436,
  "element_id": "1",       # 消息列表区域的 element_id
  "direction": "up",       # 向上滚 = 看更早的历史
  "pages": 3
})
```

滚动后重新 `get_app_state` + `Read` 截图，读取新出现的消息。

### 步骤 6：循环收集

重复「滚动 → 截图 → 读取」直到到达群聊顶部或收集够目标时间范围的消息。

## 4. 微信操作要点

### 4.1 UI 框架特性
- 微信用自定义渲染框架，无障碍树极浅，通常只能看到 `pane "MMUIRenderSubWindowHW"`
- **不能依赖 element_id 精确点击**，要用截图坐标 `x/y` 点击
- `element_id` 是必填字段，无具体 id 时传 `"0"`，配合 `x/y` 使用

### 4.2 窗口聚焦
- `get_app_state` 可能提示目标窗口未聚焦，但仍能返回该窗口的截图和 UI 树
- 如需将窗口置前，可在 UI 树中找到 `window` 节点的 `[set_focus]` 动作，用 `perform_action` 聚焦

### 4.3 消息识别
- 消息发送者：每条消息上方的小字
- 时间：消息分组的时间分隔条（如 "8月5日 20:52"）
- 链接消息：带卡片预览（标题 + 摘要 + 来源域名）
- 系统消息：居中灰色文字（如 "你邀请...加入了群聊"）

### 4.4 滚动策略
- 微信消息列表向上滚动 = 查看更早历史
- 每次 `pages: 2-3` 比较稳，太多可能跳过内容
- 滚动后微信会加载更多历史消息，需要重新截图读取

## 5. 委派给子 agent 的建议

直接在主 agent 里调 `run_mcp` 无法「看」截图（主 agent 的 Read 只读文本）。**推荐委派给 `computer_use` 子 agent**，因为它有：

- `run_mcp`：调用 `mcp_Computer_Use` 所有工具
- `Read`：读取截图文件并视觉理解图片内容

委派时的关键提示（务必写进子 agent 的任务描述）：

1. 明确告知用 `run_mcp(server_name="mcp_Computer_Use", ...)` 调用桌面控制工具
2. 给出 pid（如已知）或要求先 `list_apps` 获取
3. 要求每步先 `get_app_state` 截图，再用 `Read` 看截图，再决定下一步
4. 说明微信 UI 树很浅，需用 `x/y` 坐标点击，`element_id` 传 `"0"`

## 6. 工具描述符位置

MCP 工具的 JSON 描述符存放在：

```
c:\Users\<用户名>\.trae-cn\mcps\s_daily_notes-<hash>\solo_agent_lite\mcp_Computer_Use\tools\<tool>.json
```

用 `Read` 读取这些 `.json` 可查看每个工具的完整参数 schema。

## 7. 已验证可用的操作序列

批次1已验证完整的操作链路：

```
list_apps (找到微信 pid=16436)
  → get_app_state (截图微信窗口)
  → Read 截图 (看到聊天列表)
  → click (点击 daily 群 或 搜索框)
  → type_text (输入 "daily")
  → click (点击搜索结果进入群聊)
  → get_app_state (截图群消息)
  → Read 截图 (读取消息)
  → scroll up (滚动查看更早消息)
  → get_app_state + Read (循环读取)
  → 到达群顶部，收集完成
```

全程通过 `run_mcp` 调用，子 agent 用 `Read` 看截图做视觉判断。该链路稳定可用。
