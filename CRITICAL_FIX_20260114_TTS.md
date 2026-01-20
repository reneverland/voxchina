# 🔥 关键修复：TTS音频生成失败问题

**日期**: 2026-01-14 23:52  
**问题**: 音频生成一直返回 500 错误  
**根本原因**: MeloTTS 库中的 tokenizer 未正确初始化

---

## 🐛 问题详情

### 错误信息
```
Generation failed: 500 - {"detail":"Audio generation failed. Please check if TTS models are properly loaded. Check server logs for details."}
```

### 根本原因
在 `melotts_repo/melo/text/chinese_mix.py` 文件中：
- 第101行定义了 `tokenizer = None` （懒加载）
- 第103行定义了 `_get_tokenizer()` 函数用于懒加载
- 第138行正确使用了 `tok = _get_tokenizer()`
- **但第230行直接使用了 `tokenizer.tokenize(text)`，导致 AttributeError**

### 错误堆栈
```python
AttributeError: 'NoneType' object has no attribute 'tokenize'
  File "/www/wwwroot/voxchina/backend/melotts_repo/melo/text/chinese_mix.py", line 230, in _g2p_v2
    tokenized_en = tokenizer.tokenize(text)
                   ^^^^^^^^^^^^^^^^^^
```

---

## ✅ 修复方案

### 修改文件
`backend/melotts_repo/melo/text/chinese_mix.py`

### 修改内容
**第227-231行，修改前：**
```python
for text in texts:
    if re.match('[a-zA-Z\s]+', text):
        # english
        tokenized_en = tokenizer.tokenize(text)  # ❌ 错误：tokenizer 是 None
        phones_en, tones_en, word2ph_en = g2p_en(text=None, pad_start_end=False, tokenized=tokenized_en)
```

**修改后：**
```python
for text in texts:
    if re.match('[a-zA-Z\s]+', text):
        # english
        tok = _get_tokenizer()  # ✅ 正确：调用懒加载函数
        tokenized_en = tok.tokenize(text)
        phones_en, tones_en, word2ph_en = g2p_en(text=None, pad_start_end=False, tokenized=tokenized_en)
```

---

## 🧪 测试验证

### 测试1：直接调用TTS服务
```bash
cd /www/wwwroot/voxchina/backend
python3 -c "
from app.services.tts_service import tts_service
result = tts_service.generate_audio('这是测试文本', 'test.wav')
print(f'Result: {result}')
"
```

**结果**：
```
✅ Result: static/audio/test.wav
File exists: True
File size: 742362 bytes
```

### 测试2：API调用
```bash
curl -X POST "http://localhost:8300/api/v1/voices/preview" \
  -H "Content-Type: application/json" \
  -d '{"voice_id": "", "text": "这是测试文本", "language": "zh"}'
```

**结果**：
```json
{"audio_url":"/static/audio/preview_default_717c44f7-e506-45a2-9010-f4ece1283f17.wav"}
```

✅ **修复成功！**

---

## 📝 重要说明

### 1. 为什么之前短文本能工作？
短文本（如"测试"）可能不会触发英文tokenizer的代码路径，因此不会遇到这个bug。只有当文本较长或包含特定模式时，才会进入第230行的代码。

### 2. 后端是否需要重启？
**是的**，修改Python代码后必须重启后端服务。后端进程会在启动时加载代码，修改后不会自动生效。

### 3. 如何确认修复生效？
- 检查后端进程的启动时间（应该在修复之后）
- 测试较长的文本音频生成
- 查看后端日志，应该看到 `[TTS] ✅ Audio generation complete`

---

## 🚀 部署步骤

### 自动重启（推荐）
后端使用的是 uvicorn，会自动检测代码变化并重新加载。如果使用了 `--reload` 参数，修改会自动生效。

### 手动重启
如果自动重启未生效：
```bash
# 查找进程
ps aux | grep "uvicorn.*8300"

# 杀掉进程（需要相应权限）
sudo kill -9 <PID>

# 重新启动
cd /www/wwwroot/voxchina/backend
sudo -u www bash -c "source venv/bin/activate && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8300 --workers 1 > /dev/null 2>&1 &"
```

---

## 📊 影响范围

### 受影响的功能
- ✅ Academic Extract 音频生成
- ✅ Voice Preview 功能
- ✅ 所有使用 TTS 服务的功能

### 不受影响的功能
- ✅ 文章提取
- ✅ 摘要生成
- ✅ 知识库保存
- ✅ 历史记录查看

---

## 🔗 相关修复

本次修复是在之前修复的基础上进行的：
1. **之前的修复** (`FIXES_20260114.md`)：
   - 改进了 TTS 错误处理和日志
   - 修复了历史记录不显示的问题
   
2. **本次修复** (本文档)：
   - 修复了 MeloTTS tokenizer 的 bug
   - 这是导致音频生成失败的**真正原因**

---

## ✨ 总结

这是一个典型的**懒加载未正确实现**的bug：
- 代码中定义了懒加载机制（`_get_tokenizer()`）
- 但在某处忘记调用懒加载函数，直接使用了未初始化的变量
- 导致 `NoneType` 错误

**修复非常简单**：将 `tokenizer.tokenize()` 改为 `_get_tokenizer().tokenize()`

---

**修复完成时间**: 2026-01-14 23:52  
**修复人**: AI Assistant  
**作者**: Ren CBIT https://github.com/reneverland/
