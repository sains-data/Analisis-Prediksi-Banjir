#!/bin/bash
# Quick start script for Flood Analytics with Spark
# This script sets up and runs the flood analytics pipeline

set -e  # Exit on any error

echo "🌊 Flood Analytics with Spark - Quick Start"
echo "==========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

echo "✅ docker-compose is available"

# Function to wait for service to be ready
wait_for_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is ready!"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts - waiting..."
        sleep 10
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed to start within timeout"
    return 1
}

# Ask user which setup to use
echo ""
echo "Choose deployment option:"
echo "1) Full stack (HDFS + Spark + Hive + Kafka + etc.)"
echo "2) Minimal stack (HDFS + Spark only)"
echo ""
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        echo "🚀 Starting full stack deployment..."
        docker-compose up -d
        
        # Wait for key services
        wait_for_service "HDFS NameNode" "http://localhost:9870"
        wait_for_service "Spark Master" "http://localhost:8080"
        
        echo ""
        echo "🎉 Full stack is ready!"
        echo "📊 Access points:"
        echo "   - HDFS NameNode: http://localhost:9870"
        echo "   - Spark Master: http://localhost:8080"
        echo "   - YARN ResourceManager: http://localhost:8088"
        echo "   - Hive Server: http://localhost:10002"
        ;;
    2)
        echo "🚀 Starting minimal stack deployment..."
        docker-compose -f docker-compose-minimal.yml up -d
        
        # Wait for services
        wait_for_service "HDFS NameNode" "http://localhost:9870"
        wait_for_service "Spark Master" "http://localhost:8080"
        
        echo ""
        echo "🎉 Minimal stack is ready!"
        echo "📊 Access points:"
        echo "   - HDFS NameNode: http://localhost:9870"
        echo "   - Spark Master: http://localhost:8080"
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

# Validate the pipeline
echo ""
echo "🔍 Validating flood analytics pipeline..."
if docker exec spark-master python3 /opt/spark/work-dir/validate_pipeline.py; then
    echo ""
    echo "✅ Pipeline validation successful!"
    echo ""
    echo "🚀 Ready to run flood analytics!"
    echo ""
    echo "To run the improved flood analytics pipeline:"
    echo "docker exec -it spark-master /opt/spark/bin/spark-submit \\"
    echo "  --master spark://spark-master:7077 \\"
    echo "  /opt/spark/work-dir/improved_flood_analytics.py"
    echo ""
    echo "For detailed instructions, see: FLOOD_ANALYTICS_SPARK_GUIDE.md"
else
    echo "❌ Pipeline validation failed. Check the logs above."
    exit 1
fi
