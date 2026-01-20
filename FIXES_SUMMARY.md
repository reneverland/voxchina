# VoxChina 问题修复总结
**日期**: 2026-01-14  
**修复人**: AI Assistant

---

## 🔧 已修复的问题

### 1. Academic Extract 功能 500 错误 ✅

**问题描述**:
- Academic Extract 提取后报错
- 多个 API 端点返回 500 错误（config, extracts, voices, extract）
- 保存到知识库时报错：`Embedding service unavailable`

**根本原因**:
- Qdrant 数据库配置文件与新版 `qdrant-client` (1.16.0) 不兼容
- `knowledge_service` 初始化失败，导致所有依赖它的功能崩溃

**解决方案**:
1. 修改 `backend/app/services/knowledge_service.py`
   - 添加自动检测和清理损坏数据库的逻辑
   - 当初始化失败时自动删除旧数据并重建

2. 创建修复脚本 `backend/fix_and_restart.sh`
   - 停止后端服务
   - 清理 qdrant_data 目录
   - 重启服务

**执行步骤**:
```bash
cd /www/wwwroot/voxchina/backend
sudo bash fix_and_restart.sh
```

---

### 2. Knowledge Database "View Details" 按钮无效 ✅

**问题描述**:
- 点击 "View Details" 按钮没有任何反应

**根本原因**:
- 按钮缺少 `@click` 事件绑定
- 没有实现对应的处理函数

**解决方案**:
1. 修改 `frontend/src/views/MainPage.vue`
   - 添加 `@click="viewKnowledgeDetail(doc)"` 到按钮
   - 实现 `viewKnowledgeDetail()` 函数，显示文档详细信息

**修改文件**:
- `frontend/src/views/MainPage.vue` (行 1043, 2561-2609)

---

### 3. 音频生成失败 (500 错误) ✅

**问题描述**:
- TTS 音频生成失败
- 错误信息：`Generation failed: 500 - {"detail":"500: Audio generation failed"}`

**根本原因**:
- `/api/v1/voices/preview` 端点对空 `voice_id` 处理不当
- 当用户未选择声音时，应该使用默认声音，但代码直接返回 404 错误

**解决方案**:
1. 修改 `backend/app/api/v1/endpoints/voices.py`
   - 允许空 `voice_id`，使用默认基础声音
   - 改进错误处理和日志记录
   - 当指定的 voice_id 不存在时，降级到默认声音而不是报错

**修改文件**:
- `backend/app/api/v1/endpoints/voices.py` (行 62-97)

---

## 📝 需要执行的操作

### 必须执行（修复 Qdrant 数据库问题）:

```bash
# 1. 执行修复脚本（需要 root 权限）
cd /www/wwwroot/voxchina/backend
sudo bash fix_and_restart.sh

# 2. 验证服务健康
curl http://localhost:8300/health
# 应该返回: {"status":"ok"}

# 3. 测试 knowledge service
curl http://localhost:8300/api/v1/knowledge/list
# 应该返回空数组或文档列表，不应该是 500 错误
```

### 前端代码已修复（自动生效）:

前端代码修改会在下次访问页面时自动生效（如果使用了热重载）。
如果需要强制刷新：
```bash
# 清除浏览器缓存或使用 Ctrl+Shift+R 强制刷新页面
```

---

## 🧪 测试验证

### 1. 测试 Academic Extract
1. 上传一个学术文章（DOCX/PDF）
2. 点击 "Start Extraction"
3. 等待提取完成
4. 点击 "Save to Knowledge Base"
5. 应该成功保存，不再报 embedding 错误

### 2. 测试 Knowledge Database
1. 切换到 "Knowledge Database" 标签
2. 应该能看到已保存的文档
3. 点击 "View Details" 按钮
4. 应该弹出详细信息对话框

### 3. 测试音频生成
1. 在 Academic Extract 结果页面
2. 选择一个声音（或不选择，使用默认）
3. 点击 "Generate Audio"
4. 应该成功生成音频，不再报 500 错误

---

## 📁 修改的文件清单

### 后端文件:
1. `backend/app/services/knowledge_service.py` - 添加自动修复逻辑
2. `backend/app/api/v1/endpoints/voices.py` - 修复音频生成 API
3. `backend/fix_and_restart.sh` - 新建修复脚本
4. `backend/cleanup_qdrant.sh` - 新建清理脚本
5. `backend/test_tts_import.py` - 新建 TTS 诊断脚本

### 前端文件:
1. `frontend/src/views/MainPage.vue` - 修复 View Details 按钮

---

## ⚠️ 注意事项

1. **数据丢失警告**: 执行 `fix_and_restart.sh` 会删除现有的知识库数据。如果有重要数据，请先备份 `backend/qdrant_data/` 目录。

2. **权限要求**: 修复脚本需要 root 权限才能停止和重启服务。

3. **服务中断**: 修复过程中后端服务会短暂中断（约 10-15 秒）。

4. **TTS 模型**: 首次使用 TTS 功能时，模型会自动加载，可能需要 10-30 秒。

---

## 🔍 故障排查

### 如果修复脚本执行失败:

```bash
# 查看详细日志
tail -50 /tmp/voxchina_restart.log

# 手动检查进程
ps aux | grep uvicorn

# 手动检查端口
lsof -i :8300

# 手动重启
cd /www/wwwroot/voxchina/backend
pkill -9 -f "uvicorn.*8300"
su - www -c "cd /www/wwwroot/voxchina/backend && nohup ./venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8300 --workers 1 &"
```

### 如果音频生成仍然失败:

```bash
# 运行 TTS 诊断
cd /www/wwwroot/voxchina/backend
./venv/bin/python3 test_tts_import.py

# 检查模型文件
ls -la OpenVoice/checkpoints_v2/converter/
# 应该看到 config.json 和 checkpoint.pth
```

---

## 📞 联系信息

如有问题，请查看：
- 后端日志: `/www/wwwroot/voxchina/backend/logs/`
- 浏览器控制台: F12 -> Console
- 服务器日志: `journalctl -u voxchina` (如果使用 systemd)

---

**修复完成时间**: 2026-01-14 12:10  
**状态**: ✅ 所有代码修改完成，等待执行修复脚本
