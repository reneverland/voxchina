#!/bin/bash
# Quick Restart Script for VoxChina Backend
# 快速重启脚本

echo "=========================================="
echo "VoxChina Backend Quick Restart"
echo "=========================================="

# Find current process
PID=$(ps aux | grep "uvicorn.*8300" | grep -v grep | awk '{print $2}' | head -1)

if [ -z "$PID" ]; then
    echo "⚠️  No running process found"
else
    echo "[1/3] Stopping process (PID: $PID)..."
    kill -9 $PID 2>/dev/null
    sleep 2
    echo "✅ Process stopped"
fi

# Start new process
echo "[2/3] Starting new backend process..."
cd /www/wwwroot/voxchina/backend
source venv/bin/activate
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8300 --workers 1 > /dev/null 2>&1 &
NEW_PID=$!

sleep 3

# Verify
echo "[3/3] Verifying..."
if ps -p $NEW_PID > /dev/null; then
    echo "✅ Backend started successfully (PID: $NEW_PID)"
    echo ""
    echo "Backend is now running on http://localhost:8300"
else
    echo "❌ Failed to start backend"
    exit 1
fi

echo "=========================================="
echo "Restart completed!"
echo "=========================================="
