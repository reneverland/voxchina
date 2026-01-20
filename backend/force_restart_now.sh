#!/bin/bash
# VoxChina 强制重启脚本 - 需要 root 权限执行
# 使用方法: sudo ./force_restart_now.sh

set -e

echo "=========================================="
echo "VoxChina Backend Force Restart"
echo "=========================================="

cd /www/wwwroot/voxchina/backend

# 1. 清理缓存
echo "[1/5] Cleaning Python cache..."
find /www/wwwroot/voxchina/backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find /www/wwwroot/voxchina/backend -name "*.pyc" -delete 2>/dev/null || true
echo "✅ Cache cleaned"

# 2. 强制杀掉旧进程
echo "[2/5] Force killing old processes..."
pkill -9 -f "uvicorn main:app.*8300" 2>/dev/null || echo "No old process found"
sleep 3
echo "✅ Old processes killed"

# 3. 确认端口已释放
echo "[3/5] Checking port 8300..."
if lsof -i :8300 2>/dev/null | grep -q LISTEN; then
    echo "❌ Port 8300 still in use!"
    lsof -i :8300
    exit 1
fi
echo "✅ Port 8300 is free"

# 4. 启动新进程
echo "[4/5] Starting new backend process..."
cd /www/wwwroot/voxchina/backend
su - www -c "cd /www/wwwroot/voxchina/backend && nohup ./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8300 --workers 1 --log-level info > /tmp/voxchina_backend_new.log 2>&1 &"
sleep 5
echo "✅ New process started"

# 5. 验证启动成功
echo "[5/5] Verifying backend health..."
if curl -s http://localhost:8300/health | grep -q "ok"; then
    NEW_PID=$(ps aux | grep "uvicorn main:app.*8300" | grep -v grep | awk '{print $2}')
    echo "✅ Backend is healthy (PID: $NEW_PID)"
    echo "=========================================="
    echo "Restart completed successfully!"
    echo "Log file: /tmp/voxchina_backend_new.log"
    echo "=========================================="
else
    echo "❌ Backend health check failed!"
    echo "Check logs: tail -n 50 /tmp/voxchina_backend_new.log"
    exit 1
fi
