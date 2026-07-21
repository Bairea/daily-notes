# 启动检查清单

1. 运行 `which daily-notes` 检查 CLI 是否安装
2. 未安装 → 告诉用户运行 `uv pip install daily-notes` 并停止
3. 已安装 → 运行 `daily-notes setup`（若未初始化）
