#!/bin/bash

# Backup script for Big Data ecosystem

BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Creating backup in: $BACKUP_DIR"

# Backup HDFS data
echo "Backing up HDFS data..."
docker exec namenode hdfs dfs -get /data "$BACKUP_DIR/hdfs_data"

# Backup Hive metastore
echo "Backing up Hive metastore..."
docker exec hive-metastore mysqldump -h localhost -u hive -phive123 metastore > "$BACKUP_DIR/hive_metastore.sql"

# Backup HBase
echo "Backing up HBase..."
docker exec hbase-master hbase org.apache.hadoop.hbase.mapreduce.Export flood_predictions "$BACKUP_DIR/hbase_export"

# Backup configurations
echo "Backing up configurations..."
cp -r config/ "$BACKUP_DIR/config"
cp -r scripts/ "$BACKUP_DIR/scripts"
cp docker-compose.yml "$BACKUP_DIR/"

echo "Backup completed: $BACKUP_DIR"
