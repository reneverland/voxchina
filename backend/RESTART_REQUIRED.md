# ⚠️ 需要重启后端以应用修复

## 问题
`KeyError: '"type"'` 已经在代码中修复，但需要重启后端进程才能生效。

## 修复内容
✅ 添加了 `_sanitize_json_keys()` 方法来清理 LLM 返回的错误 JSON 键名
✅ 在 3 个关键位置调用了该方法
✅ 测试验证通过

## 重启方法（选择其中一种）

### 方法 1：SSH 重启（推荐）
```bash
# 切换到 www 用户
sudo su - www

# 杀掉旧进程
pkill -9 -f "uvicorn main:app.*8300"

# 启动新进程
cd /www/wwwroot/voxchina/backend
nohup ./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8300 --workers 1 --log-level info > backend.log 2>&1 &
exit
```

### 方法 2：使用已有脚本（如果有权限）
```bash
cd /www/wwwroot/voxchina/backend
sudo -u www ./force_restart.sh
```

### 方法 3：直接用 root 权限
```bash
# 杀掉旧进程
sudo pkill -9 -f "uvicorn main:app.*8300"

# 启动新进程
cd /www/wwwroot/voxchina/backend
sudo -u www nohup ./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8300 --workers 1 --log-level info > backend.log 2>&1 &
```

## 验证重启成功
```bash
# 检查进程启动时间（应该是最新的）
ps aux | grep "uvicorn main:app.*8300" | grep -v grep

# 检查健康状态
curl http://localhost:8300/health

# 查看启动日志
tail -n 50 /www/wwwroot/voxchina/backend/backend.log
```

## 重启后测试
访问 http://llmhi.com:8400/legacy 并尝试提取文章，`KeyError: '"type"'` 应该已经解决。

---
**修复时间**: 2026-01-11 22:44
**修改文件**: `/www/wwwroot/voxchina/backend/app/services/article_extract_service.py`
