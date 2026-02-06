# 🎯 工具名称和 Progress 事件命名规律分析

**分析日期**: 2026-02-06  
**数据来源**: PC1 (101 logs) + PC2 (146 logs) = **247 个日志文件**  
**分析目标**: 发现命名规律，决定是否用正则替代硬编码

---

## 📊 **一、工具名称统计（27 种）**

### **按出现次数排序**

| 排名 | 工具名称 | 次数 | 命名风格 | 功能分类 |
|-----|---------|------|---------|---------|
| 1 | `Bash` | 813 | PascalCase | 执行 |
| 2 | `Edit` | 720 | PascalCase | 文件 I/O |
| 3 | `Read` | 686 | PascalCase | 文件 I/O |
| 4 | `Write` | 197 | PascalCase | 文件 I/O |
| 5 | `TodoWrite` | 196 | CamelCase | 计划管理 |
| 6 | `TaskOutput` | 153 | CamelCase | Agent |
| 7 | `Grep` | 104 | PascalCase | 搜索 |
| 8 | `Glob` | 97 | PascalCase | 搜索 |
| 9 | `KillShell` | 33 | CamelCase | 执行 |
| 10 | `Skill` | 23 | PascalCase | 技能 |
| 11 | `mcp__context7__query-docs` | 16 | MCP | MCP |
| 12 | `mcp__context7__resolve-library-id` | 15 | MCP | MCP |
| 13 | `mcp__open-websearch__fetchGithubReadme` | 13 | MCP | MCP |
| 14 | `AskUserQuestion` | 8 | CamelCase | 交互 |
| 15 | `mcp__MiniMax_Coding_Plan_MCP__understand_image` | 8 | MCP | MCP |
| 16 | `WebSearch` | 5 | CamelCase | 网络 |
| 17 | `Task` | 4 | PascalCase | Agent |
| 18 | `mcp__MiniMax_Coding_Plan_MCP__web_search` | 3 | MCP | MCP |
| 19 | `mcp__open-websearch__search` | 3 | MCP | MCP |
| 20 | `WebFetch` | 2 | CamelCase | 网络 |
| 21 | `mcp__Playwright__browser_navigate` | 2 | MCP | MCP |
| 22 | `mcp__Playwright__browser_take_screenshot` | 2 | MCP | MCP |
| 23 | `mcp__mcp-deepwiki__deepwiki_fetch` | 1 | MCP | MCP |
| 24 | `mcp__serena__list_dir` | 1 | MCP | MCP |
| **25** | **`EnterPlanMode`** | **？** | **CamelCase** | **计划管理** ⭐ |
| **26** | **`ExitPlanMode`** | **？** | **CamelCase** | **计划管理** ⭐ |
| **27** | **`NotebookEdit`** | **？** | **CamelCase** | **Notebook** ⭐ |

**注**: ⭐ 标记的工具来自 PixelHQ-bridge，尚未在 PC1+PC2 日志中发现

---

## 🎯 **二、命名风格分析**

### **1. PascalCase（首字母大写）- 8 种（33%）**

**特征**: 单个英文单词，首字母大写

| 工具名称 | 次数 | 功能 |
|---------|------|------|
| `Bash` | 813 | 执行 Shell 命令 |
| `Edit` | 720 | 编辑文件 |
| `Read` | 686 | 读取文件 |
| `Write` | 197 | 写入文件 |
| `Grep` | 104 | 代码搜索 |
| `Glob` | 97 | 文件匹配 |
| `Skill` | 23 | 加载技能 |
| `Task` | 4 | 启动子 Agent |

**规律**:
- ✅ **动词为主** (`Read`, `Write`, `Edit`)
- ✅ **Unix 命令风格** (`Bash`, `Grep`, `Glob`)
- ✅ **单一职责** - 每个工具功能明确
- ✅ **高频工具** - 占总调用次数的 **~80%**

---

### **2. CamelCase（驼峰命名）- 9 种（33%）**

**特征**: 多个单词组合，首字母大写

| 工具名称 | 次数 | 功能 |
|---------|------|------|
| `TodoWrite` | 196 | 写入待办事项 |
| `TaskOutput` | 153 | 等待子 Agent 输出 |
| `KillShell` | 33 | 终止 Shell 进程 |
| `AskUserQuestion` | 8 | 询问用户 |
| `WebSearch` | 5 | 网络搜索 |
| `WebFetch` | 2 | 网页抓取 |
| `EnterPlanMode` | ？ | 进入计划模式 ⭐ |
| `ExitPlanMode` | ？ | 退出计划模式 ⭐ |
| `NotebookEdit` | ？ | Notebook 编辑 ⭐ |

**规律**:
- ✅ **动词 + 名词** (`KillShell`, `AskUserQuestion`)
- ✅ **功能组合** (`TodoWrite` = Todo + Write)
- ✅ **描述性** - 名称直观表达功能
- ✅ **中频工具** - 特定场景使用

---

### **3. MCP 工具（mcp__*）- 10 种（42%）**

**特征**: `mcp__<server>__<tool>` 三段式

| 工具名称 | 次数 | 服务器 | 实际工具 |
|---------|------|--------|---------|
| `mcp__context7__query-docs` | 16 | context7 | query-docs |
| `mcp__context7__resolve-library-id` | 15 | context7 | resolve-library-id |
| `mcp__open-websearch__fetchGithubReadme` | 13 | open-websearch | fetchGithubReadme |
| `mcp__MiniMax_Coding_Plan_MCP__understand_image` | 8 | MiniMax_Coding_Plan_MCP | understand_image |
| `mcp__MiniMax_Coding_Plan_MCP__web_search` | 3 | MiniMax_Coding_Plan_MCP | web_search |
| `mcp__open-websearch__search` | 3 | open-websearch | search |
| `mcp__Playwright__browser_navigate` | 2 | Playwright | browser_navigate |
| `mcp__Playwright__browser_take_screenshot` | 2 | Playwright | browser_take_screenshot |
| `mcp__mcp-deepwiki__deepwiki_fetch` | 1 | mcp-deepwiki | deepwiki_fetch |
| `mcp__serena__list_dir` | 1 | serena | list_dir |

**规律**:
- ✅ **标准前缀** - 100% 使用 `mcp__`
- ✅ **三段结构** - `mcp__<server>__<tool>`
- ✅ **服务器名多样** - 短横线 (`open-websearch`)、下划线 (`MiniMax_Coding_Plan_MCP`)、驼峰 (`Playwright`)
- ✅ **工具名多样** - 短横线 (`query-docs`)、下划线 (`understand_image`)、驼峰 (`fetchGithubReadme`)
- ✅ **可扩展** - 支持任意新 MCP 服务器

---

## 🔍 **三、命名规律总结**

### **核心发现**

| 命名风格 | 数量 | 占比 | 特征 | 可正则化 |
|---------|------|------|------|---------|
| **PascalCase** | 8 | 33% | 单词，首字母大写 | ✅ **可以** |
| **CamelCase** | 6 | 25% | 多词组合，驼峰 | ✅ **可以** |
| **MCP** | 10 | 42% | `mcp__*` 前缀 | ✅ **已实现** |

### **分类规律**

#### **1. 按动词分类（语义化）**

| 动词类型 | 工具 | 状态 |
|---------|------|------|
| **读取类** | `Read`, `Grep`, `Glob`, `WebFetch` | `Status.WORKING` |
| **写入类** | `Write`, `Edit`, `TodoWrite` | `Status.WORKING` |
| **执行类** | `Bash`, `KillShell` | `Status.EXECUTING` |
| **等待类** | `AskUserQuestion`, `TaskOutput` | `Status.IDLE` / `Status.WORKING` |
| **启动类** | `Task`, `Skill` | `Status.WORKING` |
| **网络类** | `WebSearch`, `WebFetch` | `Status.WORKING` |

#### **2. 按首字母分类（形式化）**

```regex
# 读取类工具
^(Read|Get|Fetch|Query|Search|Grep|Glob|List).*
→ Status.WORKING

# 写入类工具
^(Write|Edit|Create|Update|Delete|Modify|Todo).*
→ Status.WORKING

# 执行类工具
^(Bash|Execute|Run|Kill|Stop|Terminate).*
→ Status.EXECUTING

# 等待类工具
^(Ask|Wait|Pause|Question).*
→ Status.IDLE
```

---

## 📊 **四、Progress 事件分析**

### **已知的 3 种 Progress 类型**

| 类型 | 出现次数 | 特征字段 | 当前支持 |
|------|---------|---------|---------|
| **`bash_progress`** | 105 | `command`, `exitCode`, `shellId` | ✅ 已支持 |
| **`mcp_progress`** | 20 | `serverName`, `toolName` | ✅ 已支持 |
| **`hook_progress`** | 14 | `hookName`, `hookType` | ✅ 已支持 |

### **识别算法（当前实现）**

```python
# 方法 1: 硬编码字段检查（当前）
if 'serverName' in progress_data:
    progress_type = 'mcp_progress'
elif 'command' in progress_data or 'exitCode' in progress_data:
    progress_type = 'bash_progress'
elif 'hookName' in progress_data:
    progress_type = 'hook_progress'
else:
    progress_type = 'unknown_progress'
```

### **字段签名分析**

| Progress 类型 | 必有字段 | 可选字段 | 唯一特征 |
|--------------|---------|---------|---------|
| `bash_progress` | `status` | `command`, `exitCode`, `shellId`, `elapsedTimeMs` | `command` / `exitCode` |
| `mcp_progress` | `status`, `serverName`, `toolName` | `elapsedTimeMs` | `serverName` ✅ |
| `hook_progress` | `status`, `hookName` | `hookType`, `elapsedTimeMs` | `hookName` ✅ |

**结论**: 
- ✅ `serverName` 和 `hookName` 是**唯一特征**，可以准确识别
- ✅ `bash_progress` 通过排除法识别（无 `serverName`, `hookName`）
- ✅ **不需要正则**，当前字段检查已经足够

---

## 🎯 **五、是否需要正则匹配？**

### **工具名称映射**

#### **方案 A: 硬编码（当前）**
```python
TOOL_STATUS_MAP = {
    'Read': Status.WORKING,
    'Write': Status.WORKING,
    'Edit': Status.WORKING,
    'Bash': Status.EXECUTING,
    # ... 18 种工具
}
```

**优点**:
- ✅ 清晰直观
- ✅ 精确控制
- ✅ 易于维护

**缺点**:
- ❌ 新工具需要手动添加
- ❌ 维护成本（假设频繁增加新工具）

---

#### **方案 B: 正则匹配（语义化）**
```python
def classify_tool_by_verb(tool_name: str) -> Status:
    """基于动词前缀的语义分类"""
    if re.match(r'^(Read|Get|Fetch|Query|Search|Grep|Glob|List)', tool_name):
        return Status.WORKING
    elif re.match(r'^(Write|Edit|Create|Update|Delete|Modify|Todo)', tool_name):
        return Status.WORKING
    elif re.match(r'^(Bash|Execute|Run|Kill|Stop|Terminate)', tool_name):
        return Status.EXECUTING
    elif re.match(r'^(Ask|Wait|Pause|Question)', tool_name):
        return Status.IDLE
    elif tool_name == 'thinking':
        return Status.THINKING
    else:
        return Status.WORKING  # 默认
```

**优点**:
- ✅ 自动支持新工具（如果符合命名规范）
- ✅ 减少维护成本
- ✅ 语义化分类

**缺点**:
- ❌ 依赖命名规范（假设未来工具遵循）
- ❌ 特殊工具难以处理（如 `Skill`, `Task`）
- ❌ 可能误判（如 `ReadConfig` 被判为读取，实际可能是写入）

---

#### **方案 C: 混合方案（推荐）**
```python
# 1. 特殊工具（硬编码，精确控制）
SPECIAL_TOOLS = {
    'thinking': Status.THINKING,
    'AskUserQuestion': Status.IDLE,
    'TaskOutput': Status.WORKING,
    'Skill': Status.WORKING,
    'Task': Status.WORKING,
}

# 2. 通用规则（正则，自动支持新工具）
TOOL_VERB_PATTERNS = {
    r'^(Read|Get|Fetch|Query|Search|Grep|Glob|List)': Status.WORKING,
    r'^(Write|Edit|Create|Update|Delete|Modify|Todo)': Status.WORKING,
    r'^(Bash|Execute|Run|Kill|Stop|Terminate)': Status.EXECUTING,
    r'^(Ask|Wait|Pause|Question)': Status.IDLE,
}

def classify_tool(tool_name: str) -> Status:
    # 1. 检查特殊工具
    if tool_name in SPECIAL_TOOLS:
        return SPECIAL_TOOLS[tool_name]
    
    # 2. 检查 MCP 工具
    if tool_name.startswith('mcp__'):
        return Status.WORKING
    
    # 3. 正则匹配动词前缀
    for pattern, status in TOOL_VERB_PATTERNS.items():
        if re.match(pattern, tool_name):
            return status
    
    # 4. 默认
    return Status.WORKING
```

**优点**:
- ✅ 结合硬编码和正则的优点
- ✅ 特殊工具精确控制
- ✅ 新工具自动支持（如果符合命名规范）
- ✅ 维护成本低

**缺点**:
- ⚠️ 稍微复杂

---

### **Progress 事件识别**

**结论**: **不需要正则**

**原因**:
1. ✅ 只有 3 种类型，数量固定
2. ✅ 字段特征明确（`serverName`, `hookName`）
3. ✅ 当前字段检查已经足够准确
4. ❌ 未来不太可能频繁增加新类型

---

## 🎯 **六、最终建议**

### **1. 工具名称映射**

| 方案 | 推荐度 | 理由 |
|------|-------|------|
| **硬编码** | ⭐⭐⭐ | 如果工具集稳定，**保持当前方案** |
| **混合方案** | ⭐⭐⭐⭐⭐ | **最佳选择** - 兼顾精确和灵活 |
| **纯正则** | ⭐⭐ | 不推荐 - 过度设计 |

### **2. Progress 事件识别**

| 方案 | 推荐度 | 理由 |
|------|-------|------|
| **字段检查** | ⭐⭐⭐⭐⭐ | **保持当前方案** - 简单有效 |
| **正则匹配** | ⭐ | 不推荐 - 无必要 |

---

## 📊 **七、数据统计**

### **工具类型分布**

```
PascalCase  ████████████████████████████████  33% (8 种, ~3200 次)
CamelCase   █████████████████████            25% (6 种, ~400 次)
MCP         █████████████████████████████    42% (10 种, ~90 次)
```

### **调用频率分布**

```
高频 (100+)   ████████████████████████████  75% (5 种工具)
中频 (10-99)  ████████████                  20% (7 种工具)
低频 (<10)    ██                            5%  (12 种工具)
```

---

## ✅ **八、结论**

### **工具名称映射**

**建议采用混合方案**:
1. ✅ 特殊工具硬编码（精确控制）
2. ✅ 通用工具正则匹配（自动支持新工具）
3. ✅ MCP 工具前缀匹配（已实现）

### **Progress 事件识别**

**建议保持当前方案**:
1. ✅ 字段检查简单有效
2. ✅ 3 种类型固定，不会频繁变化
3. ❌ 正则匹配无必要

---

**最后更新**: 2026-02-06  
**数据来源**: 247 个真实日志文件  
**分析工具**: `extract_tools.py`
