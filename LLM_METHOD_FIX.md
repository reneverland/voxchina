# LLM Method Fix - call_llm 不存在

**错误**: 'LLMService' object has no attribute 'call_llm'  
**修复日期**: 2026-01-17  
**状态**: ✅ 已修复

---

## 问题分析

### 错误信息
```
Generation failed
'LLMService' object has no attribute 'call_llm'
```

### 根本原因

在 `integrated_voiceover_service.py` 中使用了不存在的方法：
```python
# ❌ 错误的方法调用
response = await llm_service.call_llm(
    prompt=prompt,
    model_type="openai",
    temperature=0.3
)
```

但 `LLMService` 类实际的方法是：
```python
# ✅ 正确的方法
async def _generate_with_provider(
    self, 
    prompt: str, 
    timeout: float = 60.0, 
    model: str = None, 
    system_prompt: str = None
) -> str:
```

---

## 已修复内容

### 修复方式

将所有 `call_llm()` 调用替换为 `_generate_with_provider()`:

**修复前** ❌:
```python
response = await llm_service.call_llm(
    prompt=prompt,
    model_type="openai",
    temperature=0.3
)
```

**修复后** ✅:
```python
response = await llm_service._generate_with_provider(
    prompt=prompt,
    timeout=120.0
)
```

### 修改位置

在 `integrated_voiceover_service.py` 中的4处调用：
1. ✅ `_generate_style_profile()` - Line 242
2. ✅ `_build_evidence_ledger()` - Line 321
3. ✅ `_select_structure()` - Line 481
4. ✅ `_generate_script_review()` - Line 584

---

## 验证修复

### 1. 语法检查
```bash
cd /home/dell/workspace_links/wwwroot/voxchina/backend
python3 -c "import ast; ast.parse(open('app/services/integrated_voiceover_service.py').read())"
# 应该输出：✅ Syntax OK
```

### 2. 导入测试
```bash
cd /home/dell/workspace_links/wwwroot/voxchina/backend
python3 -c "from app.services.integrated_voiceover_service import integrated_voiceover_service; print('✅ Import OK')"
```

### 3. 方法验证
```bash
cd /home/dell/workspace_links/wwwroot/voxchina/backend
python3 -c "
from app.services.llm_service import llm_service
print('✅ LLM Service methods:')
print([m for m in dir(llm_service) if not m.startswith('_') and callable(getattr(llm_service, m))])
print('\n✅ _generate_with_provider exists:', hasattr(llm_service, '_generate_with_provider'))
"
```

---

## 后端重启（必需）

修改代码后**必须重启**后端服务：

### 方法1: Supervisor（推荐）
```bash
# 查看服务状态
supervisorctl status

# 重启voxchina服务
supervisorctl restart voxchina

# 查看日志
supervisorctl tail -f voxchina stdout
```

### 方法2: 手动重启
```bash
# 查找并杀死进程
ps aux | grep "uvicorn.*8300"
kill -9 [PID]

# 重新启动
cd /www/wwwroot/voxchina/backend
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8300 --workers 1 >> logs/uvicorn.log 2>&1 &
```

### 方法3: 使用现有脚本（如果有）
```bash
cd /www/wwwroot/voxchina/backend
./restart.sh  # 或类似的重启脚本
```

---

## 完整测试流程

### 1️⃣ 重启后端
```bash
supervisorctl restart voxchina
```

### 2️⃣ 检查日志
```bash
tail -f /www/wwwroot/voxchina/backend/logs/voxchina_*.log
# 或
supervisorctl tail -f voxchina stdout
```

查看是否有启动错误

### 3️⃣ 刷新前端
- 在浏览器中按 `Ctrl + F5` 强制刷新

### 4️⃣ 测试功能
1. 登录系统
2. 点击 "Integrated Voiceover"
3. 上传一个小的Word文档
4. 填写主题
5. 点击"开始生成"

### 5️⃣ 观察结果

**✅ 成功的标志**:
- Console显示: `[Integrated] Task created: {task_id: "..."}`
- 进度条开始移动
- 显示当前步骤更新
- 最终完成或显示具体错误（不是"call_llm"错误）

**❌ 如果还有问题**:
- 查看Console错误信息
- 检查后端日志
- 确认后端已重启

---

## 常见问题

### Q1: 修复后仍报同样的错误

**原因**: 后端没有重启，还在使用旧代码

**解决**:
```bash
# 强制重启
supervisorctl restart voxchina

# 检查进程
ps aux | grep "uvicorn.*8300"
```

### Q2: 后端启动失败

**原因**: 可能有语法错误或其他问题

**解决**:
```bash
# 检查语法
cd /www/wwwroot/voxchina/backend
python3 -c "from app.services.integrated_voiceover_service import integrated_voiceover_service"

# 查看详细错误
python3 -m uvicorn main:app --host 0.0.0.0 --port 8300
```

### Q3: LLM调用失败

**原因**: LLM配置问题

**解决**:
```bash
# 检查LLM配置
cat /www/wwwroot/voxchina/backend/llm_config.json

# 测试LLM连接
cd /www/wwwroot/voxchina/backend
python3 -c "
import asyncio
from app.services.llm_service import llm_service
async def test():
    result = await llm_service._generate_with_provider('test prompt')
    print('✅ LLM works:', result[:50])
asyncio.run(test())
"
```

---

## 技术细节

### LLMService 实际方法

```python
class LLMService:
    # ✅ 可用的方法
    async def _generate_with_provider(self, prompt, timeout=60.0, model=None, system_prompt=None)
    async def generate_summary(self, content, max_words=200, language="zh")
    async def integrate_articles(self, contents, max_words=500, focus=None, language="zh")
    async def answer_query(self, query, context_texts, language="zh")
    async def generate_trending_post(self, topic, web_context, local_context, language="zh")
    async def generate_video_script(self, content, language="zh")
    
    # ❌ 不存在的方法
    # call_llm()  <- 这个方法不存在！
```

### 参数映射

| 旧参数 (call_llm) | 新参数 (_generate_with_provider) |
|------------------|----------------------------------|
| prompt | prompt ✅ |
| model_type | (自动使用配置的provider) |
| temperature | (固定在方法内部) |
| max_tokens | (固定在方法内部) |
| - | timeout (新增，默认60秒) |

---

## 总结

### 问题
- ❌ 使用了不存在的`call_llm`方法
- ❌ 后端启动时没有报错（延迟到运行时）
- ❌ 前端显示错误信息不清晰

### 解决方案
- ✅ 替换为正确的`_generate_with_provider`方法
- ✅ 统一参数格式
- ✅ 增加timeout到120秒（处理大文档）

### 影响范围
- ✅ 仅影响integrated_voiceover功能
- ✅ 不影响其他功能
- ✅ 向后兼容

---

## 验证清单

- [ ] 代码语法检查通过
- [ ] 后端成功重启
- [ ] 前端页面已刷新
- [ ] 上传测试文档
- [ ] 任务成功创建
- [ ] 进度正常更新
- [ ] 最终生成成功或显示清晰错误

---

**重要**: 记得重启后端服务！代码修改后必须重启才能生效。

---

**开发团队**: VoxChina AI Team  
**修复日期**: 2026-01-17  
**版本**: 1.1.3 (LLM Method Fix)
