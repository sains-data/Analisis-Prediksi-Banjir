#!/bin/bash

# Script to restart Hive service and clean Derby locks
# Usage: ./restart_hive.sh

echo "🔄 Restarting Hive service to fix Derby metastore issues..."

# Stop Hive container
echo "📦 Stopping Hive container..."
docker-compose stop hive-server

# Clean up Derby lock files
echo "🧹 Cleaning Derby lock files..."
rm -rf ./hive/data/metastore/metastore_db
rm -rf ./hive/data/metastore/derby.log
mkdir -p ./hive/data/metastore

# Start Hive container
echo "🚀 Starting Hive container..."
docker-compose up -d hive-server

# Wait for service to be ready
echo "⏳ Waiting for Hive to be ready..."
sleep 30

# Test connection
echo "🔍 Testing Hive connection..."
docker exec hive-server /opt/hive/bin/beeline -u jdbc:hive2://localhost:10000 -e "SHOW DATABASES;" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Hive is ready!"
    echo "📋 You can now connect using: docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000"
else
    echo "❌ Hive connection failed. Check logs with: docker logs hive-server"
fi
