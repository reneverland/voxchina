# Bug修复 - Integrated Voiceover - 2026-01-19

## 问题描述

用户报告了两个关键问题：

### 1. ❌ "Image not extracted" - 图片未提取
- **现象**：Visual Assets 页面显示 "Image not extracted" 占位符
- **影响**：无法查看文档中的图片

### 2. ❌ "Document data not loaded" - 文档数据未加载
- **现象**：点击 RELATED DOCUMENTS 时弹出 "Document data not loaded"
- **影响**：无法查看文档详情和原文回溯

---

## 根本原因分析

### 问题1：图片未提取
**原因**：
1. 图片保存路径使用相对路径 `static/images/extracted`，在不同工作目录下会失败
2. 图片保存失败时没有详细日志，难以排查
3. 路径处理不够健壮

### 问题2：文档数据未加载
**原因**：
1. `/status` API 返回的数据结构中不包含 `parsed_docs`
2. 前端 `openDocumentDetail()` 函数从 `integratedStatus.value?.parsed_docs` 读取数据
3. 数据缺失导致无法找到文档

---

## 解决方案

### ✅ 修复1：改进图片保存路径逻辑

**文件**：`backend/app/services/document_parser_service.py`

**修改内容**：

```python
def extract_images_from_docx(self, doc_obj) -> List[Dict[str, str]]:
    """从文档对象中提取图片并保存"""
    images = []
    try:
        # 获取当前文件所在目录，向上两级到达backend目录
        current_file = Path(__file__)
        backend_dir = current_file.parent.parent.parent  # backend/
        save_dir = backend_dir / "static" / "images" / "extracted"
        
        # 确保目录存在
        try:
            save_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"图片保存目录: {save_dir}")
        except Exception as e:
            logger.error(f"无法创建图片保存目录: {e}")
            # 尝试备用路径
            try:
                save_dir = Path("/www/wwwroot/voxchina/backend/static/images/extracted")
                save_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"使用备用图片保存目录: {save_dir}")
            except Exception as e2:
                logger.error(f"无法创建备用图片保存目录: {e2}")
                return []
        # ... 其余代码保持不变
```

**改进点**：
- ✅ 使用 `Path(__file__)` 获取当前文件路径，计算相对路径
- ✅ 添加详细日志，记录图片保存目录
- ✅ 备用路径作为fallback
- ✅ 路径处理更加健壮

---

### ✅ 修复2：API返回 parsed_docs 数据

**文件**：`backend/app/api/v1/endpoints/integrated_voiceover.py`

**修改内容**：

```python
@router.get("/status/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    查询任务状态
    
    返回任务的当前状态、进度和当前步骤
    包含 parsed_docs 用于文档详情查看
    """
    try:
        task_data = integrated_voiceover_service.get_task_status(task_id)
        
        if not task_data:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 如果任务完成，返回完整结果
        result = None
        if task_data["status"] == "completed":
            result = integrated_voiceover_service.get_task_result(task_id)
        
        # 构建响应，包含 parsed_docs
        response = {
            "task_id": task_id,
            "status": task_data["status"],
            "progress": task_data["progress"],
            "current_step": task_data["current_step"],
            "error": task_data.get("error"),
            "result": result,
            "parsed_docs": task_data.get("parsed_docs", [])  # ✅ 添加 parsed_docs
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(status_code=500, detail=f"查询任务状态失败: {str(e)}")
```

**改进点**：
- ✅ 移除了严格的 `response_model=IntegratedVoiceoverStatus` 限制
- ✅ 在响应中添加 `parsed_docs` 字段
- ✅ 保持向后兼容，不影响其他字段

---

### ✅ 修复3：统一文档数据结构

**文件**：`backend/app/services/document_parser_service.py`

**问题**：不同文档格式返回的数据结构不一致
- DOCX 返回：`images`（有）、`total_tables`（无）
- PDF 返回：`images`（无）、`total_tables`（无）

**修改内容**：

#### DOCX 解析改进
```python
# 处理表格内容
table_count = 0
for table_idx, table in enumerate(doc.tables):
    table_count += 1
    # ... 处理表格行

logger.info(f"Parsed DOCX: {len(paragraphs)} paragraphs, {table_count} tables, {len(extracted_images)} images, title: {title[:50]}")

return {
    "title": title,
    "total_paragraphs": len(paragraphs),
    "total_tables": table_count,  # ✅ 添加表格数量
    "paragraphs": paragraphs,
    "images": extracted_images,
    "format": "docx"
}
```

#### PDF 解析改进
```python
return {
    "title": title,
    "total_paragraphs": len(paragraphs),
    "paragraphs": paragraphs,
    "images": [],  # ✅ PDF暂不支持图片提取，返回空数组
    "total_tables": 0,  # ✅ PDF表格数量
    "format": "pdf"
}
```

**改进点**：
- ✅ 所有文档格式返回统一的数据结构
- ✅ 确保前端访问 `doc.images` 和 `doc.total_tables` 不会出错
- ✅ 添加更详细的日志信息

---

## 测试验证

### 测试场景1：图片提取
1. ✅ 上传包含图片的 Word 文档
2. ✅ 检查后端日志，确认图片保存目录
3. ✅ 检查 `static/images/extracted/` 目录，确认图片文件存在
4. ✅ 在 Visual Assets 页面查看图片是否正常显示

### 测试场景2：文档详情查看
1. ✅ 上传多个文档，等待处理完成
2. ✅ 在 Structure 页面点击 RELATED DOCUMENTS
3. ✅ 确认文档详情模态框正常打开
4. ✅ 确认显示文档标题、段落、图片等信息
5. ✅ 在 Evidence Ledger 点击"查看原文"和"↗ 原文"按钮
6. ✅ 确认能正确打开对应文档

### 测试场景3：不同文档格式
1. ✅ 测试 DOCX 文档（带图片、表格）
2. ✅ 测试 PDF 文档（纯文本）
3. ✅ 确认两种格式都能正常处理，不出现错误

---

## 部署说明

### 1. 确保目录权限
```bash
# 确保图片保存目录有写权限
mkdir -p /www/wwwroot/voxchina/backend/static/images/extracted
chmod 755 /www/wwwroot/voxchina/backend/static/images/extracted
```

### 2. 重启后端服务
```bash
# 使用 supervisor 重启
sudo supervisorctl restart voxchina

# 或使用提供的脚本
cd /www/wwwroot/voxchina/backend
./quick_restart.sh
```

### 3. 检查日志
```bash
# 查看实时日志
tail -f /www/wwwroot/voxchina/backend/logs/voxchina.log

# 查找图片相关日志
grep "图片保存目录" /www/wwwroot/voxchina/backend/logs/voxchina.log
grep "Extracted.*images" /www/wwwroot/voxchina/backend/logs/voxchina.log
```

---

## 技术细节

### 修改的文件
1. `backend/app/api/v1/endpoints/integrated_voiceover.py` - API endpoint
2. `backend/app/services/document_parser_service.py` - 文档解析服务

### API 变更
- ✅ `/status/{task_id}` 现在返回 `parsed_docs` 字段
- ✅ 保持向后兼容，不影响现有客户端

### 数据结构变更
- ✅ 所有文档解析结果包含 `images` 和 `total_tables` 字段
- ✅ DOCX 返回实际的图片和表格数据
- ✅ PDF 返回空数组和0

---

## 后续优化建议

### 短期（1-2周）
1. **图片格式转换**：统一转换为 WebP 格式，减小文件大小
2. **图片压缩**：对大图进行压缩，提高加载速度
3. **缓存机制**：添加图片缓存，避免重复提取

### 中期（1-2个月）
1. **PDF图片支持**：实现 PDF 文档的图片提取
2. **图片OCR**：对图片中的文字进行识别
3. **缩略图生成**：自动生成缩略图，提高列表页加载速度

### 长期（3-6个月）
1. **云存储**：将图片存储到云端（OSS/S3）
2. **CDN加速**：使用 CDN 加速图片访问
3. **图片管理**：实现图片的版本管理和清理机制

---

## 相关文档

- [INTEGRATED_VOICEOVER_IMPROVEMENTS_20260119.md](./INTEGRATED_VOICEOVER_IMPROVEMENTS_20260119.md) - 主要功能改进
- [INTEGRATED_VOICEOVER_FEATURE.md](./INTEGRATED_VOICEOVER_FEATURE.md) - 功能说明
- [INTEGRATED_VOICEOVER_IMPLEMENTATION.md](./INTEGRATED_VOICEOVER_IMPLEMENTATION.md) - 实现细节

---

## 问题追踪

| 问题 | 状态 | 修复日期 | 备注 |
|------|------|----------|------|
| Image not extracted | ✅ 已修复 | 2026-01-19 | 改进图片保存路径逻辑 |
| Document data not loaded | ✅ 已修复 | 2026-01-19 | API返回parsed_docs |
| 数据结构不统一 | ✅ 已修复 | 2026-01-19 | 统一DOCX和PDF返回值 |

---

## 作者信息

**开发者**: Ren CBIT  
**GitHub**: https://github.com/reneverland/  
**修复日期**: 2026-01-19  
**版本**: v1.1.0
