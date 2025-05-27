# Flood Analytics with PySpark Guide

This guide explains how to run the improved flood analytics pipeline using PySpark in a Docker environment.

## Overview

The flood analytics pipeline processes flood-related data using Apache Spark. The main script `improved_flood_analytics.py` has been optimized to work with timestamp-based data and provides comprehensive flood analytics capabilities.

## Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available for containers
- Git (for cloning)

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/sains-data/Analisis-Prediksi-Banjir.git
cd Analisis-Prediksi-Banjir
```

### 2. Start Infrastructure (Full Stack)
```bash
# Start all services (HDFS, Spark, Hive, etc.)
docker-compose up -d

# Or start minimal stack (HDFS + Spark only)
docker-compose -f docker-compose-minimal.yml up -d
```

### 3. Verify Services
```bash
# Check all containers are running
docker ps

# Check Spark Master UI
# Open http://localhost:8080 in browser

# Check HDFS UI
# Open http://localhost:9870 in browser
```

### 4. Run Flood Analytics

#### Option A: Using Spark Submit (Recommended)
```bash
# Copy script to Spark master container and run
docker exec -it spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --conf spark.sql.adaptive.enabled=true \
  --conf spark.sql.adaptive.coalescePartitions.enabled=true \
  /opt/spark/work-dir/improved_flood_analytics.py
```

#### Option B: Interactive Python Session
```bash
# Access Spark master container
docker exec -it spark-master bash

# Run the analytics script
cd /opt/spark/work-dir
python3 improved_flood_analytics.py
```

## Configuration Files

### Spark Configuration (`clean-spark-defaults.conf`)
```properties
# Minimal Spark Configuration for Flood Analytics
spark.master                     spark://spark-master:7077
spark.app.name                   FloodAnalytics

# Driver Configuration
spark.driver.memory              1g
spark.driver.cores               1
spark.driver.maxResultSize       512m

# Executor Configuration
spark.executor.memory            1g
spark.executor.cores             1
spark.executor.instances         2

# SQL Configuration
spark.sql.adaptive.enabled                    true
spark.sql.adaptive.coalescePartitions.enabled true
spark.sql.catalogImplementation               in-memory

# HDFS Configuration
spark.hadoop.fs.defaultFS                   hdfs://namenode:8020
```

## Data Structure

### Input Data Location
- Raw data: `./data/raw/`
- Processed data: `./data/processed/`
- Sample data: `./data/sample/`

### Expected Data Format
The script expects CSV files with the following columns:
- `timestamp`: Date/time information
- `location`: Geographic location
- `water_level`: Water level measurements
- `rainfall`: Rainfall data
- Other meteorological parameters

## Script Features

### `improved_flood_analytics.py`
This script includes:

1. **Data Loading**: Reads CSV files from HDFS or local filesystem
2. **Data Cleaning**: Handles missing values and data type conversions
3. **Timestamp Processing**: Correctly processes timestamp columns
4. **Flood Analytics**: 
   - Water level trend analysis
   - Rainfall pattern analysis
   - Flood risk assessment
   - Statistical summaries
5. **Results Export**: Saves processed results to HDFS

### Key Improvements Made
- ✅ Fixed column name references (changed from "date" to "timestamp")
- ✅ Added proper import statements for Spark functions
- ✅ Fixed indentation issues
- ✅ Optimized for timestamp-based data processing

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│      HDFS       │───▶│   Spark Cluster │
│                 │    │   (Storage)     │    │   (Processing)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                              ┌─────────────────┐
                                              │     Results     │
                                              │   (Analytics)   │
                                              └─────────────────┘
```

## Monitoring

### Spark Web UIs
- **Spark Master**: http://localhost:8080
- **Spark Worker**: http://localhost:8081
- **Spark Application**: http://localhost:4040 (when job is running)

### HDFS Web UI
- **NameNode**: http://localhost:9870
- **DataNode**: http://localhost:9864

## Troubleshooting

### Common Issues

#### 1. Container Memory Issues
```bash
# Increase Docker memory allocation to at least 4GB
# Check Docker Desktop settings
```

#### 2. Port Conflicts
```bash
# Check if ports are already in use
netstat -an | findstr "8080\|7077\|9870"

# Stop conflicting services or change ports in docker-compose.yml
```

#### 3. Data Loading Issues
```bash
# Check if data files exist
docker exec -it spark-master ls -la /opt/spark/data/

# Check HDFS status
docker exec -it namenode hdfs dfsadmin -report
```

#### 4. Spark Job Failures
```bash
# Check Spark logs
docker logs spark-master
docker logs spark-worker-1

# Check application logs in Spark UI
# http://localhost:4040
```

### Performance Tuning

#### For Large Datasets
```bash
# Increase executor memory and cores in clean-spark-defaults.conf
spark.executor.memory            2g
spark.executor.cores             2
spark.executor.instances         4

# Enable dynamic allocation
spark.dynamicAllocation.enabled  true
spark.dynamicAllocation.minExecutors 1
spark.dynamicAllocation.maxExecutors 10
```

## Development

### Adding New Analytics Functions
1. Edit `scripts/improved_flood_analytics.py`
2. Follow the existing pattern for data processing
3. Test with sample data first
4. Use proper error handling and logging

### Sample Code Structure
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, isnan, count, countDistinct

def create_spark_session():
    return SparkSession.builder \
        .appName("FloodAnalytics") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()

def load_data(spark, file_path):
    return spark.read.csv(file_path, header=True, inferSchema=True)

def analyze_flood_data(df):
    # Your analytics logic here
    return results
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Test your changes with the Docker environment
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section above
- Review Spark logs in the web UI
- Open an issue on the GitHub repository
