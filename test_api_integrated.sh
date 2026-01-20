#!/bin/bash
# 测试Integrated Voiceover API

echo "==================================="
echo "Testing Integrated Voiceover API"
echo "==================================="

# 获取token
echo -e "\n1. Getting auth token..."
TOKEN=$(curl -s -X POST "http://localhost:8300/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get token"
  exit 1
fi
echo "✅ Got token: ${TOKEN:0:20}..."

# 创建测试文件
echo -e "\n2. Creating test file..."
cat > /tmp/test_doc.txt << 'EOF'
Test Document for Integrated Voiceover

Introduction
This is a test document to verify the integrated voiceover functionality.

Data Analysis
In 2020, China's digital economy reached 39.2 trillion yuan.
This represents 38.6% of total GDP.
The growth rate was 9.7% year-over-year.

Conclusion
The digital economy continues to be a major driver of economic growth.
EOF
echo "✅ Test file created"

# 测试create端点
echo -e "\n3. Testing create endpoint..."
RESPONSE=$(curl -s -X POST "http://localhost:8300/api/v1/integrated-voiceover/create" \
  -H "Authorization: Bearer $TOKEN" \
  -F "topic_hint=Test Topic: China Digital Economy" \
  -F "speaker_affiliation=VoxChina" \
  -F "speaker_name=Test Speaker" \
  -F "include_vox_intro=true" \
  -F "language=zh" \
  -F "files=@/tmp/test_doc.txt")

echo "Response: $RESPONSE"

TASK_ID=$(echo $RESPONSE | grep -o '"task_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$TASK_ID" ]; then
  echo "❌ Failed to create task"
  echo "Full response: $RESPONSE"
  exit 1
fi

echo "✅ Task created: $TASK_ID"

# 等待并检查状态
echo -e "\n4. Checking task status..."
for i in {1..10}; do
  echo "  Check $i/10..."
  STATUS_RESPONSE=$(curl -s -X GET "http://localhost:8300/api/v1/integrated-voiceover/status/$TASK_ID" \
    -H "Authorization: Bearer $TOKEN")
  
  echo "  $STATUS_RESPONSE"
  
  STATUS=$(echo $STATUS_RESPONSE | grep -o '"status":"[^"]*' | cut -d'"' -f4)
  PROGRESS=$(echo $STATUS_RESPONSE | grep -o '"progress":[0-9]*' | cut -d':' -f2)
  
  echo "  Status: $STATUS, Progress: $PROGRESS%"
  
  if [ "$STATUS" = "completed" ]; then
    echo "✅ Task completed!"
    break
  elif [ "$STATUS" = "failed" ]; then
    echo "❌ Task failed!"
    ERROR=$(echo $STATUS_RESPONSE | grep -o '"error":"[^"]*' | cut -d'"' -f4)
    echo "Error: $ERROR"
    break
  fi
  
  sleep 3
done

# 清理
rm -f /tmp/test_doc.txt

echo -e "\n==================================="
echo "Test completed"
echo "==================================="
