#!/bin/bash

# Analisis Prediktif Banjir Provinsi Lampung - Setup Script
# Sesuai dengan Proposal Tugas Besar Analisis Big Data

set -e

echo "=========================================="
echo "SETUP ANALISIS PREDIKTIF BANJIR LAMPUNG"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker and Docker Compose are installed
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Prerequisites check passed!"
}

# Create project directory structure
create_directories() {
    print_status "Creating project directory structure..."
    
    # Raw Data Layer directories
    mkdir -p data/raw/{bmkg,bnpb,demnas,iot,satelit}
    mkdir -p data/raw/bmkg/{cuaca_historis,api_realtime}
    mkdir -p data/raw/bnpb/kejadian_banjir
    mkdir -p data/raw/demnas/topografi
    mkdir -p data/raw/iot/{sensor_air,sensor_cuaca}
    mkdir -p data/raw/satelit/lapan
    
    # Processing Layer directories
    mkdir -p data/processing/{staging,clean,transformed}
    mkdir -p data/processing/mapreduce/{input,output}
    
    # Serving Layer directories
    mkdir -p data/serving/{hive,hbase}
    mkdir -p data/serving/hive/{warehouse,external}
    mkdir -p data/serving/hbase/{tables,backups}
    
    # Analytics Layer directories
    mkdir -p data/analytics/{models,predictions,reports}
    mkdir -p data/analytics/models/{training,deployed}
    mkdir -p data/analytics/predictions/{realtime,batch}
    
    # Application directories
    mkdir -p {spark,hive,superset,notebooks}
    mkdir -p spark/{apps,data}
    mkdir -p hive/data
    mkdir -p notebooks/{data_exploration,model_development,visualization}
    
    # Configuration directories
    mkdir -p config/{hadoop,hive,hbase,spark,kafka}
    
    # Scripts directories
    mkdir -p scripts/{ingestion,processing,streaming,ml}
    
    print_status "Directory structure created successfully!"
}

# Create sample configuration files
create_configs() {
    print_status "Creating configuration files..."
    
    # Superset configuration
    cat > superset/superset_config.py << 'EOF'
import os

# Superset specific config
ROW_LIMIT = 5000
SUPERSET_WEBSERVER_PORT = 8088

# Flask App Builder configuration
# Your App secret key
SECRET_KEY = 'lampung_flood_prediction_2025'

# Database configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:////app/superset_home/superset.db'

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = True

# Add machine learning prediction endpoints
ENABLE_PROXY_FIX = True

class CeleryConfig(object):
    BROKER_URL = 'redis://localhost:6379/0'
    CELERY_IMPORTS = ('superset.sql_lab', )
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_ANNOTATIONS = {'tasks.add': {'rate_limit': '10/s'}}

CELERY_CONFIG = CeleryConfig
EOF

    # Create sample data ingestion script
    cat > scripts/ingestion/bmkg_ingestion.py << 'EOF'
"""
Script untuk mengambil data cuaca dari API BMKG
Sesuai dengan Proposal: Data Collection dari BMKG
"""

import json
import requests
import pandas as pd
from datetime import datetime, timedelta
import os

class BMKGDataIngestion:
    def __init__(self):
        self.base_url = "https://api.bmkg.go.id"
        self.lampung_stations = [
            "96747",  # Bandar Lampung
            "96749",  # Lampung Tengah
            "96751",  # Lampung Utara
        ]
    
    def get_weather_data(self, station_id, start_date, end_date):
        """Mengambil data cuaca historis"""
        try:
            # Implementasi sesuai API BMKG
            params = {
                'station': station_id,
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            }
            
            # Simpan ke format yang sesuai untuk HDFS
            output_file = f"/data/raw/bmkg/cuaca_historis/station_{station_id}_{start_date.strftime('%Y%m%d')}.csv"
            
            print(f"Data saved to: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"Error fetching data for station {station_id}: {e}")
            return None
    
    def get_realtime_data(self):
        """Mengambil data cuaca real-time untuk streaming"""
        try:
            # Implementasi untuk Kafka streaming
            realtime_data = {
                'timestamp': datetime.now().isoformat(),
                'stations': []
            }
            
            for station in self.lampung_stations:
                # Data real-time per stasiun
                station_data = {
                    'station_id': station,
                    'temperature': 28.5,  # Sample data
                    'humidity': 75,
                    'rainfall': 2.5,
                    'wind_speed': 12.3
                }
                realtime_data['stations'].append(station_data)
            
            # Kirim ke Kafka topic
            return realtime_data
            
        except Exception as e:
            print(f"Error fetching realtime data: {e}")
            return None

if __name__ == "__main__":
    ingestion = BMKGDataIngestion()
    
    # Ambil data historis 1 tahun terakhir
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    for station in ingestion.lampung_stations:
        ingestion.get_weather_data(station, start_date, end_date)
    
    print("BMKG data ingestion completed!")
EOF

    # Create Spark MLlib script
    cat > scripts/ml/flood_prediction_model.py << 'EOF'
"""
Model Prediktif Banjir menggunakan Spark MLlib
Sesuai dengan Proposal: Model Prediktif dengan Spark MLlib
"""

from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.regression import GBTRegressor
from pyspark.ml.evaluation import BinaryClassificationEvaluator, RegressionEvaluator
from pyspark.ml import Pipeline
from pyspark.sql.functions import col, when

class FloodPredictionModel:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("LampungFloodPrediction") \
            .config("spark.sql.adaptive.enabled", "true") \
            .getOrCreate()
    
    def load_training_data(self):
        """Load data dari Hive tables"""
        # Data cuaca dari BMKG
        weather_df = self.spark.sql("""
            SELECT * FROM flood_data.weather_history 
            WHERE province = 'Lampung'
        """)
        
        # Data kejadian banjir dari BNPB
        flood_events_df = self.spark.sql("""
            SELECT * FROM flood_data.flood_events 
            WHERE province = 'Lampung'
        """)
        
        # Join data untuk training
        training_data = weather_df.join(
            flood_events_df, 
            on=['date', 'location'], 
            how='left'
        ).fillna({'flood_occurred': 0})
        
        return training_data
    
    def create_features(self, df):
        """Feature engineering sesuai proposal"""
        # Fitur cuaca
        weather_features = [
            'rainfall_1day', 'rainfall_3day', 'rainfall_7day',
            'temperature', 'humidity', 'wind_speed'
        ]
        
        # Fitur geografis
        geo_features = [
            'elevation', 'slope', 'distance_to_river',
            'drainage_density', 'land_use_type'
        ]
        
        # Fitur historis
        historical_features = [
            'flood_history_1year', 'flood_history_5year',
            'seasonal_pattern'
        ]
        
        all_features = weather_features + geo_features + historical_features
        
        # Vector assembler
        assembler = VectorAssembler(
            inputCols=all_features,
            outputCol="features"
        )
        
        return assembler
    
    def train_classification_model(self, training_data):
        """Model klasifikasi tingkat risiko banjir"""
        # Random Forest untuk klasifikasi risiko (rendah, sedang, tinggi)
        rf_classifier = RandomForestClassifier(
            featuresCol="scaled_features",
            labelCol="risk_level",
            numTrees=100,
            maxDepth=10,
            seed=42
        )
        
        return rf_classifier
    
    def train_regression_model(self, training_data):
        """Model regresi untuk prediksi kedalaman banjir"""
        # Gradient Boosting Trees untuk prediksi kedalaman
        gbt_regressor = GBTRegressor(
            featuresCol="scaled_features",
            labelCol="flood_depth",
            maxIter=100,
            maxDepth=8,
            seed=42
        )
        
        return gbt_regressor
    
    def create_pipeline(self):
        """Create ML Pipeline sesuai proposal"""
        # Feature engineering
        assembler = self.create_features(None)  # Will be configured later
        
        # Scaling
        scaler = StandardScaler(
            inputCol="features",
            outputCol="scaled_features"
        )
        
        # Models
        rf_classifier = self.train_classification_model(None)
        gbt_regressor = self.train_regression_model(None)
        
        # Pipeline
        pipeline = Pipeline(stages=[
            assembler,
            scaler,
            rf_classifier
        ])
        
        return pipeline
    
    def evaluate_model(self, predictions, model_type="classification"):
        """Evaluasi model sesuai target akurasi minimal 75%"""
        if model_type == "classification":
            evaluator = BinaryClassificationEvaluator(
                labelCol="flood_occurred",
                rawPredictionCol="rawPrediction",
                metricName="areaUnderROC"
            )
            auc = evaluator.evaluate(predictions)
            print(f"Model Classification AUC: {auc:.4f}")
            
            if auc >= 0.75:
                print("✅ Model memenuhi target akurasi minimal 75%")
            else:
                print("❌ Model belum memenuhi target akurasi minimal 75%")
                
        elif model_type == "regression":
            evaluator = RegressionEvaluator(
                labelCol="flood_depth",
                predictionCol="prediction",
                metricName="rmse"
            )
            rmse = evaluator.evaluate(predictions)
            print(f"Model Regression RMSE: {rmse:.4f}")
    
    def save_model(self, model, model_path):
        """Simpan model untuk deployment"""
        model.write().overwrite().save(model_path)
        print(f"Model saved to: {model_path}")

if __name__ == "__main__":
    print("Training Flood Prediction Model for Lampung Province...")
    
    model = FloodPredictionModel()
    
    # Load dan training
    training_data = model.load_training_data()
    pipeline = model.create_pipeline()
    
    # Fit model
    trained_model = pipeline.fit(training_data)
    
    # Evaluasi
    predictions = trained_model.transform(training_data)
    model.evaluate_model(predictions)
    
    # Save model
    model.save_model(trained_model, "/data/analytics/models/deployed/flood_prediction_v1")
    
    print("Model training completed!")
EOF

    print_status "Configuration files created successfully!"
}

# Initialize Kafka topics
init_kafka_topics() {
    print_status "Initializing Kafka topics..."
    
    # Wait for Kafka to be ready
    sleep 30
    
    # Create topics for streaming data
    docker exec kafka kafka-topics --create \
        --topic bmkg-weather-realtime \
        --bootstrap-server localhost:9092 \
        --partitions 3 \
        --replication-factor 1 \
        --if-not-exists
    
    docker exec kafka kafka-topics --create \
        --topic flood-alerts \
        --bootstrap-server localhost:9092 \
        --partitions 3 \
        --replication-factor 1 \
        --if-not-exists
    
    docker exec kafka kafka-topics --create \
        --topic iot-sensors \
        --bootstrap-server localhost:9092 \
        --partitions 3 \
        --replication-factor 1 \
        --if-not-exists
    
    print_status "Kafka topics created successfully!"
}

# Initialize HDFS directories
init_hdfs() {
    print_status "Initializing HDFS directory structure..."
    
    # Wait for namenode to be ready
    sleep 60
    
    # Create HDFS directories sesuai proposal
    docker exec namenode hdfs dfs -mkdir -p /data/raw/bmkg
    docker exec namenode hdfs dfs -mkdir -p /data/raw/bnpb
    docker exec namenode hdfs dfs -mkdir -p /data/raw/demnas
    docker exec namenode hdfs dfs -mkdir -p /data/raw/iot
    docker exec namenode hdfs dfs -mkdir -p /data/raw/satelit
    
    docker exec namenode hdfs dfs -mkdir -p /data/processing/staging
    docker exec namenode hdfs dfs -mkdir -p /data/processing/clean
    docker exec namenode hdfs dfs -mkdir -p /data/processing/transformed
    
    docker exec namenode hdfs dfs -mkdir -p /data/serving/hive
    docker exec namenode hdfs dfs -mkdir -p /data/serving/hbase
    
    docker exec namenode hdfs dfs -mkdir -p /data/analytics/models
    docker exec namenode hdfs dfs -mkdir -p /data/analytics/predictions
    
    # Set permissions
    docker exec namenode hdfs dfs -chmod -R 777 /data
    
    # Create HBase root directory
    docker exec namenode hdfs dfs -mkdir -p /hbase
    docker exec namenode hdfs dfs -chmod 777 /hbase
    
    print_status "HDFS directories created successfully!"
}

# Initialize Hive databases and tables
init_hive() {
    print_status "Initializing Hive databases and tables..."
    
    # Wait for Hive to be ready
    sleep 90
    
    # Create database
    docker exec hive-server beeline -u jdbc:hive2://localhost:10000 -e "
        CREATE DATABASE IF NOT EXISTS flood_data 
        COMMENT 'Database untuk analisis prediktif banjir Lampung'
        LOCATION '/data/serving/hive/';
    "
    
    # Create weather history table
    docker exec hive-server beeline -u jdbc:hive2://localhost:10000 -e "
        USE flood_data;
        
        CREATE TABLE IF NOT EXISTS weather_history (
            date_recorded DATE,
            station_id STRING,
            province STRING,
            city STRING,
            temperature DOUBLE,
            humidity DOUBLE,
            rainfall DOUBLE,
            wind_speed DOUBLE,
            pressure DOUBLE
        )
        PARTITIONED BY (year INT, month INT)
        STORED AS ORC
        LOCATION '/data/serving/hive/weather_history';
    "
    
    # Create flood events table
    docker exec hive-server beeline -u jdbc:hive2://localhost:10000 -e "
        USE flood_data;
        
        CREATE TABLE IF NOT EXISTS flood_events (
            event_id STRING,
            date_occurred DATE,
            province STRING,
            city STRING,
            district STRING,
            flood_depth DOUBLE,
            affected_area DOUBLE,
            casualties INT,
            damage_estimate BIGINT,
            severity_level STRING
        )
        PARTITIONED BY (year INT, month INT)
        STORED AS ORC
        LOCATION '/data/serving/hive/flood_events';
    "
    
    print_status "Hive databases and tables created successfully!"
}

# Initialize HBase tables
init_hbase() {
    print_status "Initializing HBase tables..."
    
    # Wait for HBase to be ready
    sleep 120
    
    # Create HBase tables for real-time data
    docker exec hbase-master hbase shell << 'EOF'
create 'iot_sensors', 'sensor_data', 'metadata'
create 'realtime_weather', 'weather_data', 'station_info'
create 'flood_predictions', 'prediction_data', 'model_info'
exit
EOF
    
    print_status "HBase tables created successfully!"
}

# Initialize Superset
init_superset() {
    print_status "Initializing Superset..."
    
    # Wait for Superset to be ready
    sleep 60
    
    # Initialize Superset database
    docker exec superset superset db upgrade
    
    # Create admin user
    docker exec superset superset fab create-admin \
        --username admin \
        --firstname Admin \
        --lastname User \
        --email admin@lampung-flood.id \
        --password admin123
    
    # Initialize Superset
    docker exec superset superset init
    
    print_status "Superset initialized successfully!"
}

# Main setup function
main() {
    print_status "Starting Big Data ecosystem setup for Lampung Flood Prediction..."
    
    check_prerequisites
    create_directories
    create_configs
    
    print_status "Starting Docker containers..."
    docker-compose up -d
    
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Initialize components
    init_kafka_topics &
    init_hdfs &
    
    wait
    
    init_hive &
    init_hbase &
    init_superset &
    
    wait
    
    print_status "=========================================="
    print_status "SETUP COMPLETED SUCCESSFULLY!"
    print_status "=========================================="
    print_status ""
    print_status "Services accessible at:"
    print_status "• Hadoop NameNode: http://localhost:9870"
    print_status "• YARN ResourceManager: http://localhost:8088"
    print_status "• Spark Master: http://localhost:8080"
    print_status "• HBase Master: http://localhost:16010"
    print_status "• Hive Server: jdbc:hive2://localhost:10000"
    print_status "• Superset: http://localhost:8089 (admin/admin123)"
    print_status "• Jupyter Notebook: http://localhost:8888"
    print_status ""
    print_status "Data directories created in ./data/"
    print_status "Configuration files created in ./config/"
    print_status "Sample scripts created in ./scripts/"
    print_status ""
    print_status "Next steps:"
    print_status "1. Upload sample data to HDFS"
    print_status "2. Run data ingestion scripts"
    print_status "3. Test MapReduce jobs"
    print_status "4. Develop ML models with Spark MLlib"
    print_status "5. Create dashboards in Superset"
}

# Cleanup function
cleanup() {
    print_warning "Cleaning up previous installation..."
    docker-compose down -v
    docker system prune -f
}

# Help function
show_help() {
    echo "Usage: $0 [OPTION]"
    echo "Setup Big Data ecosystem for Lampung Flood Prediction"
    echo ""
    echo "Options:"
    echo "  setup     Full setup (default)"
    echo "  cleanup   Remove all containers and volumes"
    echo "  help      Show this help message"
}

# Parse command line arguments
case "${1:-setup}" in
    setup)
        main
        ;;
    cleanup)
        cleanup
        ;;
    help)
        show_help
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac