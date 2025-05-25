#!/bin/bash

# ==============================================================================
# ANALISIS-PREDIKSI-BANJIR - FIRST TIME SETUP SCRIPT
# ==============================================================================
# This script sets up the complete Hadoop big data ecosystem for flood analysis
# Run this script after cloning the repository for the first time
# ==============================================================================

echo "🌊 Starting Analisis-Prediksi-Banjir Setup..."
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Check if Docker Compose is available
if ! docker-compose --version > /dev/null 2>&1; then
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker Compose is available"

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p data/{processed,serving}
mkdir -p hive/data
mkdir -p spark/data
mkdir -p notebooks/{data_exploration,model_development,visualization}

# Download PostgreSQL JDBC driver for Hive
echo "📦 Downloading PostgreSQL JDBC driver..."
if [ ! -f "postgresql-42.7.4.jar" ]; then
    curl -L -o postgresql-42.7.4.jar https://jdbc.postgresql.org/download/postgresql-42.7.4.jar
    echo "✅ PostgreSQL JDBC driver downloaded"
else
    echo "✅ PostgreSQL JDBC driver already exists"
fi

# Pull Docker images
echo "🐳 Pulling Docker images..."
docker-compose -f docker-compose-latest.yml pull

# Start the services
echo "🚀 Starting Hadoop ecosystem..."
docker-compose -f docker-compose-latest.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 30

# Check if namenode is running
echo "🔍 Checking Namenode status..."
if docker exec namenode hdfs dfsadmin -safemode get | grep -q "OFF"; then
    echo "✅ Namenode is ready"
else
    echo "⏳ Waiting for Namenode to exit safe mode..."
    sleep 30
fi

# Format namenode if needed (only on first run)
echo "🔧 Checking if namenode needs formatting..."
if ! docker exec namenode test -d /opt/hadoop/dfs/name/current; then
    echo "🔧 Formatting namenode..."
    docker exec namenode hdfs namenode -format -force -clusterId hadoop-cluster
    echo "✅ Namenode formatted"
    
    # Restart namenode after formatting
    docker-compose -f docker-compose-latest.yml restart namenode
    sleep 20
fi

# Create HDFS directories
echo "📁 Creating HDFS directory structure..."
docker exec namenode hdfs dfs -mkdir -p /analisis-prediksi-banjir/data/raw
docker exec namenode hdfs dfs -mkdir -p /analisis-prediksi-banjir/data/processed
docker exec namenode hdfs dfs -mkdir -p /analisis-prediksi-banjir/data/serving
docker exec namenode hdfs dfs -mkdir -p /user/hive/warehouse

echo "✅ HDFS directories created"

# Install PostgreSQL JDBC driver in Hive containers
echo "🔧 Installing PostgreSQL JDBC driver in Hive containers..."
docker cp postgresql-42.7.4.jar hive-metastore:/opt/hive/lib/postgresql-jdbc.jar
docker cp postgresql-42.7.4.jar hive-server:/opt/hive/lib/postgresql-jdbc.jar

# Restart Hive services to load the driver
echo "🔄 Restarting Hive services..."
docker-compose -f docker-compose-latest.yml restart hive-metastore hive-server

# Wait for Hive services
echo "⏳ Waiting for Hive services to start..."
sleep 45

# Display service status
echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================"
echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose-latest.yml ps

echo ""
echo "🌐 Web Interfaces:"
echo "• Hadoop Namenode:      http://localhost:9870"
echo "• YARN ResourceManager: http://localhost:8088"
echo "• Spark Master:         http://localhost:8080"
echo "• HBase Master:         http://localhost:16010"
echo "• Jupyter Lab:          http://localhost:8888"
echo "• Apache Superset:      http://localhost:8089"

echo ""
echo "🔧 Useful Commands:"
echo "• Check HDFS status:    docker exec namenode hdfs dfsadmin -report"
echo "• Access Hive CLI:      docker exec -it hive-server hive"
echo "• Check YARN nodes:     docker exec resourcemanager yarn node -list"
echo "• View logs:            docker-compose -f docker-compose-latest.yml logs [service]"

echo ""
echo "📂 Sample data can be uploaded to: /analisis-prediksi-banjir/data/raw/"
echo ""
echo "✅ Your Hadoop big data ecosystem is ready for flood analysis! 🌊"
