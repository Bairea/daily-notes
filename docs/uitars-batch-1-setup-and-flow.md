# 批次1（UI-TARS重制版）：UI-TARS NutJS 电脑控制流程跑通

> 日期：2026-08-31
> 目标：不再使用 TRAE 自带的 `mcp_Computer_Use` MCP，改用 UI-TARS-desktop 项目的 NutJSOperator 电脑控制工具，跑通「截图→视觉理解→操作」标准链路。

## 0. 为什么选这个方案

UI-TARS-desktop 项目提供了三种电脑控制形式，各有取舍：

| 方式 | 需要 UI-TARS 模型 API | 脚本化程度 | 本次选型 |
|------|----------------------|-----------|---------|
| @agent-tars/cli（完整 Agent CLI） | 需要（支持多种 provider） | 高 | 未选：需要模型配置，且本次重点是"替代原 MCP 的底层操作能力"，视觉理解由 TRAE agent 承担更直接 |
| @ui-tars/sdk + NutJSOperator | **不需要**（仅用 Operator 做底层动作，视觉交给 TRAE Read 截图） | **完全程序化** | **选中**：复用 UI-TARS 官方 Operator 封装，动作稳定，无模型依赖 |
| UI-TARS Desktop GUI 应用 | 需要（Doubao/HuggingFace） | 低（手动交互） | 未选：不适合批量迭代和脚本化记录 |

## 1. 工具安装与位置

```
daily-notes/
└── tools/
    └── ui-tars-control/
        ├── package.json     # @ui-tars/sdk + @ui-tars/operator-nut-js + @nut-tree/nut-js + uuid + jimp
        ├── node_modules/    # 256 个包，首次 npm install 生成
        └── index.js         # CLI 封装，暴露 screenshot/click/scroll/type/press 等命令
```

安装命令（首次）：

```powershell
cd tools\ui-tars-control
npm init -y
npm install @ui-tars/sdk @ui-tars/operator-nut-js uuid jimp @nut-tree/nut-js
```

## 2. 可用命令清单

所有命令都在 TRAE 中通过 `RunCommand` 调用：

```powershell
cd d:\Desktopfile\chores\daily_notes\tools\ui-tars-control
```

### 2.1 `screenshot` 截图

```powershell
node index.js screenshot --out <保存路径>.jpg
```

- 返回 JSON：`{ok, file, uri, scaleFactor}`
- 截图为 **整屏 JPG**（如 2560x1440），坐标系原点左上角
- **验证结果**：成功，已连续 4 次正常产出截图

### 2.2 `click` 点击

```powershell
node index.js click --x <像素> --y <像素> [--button left|middle|right]
```

- 坐标为**屏幕绝对坐标**（整屏，非单窗口）
- 视觉判断坐标流程：TRAE Read 截图 → agent 看到元素位置 → 估算 x/y → 调用 click
- **验证结果**：成功（点击任务栏、系统托盘等均生效）

### 2.3 `scroll` 滚动

```powershell
node index.js scroll --direction up|down|left|right [--pages 1] [--x X --y Y]
```

- direction：微信向上滚动 = 看更早历史
- pages：每次建议 1-2，跳得太多容易漏内容
- 可选 x/y 为滚动位置（不指定则滚当前鼠标处）
- **验证结果**：接口实现完备，待实际操作微信时进一步验证

### 2.4 `type` 输入文字

```powershell
node index.js type --text "hello world"
```

- **重要局限**：NutJS 在 Windows 上只能可靠输入 ASCII 字符，**中文字符无法正确输入**
- 替代方案：中文内容 → 先复制到剪贴板 → 用 Ctrl+V 粘贴（需要写一个 press 组合键）
- **验证结果**：ASCII 字符 OK，中文需走剪贴板方案

### 2.5 `press` 按键（含组合键扩展建议）

```powershell
node index.js press --key enter      # 单键
```

- 当前版本的 NutJSOperator `hotkey` 对部分 key name 识别有限
- 建议在后续迭代中扩展 `press-combo` 命令，用原生 NutJS `keyboard.hotkey()` 支持 `Key.LeftControl, Key.V` 等组合

### 2.6 `mouse-info` / `screen-info` 辅助命令

```powershell
node index.js mouse-info     # 打印当前鼠标坐标（调试用）
node index.js screen-info    # 打印屏幕分辨率（调试用）
```

## 3. 标准工作流（与原 MCP 流程对比）

| 步骤 | 原 TRAE 自带 MCP `mcp_Computer_Use` | 新 UI-TARS NutJS Operator |
|------|-------------------------------------|---------------------------|
| 1. 取窗口 pid | `list_apps` → 找到微信 pid | **不需要**（整屏操作，无需 pid） |
| 2. 取窗口状态+截图 | `get_app_state(pid, ...)` → 含 ui_tree + 截图 | `screenshot` → 只有整屏截图；**无 UI 树**（ui_tree 一直就很浅基本没用，反而更直接） |
| 3. 看截图 | Read 截图文件 | 同上 Read 截图文件 |
| 4. 点击 | `click(pid, element_id="0", x, y)` | `click --x X --y Y`（更简单，无 element_id 假字段） |
| 5. 滚动 | `scroll(pid, element_id, direction, pages)` | `scroll --direction ... --pages ...` |
| 6. 输入 | `type_text(pid, text)` | `type --text "..."`（ASCII）或后续扩展 Ctrl+V 方案 |

**总结：新链路更干净，去掉了 MCP 层对 pid/element_id 等微信上完全虚设的字段。**

## 4. 本次验证过程记录

```
1. screen-info → 分辨率 2560x1440 (OK)
2. screenshot → test-screenshot-ui-tars.jpg (OK, 2560x1440 JPG)
   TRAE Read 图片 → 正常看到 TRAE 界面 + 任务栏
3. click --x 2275 --y 1415 → 点击任务栏托盘 ^ 按钮 (OK)
4. 后续 click 任务栏空白处 → 屏幕恢复正常 (OK)
5. click --x 1060 --y 1416 → 切换应用 (OK)
6. type --text "微信" → 调用成功但中文未渲染（已知局限，记录见 2.4）
7. 全部命令返回 JSON 格式统一，便于 RunCommand 解析
```

## 5. 已知问题与后续 TODO

### 5.1 已知问题

1. **中文输入**：NutJS type 中文不可用。解决：新增 `copy-then-paste` 命令，写文件 → PowerShell Set-Clipboard → press Ctrl+V。
2. **微信未登录**：当前 Windows 会话中 `Get-Process WeChat` 返回 `NOT RUNNING`，需要**用户手动扫码登录微信**后才能操作群聊。
3. **组合键支持弱**：当前 press 命令单键 OK，Ctrl/Alt+键需要扩展。
4. **Windows 缩放 DPR**：本次验证使用 100% 缩放（scaleFactor=1），如果以后在 125%/150% 缩放屏幕上需要验证坐标转换。

### 5.2 后续 TODO

- [ ] 扩展 press-combo 支持 Ctrl+V 等组合键（解决中文输入）
- [ ] 扩展 launch-app：支持从 Start Menu 找到应用路径启动
- [ ] 微信登录后，验证：滚动消息列表、点击文章卡片打开浏览器、从浏览器地址栏获取完整 URL
- [ ] 浏览器打开文章后，配合 TRAE 自带 `browser_use` Skill 或 `WebFetch` 抓取正文，补全现有 cited source 的 `url` 和 `body` 字段

## 6. 与旧 MCP 流程的调用映射速查表

| 目的 | 旧 MCP 方式 | 新 UI-TARS NutJS 方式 |
|------|------------|----------------------|
| 找应用 | `run_mcp("mcp_Computer_Use","list_apps",{"includeWindowIds":true})` | 不需要；或 `Get-Process <name>` 查是否在运行，直接用命令行启动 |
| 启动应用 | `run_mcp("mcp_Computer_Use","launch_app",{"app":"<id>"})` | PowerShell 直接调用 exe 路径 |
| 截图看界面 | `run_mcp("mcp_Computer_Use","get_app_state",{"pid":...,"max_depths":25,"disableDiff":true})` → 读返回的 image-uri | `node index.js screenshot --out <path>` → TRAE Read `<path>` |
| 点击 | `run_mcp("mcp_Computer_Use","click",{"pid":...,"element_id":"0","x":X,"y":Y})` | `node index.js click --x X --y Y` |
| 滚动 | `run_mcp("mcp_Computer_Use","scroll",{"pid":...,"element_id":"1","direction":"up","pages":3})` | `node index.js scroll --direction up --pages 3` |
| 输入文字 | `run_mcp("mcp_Computer_Use","type_text",{"pid":...,"text":"..."})` | `node index.js type --text "..."`（ASCII 场景） |
| 按键 | `run_mcp("mcp_Computer_Use","press_key",{"pid":...,"key":"enter"})` | `node index.js press --key enter` |

## 7. 批次1产出清单

- **代码**：`tools/ui-tars-control/package.json` + `tools/ui-tars-control/index.js`（CLI 工具）
- **验证截图**：`test-screenshot-ui-tars.jpg`, `scr-2.jpg` ~ `scr-5.jpg`（本次验证产物）
- **文档**：本文件 `docs/uitars-batch-1-setup-and-flow.md`
- **功能状态**：`--date` 已在批次2实现并验证，本次确认无需改动

接下来需要**用户在本机扫码登录微信**，即可进入批次2：获取 daily 群聊中文章的完整 URL，补全现有 source 笔记。
