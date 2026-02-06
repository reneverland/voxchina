#!/bin/bash
# VoxChina Backend Startup Script
# 作者：Ren CBIT https://github.com/reneverland/

# 停止现有进程
pkill -9 -f "uvicorn main:app.*8300" 2>/dev/null
sleep 2

# 切换到后端目录
cd /www/wwwroot/voxchina/backend || exit 1

# 确保目录权限
mkdir -p /www/wwwroot/voxchina/backend/qdrant_data
mkdir -p /www/wwwroot/voxchina/backend/logs

# 清理锁文件
rm -f /www/wwwroot/voxchina/backend/qdrant_data/.lock 2>/dev/null

# 启动服务（不使用workers，避免多进程问题）
/www/wwwroot/voxchina/backend/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8300
