# 🌊 Predictive Flood Analytics with Hadoop Ecosystem in Lampung

Welcome to the **Flood Prediction Big Data Project** repository! 🚀
This project showcases the integration of **multi-source flood data** using a full-fledged **Apache Hadoop Ecosystem**. The system is designed to support **real-time and batch processing** for flood prediction in **Lampung Province**, Indonesia.

> **Team Members:**  
> Gymnastiar Al Khoarizmy (122450096) | Hermawan Manurung (122450069) | Shula Talitha A P (121450087) | Esteria Rohanauli Sidauruk (122450025)

## 🎯 Project Status: **PRODUCTION READY** ✅

**Recent Updates (May 2025):**
- ✅ **Fixed ResourceManager restart loop issue** - YARN cluster now stable
- ✅ **Resolved HBase RegionServer standalone mode** - Full distributed configuration
- ✅ **Enhanced service startup dependencies** - Sequential startup prevents conflicts  
- ✅ **All web UIs accessible** - Complete monitoring and management interfaces
- ✅ **Production-grade Docker environment** - Ready for analytics workloads

---

## 🔧 Installation & Setup

### Prerequisites
- Docker and Docker Compose installed
- Git
- At least 8GB RAM available for Docker

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/sains-data/Analisis-Prediksi-Banjir.git
   cd Analisis-Prediksi-Banjir
   ```

2. Initialize the system (formats namenode and starts all services):
   ```bash
   chmod +x scripts/init-namenode.sh
   bash ./scripts/init-namenode.sh
   docker-compose up -d
   ```

3. Verify all services are running:
   ```bash
   docker-compose ps
   ```

4. Access web interfaces:
   - HDFS NameNode: `http://localhost:9870`
   - YARN ResourceManager: `http://localhost:8088`
   - Spark Master: `http://localhost:8080`
   - Jupyter Notebook: `http://localhost:8888`
   - Superset: `http://localhost:8089`
   - HBase Master: `http://localhost:16010`

### Troubleshooting

If you encounter issues with the namenode not starting properly:
```bash
# Stop all containers
docker-compose down

# Run the init script again
./scripts/init-namenode.sh
```

---

## 🧱 System Architecture

We adopt a **multi-layered architecture** and hybrid processing approach:


| Layer                | Description                         | Tools                         | Format             |
| -------------------- | ----------------------------------- | ----------------------------- | ------------------ |
| **Raw Data Layer**   | Stores raw data from all sources    | Kafka, Flume, HDFS            | CSV, JSON, GeoTIFF |
| **Processing Layer** | ETL, transformation, model training | Spark, Spark Streaming, MLlib | Parquet, Avro      |
| **Serving Layer**    | Ready-to-query structured data      | Hive, HBase                   | ORC, Parquet       |
| **Analytics Layer**  | Visual dashboards and early alerts  | Superset, Kafka               |  -                  |

---

## 📖 Project Overview

This project includes:

1. **Hybrid Pipeline**: Batch + Streaming for multi-source flood data
2. **Machine Learning**: Flood prediction with Spark MLlib
3. **IoT Integration**: Real-time sensor data via Kafka & HBase
4. **BI & Alerting**: Dashboard + early warning system via Superset

🌟 Key Focus Areas:

* Apache Hadoop Distributed File System
* Apache Spark (MLlib, Streaming)
* Apache Kafka & Hive
* Data Modeling for Streaming & Batch
* Docker-based Orchestration (Airflow, Docker Compose)

---

## ⚙️ System Components

### 🧹 Tech Stack

| Category            | Tools                  |
| ------------------- | ---------------------- |
| Distributed Storage | Hadoop HDFS            |
| Batch Processing    | Apache Spark           |
| Stream Processing   | Spark Streaming, Kafka |
| Query Layer         | Hive, Spark SQL        |
| Data Lake Store     | Parquet, ORC           |
| ML                  | Spark MLlib            |
| IoT Data            | HBase, Kafka           |
| Orchestration       | Apache Airflow         |
| Monitoring          | Apache Ambari          |
| Dashboard           | Apache Superset        |

---

## 🔄 Workflow DAG (Airflow)

```
flood_prediction_pipeline/
├── ingest_bmkg_data
├── ingest_bnpb_data
├── process_demnas_geotiff
├── load_data_to_hdfs
├── spark_data_cleaning
├── feature_engineering
├── model_training
├── generate_risk_map
├── hive_refresh
└── notify_stakeholders
```

---

## 📦 Folder Structure

```
Analisis-Prediksi-Banjir/
└── Analisis-Prediksi-Banjir/
    ├── .gitignore
    ├── docker-compose.yml
    ├── hive-server-entrypoint.sh
    ├── LICENSE
    ├── README.md
    ├── setup.sh
    ├── test_mapreduce.sh
    ├── .git/
    │   ├── config, HEAD, index, etc.
    │   └── ... (standard Git repo files and structure)
    ├── config/
    │   ├── hadoop/
    │   │   ├── core-site.xml
    │   │   ├── hdfs-site.xml
    │   │   ├── mapred-site.xml
    │   │   └── yarn-site.xml
    │   ├── hbase/
    │   │   └── hbase-site.xml
    │   ├── hive/
    │   │   ├── hive-site.xml
    │   │   └── simple-hive-site.xml
    │   └── spark/
    │       └── spark-defaults.conf
    ├── data/
    │   ├── processed/
    │   │   └── .gitkeep
    │   ├── raw/
    │   │   ├── .gitkeep
    │   │   ├── bmkg/cuaca_historis/data_cuaca_bmkg.csv
    │   │   ├── bnpb/kejadian_banjir/data_banjir_historis.csv
    │   │   ├── demnas/topografi/data_elevasi_demnas.csv
    │   │   └── iot/data_sensor_iot.json
    │   ├── sample/
    │   │   └── .gitkeep
    │   └── serving/
    │       └── .gitkeep
    ├── docker/
    │   ├── README.md
    │   ├── hadoop/
    │   │   ├── .gitkeep
    │   │   ├── Dockerfile.datanode
    │   │   ├── Dockerfile.namenode
    │   │   ├── Dockerfile.resourcemanager
    │   │   ├── config/
    │   │   │   ├── core-site.xml
    │   │   │   ├── hadoop-env.sh
    │   │   │   ├── hdfs-site.xml
    │   │   │   ├── mapred-site.xml
    │   │   │   └── yarn-site.xml
    │   │   └── scripts/
    │   │       ├── entrypoint-datanode.sh
    │   │       ├── entrypoint-namenode.sh
    │   │       └── entrypoint-resourcemanager.sh
    │   ├── hbase/
    │   │   ├── Dockerfile.master
    │   │   ├── config/
    │   │   │   ├── hbase-env.sh
    │   │   │   └── hbase-site.xml
    │   │   └── scripts/
    │   │       └── entrypoint-hbase-master.sh
    │   ├── hive/
    │   │   ├── .gitkeep
    │   │   ├── Dockerfile
    │   │   ├── Dockerfile.hive
    │   │   ├── config/
    │   │   │   ├── hive-env.sh
    │   │   │   └── hive-site.xml
    │   │   └── scripts/
    │   │       └── entrypoint-hive.sh
    │   ├── kafka/
    │   │   └── .gitkeep
    │   ├── scripts/
    │   │   └── .gitkeep
    │   ├── spark/
    │   │   ├── .gitkeep
    │   │   ├── Dockerfile.master
    │   │   ├── Dockerfile.worker
    │   │   ├── config/
    │   │   │   ├── spark-defaults.conf
    │   │   │   └── spark-env.sh
    │   │   └── scripts/
    │   │       ├── entrypoint-spark-master.sh
    │   │       └── entrypoint-spark-worker.sh
    │   └── zookeeper/
    │       ├── Dockerfile
    │       ├── config/
    │       │   └── zoo.cfg
    │       └── scripts/
    │           └── entrypoint-zookeeper.sh
    ├── hive/
    │   ├── .gitkeep
    │   └── data/metastore/.gitkeep
    ├── notebooks/
    │   ├── .gitkeep
    │   └── hive_spark_integration_test.ipynb
    ├── scripts/
    │   ├── backup_system.sh
    │   ├── init-namenode.sh
    │   ├── init_system.sh
    │   ├── stop.sh
    │   ├── test_pipeline.py
    │   ├── analytics/
    │   │   └── .gitkeep
    │   ├── ingestion/
    │   │   ├── .gitkeep
    │   │   ├── bmkg_ingestion.py
    │   │   └── ingest_bmkg.py
    │   ├── ml/
    │   │   └── flood_prediction_model.py
    │   └── processing/
    │       └── .gitkeep
    ├── spark/
    │   └── data/
    │       └── .gitkeep
    └── superset/
        └── superset_config.py

```

---

## 🚀 How to Run the Project (Deployment)

1. Clone the repo:

   ```bash
   git clone https://github.com/your-repo/flood-bigdata-lampung.git
   cd flood-bigdata-lampung
   ```

2. Start the cluster:

   ```bash
   docker-compose up -d
   ```

3. Access services:

   * Hadoop UI: `localhost:9870`
   * Spark UI: `localhost:4040`
   * Hive: `localhost:10000`
   * Superset: `localhost:8088`
   * Airflow: `localhost:8080`

4. Load sample data into `/data/raw/` and trigger Airflow DAG.

---

## 📊 Dashboard Preview

<p align="center">
  <img src="docs/superset_dashboard.png" width="800px"/>
</p>

---

## 🛡️ Requirements & Functional Specs

### ✅ Functional Requirements

* Ingest BMKG, BNPB, and sensor data into HDFS
* Stream IoT sensor data using Kafka → Spark Streaming
* Train flood prediction model with Spark MLlib
* Provide SQL interface with Hive
* Trigger early warning alerts
* Generate flood risk maps

### ⚙️ Non-Functional Requirements

* High availability and scalability
* Max streaming latency: 5 minutes
* Access control per user role
* Efficient storage with Parquet/ORC
* Dockerized for easy deployment

---

## 🏠 Sample Use Case: Bandar Lampung

On **11 June 2020**, Kalibalau River overflowed, causing urban flooding. This system integrates:

* 🌧️ BMKG weather data
* 🤭 DEMNAS elevation data
* 💧 IoT sensor water level
* 📊 Historical flood incidents

> Result: Real-time analytics and accurate flood predictions help mitigate disaster impact.

---

## ☁️ Sample Dataset Sources

* BMKG: Rainfall, humidity, temperature
* BNPB: Historical flood reports
* DEMNAS: Digital Elevation Maps
* IoT: Local sensors from BPBD

---

## 📬 Contact & Credits

Developed by **Kelompok 6** – Institut Teknologi Sumatera
