# "Task processing failed - undefined" 错误修复

**问题**: Generation failed, Task processing failed, error is "undefined"  
**修复日期**: 2026-01-17  
**状态**: ✅ 已修复error字段传递问题

---

## 问题分析

### 错误信息
```
Generation failed
Task processing failed
[Integrated] Task failed: – undefined
```

### 根本原因
**IntegratedVoiceoverStatus模型缺少error字段**

在后端模型定义中：
```python
class IntegratedVoiceoverStatus(BaseModel):
    task_id: str
    status: str
    progress: int
    current_step: str
    result: Optional[IntegratedVoiceoverResponse] = None
    # ❌ 缺少 error 字段！
```

导致：
1. 任务失败时，后端设置了`task_data["error"]`
2. 但返回IntegratedVoiceoverStatus时没有包含error字段
3. 前端收到的status对象中error是undefined
4. 显示"Task processing failed - undefined"

---

## 已修复内容

### 1. 后端Schema修复 ✅

**文件**: `backend/app/models/schemas.py`

```python
class IntegratedVoiceoverStatus(BaseModel):
    task_id: str
    status: str
    progress: int  # 0-100
    current_step: str  # Step0/StepA/StepA2/StepB/StepC/StepD
    error: Optional[str] = None  # ✅ 新增：错误信息（仅在failed时）
    result: Optional[IntegratedVoiceoverResponse] = None
```

### 2. 后端API修复 ✅

**文件**: `backend/app/api/v1/endpoints/integrated_voiceover.py`

```python
return IntegratedVoiceoverStatus(
    task_id=task_id,
    status=task_data["status"],
    progress=task_data["progress"],
    current_step=task_data["current_step"],
    error=task_data.get("error"),  # ✅ 新增：传递错误信息
    result=result
)
```

### 3. 前端错误处理增强 ✅

**文件**: `frontend/src/views/MainPage.vue`

```javascript
} else if (status.status === 'failed') {
  console.error('[Integrated] Task failed!');
  console.error('[Integrated] Error details:', status);
  const errorMsg = status.error || status.result?.error || 'Task processing failed (no error details)';
  console.error('[Integrated] Error message:', errorMsg);
  integratedError.value = errorMsg;
  stopIntegratedPolling();
}
```

---

## 调试步骤

### 1. 检查Console日志

刷新页面后，重新测试功能，观察Console输出：

**正常情况** (任务成功):
```
[Integrated] Submitting task to: ...
[Integrated] Response status: 200
[Integrated] Task created: {task_id: "..."}
[Integrated] Status update: {"status":"processing","progress":5,...}
[Integrated] Status update: {"status":"processing","progress":20,...}
...
[Integrated] Task completed!
```

**错误情况** (任务失败):
```
[Integrated] Submitting task to: ...
[Integrated] Response status: 200
[Integrated] Task created: {task_id: "..."}
[Integrated] Status update: {"status":"processing","progress":5,...}
[Integrated] Task failed!
[Integrated] Error details: {status:"failed",error:"具体错误信息"}
[Integrated] Error message: 具体错误信息
```

### 2. 使用测试脚本

运行提供的测试脚本：
```bash
bash /home/dell/workspace_links/wwwroot/voxchina/test_api_integrated.sh
```

观察输出，查看：
- ✅ Token是否获取成功
- ✅ Task是否创建成功
- ✅ Status是否正常返回
- ❌ Error信息是什么

### 3. 查看后端日志

```bash
# 实时监控后端日志
tail -f /www/wwwroot/voxchina/backend/logs/voxchina_*.log

# 或者使用supervisor日志
tail -f /var/log/supervisor/voxchina-stdout.log
tail -f /var/log/supervisor/voxchina-stderr.log
```

---

## 常见错误原因

### 错误1: 文档解析失败

**症状**: Task fails at "Parsing" step  
**原因**: 
- 文档格式不支持或损坏
- 文件太大
- 编码问题

**解决**:
```python
# 检查文档解析服务
from app.services.document_parser_service import document_parser_service
# 测试解析
```

### 错误2: LLM调用失败

**症状**: Task fails at "Step0", "StepA", etc.  
**原因**:
- LLM API配置错误
- API密钥无效
- 网络连接问题
- Rate limit

**解决**:
```bash
# 检查LLM配置
cat /www/wwwroot/voxchina/backend/llm_config.json

# 测试LLM连接
cd /www/wwwroot/voxchina/backend
python3 -c "from app.services.llm_service import llm_service; import asyncio; asyncio.run(llm_service.call_llm('test', 'openai', 0.1))"
```

### 错误3: 内存不足

**症状**: Task fails randomly  
**原因**: 大文件处理时内存不足

**解决**:
```bash
# 检查内存使用
free -h
top -p $(pgrep -f "uvicorn.*8300")
```

---

## 后端重启（如需要）

如果修改了后端代码，需要重启：

```bash
# 方法1: 使用supervisor
cd /www/wwwroot/voxchina/backend
supervisorctl restart voxchina

# 方法2: 手动重启
pkill -f "uvicorn.*8300"
cd /www/wwwroot/voxchina/backend
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8300 --workers 1 &
```

---

## 验证修复

### 步骤1: 刷新前端
- 刷新浏览器页面 (Ctrl+F5)
- 确保加载最新代码

### 步骤2: 测试简单任务
- 上传1个小的Word文档 (<1MB)
- 主题: "Test"
- 观察Console输出

### 步骤3: 检查错误信息
如果仍然失败，现在应该看到**具体的错误信息**而不是"undefined"

---

## 期望结果

### 修复前 ❌
```
Error message: undefined
UI显示: Task processing failed
Console: [Integrated] Task failed: – undefined
```

### 修复后 ✅
```
Error message: 具体的错误描述（例如：Failed to parse document: Invalid file format）
UI显示: 具体的错误描述
Console: [Integrated] Task failed!
         [Integrated] Error message: 具体的错误描述
```

---

## 如果问题仍然存在

### 收集信息

1. **浏览器Console完整日志**
   - 打开DevTools (F12)
   - Console tab
   - 复制所有[Integrated]相关的日志

2. **Task ID**
   - 从UI或Console获取

3. **后端日志**
   ```bash
   tail -100 /www/wwwroot/voxchina/backend/logs/voxchina_*.log | grep -A 10 "Task.*failed"
   ```

4. **手动查询任务状态**
   ```bash
   TOKEN="your_token_here"
   TASK_ID="your_task_id_here"
   
   curl -X GET "http://localhost:8300/api/v1/integrated-voiceover/status/$TASK_ID" \
     -H "Authorization: Bearer $TOKEN" | jq
   ```

---

## 总结

### 修复内容
- ✅ 添加error字段到IntegratedVoiceoverStatus模型
- ✅ API端点返回error信息
- ✅ 前端增强错误处理和日志
- ✅ 提供测试脚本和调试工具

### 下一步
1. 刷新页面重新测试
2. 查看Console获取详细错误信息
3. 根据具体错误进行针对性修复

---

**开发团队**: VoxChina AI Team  
**修复日期**: 2026-01-17  
**版本**: 1.1.2 (Error Handling Fix)
