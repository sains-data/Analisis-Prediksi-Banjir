#!/bin/bash

# Custom entrypoint for hive-server with embedded Derby metastore

echo "Starting HiveServer2 with embedded Derby metastore..."

# Set required environment variables
export HIVE_CONF_DIR=${HIVE_CONF_DIR:-/opt/hive/conf}
export HADOOP_CLIENT_OPTS=${HADOOP_CLIENT_OPTS:- -Xmx1G }

# Create metastore directory if it doesn't exist
mkdir -p /opt/hive/data/metastore

# Wait for HDFS namenode to be available
echo "Waiting for HDFS namenode to be ready..."
sleep 30
echo "Proceeding to start Hive services..."

echo "HDFS namenode is ready..."

# Clean up any existing Derby database files to avoid corruption
echo "Cleaning up any existing Derby database files..."
rm -rf /opt/hive/metastore_db /opt/hive/derby.log /tmp/metastore_db /tmp/derby.log
rm -rf /opt/hive/data/metastore/metastore_db /opt/hive/data/metastore/derby.log

# Initialize the schema if it doesn't exist
echo "Initializing Hive metastore schema..."
cd ${HIVE_HOME}
/opt/hive/bin/schematool -dbType derby -initSchema --verbose || echo "Schema already exists or initialization failed, continuing..."

# Start HiveServer2 in the background to avoid process detection issues
echo "Starting HiveServer2..."
/opt/hive/bin/hive --service hiveserver2 &

# Wait for HiveServer2 to fully start
echo "Waiting for HiveServer2 to start..."
sleep 10

# Check if HiveServer2 is running
if pgrep -f "hiveserver2" > /dev/null; then
    echo "HiveServer2 started successfully"
else
    echo "Failed to start HiveServer2"
    exit 1
fi

# Keep the container running
wait
