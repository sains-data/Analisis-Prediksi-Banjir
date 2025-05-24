#!/bin/bash
# init_system.sh - Konfigurasi awal sistem prediksi banjir

echo "Initializing Flood Prediction System..."

# Wait for namenode to be ready
echo "Waiting for namenode to be ready..."
until docker exec namenode hdfs dfsadmin -safemode get | grep -q "Safe mode is OFF"; do
    echo "Waiting for namenode to leave safe mode..."
    docker exec namenode hdfs dfsadmin -safemode leave || true
    sleep 5
done

# Buat struktur direktori di HDFS
echo "Creating HDFS directory structure..."
docker exec namenode hdfs dfs -mkdir -p /data/raw/bmkg
docker exec namenode hdfs dfs -mkdir -p /data/raw/bnpb
docker exec namenode hdfs dfs -mkdir -p /data/raw/demnas
docker exec namenode hdfs dfs -mkdir -p /data/raw/iot
docker exec namenode hdfs dfs -mkdir -p /data/processing
docker exec namenode hdfs dfs -mkdir -p /data/serving
docker exec namenode hdfs dfs -mkdir -p /data/analytics/models
docker exec namenode hdfs dfs -mkdir -p /data/analytics/predictions
docker exec namenode hdfs dfs -mkdir -p /data/tmp/checkpoint

# Create HBase root directory
docker exec namenode hdfs dfs -mkdir -p /hbase

# Set permissions
docker exec namenode hdfs dfs -chmod -R 777 /data
docker exec namenode hdfs dfs -chmod -R 777 /hbase

echo "Initialization complete!"