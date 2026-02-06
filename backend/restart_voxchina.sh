#!/bin/bash
# VoxChina Backend Restart Script
# 作者：Ren CBIT https://github.com/reneverland/

echo "正在停止 VoxChina Backend..."

# 停止所有 8300 端口的进程
pkill -9 -f "uvicorn main:app.*8300"

# 等待进程完全停止
sleep 3

# 清理锁文件
rm -f /www/wwwroot/voxchina/backend/qdrant_data/.lock

echo "进程已停止，正在重新启动..."

# 切换到后端目录并启动
cd /www/wwwroot/voxchina/backend
bash start_voxchina.sh &

echo "VoxChina Backend 重启完成！"
echo "请稍等几秒，然后访问 http://localhost:8300/api/v1/knowledge/tags 测试"
