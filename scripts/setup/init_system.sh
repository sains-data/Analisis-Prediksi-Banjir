#!/bin/bash
# init_system.sh - Konfigurasi awal sistem prediksi banjir

echo "Initializing Flood Prediction System..."

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

# Set permissions
docker exec namenode hdfs dfs -chmod -R 777 /data

# Buat Kafka topics
echo "Creating Kafka topics..."
docker exec kafka kafka-topics --create --bootstrap-server kafka:9092 --replication-factor 1 --partitions 3 --topic weather-stream
docker exec kafka kafka-topics --create --bootstrap-server kafka:9092 --replication-factor 1 --partitions 5 --topic iot-sensors
docker exec kafka kafka-topics --create --bootstrap-server kafka:9092 --replication-factor 1 --partitions 1 --topic flood-alerts

echo "Initialization complete!"