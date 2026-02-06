# AI-ClaudeCat 快速开始指南

**版本**: v4.0.0  
**预计时间**: 5 分钟

---

## 📦 安装

### 1. 克隆仓库

```bash
git clone https://github.com/example/ai-claudecat.git
cd ai-claudecat
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

**依赖列表**:
- `watchdog` - 文件监控
- `websockets` - WebSocket 服务器
- `flask` - HTTP 服务器
- `flask-cors` - CORS 支持
- `psutil` - 进程监控（可选）

---

## 🚀 运行

### 1. 启动应用

```bash
python main.py
```

### 2. 查看输出

```
=== AI-ClaudeCat v4.0 ===
Status monitoring for Claude Code

✓ Claude Code detected at C:\Users\YourName\.claude\projects
✓ Middleware initialized
✓ WebSocket server on port 8765
✓ HTTP server on port 8080
✓ Privacy filter enabled
✓ History storage enabled

[ClaudeLogPlugin] Started, watching: C:\Users\YourName\.claude\projects
```

**成功！** AI-ClaudeCat 已启动，正在监控 Claude Code 日志。

---

## 🧪 测试

### 方式 1: WebSocket（推荐）

**在浏览器控制台运行**:

```javascript
// 连接 WebSocket
const ws = new WebSocket('ws://127.0.0.1:8765');

// 监听消息
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('=== AI 状态更新 ===');
    console.log('状态:', data.status);
    console.log('置信度:', data.confidence);
    console.log('工具:', data.details?.tool);
    console.log('文件:', data.details?.context);
    console.log('时间:', data.timestamp);
};

// 连接成功
ws.onopen = () => {
    console.log('✓ 已连接到 AI-ClaudeCat');
};

// 连接失败
ws.onerror = (error) => {
    console.error('❌ 连接失败:', error);
};
```

**现在使用 Claude Code，你会看到实时状态更新！**

### 方式 2: HTTP REST API

```bash
# 获取当前状态
curl http://127.0.0.1:8080/api/status

# 查询历史事件（最近 10 条）
curl http://127.0.0.1:8080/api/history?limit=10

# 获取 Token 统计
curl http://127.0.0.1:8080/api/tokens
```

### 方式 3: 终端输出

AI-ClaudeCat 默认会在终端输出状态变化：

```
[2026-02-06 12:34:56] Status: thinking (0.95)
[2026-02-06 12:34:58] Status: working (0.95) - Tool: Read, File: main.py
[2026-02-06 12:35:02] Status: idle (0.85)
```

---

## 📊 示例输出

### WebSocket 消息

```json
{
    "type": "state_change",
    "data": {
        "timestamp": "2026-02-06T12:34:56.789Z",
        "status": "working",
        "confidence": 0.95,
        "source_plugin": "claude_log",
        "details": {
            "method": "log",
            "event": "tool_use",
            "tool": "Read",
            "context": "main.py",
            "session_id": "abc123"
        }
    }
}
```

### HTTP `/api/status` 响应

```json
{
    "status": "working",
    "confidence": 0.95,
    "timestamp": "2026-02-06T12:34:56.789Z",
    "details": {
        "tool": "Read",
        "context": "main.py"
    }
}
```

### HTTP `/api/tokens` 响应

```json
{
    "total": {
        "input": 50000,
        "output": 20000,
        "cache_read": 10000,
        "cache_write": 5000
    },
    "runtime_seconds": 3600,
    "average_per_minute": {
        "input": 833.33,
        "output": 333.33
    },
    "cache_hit_rate": 0.167
}
```

---

## ⚙️ 配置（可选）

### 最小配置

默认配置已可用，无需修改。如需自定义，编辑 `config.json`：

```json
{
  "version": "4.0.0",
  "claude": {
    "projects_dir": "auto"
  }
}
```

### 常用配置

#### 修改端口

```json
{
  "adapters": {
    "websocket": {
      "port": 9000
    },
    "http": {
      "port": 9001
    }
  }
}
```

#### 禁用隐私保护（开发调试）

```json
{
  "middleware": {
    "privacy_filter": {
      "enabled": false
    }
  }
}
```

#### 指定 Claude Code 目录

```json
{
  "claude": {
    "projects_dir": "C:\\Users\\YourName\\.claude\\projects"
  }
}
```

详细配置请参考 [CONFIG.md](./CONFIG.md)

---

## 🎯 监控的状态

AI-ClaudeCat 可以检测 8 种状态：

| 状态 | 描述 | 示例 |
|------|------|------|
| 🟢 **idle** | 空闲 | 等待用户输入 |
| 🔵 **running** | 运行中 | AI 接收到提示词 |
| 🟡 **thinking** | 思考中 | AI 内部推理 |
| 🟠 **working** | 工作中 | 读/写文件、搜索 |
| 🔴 **executing** | 执行中 | 运行 Bash 命令 |
| ⚪ **waiting** | 等待 | 等待用户确认 |
| ❌ **error** | 错误 | 工具调用失败 |
| ⚫ **stopped** | 停止 | Claude Code 关闭 |

---

## 🛠️ 监控的工具

| 工具 | 状态 | 描述 |
|------|------|------|
| `Read` | working | 读取文件 |
| `Write` | working | 写入文件 |
| `Edit` | working | 编辑文件 |
| `Bash` | executing | 执行命令 |
| `Grep` | working | 搜索代码 |
| `Glob` | working | 文件匹配 |
| `WebFetch` | working | 网络请求 |
| `WebSearch` | working | 网络搜索 |
| `Task` | working | 派生子 Agent |
| `TodoWrite` | working | 写入待办 |

---

## 🔧 常见问题

### Q1: 找不到 Claude Code？

**错误**: `❌ Claude Code not found!`

**解决方案**:

1. 确认 Claude Code 已安装
2. 检查项目目录是否存在：
   ```bash
   # Windows
   dir "C:\Users\YourName\.claude\projects"
   
   # macOS/Linux
   ls ~/.claude/projects
   ```
3. 手动指定路径（编辑 `config.json`）：
   ```json
   {
     "claude": {
       "projects_dir": "C:\\Users\\YourName\\.claude\\projects"
     }
   }
   ```

### Q2: WebSocket 连接失败？

**错误**: `WebSocket connection failed`

**解决方案**:

1. 检查 AI-ClaudeCat 是否正在运行
2. 检查端口是否被占用：
   ```bash
   # Windows
   netstat -ano | findstr :8765
   
   # macOS/Linux
   lsof -i :8765
   ```
3. 尝试修改端口（编辑 `config.json`）

### Q3: 没有收到状态更新？

**可能原因**:

1. Claude Code 没有运行
2. Claude Code 没有活动（正在等待用户输入）
3. 日志文件没有变化

**测试方法**:

在 Claude Code 中输入一个简单的提示词：
```
请读取 README.md 文件
```

你应该会看到状态变化：
```
idle → running → thinking → working (Read) → idle
```

---

## 📚 下一步

### 1. 查看完整文档

- 📘 [CLAUDE.md](./CLAUDE.md) - 完整项目文档
- 📗 [AGENTS.md](./AGENTS.md) - 项目知识库
- 📕 [CONFIG.md](./CONFIG.md) - 配置说明

### 2. 构建前端应用

使用 WebSocket API 构建你的桌面宠物 GUI：

```javascript
// 示例：简单的状态显示
const ws = new WebSocket('ws://127.0.0.1:8765');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    // 更新 UI
    document.getElementById('status').textContent = data.status;
    document.getElementById('tool').textContent = data.details?.tool || '-';
    document.getElementById('file').textContent = data.details?.context || '-';
    
    // 更新宠物动画
    updatePetAnimation(data.status);
};
```

### 3. 数据分析

查询历史数据，分析 AI 的工作模式：

```bash
# 导出历史数据
sqlite3 data/history.db ".dump" > history.sql

# 统计工具使用频率
sqlite3 data/history.db "SELECT 
    json_extract(details, '$.tool') as tool,
    COUNT(*) as count
FROM events
WHERE tool IS NOT NULL
GROUP BY tool
ORDER BY count DESC;"
```

---

## 🎨 应用场景

### 场景 1: 桌面宠物

创建一个可爱的桌面宠物，实时显示 AI 状态。

**推荐技术栈**:
- Electron + React
- Python + PyQt
- Tauri + Vue

### 场景 2: 浏览器插件

在浏览器中显示 AI 工作状态。

**推荐技术栈**:
- Chrome Extension API
- WebSocket 连接

### 场景 3: 移动端 App

远程监控 AI 编程进度。

**推荐技术栈**:
- React Native
- Flutter

### 场景 4: 数据统计

分析 Token 使用量、工具调用频率。

**推荐工具**:
- SQLite Browser
- Python + Pandas
- Jupyter Notebook

---

## 💡 提示

1. **实时性**: AI-ClaudeCat 的状态更新是实时的（< 100ms 延迟）
2. **隐私**: 默认启用隐私保护，只输出元数据
3. **历史**: 所有事件都会保存到 SQLite 数据库
4. **Token**: 可以实时追踪 Token 使用量
5. **工具级**: 不仅知道"工作中"，还知道在"读文件"还是"写代码"

---

## 🎉 开始使用

现在你已经完成了 AI-ClaudeCat 的快速开始！

**开始监控你的 AI 助手吧！** 🐱

---

**需要帮助？**
- 📖 查看 [完整文档](./CLAUDE.md)
- 🐛 [提交问题](https://github.com/example/ai-claudecat/issues)
- 💬 [加入社区](https://discord.gg/example)

---

**最后更新**: 2026-02-06  
**版本**: v4.0.0
