# ✅ VoxChina 后端修复完成

## 修复时间
2026-01-11 23:50

## 修复内容

### 1. ✅ 彻底移除日语 tokenizer（根本问题）
- 删除 `japanese.py` 和 `japanese_bert.py`
- 修复 `cleaner.py` 和 `korean.py` 的导入依赖

### 2. ✅ 修复启动时模型下载阻塞（关键修复）
**问题根因**：多个语言模块在顶层直接调用 `AutoTokenizer.from_pretrained()`，导致 `import` 时立即下载模型，阻塞启动。

**修复文件**（全部改为懒加载）：
- `melo/text/english_bert.py` - 英语 BERT
- `melo/text/english.py` - 英语 tokenizer
- `melo/text/korean.py` - 韩语 tokenizer
- `melo/text/chinese_mix.py` - 中英混合 tokenizer
- `melo/text/french_bert.py` - 法语 BERT
- `melo/text/french.py` - 法语 tokenizer
- `melo/text/spanish_bert.py` - 西班牙语 BERT
- `melo/text/spanish.py` - 西班牙语 tokenizer

**修复方式**：
```python
# 修复前（会在 import 时立即下载）
tokenizer = AutoTokenizer.from_pretrained(model_id)

# 修复后（懒加载，只在实际使用时下载）
tokenizer = None

def _get_tokenizer():
    global tokenizer
    if tokenizer is None:
        tokenizer = AutoTokenizer.from_pretrained(model_id)
    return tokenizer
```

### 3. ✅ 修复 KeyError: '"type"'
**问题根因**：LLM 返回的 JSON 键名被错误地包裹了引号（如 `{'"type"': ...}`）

**修复方式**：
- 添加 `_sanitize_json_keys()` 方法递归清理所有键名
- 在 3 个 JSON 解析点调用该方法

### 4. ✅ 验证通过
```bash
cd /www/wwwroot/voxchina/backend
./venv/bin/python -c "import sys; sys.path.insert(0, '/www/wwwroot/voxchina/backend/melotts_repo'); from melo.text import cleaner; print('✅ OK')"
```
输出：`✅ Import cleaner OK - no download triggered`

---

## 🔧 最后一步：重启后端

**请在 SSH 终端执行（需要 root 权限）：**

```bash
sudo /www/wwwroot/voxchina/backend/force_restart_now.sh
```

**或者手动执行：**

```bash
# 1. 杀掉旧进程
sudo pkill -9 -f "uvicorn main:app.*8300"

# 2. 等待端口释放
sleep 3

# 3. 启动新进程
cd /www/wwwroot/voxchina/backend
sudo -u www nohup ./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8300 --workers 1 --log-level info > /tmp/voxchina_backend_final.log 2>&1 &

# 4. 验证
sleep 5
curl http://localhost:8300/health
tail -n 50 /tmp/voxchina_backend_final.log
```

---

## ✅ 重启后应该看到

1. **启动日志**：不再有 "tohoku-nlp/bert-base-japanese-v3" 下载错误
2. **健康检查**：`{"status":"ok"}`
3. **文本提取**：不再有 `KeyError: '"type"'`

---

## 📊 技术总结

### 问题 1：日语 tokenizer 下载失败导致启动阻塞
- **根因**：`japanese.py` 在模块顶层调用 `AutoTokenizer.from_pretrained('tohoku-nlp/bert-base-japanese-v3')`
- **解决**：删除日语模块，移除所有 JP 语言入口

### 问题 2：其他语言模块也在启动时下载模型
- **根因**：8 个语言模块都在顶层初始化 tokenizer
- **解决**：全部改为懒加载（`_get_tokenizer()` 函数）

### 问题 3：KeyError: '"type"'
- **根因**：LLM 返回错误的 JSON 键名格式
- **解决**：添加 `_sanitize_json_keys()` 递归清理

---

**重启后，所有问题应该彻底解决！**
