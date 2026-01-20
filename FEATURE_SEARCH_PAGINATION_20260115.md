# 搜索和分页功能实现
**日期**: 2026-01-15  
**功能**: Extraction History 搜索+分页 & Knowledge Database 分页

---

## ✅ 新增功能

### 功能1: Extraction History 搜索和分页 ✅

**新增特性**:
1. **搜索功能**
   - 实时搜索标题和摘要内容
   - 支持中英文搜索
   - 搜索时自动重置到第一页

2. **分页功能**
   - 每页显示 10 条记录
   - 显示总记录数和当前页范围
   - 上一页/下一页按钮
   - 页码快速跳转

**修改文件**:
- `frontend/src/views/MainPage.vue`
  - 添加搜索框 UI
  - 添加分页器 UI
  - 添加状态变量：`academicHistorySearch`, `academicHistoryPage`, `academicHistoryPageSize`, `academicHistoryTotal`
  - 更新 `fetchAcademicHistory()` 函数支持搜索和分页
  - 添加 `searchAcademicHistory()` 函数
  - 添加 `paginationPages()` 辅助函数

- `backend/app/api/v1/endpoints/academic_extract.py`
  - 更新 `get_academic_extracts()` API
  - 添加 `search` 参数支持搜索
  - 返回格式改为 `{items: [], total: number, limit: number, offset: number}`
  - 支持标题和摘要的模糊搜索

---

### 功能2: Knowledge Database 分页 ✅

**新增特性**:
1. **分页功能**
   - 每页显示 12 条记录（3列 x 4行）
   - 显示总记录数和当前页范围
   - 上一页/下一页按钮
   - 页码快速跳转

2. **搜索模式分页**
   - 搜索结果也支持分页
   - 搜索时自动重置到第一页

**修改文件**:
- `frontend/src/views/MainPage.vue`
  - 添加分页器 UI
  - 添加状态变量：`knowledgePage`, `knowledgePageSize`, `knowledgeTotal`
  - 更新 `fetchKnowledgeDocs()` 函数支持分页
  - 更新 `searchKnowledge()` 函数

- `backend/app/api/v1/endpoints/knowledge.py`
  - 更新 `list_documents()` API
  - 更新 `search_documents()` API
  - 返回格式改为 `{items: [], total: number, limit: number, offset: number}`
  - `SearchQuery` 模型添加 `offset` 参数

---

## 🎨 UI 设计

### Extraction History 搜索框
```
┌─────────────────────────────────────────┐
│ 🔍 Search by title or summary...       │
└─────────────────────────────────────────┘
```

### 分页器样式
```
Showing 1 - 10 of 45        [Previous] [1] [2] [3] [4] [5] [Next]
                                         ↑ 当前页高亮
```

---

## 📊 API 变更

### 1. GET /api/v1/academic-extract/extracts

**新增参数**:
- `search` (optional): 搜索关键词
- `limit` (default: 20): 每页数量
- `offset` (default: 0): 偏移量

**返回格式**:
```json
{
  "items": [
    {
      "id": "...",
      "title": "...",
      "summary_zh": "...",
      "summary_en": "...",
      "created_at": "...",
      "user": "...",
      "metadata": {}
    }
  ],
  "total": 45,
  "limit": 10,
  "offset": 0
}
```

### 2. GET /api/v1/knowledge/list

**参数**:
- `limit` (default: 20): 每页数量
- `offset` (default: 0): 偏移量

**返回格式**:
```json
{
  "items": [
    {
      "id": "...",
      "payload": {
        "title": "...",
        "content": "...",
        "type": "...",
        "created_at": "..."
      }
    }
  ],
  "total": 120,
  "limit": 12,
  "offset": 0
}
```

### 3. POST /api/v1/knowledge/search

**请求体**:
```json
{
  "query": "search term",
  "limit": 12,
  "offset": 0
}
```

**返回格式**: 同 `/list`

---

## 🚀 使用方法

### Extraction History

1. **搜索**:
   - 在搜索框输入关键词
   - 实时过滤结果
   - 支持搜索标题和摘要内容

2. **分页**:
   - 点击页码快速跳转
   - 使用 Previous/Next 按钮翻页
   - 每页显示 10 条记录

### Knowledge Database

1. **浏览**:
   - 每页显示 12 个卡片（3列 x 4行）
   - 使用分页器浏览所有文档

2. **搜索后分页**:
   - 输入搜索词后按 Enter
   - 搜索结果也支持分页

---

## 💡 实现细节

### 前端分页逻辑
```javascript
// 计算偏移量
const offset = (page - 1) * pageSize;

// 构建请求参数
const params = new URLSearchParams({
  limit: pageSize.toString(),
  offset: offset.toString()
});

// 发送请求
const response = await fetch(`${API_URL}?${params}`);
```

### 后端分页逻辑
```python
# 获取所有文档
all_docs = await knowledge_service.list_documents(limit=100)

# 应用搜索过滤（如果有）
if search:
    filtered_docs = [doc for doc in all_docs if search in doc['title']]
else:
    filtered_docs = all_docs

# 计算总数
total = len(filtered_docs)

# 应用分页
paginated_docs = filtered_docs[offset:offset+limit]

# 返回结果
return {
    "items": paginated_docs,
    "total": total,
    "limit": limit,
    "offset": offset
}
```

### 分页器页码生成
```javascript
// 智能显示页码（最多7个）
// 例如：[1] ... [4] [5] [6] ... [10]
function paginationPages(total, pageSize, currentPage) {
  const totalPages = Math.ceil(total / pageSize);
  
  if (totalPages <= 7) {
    return [1, 2, 3, 4, 5, 6, 7];
  }
  
  // 显示当前页附近的页码
  return [1, ..., currentPage-1, currentPage, currentPage+1, ..., totalPages];
}
```

---

## 🔧 部署步骤

### 前端（自动生效）
前端使用 Vite 热重载，刷新浏览器即可：
```bash
# 硬刷新
Ctrl+Shift+R (Windows) 或 Cmd+Shift+R (Mac)
```

### 后端（需要重启）
```bash
cd /www/wwwroot/voxchina/backend
bash quick_restart.sh
```

或者：
```bash
# 找到进程
ps aux | grep "uvicorn.*8300" | grep -v grep

# 停止进程
kill -9 <PID>

# 启动新进程
cd /www/wwwroot/voxchina/backend
source venv/bin/activate
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8300 --workers 1 > /dev/null 2>&1 &
```

---

## ✅ 验证步骤

### 验证 Extraction History

1. **搜索功能**:
   - 进入 Academic Extract 标签页
   - 在 Extraction History 的搜索框输入关键词
   - 验证结果实时过滤

2. **分页功能**:
   - 查看页面底部的分页器
   - 点击不同页码，验证内容切换
   - 验证显示的记录范围正确

### 验证 Knowledge Database

1. **分页功能**:
   - 进入 Knowledge Database 标签页
   - 如果有超过 12 条记录，应该看到分页器
   - 点击翻页，验证卡片内容切换

2. **搜索后分页**:
   - 在搜索框输入关键词
   - 按 Enter 搜索
   - 如果结果超过 12 条，验证分页器显示

---

## 📝 注意事项

1. **性能优化**:
   - 当前实现在后端获取所有数据后在内存中分页
   - 如果数据量很大（>1000条），建议改为数据库层面分页

2. **搜索优化**:
   - 当前是简单的字符串匹配
   - 可以考虑使用全文搜索或向量搜索提升体验

3. **缓存**:
   - 可以考虑添加客户端缓存，减少重复请求

4. **兼容性**:
   - 前端代码兼容旧API格式（如果返回数组而不是对象）
   - 确保平滑升级

---

## 🔗 相关文档

- `FIXES_20260114.md` - TTS错误处理和历史记录修复
- `CRITICAL_FIX_20260114_TTS.md` - MeloTTS tokenizer bug修复
- `FIXES_20260115_UI_IMPROVEMENTS.md` - UI改进（音频自动播放、命名规范）
- `FEATURE_SEARCH_PAGINATION_20260115.md` - 本文档（搜索和分页功能）

---

**完成时间**: 2026-01-15 00:45  
**功能**: 搜索和分页  
**作者**: Ren CBIT https://github.com/reneverland/
