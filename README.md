# AI-ClaudeCat 🐱

<div align="center">

**Claude Code 智能状态监控工具**

[![Version](https://img.shields.io/badge/version-4.0.0-blue.svg)](https://github.com/example/ai-claudecat)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-refactoring-yellow.svg)](https://github.com/example/ai-claudecat)

</div>

---

## 📖 简介

AI-ClaudeCat 是一款专为 **Claude Code** 设计的智能状态监控工具。通过监控 Claude Code 的官方 JSONL 日志文件，实时追踪 AI 的运行状态、工具调用和 Token 使用情况。

### 🎯 核心特性

- ✅ **工具级精度** - 不仅知道 AI 在"工作"，还知道在"读文件"还是"写代码"
- ✅ **可靠性高** - 使用 Claude Code 官方日志数据源（格式稳定，已验证）
- ✅ **隐私保护** - 内置白名单过滤机制，只输出元数据
- ✅ **多输出协议** - WebSocket、HTTP REST API、SQLite 存储
- ✅ **Token 统计** - 追踪输入/输出 Token、缓存命中率
- ✅ **插件化架构** - 易扩展，支持更多 AI 编程工具

---

## 🚀 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/example/ai-claudecat.git
cd ai-claudecat

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行

```bash
python main.py
```

**输出示例**:
```
=== AI-ClaudeCat v4.0 ===
Status monitoring for Claude Code

✓ Claude Code detected at C:\Users\YourName\.claude\projects
✓ Middleware initialized
✓ WebSocket server on port 8765
✓ HTTP server on port 8080
✓ Privacy filter enabled
✓ History storage enabled
```

### 3. 测试

**WebSocket 客户端**（浏览器控制台）:
```javascript
const ws = new WebSocket('ws://127.0.0.1:8765');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('AI 状态:', data.status);
    console.log('工具:', data.details.tool);
};
```

**HTTP 查询**:
```bash
# 当前状态
curl http://127.0.0.1:8080/api/status

# 历史事件
curl http://127.0.0.1:8080/api/history?limit=10

# Token 统计
curl http://127.0.0.1:8080/api/tokens
```

---

## 📊 监控状态

AI-ClaudeCat 可以检测 8 种状态：

| 状态 | 描述 | 触发条件 |
|------|------|---------|
| 🟢 **idle** | 空闲 | 等待用户输入 |
| 🔵 **running** | 运行中 | AI 接收到提示词 |
| 🟡 **thinking** | 思考中 | AI 内部推理（`thinking` 块）|
| 🟠 **working** | 工作中 | 读/写文件、搜索（`Read`/`Write`/`Grep`）|
| 🔴 **executing** | 执行中 | 运行命令（`Bash` 工具）|
| ⚪ **waiting** | 等待 | 等待用户确认（`AskUserQuestion`）|
| ❌ **error** | 错误 | 工具调用失败 |
| ⚫ **stopped** | 停止 | Claude Code 关闭 |

---

## 🛠️ 工具调用监控

支持的工具类型：

- 📖 **Read** - 读取文件
- ✏️ **Write** - 写入文件
- 🖊️ **Edit** - 编辑文件
- 🔍 **Grep** - 搜索代码
- 📁 **Glob** - 文件匹配
- 💻 **Bash** - 执行命令
- 🌐 **WebFetch** - 网络请求
- 🔎 **WebSearch** - 网络搜索
- 🤖 **Task** - 派生子 Agent
- ✅ **TodoWrite** - 写入待办事项

**示例输出**:
```json
{
    "status": "working",
    "confidence": 0.95,
    "details": {
        "tool": "Read",
        "context": "main.py",
        "session_id": "abc123"
    },
    "timestamp": "2026-02-06T12:34:56.789Z"
}
```

---

## 📈 Token 统计

实时追踪 Token 使用情况：

```json
{
    "total": {
        "input": 50000,
        "output": 20000,
        "cache_read": 10000,
        "cache_write": 5000
    },
    "cache_hit_rate": 0.167,
    "average_per_minute": {
        "input": 833.33,
        "output": 333.33
    }
}
```

---

## 🏗️ 技术架构

### v4.0 架构

```
数据源: ~/.claude/projects/**/*.jsonl (官方日志)
   ↓
核心插件: ClaudeLogPlugin (Watchdog + 增量读取 + JSONL 解析)
   ↓
中间件:
  - PrivacyFilter (隐私过滤)
  - TokenStats (Token 统计)
  - StateFusion (状态融合)
   ↓
输出:
  - WebSocketAdapter (ws://8765)
  - HTTPAdapter (http://8080)
  - HistoryAdapter (SQLite)
  - StdoutAdapter (终端)
```

### 核心组件

| 组件 | 文件 | 功能 |
|------|------|------|
| **ClaudeLogPlugin** | `src/plugins/claude_log.py` | 日志监控（核心）|
| **PrivacyFilter** | `src/middleware/privacy.py` | 隐私保护 |
| **TokenStats** | `src/middleware/token_stats.py` | Token 统计 |
| **HistoryAdapter** | `src/adapters/history_adapter.py` | SQLite 存储 |

---

## 📚 文档

- 📘 [CLAUDE.md](./CLAUDE.md) - 完整项目文档
- 📗 [AGENTS.md](./AGENTS.md) - 项目知识库（代码地图）
- 📙 [QUICKSTART.md](./QUICKSTART.md) - 快速开始指南
- 📕 [CONFIG.md](./CONFIG.md) - 配置说明

---

## 🔧 配置

### 最小配置（`config.json`）

```json
{
  "version": "4.0.0",
  "claude": {
    "projects_dir": "auto"
  }
}
```

### 自定义配置

```json
{
  "claude": {
    "projects_dir": "C:\\Users\\YourName\\.claude\\projects"
  },
  "middleware": {
    "privacy_filter": {
      "enabled": true
    }
  },
  "adapters": {
    "websocket": {
      "port": 8765
    },
    "http": {
      "port": 8080
    }
  }
}
```

详细配置请参考 [CONFIG.md](./CONFIG.md)

---

## 🔌 API 文档

### WebSocket API

**连接**: `ws://127.0.0.1:8765`

**消息格式**:
```json
{
    "type": "state_change",
    "data": {
        "status": "working",
        "confidence": 0.95,
        "details": {
            "tool": "Read",
            "context": "main.py"
        }
    }
}
```

### HTTP REST API

#### `GET /api/status`
获取当前状态

#### `GET /api/history`
查询历史事件
- 参数: `start_time`, `end_time`, `limit`

#### `GET /api/tokens`
获取 Token 统计

详细 API 文档请参考 [CLAUDE.md](./CLAUDE.md#api-文档)

---

## 🎨 应用场景

### 1. 桌面宠物 GUI

```
┌─────────────────┐
│  🐱 ClaudeCat   │
│                 │
│  Status: 📖 Reading
│  File: main.py  │
│  Tokens: 5.2K   │
└─────────────────┘
```

### 2. 浏览器插件

在浏览器中实时显示 AI 状态

### 3. 移动端 App

远程监控 AI 编程进度

### 4. 数据统计

分析 Token 使用量、工具调用频率

---

## 📦 依赖

- Python 3.8+
- watchdog - 文件监控
- websockets - WebSocket 服务器
- flask - HTTP 服务器
- flask-cors - CORS 支持

```bash
pip install -r requirements.txt
```

---

## 🔄 版本历史

### v4.0.0 (2026-02-06) - 🚀 重大重构

**核心改动**:
- ✅ 采用日志监控方案（借鉴 PixelHQ-bridge）
- ✅ 弃用系统 API 检测（窗口标题、CPU 阈值）
- ✅ 增加工具级状态检测
- ✅ 增加 Token 统计功能
- ✅ 增加隐私保护机制
- ✅ 增加事件历史存储

**新增功能**:
- 📁 ClaudeLogPlugin（日志监控插件）
- 🔒 PrivacyFilter（隐私过滤器）
- 📊 TokenStats（Token 统计器）
- 💾 HistoryAdapter（SQLite 历史存储）

### v3.1.0 (2026-02-05) - 已归档

**备份位置**: `backup-v3.1/`

---

## 🤝 致谢

本项目的日志监控方案受到 [PixelHQ-bridge](https://github.com/example/pixelhq-bridge) 的启发，感谢其开源贡献。

---

## 📄 许可证

MIT License - 详见 [LICENSE](./LICENSE)

---

## 🔗 链接

- 📦 [GitHub 仓库](https://github.com/example/ai-claudecat)
- 🐛 [问题反馈](https://github.com/example/ai-claudecat/issues)
- 📧 [联系我们](mailto:example@example.com)

---

<div align="center">

**用 AI-ClaudeCat 监控你的 AI 助手 🐱**

Made with ❤️ by AI-ClaudeCat Team

</div>
