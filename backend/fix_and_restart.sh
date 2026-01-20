#!/bin/bash
# Fix Qdrant database and restart VoxChina backend
# Run with: sudo bash fix_and_restart.sh

set -e

echo "=========================================="
echo "VoxChina Backend Fix & Restart"
echo "=========================================="

cd /www/wwwroot/voxchina/backend

# Step 1: Stop backend
echo "[1/5] Stopping backend service..."
pkill -9 -f "uvicorn main:app.*8300" 2>/dev/null || echo "No process to kill"
sleep 2
echo "✅ Backend stopped"

# Step 2: Clean Qdrant data
echo "[2/5] Cleaning corrupted Qdrant data..."
if [ -d "qdrant_data" ]; then
    rm -rf qdrant_data
    echo "✅ Old data removed"
fi
mkdir -p qdrant_data
chown -R www:www qdrant_data
echo "✅ Fresh directory created"

# Step 3: Clean Python cache
echo "[3/5] Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
echo "✅ Cache cleaned"

# Step 4: Start backend
echo "[4/5] Starting backend service..."
su - www -c "cd /www/wwwroot/voxchina/backend && nohup ./venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8300 --workers 1 > /tmp/voxchina_restart.log 2>&1 &"
sleep 5
echo "✅ Backend started"

# Step 5: Verify
echo "[5/5] Verifying backend health..."
for i in {1..10}; do
    if curl -s http://localhost:8300/health | grep -q "ok"; then
        PID=$(ps aux | grep "[u]vicorn main:app.*8300" | awk '{print $2}')
        echo "✅ Backend is healthy! (PID: $PID)"
        echo "=========================================="
        echo "Fix completed successfully!"
        echo "Log: /tmp/voxchina_restart.log"
        echo "=========================================="
        exit 0
    fi
    echo "Waiting... ($i/10)"
    sleep 2
done

echo "❌ Backend health check failed!"
echo "Check logs: tail -50 /tmp/voxchina_restart.log"
exit 1
