# ⚠️ 紧急：需要重启后端服务

**问题**: Extraction History 显示 "No history available"

**原因**: 后端代码已修复（metadata → payload），但服务还没有重启

**后端进程启动时间**: Jan 14（昨天）  
**代码修复时间**: Jan 15（今天）

---

## 🚨 必须执行的操作

### 重启后端服务

请选择以下任一方法重启：

#### 方法1：使用快速重启脚本（推荐）
```bash
cd /www/wwwroot/voxchina/backend
bash quick_restart.sh
```

#### 方法2：手动重启
```bash
# 1. 找到进程ID
ps aux | grep "uvicorn.*8300" | grep -v grep

# 2. 停止进程
kill -9 <PID>

# 3. 启动新进程
cd /www/wwwroot/voxchina/backend
source venv/bin/activate
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8300 --workers 1 > /dev/null 2>&1 &
```

#### 方法3：使用sudo（如果有权限）
```bash
cd /www/wwwroot/voxchina/backend
sudo bash restart_as_www.sh
```

---

## ✅ 验证重启成功

重启后执行：
```bash
ps aux | grep "uvicorn.*8300" | grep -v grep
```

应该看到新的进程，启动时间是今天（Jan 15）

---

## 🔍 为什么会这样？

1. **已修复的代码**:
   - `backend/app/api/v1/endpoints/academic_extract.py`
   - 将 `doc.get("metadata", {})` 改为 `doc.get("payload", {})`

2. **但服务未重启**:
   - Python 代码在进程启动时加载
   - 修改代码后必须重启进程才能生效
   - 当前进程是昨天启动的，还在使用旧代码

3. **知识库有数据**:
   - `/www/wwwroot/voxchina/backend/qdrant_data/collection/voxchina_knowledge`
   - 最后更新：Jan 15 00:17
   - 数据是存在的，只是旧代码读取字段名错误

---

## 📝 重启后的预期结果

重启后，访问前端 Academic Extract 页面：
- ✅ Extraction History 显示所有提取记录
- ✅ 可以点击查看详情
- ✅ 可以删除历史记录
- ✅ 音频不会自动播放
- ✅ 导航栏显示 "Academic Extract"

---

**创建时间**: 2026-01-15 00:20  
**重要性**: 🔴 紧急 - 必须重启后端才能看到历史记录
