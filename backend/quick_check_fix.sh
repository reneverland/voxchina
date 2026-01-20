#!/bin/bash
# 快速检查修复是否生效

echo "========================================"
echo "Quick Check: LLM Method Fix"
echo "========================================"

cd /www/wwwroot/voxchina/backend

# 1. 检查语法
echo -e "\n1. Checking Python syntax..."
python3 -c "import ast; ast.parse(open('app/services/integrated_voiceover_service.py').read())" 2>&1
if [ $? -eq 0 ]; then
  echo "   ✅ Syntax OK"
else
  echo "   ❌ Syntax Error"
  exit 1
fi

# 2. 检查导入
echo -e "\n2. Checking import..."
python3 -c "from app.services.integrated_voiceover_service import integrated_voiceover_service; print('   ✅ Import OK')" 2>&1
if [ $? -ne 0 ]; then
  echo "   ❌ Import Failed"
  exit 1
fi

# 3. 检查方法存在
echo -e "\n3. Checking LLM method..."
python3 -c "
from app.services.llm_service import llm_service
if hasattr(llm_service, '_generate_with_provider'):
    print('   ✅ _generate_with_provider exists')
else:
    print('   ❌ _generate_with_provider NOT found')
    exit(1)
    
if hasattr(llm_service, 'call_llm'):
    print('   ⚠️  call_llm exists (should not)')
else:
    print('   ✅ call_llm does not exist (correct)')
" 2>&1

# 4. 检查服务是否运行
echo -e "\n4. Checking if service is running..."
if ps aux | grep -q "[u]vicorn.*8300"; then
  echo "   ✅ Service is running on port 8300"
  PID=$(ps aux | grep "[u]vicorn.*8300" | awk '{print $2}' | head -1)
  echo "   PID: $PID"
  
  # 检查服务启动时间
  START_TIME=$(ps -p $PID -o lstart= 2>/dev/null)
  echo "   Started: $START_TIME"
  
  # 检查是否需要重启（如果启动时间早于文件修改时间）
  FILE_MOD_TIME=$(stat -c %Y app/services/integrated_voiceover_service.py 2>/dev/null || stat -f %m app/services/integrated_voiceover_service.py 2>/dev/null)
  PROC_START_TIME=$(stat -c %Y /proc/$PID 2>/dev/null || echo "0")
  
  if [ "$FILE_MOD_TIME" -gt "$PROC_START_TIME" ]; then
    echo "   ⚠️  Service was started BEFORE code was modified"
    echo "   ⚠️  Please restart the service!"
  else
    echo "   ✅ Service is up to date"
  fi
else
  echo "   ❌ Service is NOT running!"
  echo "   Please start the service"
fi

# 5. 测试API端点
echo -e "\n5. Testing API endpoint..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8300/api/v1/health 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
  echo "   ✅ API is responding (HTTP $HTTP_CODE)"
else
  echo "   ⚠️  API returned HTTP $HTTP_CODE"
fi

echo -e "\n========================================"
echo "Check completed!"
echo "========================================"
echo -e "\nNext steps:"
echo "1. If service needs restart: supervisorctl restart voxchina"
echo "2. Refresh browser (Ctrl+F5)"
echo "3. Test the integrated voiceover feature"
