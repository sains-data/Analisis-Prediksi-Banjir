# 🌊 Predictive Flood Analytics with Hadoop Ecosystem in Lampung

Welcome to the **Flood Prediction Big Data Project** repository! 🚀
This project showcases the integration of **multi-source flood data** using a full-fledged **Apache Hadoop Ecosystem**. The system is designed to support **real-time and batch processing** for flood prediction in **Lampung Province**, Indonesia.

> Gymnastiar Al Khoarizmy (122450096) | Hermawan Manurung (122450069) | Shula Talitha Ardhya Putri (121450087) | Esteria Rohanauli S (122450025)
---

## 🧱 System Architecture

We adopt a **multi-layered architecture** and hybrid processing approach:


| Layer                | Description                         | Tools                         | Format             |
| -------------------- | ----------------------------------- | ----------------------------- | ------------------ |
| **Raw Data Layer**   | Stores raw data from all sources    | Kafka, Flume, HDFS            | CSV, JSON, GeoTIFF |
| **Processing Layer** | ETL, transformation, model training | Spark, Spark Streaming, MLlib | Parquet, Avro      |
| **Serving Layer**    | Ready-to-query structured data      | Hive, HBase                   | ORC, Parquet       |
| **Analytics Layer**  | Visual dashboards and early alerts  | Superset, Kafka               | -                  |

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
flood-bigdata-lampung/
│
├── datasets/                    # Raw and sample flood datasets (BMKG, BNPB, IoT, DEMNAS)
├── docs/                        # Diagrams, specs, and documentation
│   ├── architecture.png
│   ├── data_catalog.md
│   ├── pipeline.drawio
│   └── dag_airflow.drawio
├── scripts/                     # Spark, Hive, and Kafka scripts
│   ├── batch/
│   ├── stream/
│   └── ml/
├── docker/                      # Docker & Docker Compose setup
│   ├── docker-compose.yml
│   └── cluster-config/
├── notebooks/                   # Jupyter analysis notebooks
├── airflow_dags/               # DAGs for pipeline orchestration
├── requirements.txt
├── README.md
└── LICENSE
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
