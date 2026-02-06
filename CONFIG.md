# AI-ClaudeCat 配置说明

**版本**: v4.0.0  
**最后更新**: 2026-02-06

---

## 📋 目录

1. [配置文件位置](#配置文件位置)
2. [完整配置示例](#完整配置示例)
3. [配置项详解](#配置项详解)
4. [使用场景](#使用场景)
5. [常见问题](#常见问题)

---

## 配置文件位置

配置文件位于项目根目录：

```
AI-ClaudeCat/
└── config.json  ← 配置文件
```

---

## 完整配置示例

### 最小配置

```json
{
  "version": "4.0.0",
  "claude": {
    "projects_dir": "auto"
  }
}
```

### 完整配置

```json
{
  "version": "4.0.0",
  "description": "AI-ClaudeCat configuration for v4.0",
  
  "claude": {
    "projects_dir": "auto",
    "watch_debounce_ms": 100,
    "session_ttl_minutes": 10
  },
  
  "plugins": {
    "claude_log": {
      "enabled": true,
      "check_interval": 0.5,
      "priority": 10,
      "show_all_errors": false
    }
  },
  
  "middleware": {
    "privacy_filter": {
      "enabled": true,
      "whitelist": [
        "method",
        "event",
        "tool",
        "context",
        "session_id",
        "status",
        "confidence",
        "tokens",
        "agent_type",
        "pattern",
        "description"
      ]
    },
    "token_stats": {
      "enabled": true
    }
  },
  
  "adapters": {
    "websocket": {
      "enabled": true,
      "port": 8765,
      "host": "127.0.0.1"
    },
    "http": {
      "enabled": true,
      "port": 8080,
      "host": "127.0.0.1",
      "cors": true
    },
    "stdout": {
      "enabled": true,
      "format": "simple"
    },
    "history": {
      "enabled": true,
      "db_path": "data/history.db",
      "max_events": 10000
    }
  },
  
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

---

## 配置项详解

### 1. Claude 配置

#### `claude.projects_dir`

**类型**: `string`  
**默认值**: `"auto"`  
**描述**: Claude Code 项目目录位置

**可选值**:
- `"auto"` - 自动检测（推荐）
  - Windows: `C:\Users\<YourName>\.claude\projects`
  - macOS/Linux: `~/.claude/projects`
- 绝对路径 - 手动指定路径
  - 示例: `"C:\\Users\\John\\.claude\\projects"`
  - 示例: `"/home/john/.claude/projects"`

**示例**:
```json
{
  "claude": {
    "projects_dir": "auto"
  }
}
```

#### `claude.watch_debounce_ms`

**类型**: `integer`  
**默认值**: `100`  
**单位**: 毫秒  
**描述**: 文件变化防抖时间

文件监控会在指定时间内合并多次变化事件，避免重复处理。

**推荐值**:
- 快速响应: `50` - 更实时，但 CPU 占用稍高
- 平衡: `100` - 推荐
- 节能: `200` - 降低 CPU 占用

**示例**:
```json
{
  "claude": {
    "watch_debounce_ms": 100
  }
}
```

#### `claude.session_ttl_minutes`

**类型**: `integer`  
**默认值**: `10`  
**单位**: 分钟  
**描述**: 会话存活时间

超过此时间未活动的会话将被停止追踪。

**推荐值**: `5` - `30`

**示例**:
```json
{
  "claude": {
    "session_ttl_minutes": 10
  }
}
```

---

### 2. 插件配置

#### `plugins.claude_log`

**描述**: ClaudeLogPlugin（日志监控插件）配置

##### `enabled`

**类型**: `boolean`  
**默认值**: `true`  
**描述**: 是否启用插件

##### `check_interval`

**类型**: `float`  
**默认值**: `0.5`  
**单位**: 秒  
**描述**: 检查间隔（保留字段，当前由 watchdog 触发）

##### `priority`

**类型**: `integer`  
**默认值**: `10`  
**描述**: 插件优先级（数值越大优先级越高）

##### `show_all_errors`

**类型**: `boolean`  
**默认值**: `false`  
**描述**: 是否显示所有错误（包括临时性错误）

**可选值**:
- `false` - 只显示重大错误（推荐）
  - 自动过滤：502、429、503、504、超时等临时性错误
  - 这些错误会在控制台显示 `[WARNING]`，但不触发 `[ERROR]` 状态
  - Claude Code 会自动重试，无需用户干预
- `true` - 显示所有错误（调试模式）
  - 包括所有临时性错误
  - 用于开发调试

**详细说明**: 查看 [docs/错误过滤说明.md](./docs/错误过滤说明.md)

**示例**:
```json
{
  "plugins": {
    "claude_log": {
      "enabled": true,
      "check_interval": 0.5,
      "priority": 10,
      "show_all_errors": false
    }
  }
}
```

---

### 3. 中间件配置

#### `middleware.privacy_filter`

**描述**: 隐私过滤器配置

##### `enabled`

**类型**: `boolean`  
**默认值**: `true`  
**描述**: 是否启用隐私过滤

##### `whitelist`

**类型**: `array<string>`  
**默认值**: 见下方  
**描述**: 允许输出的字段白名单

**默认白名单**:
```json
[
  "method",       // 检测方法
  "event",        // 事件类型
  "tool",         // 工具名称
  "context",      // 安全上下文（仅文件名）
  "session_id",   // 会话 ID
  "status",       // 状态
  "confidence",   // 置信度
  "tokens",       // Token 使用量
  "agent_type",   // Agent 类型
  "pattern",      // 搜索模式
  "description"   // 描述信息
]
```

**过滤规则**:
- `file_path` → 只保留文件名（`os.path.basename`）
- `command`, `cmd`, `bash_command` → 不输出
- `content`, `text`, `code`, `output` → 不输出
- 白名单中的字段 → 原样输出
- 其他字段 → 默认输出（可配置）

**示例**:
```json
{
  "middleware": {
    "privacy_filter": {
      "enabled": true,
      "whitelist": [
        "method",
        "event",
        "tool",
        "context"
      ]
    }
  }
}
```

#### `middleware.token_stats`

**描述**: Token 统计器配置

##### `enabled`

**类型**: `boolean`  
**默认值**: `true`  
**描述**: 是否启用 Token 统计

**示例**:
```json
{
  "middleware": {
    "token_stats": {
      "enabled": true
    }
  }
}
```

---

### 4. 输出适配器配置

#### `adapters.websocket`

**描述**: WebSocket 服务器配置

##### `enabled`

**类型**: `boolean`  
**默认值**: `true`  
**描述**: 是否启用 WebSocket 服务器

##### `port`

**类型**: `integer`  
**默认值**: `8765`  
**描述**: WebSocket 服务器端口

##### `host`

**类型**: `string`  
**默认值**: `"127.0.0.1"`  
**描述**: WebSocket 服务器主机

**可选值**:
- `"127.0.0.1"` - 仅本地访问（推荐）
- `"0.0.0.0"` - 允许外部访问（注意安全）

**示例**:
```json
{
  "adapters": {
    "websocket": {
      "enabled": true,
      "port": 8765,
      "host": "127.0.0.1"
    }
  }
}
```

#### `adapters.http`

**描述**: HTTP REST API 服务器配置

##### `enabled`

**类型**: `boolean`  
**默认值**: `true`  
**描述**: 是否启用 HTTP 服务器

##### `port`

**类型**: `integer`  
**默认值**: `8080`  
**描述**: HTTP 服务器端口

##### `host`

**类型**: `string`  
**默认值**: `"127.0.0.1"`  
**描述**: HTTP 服务器主机

##### `cors`

**类型**: `boolean`  
**默认值**: `true`  
**描述**: 是否启用 CORS（跨域资源共享）

**示例**:
```json
{
  "adapters": {
    "http": {
      "enabled": true,
      "port": 8080,
      "host": "127.0.0.1",
      "cors": true
    }
  }
}
```

#### `adapters.stdout`

**描述**: 标准输出适配器配置

##### `enabled`

**类型**: `boolean`  
**默认值**: `true`  
**描述**: 是否启用终端输出

##### `format`

**类型**: `string`  
**默认值**: `"simple"`  
**描述**: 输出格式

**可选值**:
- `"simple"` - 简洁格式
- `"detailed"` - 详细格式
- `"json"` - JSON 格式

**示例**:
```json
{
  "adapters": {
    "stdout": {
      "enabled": true,
      "format": "simple"
    }
  }
}
```

#### `adapters.history`

**描述**: SQLite 历史存储适配器配置

##### `enabled`

**类型**: `boolean`  
**默认值**: `true`  
**描述**: 是否启用历史存储

##### `db_path`

**类型**: `string`  
**默认值**: `"data/history.db"`  
**描述**: SQLite 数据库文件路径

##### `max_events`

**类型**: `integer`  
**默认值**: `10000`  
**描述**: 最大事件数量（超过后自动删除旧记录）

**示例**:
```json
{
  "adapters": {
    "history": {
      "enabled": true,
      "db_path": "data/history.db",
      "max_events": 10000
    }
  }
}
```

---

### 5. 日志配置

#### `logging.level`

**类型**: `string`  
**默认值**: `"INFO"`  
**描述**: 日志级别

**可选值**:
- `"DEBUG"` - 调试信息
- `"INFO"` - 常规信息（推荐）
- `"WARNING"` - 警告信息
- `"ERROR"` - 错误信息
- `"CRITICAL"` - 严重错误

#### `logging.format`

**类型**: `string`  
**默认值**: `"%(asctime)s - %(name)s - %(levelname)s - %(message)s"`  
**描述**: 日志格式

**示例**:
```json
{
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

---

## 使用场景

### 场景 1: 开发调试

**需求**: 最大化日志输出，便于调试

```json
{
  "claude": {
    "projects_dir": "auto",
    "watch_debounce_ms": 50
  },
  "plugins": {
    "claude_log": {
      "show_all_errors": true
    }
  },
  "middleware": {
    "privacy_filter": {
      "enabled": false
    }
  },
  "adapters": {
    "stdout": {
      "enabled": true,
      "format": "detailed"
    }
  },
  "logging": {
    "level": "DEBUG"
  }
}
```

### 场景 2: 生产环境

**需求**: 启用隐私保护，只输出必要信息

```json
{
  "claude": {
    "projects_dir": "auto"
  },
  "middleware": {
    "privacy_filter": {
      "enabled": true,
      "whitelist": [
        "status",
        "confidence",
        "tool",
        "tokens"
      ]
    }
  },
  "adapters": {
    "stdout": {
      "enabled": false
    },
    "websocket": {
      "enabled": true
    }
  },
  "logging": {
    "level": "WARNING"
  }
}
```

### 场景 3: 数据收集

**需求**: 收集历史数据，用于分析

```json
{
  "claude": {
    "projects_dir": "auto"
  },
  "adapters": {
    "history": {
      "enabled": true,
      "db_path": "data/history.db",
      "max_events": 100000
    },
    "websocket": {
      "enabled": false
    },
    "http": {
      "enabled": false
    }
  }
}
```

### 场景 4: 远程访问

**需求**: 允许外部设备访问（注意安全）

```json
{
  "adapters": {
    "websocket": {
      "enabled": true,
      "port": 8765,
      "host": "0.0.0.0"
    },
    "http": {
      "enabled": true,
      "port": 8080,
      "host": "0.0.0.0",
      "cors": true
    }
  }
}
```

**⚠️ 安全提示**: 外部访问时建议：
- 使用防火墙限制访问 IP
- 启用隐私过滤
- 考虑添加身份验证（未来功能）

---

## 常见问题

### Q1: 找不到 Claude Code 项目目录？

**症状**: 启动时提示 "Claude Code not found"

**解决方案**:

1. 检查 Claude Code 是否已安装
2. 手动指定路径：
   ```json
   {
     "claude": {
       "projects_dir": "C:\\Users\\YourName\\.claude\\projects"
     }
   }
   ```
3. 确认路径存在：
   ```bash
   # Windows
   dir "C:\Users\YourName\.claude\projects"
   
   # macOS/Linux
   ls ~/.claude/projects
   ```

### Q2: WebSocket 连接失败？

**症状**: 前端无法连接 WebSocket

**解决方案**:

1. 检查端口是否被占用：
   ```bash
   # Windows
   netstat -ano | findstr :8765
   
   # macOS/Linux
   lsof -i :8765
   ```

2. 修改端口：
   ```json
   {
     "adapters": {
       "websocket": {
         "port": 9000
       }
     }
   }
   ```

3. 检查防火墙设置

### Q3: 历史数据库过大？

**症状**: `data/history.db` 文件很大

**解决方案**:

1. 减小 `max_events`：
   ```json
   {
     "adapters": {
       "history": {
         "max_events": 1000
       }
     }
   }
   ```

2. 手动清理：
   ```bash
   rm data/history.db
   # 重启应用，会自动创建新数据库
   ```

3. 定期导出和清理：
   ```bash
   sqlite3 data/history.db "DELETE FROM events WHERE timestamp < datetime('now', '-7 days');"
   ```

### Q4: CPU 占用过高？

**症状**: AI-ClaudeCat 占用 CPU 过高

**解决方案**:

1. 增加防抖时间：
   ```json
   {
     "claude": {
       "watch_debounce_ms": 200
     }
   }
   ```

2. 禁用不需要的适配器：
   ```json
   {
     "adapters": {
       "stdout": {
         "enabled": false
       }
     }
   }
   ```

3. 减少会话追踪时间：
   ```json
   {
     "claude": {
       "session_ttl_minutes": 5
     }
   }
   ```

### Q5: 如何禁用隐私保护（开发调试）？

**解决方案**:

```json
{
  "middleware": {
    "privacy_filter": {
      "enabled": false
    }
  }
}
```

**⚠️ 警告**: 禁用隐私保护后，输出会包含文件路径、命令等敏感信息，不建议在生产环境使用。

---

## 配置验证

可以使用以下 Python 脚本验证配置文件：

```python
import json

# 读取配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 验证必填项
required_fields = ['version', 'claude']
for field in required_fields:
    if field not in config:
        print(f"❌ 缺少必填项: {field}")
    else:
        print(f"✓ 找到: {field}")

# 验证 Claude 配置
if 'projects_dir' not in config.get('claude', {}):
    print("❌ 缺少 claude.projects_dir")
else:
    print(f"✓ Claude 目录: {config['claude']['projects_dir']}")

print("\n配置验证完成")
```

---

## 参考资料

- [CLAUDE.md](./CLAUDE.md) - 完整项目文档
- [AGENTS.md](./AGENTS.md) - 项目知识库
- [README.md](./README.md) - 项目总览

---

**最后更新**: 2026-02-06  
**版本**: v4.0.0
