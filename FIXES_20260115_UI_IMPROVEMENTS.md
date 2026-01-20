# VoxChina UI 改进修复
**日期**: 2026-01-15  
**修复内容**: 音频自动播放 + 历史记录显示 + 命名规范

---

## ✅ 修复的问题

### 问题1: 移除音频自动播放功能 ✅

**用户反馈**: 每次生成音频后会自动播放，影响用户体验

**修改内容**:
- 文件: `frontend/src/views/MainPage.vue`
- 第622行: 移除 `<audio>` 标签的 `autoplay` 属性

**修改前**:
```html
<audio controls :src="audioUrl" class="flex-1 h-10 w-full" autoplay></audio>
```

**修改后**:
```html
<audio controls :src="audioUrl" class="flex-1 h-10 w-full"></audio>
```

**效果**: 
- ✅ 音频生成后不会自动播放
- ✅ 用户可以手动点击播放按钮控制播放

---

### 问题2: Extraction History 显示空白 ✅

**用户反馈**: 明明已经有很多提取记录，但 Extraction History 显示为空

**根本原因**:
在 `backend/app/api/v1/endpoints/academic_extract.py` 中，获取文档时使用了错误的字段名：
- 使用了 `doc.get("metadata", {})` 
- 应该使用 `doc.get("payload", {})`

因为 `knowledge_service.list_documents()` 返回的数据结构是：
```python
{
    "id": "...",
    "payload": {...}  # ← 正确的字段名
}
```

**修改内容**:
文件: `backend/app/api/v1/endpoints/academic_extract.py`

1. **第254行** (get_academic_extracts 函数):
```python
# 修改前
metadata = doc.get("metadata", {})

# 修改后
metadata = doc.get("payload", {})
```

2. **第302行** (get_academic_extract_detail 函数):
```python
# 修改前
metadata = doc.get("metadata", {})

# 修改后
metadata = doc.get("payload", {})
```

3. **第348行** (delete_academic_extract 函数):
```python
# 修改前
metadata = doc.get("metadata", {})

# 修改后
metadata = doc.get("payload", {})
```

**效果**:
- ✅ Extraction History 正确显示所有提取记录
- ✅ 可以查看历史记录详情
- ✅ 可以删除历史记录

---

### 问题3: 命名规范 - academicExtract → Academic Extract ✅

**用户反馈**: academicExtract 应该写成 Academic Extract（更规范）

**修改内容**:
文件: `frontend/src/views/MainPage.vue`

1. **英文翻译** (第1109行):
```javascript
// 修改前
// Navigation    academicExtract: 'Academic Extract',

// 修改后
// Navigation
academicExtract: 'Academic Extract',
```

2. **中文翻译** (第1183行):
```javascript
// 修改前
// Navigation    academicExtract: '学术摘要提取',

// 修改后
// Navigation
academicExtract: 'Academic Extract',
```

**效果**:
- ✅ 侧边栏导航显示为 "Academic Extract"
- ✅ 中英文界面都统一使用 "Academic Extract"
- ✅ 符合专业命名规范

---

## 🚀 部署步骤

### 前端（自动生效）
前端使用 Vite 热重载，修改会自动生效。
- 如果没有自动生效，请**刷新浏览器页面**（Ctrl+R 或 Cmd+R）
- 如果还不行，尝试**硬刷新**（Ctrl+Shift+R 或 Cmd+Shift+R）

### 后端（需要重启）
后端修改需要重启服务才能生效：

```bash
# 方法1: 使用重启脚本
cd /www/wwwroot/voxchina/backend
sudo bash restart_as_www.sh

# 方法2: 手动重启
ps aux | grep "uvicorn.*8300" | grep -v grep
sudo kill -9 <PID>
cd /www/wwwroot/voxchina/backend
sudo -u www bash -c "source venv/bin/activate && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8300 --workers 1 > /dev/null 2>&1 &"
```

---

## ✅ 验证步骤

### 验证问题1（音频不自动播放）:
1. 打开前端页面
2. 进入 Academic Extract 标签页
3. 提取一篇文章
4. 生成音频
5. **预期**: 音频生成后不会自动播放，需要手动点击播放按钮

### 验证问题2（历史记录显示）:
1. 打开前端页面
2. 进入 Academic Extract 标签页
3. 滚动到 "Extraction History" 部分
4. **预期**: 能看到之前提取的所有文章记录
5. 点击任意记录，能查看详情

### 验证问题3（命名规范）:
1. 打开前端页面
2. 查看左侧导航栏
3. **预期**: 第一个标签显示为 "Academic Extract"（不是 "academicExtract"）
4. 切换中英文语言
5. **预期**: 两种语言都显示 "Academic Extract"

---

## 📊 修改文件总结

### 前端:
- `frontend/src/views/MainPage.vue`
  - 移除音频自动播放
  - 修正翻译文本格式

### 后端:
- `backend/app/api/v1/endpoints/academic_extract.py`
  - 修复字段名错误（metadata → payload）
  - 影响3个函数：get_academic_extracts、get_academic_extract_detail、delete_academic_extract

---

## 🔗 相关文档

本次修复是在之前修复的基础上进行的：
1. `FIXES_20260114.md` - TTS错误处理和历史记录自动保存
2. `CRITICAL_FIX_20260114_TTS.md` - MeloTTS tokenizer bug修复
3. `FIXES_20260115_UI_IMPROVEMENTS.md` - 本次UI改进（本文档）

---

## 📝 注意事项

1. **历史记录依赖知识库**: 
   - Extraction History 从 Qdrant 知识库获取数据
   - 如果知识库服务不可用，历史记录将无法显示
   - 确保 Ollama 嵌入服务正常运行

2. **浏览器缓存**:
   - 如果前端修改未生效，尝试硬刷新
   - 或清除浏览器缓存后重新加载

3. **后端重启**:
   - 后端修改必须重启服务才能生效
   - 重启后可能需要等待几秒钟让服务完全启动

---

**修复完成时间**: 2026-01-15 00:05  
**修复人**: AI Assistant  
**作者**: Ren CBIT https://github.com/reneverland/
