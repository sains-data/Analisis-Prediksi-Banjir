# 🌊 Predictive Flood Risk Analytics in Lampung, Indonesia – Powered by Apache Hadoop Ecosystem

Welcome to the **Flood Risk Prediction System** repository! This project is a comprehensive implementation of a **Big Data architecture** leveraging the **Apache Hadoop ecosystem** to perform **real-time and batch flood risk analytics** using multi-source data from **BMKG, BNPB, DEMNAS, and IoT sensors**.

> Gymnastiar Al Khoarizmy (122450096), Hermawan Manurung (122450069), Shula Talitha Ardhya Putri (121450087), Esteria Rohanauli Sidauruk (122450025)

---

## 📌 Project Goals

✅ Early flood warning system  
✅ Integration of meteorological, hydrological, topographical, and real-time sensor data  
✅ Visual analytics dashboard for flood prediction  
✅ Scalable architecture using Hadoop, Spark, Kafka, and Docker

---

## 🧱 System Architecture – Multi-Layer Design

| Layer               | Description                              | Technologies                 | Data Format           |
|---------------------|------------------------------------------|------------------------------|------------------------|
| **Raw Data Layer**  | Raw ingestion from all sources           | Kafka, Flume, HDFS           | JSON, CSV, GeoTIFF     |
| **Processing Layer**| ETL, transformation, feature engineering | Spark, Spark Streaming       | Parquet, Avro          |
| **Serving Layer**   | Query-ready structured data              | Hive, HBase                  | Parquet, ORC           |
| **Analytics Layer** | Final predictions and dashboard views    | Superset, Jupyter Notebook   | -                      |

---

## 👥 Target Users

- **Data Engineers**: Build & maintain batch/streaming pipelines
- **Data Scientists**: Train & evaluate ML models for flood prediction
- **Analysts**: Perform SQL queries and dashboard insights
- **Disaster Response Officers (BPBD)**: Real-time alerts and visual monitoring
- **Government Agencies**: Strategic decision-making support

---

## 🔧 Tech Stack

| Category               | Tools & Platforms                     |
|------------------------|----------------------------------------|
| Distributed Storage    | Hadoop HDFS                            |
| Batch Processing       | Apache Spark                           |
| Stream Processing      | Spark Streaming, Apache Kafka          |
| Machine Learning       | Spark MLlib                            |
| Query Interface        | Apache Hive                            |
| IoT Data Management    | Apache HBase                           |
| Workflow Orchestration | Apache Airflow                         |
| Monitoring             | Apache Ambari, Custom Health Scripts   |
| Visualization          | Apache Superset, Jupyter Notebook      |
| Containerization       | Docker, Docker Compose                 |

---

## 🔄 Airflow Workflow (DAG)

```bash
flood_prediction_pipeline/
├── ingest_bmkg_data
├── ingest_bnpb_data
├── process_demnas_geotiff
├── load_data_to_hdfs
├── spark_data_cleaning
├── feature_engineering
├── train_prediction_model
├── generate_risk_map
├── hive_refresh
└── notify_stakeholders
````

---

## 🗂️ HDFS Directory Structure

```bash
/data/
├── raw/               # BMKG, BNPB, DEMNAS, IoT sensors
├── processing/        # Transformed & cleaned datasets
├── serving/           # Query-ready datasets
├── analytics/         # ML models and prediction output
```

---

## 🛠️ Cluster Setup (Docker Compose)

* 1 Namenode, 3 Datanodes
* 1 Spark Master, 3 Spark Workers
* 1 Kafka Broker, 3 ZooKeeper Nodes
* Hive Metastore & HiveServer2
* HBase Master
* Apache Airflow
* Apache Superset
* Apache Ambari for monitoring

> OS: Ubuntu 22.04 (via Docker)
> Deployment: Local pseudo-distributed Hadoop Cluster

---

## 🧪 Testing Highlights

| Test Case                | Objective                             | ✅ |
| ------------------------ | ------------------------------------- | - |
| BMKG/IoT Data Ingestion  | Ensure ingestion & HDFS storage       | ✅ |
| Spark Batch Processing   | Clean, transform, feature engineering | ✅ |
| Spark Streaming          | Real-time anomaly detection           | ✅ |
| ML Model Performance     | Evaluate using RMSE, F1-score         | ✅ |
| Hive Query Testing       | Query response time                   | ✅ |
| Superset Visualization   | Dashboard rendering & refresh         | ✅ |
| Alert Trigger Validation | Real-time flood risk alerting         | ✅ |

---

## 🤖 Machine Learning Model

* **Algorithm**: Random Forest Regressor (via Spark MLlib)
* **Features**: Rainfall, Humidity, Water Level, Slope, Elevation
* **Label**: Water level prediction
* **Output**: Flood risk level, probability, and confidence intervals
* **Model Path**: `/data/analytics/models/flood_prediction_rf`

---

## 🌐 Data Sources

| Source      | Data Type    | Description                                   |
| ----------- | ------------ | --------------------------------------------- |
| BMKG        | JSON/CSV     | Weather data: rainfall, temperature, humidity |
| BNPB        | CSV          | Historical flood events and statistics        |
| DEMNAS      | GeoTIFF      | Elevation and terrain slope data              |
| IoT Sensors | JSON/Parquet | Real-time river data: water level, flow rate  |

---

## 🏞️ Real Use Case – Bandar Lampung Flood (June 2020)

* Kalibalau River overflowed due to intense rainfall
* Our system ingested weather, terrain, and sensor data
* Real-time analytics and predictive ML provided early warnings
* **Outcome**: Improved awareness and disaster mitigation potential

---

## ⚙️ How to Deploy

```bash
# 1. Clone the repository
git clone https://github.com/team6/flood-prediction-system.git
cd flood-prediction-system

# 2. Start the Hadoop cluster
docker-compose up -d

# 3. Access services locally
Spark UI       → localhost:8080  
Airflow UI     → localhost:8090  
Superset       → localhost:8088  
HiveServer     → localhost:10000  
Ambari         → localhost:8080
```

---

## 📊 Dashboard Preview

<p align="center" style="font-size: 36px; font-weight: bold;">
  🚧 COMING SOON 🚧  
</p>

---


## 📬 Contact & Contributors
Developed by Group 6 — Data Science Department
Institut Teknologi Sumatera (ITERA), Indonesia
