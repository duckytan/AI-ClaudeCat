# v3.1 备份说明

**备份时间**: 2026-02-06  
**原因**: v4.0 重大重构 - 采用日志监控方案

---

## 备份内容

### 源代码

- `src/claude_code.py` - 旧的 ClaudeCodePlugin（窗口+进程+文件融合检测）
- `src/process.py` - ProcessPlugin（CPU 阈值判断）
- `src/window.py` - WindowPlugin（窗口标题检测）

### 文档

- `docs/完整架构设计.md` - v3.0 总体架构
- `docs/插件化架构详细设计.md` - v3.1 插件设计
- `docs/PixelHQ-vs-ClaudeCat对比分析.md` - 对比分析
- `docs/重构方案-借鉴PixelHQ.md` - 重构方案
- `docs/重构任务清单.md` - 任务清单

### 其他项目

- `Desktop-Pixel-Pet/` - 桌面宠物项目（参考）
- `MiniPet/` - 小程序宠物项目（参考）
- `PixelHQ-bridge/` - 参考项目（日志监控方案来源）

---

## v3.1 存在的问题

### 1. 窗口标题检测不可靠

**问题**:
- Claude Code 窗口标题不包含状态信息
- 窗口标题是静态的（如 "Claude Code - project-name"）
- 无法区分 idle/thinking/working
- 误匹配其他窗口

### 2. CPU 阈值判断不准确

**问题**:
- 阈值是猜测的，无数据支撑
- AI 思考时 CPU 可能很低（等待 API）
- 后台进程干扰
- 无法区分 idle 和 waiting for user

### 3. 文件活动检测无效

**问题**:
- `on_file_activity()` 从未被调用（无文件监控插件）
- 3 秒阈值是随意设定的
- 无法区分读操作和写操作

---

## v4.0 改进

### 核心改动

1. **采用日志监控方案**
   - 数据源: `~/.claude/projects/**/*.jsonl`（官方日志）
   - 增量读取（记录文件位置）
   - JSONL 解析（官方格式，稳定可靠）

2. **工具级状态检测**
   - 不仅知道"工作中"，还知道在"读文件"还是"写代码"
   - 支持 13+ 种工具（Read/Write/Bash/Grep/Task...）

3. **Token 统计**
   - 实时追踪 Token 使用量
   - 缓存命中率计算

4. **隐私保护**
   - 白名单过滤（只输出元数据）
   - 文件路径 → 文件名
   - 命令/内容 → 不输出

5. **事件历史**
   - SQLite 数据库存储
   - 时间范围查询
   - 统计分析接口

---

## 保留的功能

### WindowDetector（保留但不实装）

**位置**: `src/utils/window_detector.py`

**用途**:
- 未来的自动进程发现
- 自动绑定进程（无需手动配置）
- 多实例监控

**状态**: 独立工具模块，不集成到主流程

---

## 恢复方法

如果需要恢复 v3.1 代码：

```bash
# 1. 从备份恢复
cp backup-v3.1/src/* src/apps/
cp backup-v3.1/src/* src/plugins/

# 2. 恢复文档
cp backup-v3.1/docs/* docs/

# 3. 切换到 v3.1 分支（如果有）
git checkout v3.1
```

---

## 参考

- [v4.0 重构方案](重构方案-借鉴PixelHQ.md)
- [PixelHQ 对比分析](PixelHQ-vs-ClaudeCat对比分析.md)
- [重构任务清单](重构任务清单.md)

---

**备份位置**: `backup-v3.1/`  
**新版本**: v4.0.0  
**重构理由**: 采用成熟的日志监控方案，提高可靠性和精度
