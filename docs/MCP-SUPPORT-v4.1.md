# MCP 工具支持 - v4.1

## 概述

AI-ClaudeCat v4.1 现已完全支持 MCP (Model Context Protocol) 工具监控！

## MCP 工具格式

### 工具名称格式
```
mcp__<server-name>__<tool-name>
```

**示例**：
- `mcp__open-websearch__search` - 网络搜索工具
- `mcp__filesystem__read` - 文件系统读取
- `mcp__database__query` - 数据库查询

### 事件类型

#### 1. 工具调用 (tool_use)
```json
{
  "type": "assistant",
  "content": [
    {
      "type": "tool_use",
      "name": "mcp__open-websearch__search",
      "input": {
        "query": "search term",
        "engines": ["duckduckgo", "bing"]
      }
    }
  ]
}
```

**输出**：
```
[claude_log] [MCP] Tool: search (server: open-websearch)
[14:00:00] [WORKING] claude_log (90%) - MCP: search
```

#### 2. 进度事件 (progress)

**Started**：
```json
{
  "type": "progress",
  "data": {
    "type": "mcp_progress",
    "status": "started",
    "serverName": "open-websearch",
    "toolName": "search"
  }
}
```

**输出**：
```
[claude_log] [MCP] Started: search (server: open-websearch)
[14:00:00] [WORKING] claude_log (85%)
```

**Completed**：
```json
{
  "type": "progress",
  "data": {
    "type": "mcp_progress",
    "status": "completed",
    "serverName": "open-websearch",
    "toolName": "search",
    "elapsedTimeMs": 42324
  }
}
```

**输出**：
```
[claude_log] [MCP] Completed: search (42324ms)
[14:00:42] [WORKING] claude_log (80%)
```

## 状态映射

| MCP 工具 | 状态 | 置信度 |
|---------|------|--------|
| 任意 MCP 工具 | `WORKING` | 0.90 |
| MCP 进度 (started) | `WORKING` | 0.85 |
| MCP 进度 (completed) | `WORKING` | 0.80 |

## 事件详情

MCP 工具调用的事件详情包含：

```python
{
    'event': 'tool_use',
    'tool': 'mcp__open-websearch__search',
    'mcp': {
        'server': 'open-websearch',
        'tool': 'search'
    },
    'context': {
        # 安全上下文（不包含敏感内容）
    }
}
```

## 测试

### 运行测试脚本
```bash
cd d:/AI-Project/AI-ClaudeCat
python test_mcp_detection.py
```

### 预期输出
```
============================================================
测试 MCP 工具检测
============================================================

1. 工具名称: mcp__open-websearch__search
   是否 MCP: True
   服务器: open-websearch
   工具: search

2. 事件类型
   - tool_use 事件: {...}
   - progress 事件 (started): {...}
   - progress 事件 (completed): {...}

============================================================
[OK] MCP tool detection logic ready
============================================================
```

## 实战示例

### Claude Code 调用 MCP 工具
```
[14:00:00] [IDLE] claude_log (90%)
[14:00:01] [RUNNING] claude_log (95%)            # 用户输入
[14:00:02] [THINKING] claude_log (95%)           # AI 思考
[14:00:03] [WORKING] claude_log (90%)            # 开始工具调用
[claude_log] [MCP] Tool: search (server: open-websearch)
[claude_log] [MCP] Started: search (server: open-websearch)
[14:00:05] [WORKING] claude_log (85%)            # 工具运行中
[claude_log] [MCP] Completed: search (42324ms)
[14:00:47] [WORKING] claude_log (80%)            # 工具完成
[14:00:48] [IDLE] claude_log (90%)               # 回到空闲
```

## WebSocket 输出

```json
{
  "status": "working",
  "confidence": 0.90,
  "plugin": "claude_log",
  "timestamp": "2026-02-06T14:00:03.123Z",
  "details": {
    "event": "tool_use",
    "tool": "mcp__open-websearch__search",
    "mcp": {
      "server": "open-websearch",
      "tool": "search"
    }
  }
}
```

## HTTP API 查询

```bash
# 查询当前状态
curl http://127.0.0.1:8080/api/status

# 响应
{
  "status": "working",
  "confidence": 0.90,
  "details": {
    "event": "tool_use",
    "mcp": {
      "server": "open-websearch",
      "tool": "search"
    }
  }
}
```

## 常见 MCP 服务器

| 服务器名称 | 工具示例 | 描述 |
|-----------|---------|------|
| `open-websearch` | `search` | 网络搜索 |
| `filesystem` | `read`, `write` | 文件系统操作 |
| `database` | `query`, `execute` | 数据库操作 |
| `git` | `commit`, `push` | Git 操作 |
| `docker` | `run`, `stop` | Docker 容器管理 |

## 配置

无需额外配置！MCP 工具支持已内置在 v4.1 中。

## 更新日志

**v4.1.0** (2026-02-06)
- ✅ 添加 MCP 工具名称解析
- ✅ 添加 `progress` 事件处理
- ✅ 添加调试输出（`[MCP]` 前缀）
- ✅ 自动识别所有 `mcp__*` 工具

---

**文档版本**: v4.1.0  
**更新日期**: 2026-02-06  
**状态**: ✅ 已测试并验证
