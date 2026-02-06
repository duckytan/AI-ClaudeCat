# AI-ClaudeCat v4.0 快速开始

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行应用

```bash
python main.py
```

## 测试核心功能

```bash
python test_v4.py
```

## 配置

编辑 `config.json` 文件：

```json
{
  "version": "4.0.0",
  "claude": {
    "projects_dir": "auto"  # 或指定路径
  },
  "middleware": {
    "privacy_filter": {
      "enabled": true,
      "level": "internal",  # public/internal/full
      "dev_mode": false     # 开发模式：关闭隐私过滤
    }
  }
}
```

## API 使用

### WebSocket 实时推送

```javascript
// 浏览器控制台
const ws = new WebSocket('ws://127.0.0.1:8765');
ws.onmessage = (e) => {
    const event = JSON.parse(e.data);
    console.log('Status:', event.status);
    console.log('Details:', event.details);
};
```

### HTTP REST API

```bash
# 查询当前状态
curl http://127.0.0.1:8080/api/status

# 查询 Token 统计
curl http://127.0.0.1:8080/api/tokens

# 健康检查
curl http://127.0.0.1:8080/api/health
```

## 输出示例

```json
{
  "status": "working",
  "confidence": 0.95,
  "source": "claude_log",
  "timestamp": "2026-02-06T12:34:56.789",
  "details": {
    "event": "tool_use",
    "tool": "Read",
    "context": {
      "file": "main.py"
    },
    "tokens": {
      "input": 1000,
      "output": 500,
      "cache_write": 200,
      "cache_read": 300
    }
  }
}
```

## 8 种状态

| 状态 | 说明 | 触发条件 |
|------|------|---------|
| `unknown` | 未知状态 | 初始状态 |
| `idle` | 空闲 | 等待用户输入 |
| `running` | 运行中 | 接收到用户输入 |
| `thinking` | 思考中 | AI 内部推理 |
| `working` | 工作中 | 读/写文件、搜索 |
| `executing` | 执行中 | 运行 Bash 命令 |
| `error` | 错误 | 工具调用失败 |
| `stopped` | 停止 | 进程关闭 |

## 开发模式

开发模式下，隐私过滤将被关闭，输出完整信息：

```json
{
  "middleware": {
    "privacy_filter": {
      "dev_mode": true
    }
  }
}
```

## 故障排除

### 日志目录未找到

确认 Claude Code 安装正确：
- Windows: `%USERPROFILE%\.claude\projects`
- macOS/Linux: `~/.claude/projects`

### 端口被占用

修改 `config.json` 中的端口：

```json
{
  "adapters": {
    "websocket": {
      "port": 8766
    },
    "http": {
      "port": 8081
    }
  }
}
```

## 下一步

- 查看 [CLAUDE.md](CLAUDE.md) 了解完整架构
- 查看 [AGENTS.md](AGENTS.md) 了解代码地图
- 开发桌面宠物前端，连接 WebSocket
