#!/bin/bash
# Cleanup corrupted Qdrant data
# This script should be run as the www user

echo "Cleaning up Qdrant data..."
cd /www/wwwroot/voxchina/backend

if [ -d "qdrant_data" ]; then
    echo "Removing qdrant_data directory..."
    rm -rf qdrant_data
    echo "✅ qdrant_data removed"
else
    echo "qdrant_data directory does not exist"
fi

echo "Creating fresh qdrant_data directory..."
mkdir -p qdrant_data
echo "✅ Fresh directory created"

echo "Done! Please restart the backend service."
