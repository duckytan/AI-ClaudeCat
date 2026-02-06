# Git 配置说明

## `.gitignore` 规则说明

本项目的 `.gitignore` 文件配置了以下忽略规则：

### 🚫 **不会上传到 GitHub 的内容**

#### 1. **参考项目目录**
```
参考项目/
```
- 包含其他项目的备份和参考代码
- 不属于本项目的核心内容
- **完全忽略，不会被 Git 追踪**

#### 2. **Python 缓存文件**
```
__pycache__/
*.pyc
*.pyo
*.pyd
```
- Python 编译生成的字节码文件
- 每次运行会自动生成
- 不需要版本控制

#### 3. **数据库文件**
```
data/history.db
data/*.db
```
- 运行时生成的 SQLite 数据库
- 包含用户的使用历史
- 不应上传到公开仓库

#### 4. **临时文件**
```
temp_*.json
temp_*.txt
*.tmp
*.bak
*.log
```
- 开发和测试过程中的临时文件
- 分析脚本生成的报告
- 日志文件

#### 5. **IDE 配置**
```
.vscode/
.idea/
*.code-workspace
```
- 编辑器的个人配置
- 不同开发者可能使用不同 IDE

#### 6. **操作系统文件**
```
.DS_Store      # macOS
Thumbs.db      # Windows
*~             # Linux
```
- 操作系统自动生成的元数据文件

#### 7. **备份文件（可选）**
```
backup-v3.1/
```
- 如果不需要上传旧版本备份，取消注释此行
- 当前默认**保留**在 Git 中

---

## ✅ **会上传到 GitHub 的内容**

### **核心代码**
- `src/` - 所有源代码
- `main.py` - 主程序入口
- `run_with_debug.py` - 调试脚本

### **配置文件**
- `config.json` - 默认配置（不包含敏感信息）
- `requirements.txt` - 依赖清单
- `.gitignore` - Git 忽略规则
- `.gitattributes` - Git 属性配置

### **文档**
- `README.md` - 项目说明
- `AGENTS.md` - AI 知识库
- `CLAUDE.md` - 完整文档
- `docs/` - 所有技术文档

### **备份**
- `backup-v3.1/` - v3.1 版本备份（当前保留）

---

## 🔧 **配置建议**

### **如果配置文件包含敏感信息**

在 `.gitignore` 中取消注释：
```bash
# 编辑 .gitignore
# config.json  # 取消注释此行
```

然后创建示例配置：
```bash
cp config.json config.example.json
git add config.example.json
```

### **如果不想上传备份**

在 `.gitignore` 中取消注释：
```bash
backup-v3.1/  # 取消注释此行
```

---

## 📋 **Git 命令参考**

### **查看被忽略的文件**
```bash
git status --ignored
```

### **检查文件是否被忽略**
```bash
git check-ignore -v 文件名
```

### **强制添加被忽略的文件**（不推荐）
```bash
git add -f 文件名
```

### **清理已追踪的文件**
如果之前已经提交了应该被忽略的文件：
```bash
# 从 Git 中删除，但保留本地文件
git rm --cached 文件名

# 从 Git 中删除整个目录
git rm -r --cached 参考项目/

# 提交更改
git commit -m "chore: 添加 .gitignore，清理不必要的文件"
```

---

## 🎯 **验证配置**

运行以下命令验证配置是否正确：

```bash
# 1. 查看当前 Git 状态
git status

# 2. 验证 "参考项目/" 已被忽略
git check-ignore -v 参考项目/

# 3. 查看所有被忽略的文件
git status --ignored

# 4. 验证 .gitignore 语法
git check-ignore --no-index 参考项目/
```

---

## ✅ **当前状态**

- ✅ `.gitignore` 已创建并生效
- ✅ `.gitattributes` 已配置（规范行尾）
- ✅ `参考项目/` 已被忽略
- ✅ Python 缓存文件已被忽略
- ✅ 临时文件和数据库文件已被忽略

---

## 📝 **注意事项**

1. **首次提交前**，请确认所有敏感信息已被排除
2. **定期检查** `git status` 确保不会意外提交大文件
3. **数据库文件** (`data/history.db`) 永远不会被上传
4. **参考项目** 目录完全独立，不会影响 Git 仓库

---

**文档生成时间**: 2026-02-06  
**Git 配置版本**: v1.0
