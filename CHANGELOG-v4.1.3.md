# 📋 Changelog v4.1.3

**发布日期**: 2026-02-06  
**版本**: v4.1.3  
**类型**: 实验性功能 - 进程监控

---

## ✨ **新增功能**

### **🧪 Claude Code 进程监控（实验性）**

#### **核心能力**
- ✅ **进程启动检测** - 检测 `claude` 命令执行
- ✅ **进程退出检测** - 检测 `exit` 命令退出
- ✅ **多进程支持** - 同时监控多个 Claude Code 实例
- ✅ **跨平台** - Windows、macOS、Linux 通用

#### **技术实现**
- 🔍 **ProcessMonitor** - 基于 `psutil` 的进程检测
- 🔌 **ClaudeProcessPlugin** - 插件接口封装
- ⚙️ **配置驱动** - 可配置检测间隔和优先级

---

## 🛠️ **技术实现**

### **新增文件**

| 文件 | 描述 |
|------|------|
| `src/utils/process_monitor.py` | 进程监控核心逻辑 |
| `src/plugins/claude_process.py` | Claude Code 进程监控插件 |
| `test_process_monitor.py` | 进程监控测试脚本 |
| `docs/PROCESS-MONITORING.md` | 进程监控详细文档 |

### **配置更新**

**`config.json`**:
```json
{
  "plugins": {
    "claude_process": {
      "enabled": true,        // 🆕 启用进程监控
      "check_interval": 1.0,   // 🆕 检查间隔（秒）
      "priority": 1            // 🆕 优先级（1=最高）
    }
  }
}
```

---

## 🎯 **解决的问题**

### **原有方案限制**
- ❌ 无法检测 `claude` 命令执行
- ❌ 无法检测 `exit` 退出命令
- ❌ 只能监控会话内部活动

### **新方案优势**
- ✅ 直接检测进程生命周期
- ✅ 实时响应启动/退出
- ✅ 与日志监控完美互补

---

## 📊 **事件输出**

### **启动事件**
```json
{
  "status": "running",
  "confidence": 0.95,
  "details": {
    "event": "process_start",
    "pid": 12345,
    "command_line": "/usr/local/bin/claude",
    "message": "Claude Code 进程启动 (PID: 12345)"
  }
}
```

### **退出事件**
```json
{
  "status": "stopped", 
  "confidence": 0.95,
  "details": {
    "event": "process_exit",
    "pid": 12345,
    "message": "Claude Code 进程退出 (PID: 12345)"
  }
}
```

---

## 🚀 **使用方法**

### **1. 启用功能**
编辑 `config.json`，设置 `"claude_process.enabled": true`

### **2. 重启应用**
```bash
python main.py
```

### **3. 测试验证**
```bash
python test_process_monitor.py
```

### **4. 观察输出**
```
[claude_process] 🚀 Claude Code 启动 (PID: 12345)
[claude_process] 🛑 Claude Code 退出 (PID: 12345)
```

---

## ⚙️ **配置参数**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | boolean | `false` | 是否启用进程监控 |
| `check_interval` | number | `1.0` | 检查间隔（秒） |
| `priority` | number | `1` | 插件优先级 |

---

## ⚠️ **注意事项**

### **资源占用**
- 🔄 **CPU 占用** - 1秒轮询（可配置）
- 💾 **内存占用** - 约 2-5MB
- 📦 **依赖库** - `psutil`（已包含）

### **权限要求**
- 🔒 **进程信息读取权限** - 需要 psutil 权限
- 🖥️ **系统调用** - 访问 /proc 或等效接口

---

## 🔧 **故障排除**

### **无法检测启动**
```bash
# 检查 Claude 安装
which claude
claude --version

# 降低检查间隔
"check_interval": 0.5
```

### **性能影响**
```json
{
  "claude_process": {
    "check_interval": 2.0  // 增加到 2 秒
  }
}
```

---

## 🧪 **测试状态**

### **已测试平台**
- ✅ **Windows 11** - Python 3.9+
- 🔄 **macOS** - 理论支持
- 🔄 **Linux** - 理论支持

### **测试用例**
- ✅ 单个 Claude Code 实例
- ✅ 多个 Claude Code 实例
- ✅ 进程意外崩溃
- ✅ 正常退出和强制退出

---

## 📈 **未来规划**

### **v4.2.0 计划**
- 🎯 **配置化检测规则** - 用户自定义进程匹配
- 🔍 **进程详细信息** - CPU、内存使用情况
- 📊 **启动统计** - 记录启动次数和时长
- ⚡ **事件驱动** - 使用系统事件替代轮询

---

## 🎊 **总结**

### **价值**
1. **完整监控覆盖** - 从启动到退出的完整生命周期
2. **用户体验提升** - 实时响应 Claude Code 状态变化
3. **技术探索** - 为更多系统监控功能奠定基础

### **状态**
- 🧪 **实验性功能** - 欢迎反馈
- 🔧 **持续改进** - 根据用户反馈优化
- 📚 **文档完善** - 详细的使用指南和故障排除

---

## 📚 **相关文档**

- [进程监控详细文档](./docs/PROCESS-MONITORING.md) - 完整技术文档
- [配置说明](./CONFIG.md) - 完整配置指南
- [工具命名分析](./docs/TOOL-NAMING-ANALYSIS.md) - 27 种工具详解

---

**版本**: v4.1.3  
**状态**: 🧪 实验性功能  
**最后更新**: 2026-02-06