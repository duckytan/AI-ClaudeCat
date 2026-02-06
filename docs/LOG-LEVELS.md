# 📊 **日志级别说明**

## 概述

AI-ClaudeCat 支持两种日志模式：**Normal（正常）** 和 **Debug（调试）**。

---

## 🎯 **Normal 模式（推荐）**

**配置**: `"debug": false`（默认）

### ✅ **显示的信息**

| 类型 | 示例 | 说明 |
|------|------|------|
| **状态变化** | `🤔 Thinking...` | AI 思考中 |
| | `⏸️  Waiting for user input` | 等待用户输入 |
| | `🚀 User input received` | 用户输入已接收 |
| | `✅ Turn completed (1234ms)` | 回合完成 |
| **工具调用** | `🔧 Read: file=main.py` | 读取文件 |
| | `🔧 Write: file=test.py` | 写入文件 |
| | `🔧 Bash: python` | 执行命令 |
| **MCP 工具** | `🔌 MCP: search (open-websearch)` | MCP 工具调用 |
| | `🔌 MCP Started: search` | MCP 工具开始 |
| | `🔌 MCP Completed: search (1234ms)` | MCP 工具完成 |
| **Token 统计** | `📊 Session completed (Total tokens: 12,345)` | 会话完成 |
| **错误** | `❌ API Error: invalid_request` | 重大错误 |

### ❌ **隐藏的信息**

- 🚫 **JSONL 文件读取**: `[INFO] File: session-xxx.jsonl - Size: 12345 bytes`
- 🚫 **Watchdog 事件**: `[Watchdog] File changed`
- 🚫 **文件位置**: `Initialized 5 file positions`
- 🚫 **增量读取**: `[READ] 3 new lines`
- 🚫 **内部状态**: `[SKIP] No new content`

---

## 🔧 **Debug 模式（开发调试）**

**配置**: `"debug": true`

### ✅ **额外显示的信息**

| 类型 | 示例 | 说明 |
|------|------|------|
| **文件扫描** | `Found 5 logs, latest: session-xxx.jsonl` | 日志文件扫描结果 |
| **位置初始化** | `Initialized 5 file positions` | 读取位置初始化 |
| **文件监控** | `[WATCH] Directory: ~/.claude/projects` | 监控目录 |
| **Watchdog 事件** | `[Watchdog] File changed: session-xxx.jsonl` | 文件变化事件 |
| **文件读取** | `[INFO] File: session-xxx.jsonl - Size: 12345 bytes` | 文件大小变化 |
| **增量读取** | `[READ] 3 new lines` | 读取的新行数 |
| **跳过** | `[SKIP] No new content` | 无新内容 |
| **内部事件** | `[DEBUG] File history snapshot` | 文件历史快照 |

---

## 📋 **配置方法**

### **方法 1: 修改 `config.json`**

```json
{
  "version": "4.1.0",
  "debug": false,  // ← 修改这里（false=Normal, true=Debug）
  
  "claude": {
    "projects_dir": "auto"
  },
  
  "plugins": {
    "claude_log": {
      "enabled": true
    }
  }
}
```

### **方法 2: 使用环境变量（未来支持）**

```bash
# Normal 模式
python main.py

# Debug 模式
DEBUG=true python main.py
```

---

## 🎨 **输出示例**

### **Normal 模式（精简）**

```
[claude_log] Starting...
[claude_log] [OK] Started, monitoring: C:\Users\...\claude\projects
[claude_log] [INFO] Debug mode OFF - showing only meaningful events

🚀 User input received
🤔 Thinking...
🔧 Read: file=main.py
🔧 Write: file=config.json
🔧 Bash: python
✅ Turn completed (2345ms)
⏸️  Waiting for user input

📊 Session completed (Total tokens: 12,345)
```

### **Debug 模式（详细）**

```
[claude_log] Starting...
[claude_log] Found 5 logs, latest: C:\Users\...\session-abc123.jsonl
[claude_log] Initialized 5 file positions
[claude_log] [OK] Event loop acquired
[claude_log] [WATCH] Directory: C:\Users\...\claude\projects
[claude_log] [WATCH] Monitoring *.jsonl files recursively...
[claude_log] [OK] Started, monitoring: C:\Users\...\claude\projects

[Watchdog] File changed: C:\Users\...\session-abc123.jsonl
[claude_log] [INFO] File: session-abc123.jsonl - Size: 12345 bytes (was: 11000)
[claude_log] [READ] 3 new lines

🚀 User input received
🤔 Thinking...
🔧 Read: file=main.py
🔧 Write: file=config.json
🔧 Bash: python
✅ Turn completed (2345ms)
⏸️  Waiting for user input

[Watchdog] File changed: C:\Users\...\session-abc123.jsonl
[claude_log] [INFO] File: session-abc123.jsonl - Size: 15678 bytes (was: 12345)
[claude_log] [READ] 5 new lines

📊 Session completed (Total tokens: 12,345)
```

---

## 🎯 **推荐使用场景**

| 场景 | 模式 | 说明 |
|------|------|------|
| **日常使用** | Normal | 只看有意义的事件 |
| **开发调试** | Debug | 查看完整流程 |
| **生产环境** | Normal | 减少日志输出 |
| **问题排查** | Debug | 定位问题根源 |
| **演示展示** | Normal | 界面更清爽 |

---

## 📊 **日志输出对比**

| 指标 | Normal 模式 | Debug 模式 |
|------|-------------|-----------|
| **日志行数** | ~10 行/分钟 | ~50 行/分钟 |
| **信息密度** | 高（只显示关键事件）| 低（显示所有细节）|
| **可读性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **调试能力** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎨 **表情符号说明**

| 表情 | 含义 | 说明 |
|------|------|------|
| 🚀 | 用户输入 | User input received |
| 🤔 | 思考中 | AI thinking |
| 🔧 | 工具调用 | Tool execution |
| 🔌 | MCP 工具 | MCP tool call |
| ⏸️  | 等待中 | Waiting for user |
| ✅ | 完成 | Turn/Session completed |
| 📊 | 统计 | Token statistics |
| ❌ | 错误 | Critical error |
| ⚠️ | 警告 | Warning (ignorable) |

---

## 🔄 **切换模式**

### **从 Normal 切换到 Debug**

1. 打开 `config.json`
2. 修改 `"debug": false` → `"debug": true`
3. 重启应用：`Ctrl+C` → `python main.py`

### **从 Debug 切换到 Normal**

1. 打开 `config.json`
2. 修改 `"debug": true` → `"debug": false`
3. 重启应用：`Ctrl+C` → `python main.py`

---

## 📖 **相关文档**

- [配置说明](CONFIG.md) - 完整配置选项
- [快速开始](QUICKSTART.md) - 快速上手指南
- [项目文档](CLAUDE.md) - 详细技术文档

---

**最后更新**: 2026-02-06  
**版本**: v4.1.0
