#!/bin/bash
# VoxChina 后端重启脚本 (www 用户执行)
# 使用方法: sudo -u www ./restart_as_www.sh

echo "=========================================="
echo "VoxChina Backend Restart (www user)"
echo "=========================================="

cd /www/wwwroot/voxchina/backend

# 1. 清理缓存
echo "[1/4] Cleaning cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
echo "✅ Cache cleaned"

# 2. 停止旧进程
echo "[2/4] Stopping old process..."
OLD_PID=$(ps aux | grep "uvicorn main:app.*8300" | grep -v grep | awk '{print $2}')
if [ -n "$OLD_PID" ]; then
    echo "Found PID: $OLD_PID"
    kill -9 $OLD_PID 2>/dev/null
    sleep 2
    echo "✅ Process stopped"
else
    echo "No old process found"
fi

# 3. 等待端口释放
echo "[3/4] Waiting for port 8300..."
sleep 3

# 4. 启动新进程
echo "[4/4] Starting new process..."
nohup ./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8300 --workers 1 --log-level info > backend.log 2>&1 &
NEW_PID=$!
sleep 3

# 验证
if curl -s http://localhost:8300/health > /dev/null 2>&1; then
    echo "✅ Backend started successfully (PID: $NEW_PID)"
    echo "=========================================="
else
    echo "❌ Backend failed to start, check backend.log"
    echo "=========================================="
    exit 1
fi
