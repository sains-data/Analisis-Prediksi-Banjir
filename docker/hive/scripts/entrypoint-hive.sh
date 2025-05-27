#!/bin/bash

# Custom entrypoint for hive-server with embedded Derby metastore

echo "Starting HiveServer2 with embedded Derby metastore..."

# Set required environment variables
export HIVE_CONF_DIR=${HIVE_CONF_DIR:-/opt/hive/conf}
export HADOOP_CLIENT_OPTS=${HADOOP_CLIENT_OPTS:- -Xmx1G }
export DERBY_HOME=/opt/derby

# Create metastore directory if it doesn't exist
mkdir -p /opt/hive/data/metastore

# Wait for HDFS namenode to be available
echo "Waiting for HDFS namenode to be ready..."
sleep 30

# Check if namenode is accessible
until hdfs dfs -test -d / 2>/dev/null; do
    echo "Waiting for HDFS namenode..."
    sleep 5
done
echo "HDFS namenode is ready..."

# Clean up any existing Derby database files to avoid corruption
echo "Cleaning up any existing Derby database files..."
rm -rf /opt/hive/metastore_db /opt/hive/derby.log 
rm -rf /tmp/metastore_db /tmp/derby.log
rm -rf /opt/hive/data/metastore/metastore_db /opt/hive/data/metastore/derby.log
rm -rf /opt/derby-metastore/*

# Set proper permissions for Derby directory
mkdir -p /opt/derby-metastore
chmod 755 /opt/derby-metastore

# Initialize the schema if it doesn't exist
echo "Initializing Hive metastore schema..."
cd ${HIVE_HOME}

# Try to initialize schema, but don't fail if it already exists
/opt/hive/bin/schematool -dbType derby -initSchema --verbose 2>/dev/null || {
    echo "Schema initialization failed or already exists, attempting to upgrade..."
    /opt/hive/bin/schematool -dbType derby -upgradeSchema --verbose 2>/dev/null || {
        echo "Schema upgrade failed, continuing anyway..."
    }
}

# Start HiveServer2 with proper logging
echo "Starting HiveServer2..."
exec /opt/hive/bin/hive --service hiveserver2 \
    --hiveconf hive.server2.enable.doAs=false \
    --hiveconf hive.security.authorization.enabled=false \
    --hiveconf javax.jdo.option.ConnectionURL="jdbc:derby:/opt/hive/metastore_db;create=true" \
    --hiveconf datanucleus.connectionPoolingType=None \
    --hiveconf datanucleus.autoCreateSchema=true \
    --hiveconf datanucleus.autoCreateTables=true \
    --hiveconf datanucleus.autoCreateColumns=true \
    --hiveconf datanucleus.fixedDatastore=false