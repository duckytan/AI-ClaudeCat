# 🔍 PixelHQ-bridge 工具分类方案分析

**分析日期**: 2026-02-06  
**对比项目**: AI-ClaudeCat vs PixelHQ-bridge  
**核心问题**: 工具映射是用硬编码还是正则匹配？

---

## 📊 **一、PixelHQ-bridge 的实现方案**

### **1. 工具分类策略**

PixelHQ-bridge 使用 **硬编码 + 分类映射** 的方式：

```typescript
// src/config.ts (Lines 118-145)

export const ToolCategory = {
  FILE_READ: 'file_read',
  FILE_WRITE: 'file_write',
  TERMINAL: 'terminal',
  SEARCH: 'search',
  PLAN: 'plan',
  COMMUNICATE: 'communicate',
  SPAWN_AGENT: 'spawn_agent',
  NOTEBOOK: 'notebook',
  OTHER: 'other',
} as const;

export const TOOL_TO_CATEGORY: Record<string, ToolMapping> = {
  Read:            { category: ToolCategory.FILE_READ,    detail: 'read' },
  Write:           { category: ToolCategory.FILE_WRITE,   detail: 'write' },
  Edit:            { category: ToolCategory.FILE_WRITE,   detail: 'edit' },
  Bash:            { category: ToolCategory.TERMINAL,     detail: 'bash' },
  Grep:            { category: ToolCategory.SEARCH,       detail: 'grep' },
  Glob:            { category: ToolCategory.SEARCH,       detail: 'glob' },
  WebFetch:        { category: ToolCategory.SEARCH,       detail: 'web_fetch' },
  WebSearch:       { category: ToolCategory.SEARCH,       detail: 'web_search' },
  Task:            { category: ToolCategory.SPAWN_AGENT,  detail: 'task' },
  TodoWrite:       { category: ToolCategory.PLAN,         detail: 'todo' },
  EnterPlanMode:   { category: ToolCategory.PLAN,         detail: 'enter_plan' },
  ExitPlanMode:    { category: ToolCategory.PLAN,         detail: 'exit_plan' },
  AskUserQuestion: { category: ToolCategory.COMMUNICATE,  detail: 'ask_user' },
  NotebookEdit:    { category: ToolCategory.NOTEBOOK,     detail: 'notebook' },
};
```

---

### **2. 使用方式**

```typescript
// src/adapters/claude-code.ts (Lines 178-183)

function buildToolStartedEvent(..., block: ToolUseBlock): PixelEvent {
  const toolName = block.name;
  
  // 查找映射，如果不存在则使用默认分类
  const mapping = TOOL_TO_CATEGORY[toolName] || {
    category: ToolCategory.OTHER,
    detail: toolName,
  };

  return createToolEvent(sessionId, agentId, timestamp, {
    tool: mapping.category,      // 分类（用于前端过滤、图标）
    detail: mapping.detail,       // 具体工具名（用于显示）
    status: 'started',
    toolUseId: block.id,
    context: extractSafeContext(toolName, block.input),
  });
}
```

---

### **3. 上下文提取（隐私保护）**

```typescript
// src/adapters/claude-code.ts (Lines 193-223)

function extractSafeContext(toolName: string, input: Record<string, unknown> | null): string | null {
  if (!input) return null;

  switch (toolName) {
    case 'Read':
    case 'Write':
    case 'Edit':
      return toBasename(input.file_path as string);  // 只返回文件名

    case 'Bash':
      return (input.description as string) || null;  // 只返回描述，不返回命令

    case 'Grep':
      return (input.pattern as string) || null;      // 只返回搜索模式

    case 'Glob':
      return (input.pattern as string) || null;

    case 'Task':
      return (input.subagent_type as string) || null;

    case 'TodoWrite':
      return Array.isArray(input.todos) ? `${input.todos.length} items` : null;

    case 'NotebookEdit':
      return toBasename(input.notebook_path as string);

    default:
      return null;  // 未知工具，不提取任何上下文
  }
}
```

---

### **4. 关键设计原则**

| 原则 | 说明 | 代码体现 |
|------|------|---------|
| **硬编码映射** | 不使用正则 | `TOOL_TO_CATEGORY` 是静态对象 |
| **默认分类** | 未知工具归为 `OTHER` | `|| { category: ToolCategory.OTHER, ... }` |
| **语义分类** | 按功能而非名称分类 | `FILE_READ`, `FILE_WRITE`, `TERMINAL` 等 |
| **隐私优先** | 只提取安全上下文 | `toBasename()`, 不返回完整路径/命令 |
| **可扩展** | 新工具自动归为 `OTHER` | 不会因未知工具而报错 |

---

## 🆚 **二、AI-ClaudeCat vs PixelHQ-bridge 对比**

### **1. 工具映射策略**

| 项目 | 策略 | 映射表 | 默认处理 |
|------|------|--------|---------|
| **PixelHQ-bridge** | 硬编码 + 分类 | 14 种工具 → 9 个分类 | 未知 → `OTHER` |
| **AI-ClaudeCat** | 硬编码 + 状态 | 18 种工具 → 8 种状态 | 未知 → `WORKING` |

---

### **2. 代码对比**

#### **PixelHQ-bridge（TypeScript）**
```typescript
// 分类驱动
const mapping = TOOL_TO_CATEGORY[toolName] || {
  category: ToolCategory.OTHER,
  detail: toolName,
};
```

#### **AI-ClaudeCat（Python）**
```python
# 状态驱动
status = TOOL_STATUS_MAP.get(tool_name, Status.WORKING)
```

---

### **3. 设计目标差异**

| 维度 | PixelHQ-bridge | AI-ClaudeCat |
|------|---------------|--------------|
| **目标** | 🖥️ **前端展示** - 为 Pixel Office 桌面宠物提供事件流 | 🎨 **状态检测** - 为桌面宠物提供实时动画状态 |
| **输出** | 事件分类（用于图标、过滤） | AI 状态（用于动画） |
| **粒度** | 粗粒度（9 个分类） | 细粒度（8 种状态） |
| **用途** | 前端展示、统计、过滤 | 动画控制、用户反馈 |

---

### **4. 工具覆盖对比**

| 工具名称 | PixelHQ-bridge 分类 | AI-ClaudeCat 状态 | 是否一致 |
|---------|-------------------|------------------|---------|
| `Read` | `FILE_READ` | `WORKING` | ✅ |
| `Write` | `FILE_WRITE` | `WORKING` | ✅ |
| `Edit` | `FILE_WRITE` | `WORKING` | ✅ |
| `Bash` | `TERMINAL` | `EXECUTING` | ✅ |
| `Grep` | `SEARCH` | `WORKING` | ✅ |
| `Glob` | `SEARCH` | `WORKING` | ✅ |
| `WebFetch` | `SEARCH` | `WORKING` | ✅ |
| `WebSearch` | `SEARCH` | `WORKING` | ✅ |
| `Task` | `SPAWN_AGENT` | `WORKING` | ✅ |
| `TodoWrite` | `PLAN` | `WORKING` | ✅ |
| `AskUserQuestion` | `COMMUNICATE` | `IDLE` | ✅ |
| `NotebookEdit` | `NOTEBOOK` | - | ❌ AI-ClaudeCat 未支持 |
| `EnterPlanMode` | `PLAN` | - | ❌ AI-ClaudeCat 未支持 |
| `ExitPlanMode` | `PLAN` | - | ❌ AI-ClaudeCat 未支持 |
| `TaskOutput` | - | `WORKING` | ❌ PixelHQ 未支持 |
| `KillShell` | - | `EXECUTING` | ❌ PixelHQ 未支持 |
| `Skill` | - | `WORKING` | ❌ PixelHQ 未支持 |

**覆盖率**:
- PixelHQ-bridge: **14 种工具**
- AI-ClaudeCat: **18 种工具**（含 MCP）

---

## 🎯 **三、核心发现**

### **✅ PixelHQ-bridge 使用硬编码！**

**关键证据**:
1. ✅ 静态映射表 `TOOL_TO_CATEGORY`
2. ✅ 没有任何正则表达式
3. ✅ 没有动态模式匹配
4. ✅ 未知工具默认归为 `OTHER`

---

### **📊 PixelHQ-bridge 的优势**

| 优势 | 说明 |
|------|------|
| ✅ **清晰直观** | 一眼看出所有支持的工具 |
| ✅ **精确控制** | 每个工具明确分类 |
| ✅ **易于维护** | 添加新工具只需添加一行 |
| ✅ **性能优越** | O(1) 查找，无正则开销 |
| ✅ **可靠性高** | 不会因命名不规范而误判 |
| ✅ **语义化** | 按功能分类，不依赖命名 |

---

### **🤔 为什么 PixelHQ 不用正则？**

#### **1. Claude Code 工具集相对稳定**
- ✅ 核心工具（Read, Write, Bash）不会变
- ✅ 新工具添加频率低（几个月一次）
- ✅ 工具命名没有统一规范（PascalCase + CamelCase 混合）

#### **2. 正则匹配的局限性**
```typescript
// ❌ 正则方案的问题

// 问题 1: 语义不明确
// ReadConfig 是读取还是写入？依赖前缀 "Read" 会误判

// 问题 2: 特殊工具难以处理
// AskUserQuestion - 正则可能匹配到 "Ask"，但需要特殊状态（IDLE）

// 问题 3: 工具命名不统一
// TodoWrite (CamelCase)
// Grep (PascalCase)
// 无法用单一正则覆盖
```

#### **3. 硬编码的维护成本可接受**
- ✅ 14 种工具 → 新增工具只需 1 行代码
- ✅ TypeScript 类型安全（编译时检查）
- ✅ 中心化管理（`config.ts` 单一文件）

---

## 💡 **四、对 AI-ClaudeCat 的启示**

### **1. 推荐方案：保持硬编码**

基于 PixelHQ-bridge 的实践经验，**推荐保持当前的硬编码方案**：

```python
# 当前方案（推荐保持）✅
TOOL_STATUS_MAP = {
    'Read': Status.WORKING,
    'Write': Status.WORKING,
    'Edit': Status.WORKING,
    'Bash': Status.EXECUTING,
    'Grep': Status.WORKING,
    'Glob': Status.WORKING,
    'WebFetch': Status.WORKING,
    'WebSearch': Status.WORKING,
    'Task': Status.WORKING,
    'TodoWrite': Status.WORKING,
    'Skill': Status.WORKING,
    'AskUserQuestion': Status.IDLE,
    'TaskOutput': Status.WORKING,
    'KillShell': Status.EXECUTING,
    # ... 其他工具
}

def get_tool_status(tool_name: str) -> Status:
    # MCP 工具特殊处理
    if tool_name.startswith('mcp__'):
        return Status.WORKING
    
    # 查找映射，默认 WORKING
    return TOOL_STATUS_MAP.get(tool_name, Status.WORKING)
```

**理由**:
1. ✅ PixelHQ-bridge 的成熟方案验证了硬编码的可行性
2. ✅ 工具数量有限（18 种），维护成本低
3. ✅ 精确控制，不会误判
4. ✅ MCP 已经用前缀匹配，无需再改

---

### **2. 可选改进：添加工具分类（仅用于文档）**

如果想要更好的可读性，可以添加分类注释：

```python
# 文件 I/O
TOOL_STATUS_MAP = {
    'Read': Status.WORKING,      # 读取文件
    'Write': Status.WORKING,     # 写入文件
    'Edit': Status.WORKING,      # 编辑文件
}

# 执行类
TOOL_STATUS_MAP.update({
    'Bash': Status.EXECUTING,    # Shell 命令
    'KillShell': Status.EXECUTING,  # 终止进程
})

# 搜索类
TOOL_STATUS_MAP.update({
    'Grep': Status.WORKING,      # 代码搜索
    'Glob': Status.WORKING,      # 文件匹配
    'WebSearch': Status.WORKING, # 网络搜索
    'WebFetch': Status.WORKING,  # 网页抓取
})

# Agent 类
TOOL_STATUS_MAP.update({
    'Task': Status.WORKING,      # 启动子 Agent
    'TaskOutput': Status.WORKING,  # 等待输出
    'Skill': Status.WORKING,     # 加载技能
})

# 交互类
TOOL_STATUS_MAP.update({
    'AskUserQuestion': Status.IDLE,  # 询问用户
    'TodoWrite': Status.WORKING,  # 写入待办
})
```

**优势**:
- ✅ 保持硬编码的精确性
- ✅ 增加代码可读性
- ✅ 便于理解工具功能
- ✅ 无性能损失

---

### **3. 不推荐：正则匹配方案**

基于分析，**不推荐使用正则匹配**：

```python
# ❌ 不推荐的正则方案

TOOL_VERB_PATTERNS = {
    r'^(Read|Get|Fetch|Query|Search|Grep|Glob|List)': Status.WORKING,
    r'^(Write|Edit|Create|Update|Delete|Modify|Todo)': Status.WORKING,
    r'^(Bash|Execute|Run|Kill|Stop|Terminate)': Status.EXECUTING,
    r'^(Ask|Wait|Pause|Question)': Status.IDLE,
}

def classify_tool_by_regex(tool_name: str) -> Status:
    for pattern, status in TOOL_VERB_PATTERNS.items():
        if re.match(pattern, tool_name):
            return status
    return Status.WORKING
```

**为什么不推荐？**
1. ❌ Claude Code 命名不规范（PascalCase + CamelCase）
2. ❌ 特殊工具难以匹配（`Skill`, `TaskOutput`）
3. ❌ 语义误判风险（`ReadConfig` 可能是写入）
4. ❌ 性能开销（每次工具调用都要遍历正则）
5. ❌ PixelHQ-bridge 的成功实践证明硬编码更优

---

## 📊 **五、最终建议**

### **工具映射策略**

| 方案 | 推荐度 | 理由 |
|------|-------|------|
| **硬编码（当前）** | ⭐⭐⭐⭐⭐ | **强烈推荐**，PixelHQ 验证有效 |
| **硬编码 + 分类注释** | ⭐⭐⭐⭐ | 可选改进，提升可读性 |
| **正则匹配** | ⭐ | **不推荐**，过度设计 |

---

### **Progress 事件策略**

| 方案 | 推荐度 | 理由 |
|------|-------|------|
| **字段检查（当前）** | ⭐⭐⭐⭐⭐ | **保持当前**，简单有效 |
| **正则匹配** | ⭐ | 无必要 |

---

### **MCP 工具策略**

| 方案 | 推荐度 | 理由 |
|------|-------|------|
| **前缀匹配（当前）** | ⭐⭐⭐⭐⭐ | **保持当前**，已完美 |

---

## ✅ **六、结论**

### **核心发现**

1. ✅ **PixelHQ-bridge 使用硬编码** - 没有任何正则匹配
2. ✅ **硬编码方案经过实践验证** - 稳定、可靠、易维护
3. ✅ **AI-ClaudeCat 当前方案正确** - 与 PixelHQ 一致
4. ❌ **正则匹配过度设计** - Claude Code 工具集不适合正则

---

### **最终推荐**

**保持当前的硬编码方案，无需改动！**

```python
# ✅ 当前方案（完全正确）
TOOL_STATUS_MAP = {
    'Read': Status.WORKING,
    'Write': Status.WORKING,
    'Edit': Status.WORKING,
    'Bash': Status.EXECUTING,
    # ... 18 种工具
}

# ✅ MCP 工具（前缀匹配）
if tool_name.startswith('mcp__'):
    return Status.WORKING

# ✅ 默认处理
return TOOL_STATUS_MAP.get(tool_name, Status.WORKING)
```

---

### **可选改进**

如果需要提升可读性，可以添加分类注释：

```python
# === 文件 I/O ===
TOOL_STATUS_MAP = {
    'Read': Status.WORKING,
    'Write': Status.WORKING,
    'Edit': Status.WORKING,
}

# === 执行类 ===
TOOL_STATUS_MAP.update({
    'Bash': Status.EXECUTING,
    'KillShell': Status.EXECUTING,
})

# === 搜索类 ===
# ...
```

---

**参考资料**:
- [PixelHQ-bridge GitHub](https://github.com/pixelhq/pixelhq-bridge)
- `参考项目/PixelHQ-bridge/src/config.ts` - 工具分类配置
- `参考项目/PixelHQ-bridge/src/adapters/claude-code.ts` - Claude Code 适配器

---

**最后更新**: 2026-02-06  
**结论**: **保持硬编码，无需改动** ✅
