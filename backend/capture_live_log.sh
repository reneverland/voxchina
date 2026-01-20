#!/bin/bash
# 捕获后端实时日志
echo "开始捕获日志，请在另一个窗口执行文本提取..."
echo "日志将保存到 /tmp/voxchina_live.log"
echo "按 Ctrl+C 停止"
echo "=========================================="

# 启动一个临时的日志捕获进程
strace -p 2965236 -e write -s 1000 2>&1 | grep -E "write\(1\|write\(2" > /tmp/voxchina_live.log &
STRACE_PID=$!

echo "Strace PID: $STRACE_PID"
echo "等待 30 秒..."
sleep 30

# 停止捕获
kill $STRACE_PID 2>/dev/null

echo "=========================================="
echo "日志已保存，显示最后 100 行："
tail -n 100 /tmp/voxchina_live.log
