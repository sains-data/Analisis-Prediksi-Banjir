# Flood Prediction System

Implementasi ekosistem Hadoop untuk analisis prediktif banjir menggunakan Docker. Sistem ini menggunakan komponen Big Data berikut:

- Apache Hadoop 3.4.1
- Apache HBase 2.5.10
- Apache Hive 4.0.1
- Apache Spark 3.5.4
- Apache Zookeeper 3.8.4
- Derby 10.14.2.0

## Struktur Proyek

Proyek ini terstruktur sebagai berikut:

```
flood-prediction-system/
├── docker/
│   ├── hadoop/
│   ├── hbase/
│   ├── hive/
│   ├── spark/
│   └── zookeeper/
├── packages/
│   ├── apache-hive-4.0.1-bin.tar.gz
│   ├── apache-zookeeper-3.8.4-bin.tar.gz
│   ├── db-derby-10.14.2.0-bin.tar.gz
│   ├── hadoop-3.4.1.tar.gz
│   ├── hbase-2.5.10-bin.tar.gz
│   └── spark-3.5.4-bin-hadoop3.tgz
├── data/
│   ├── sample/
│   ├── raw/
│   └── processed/
├── scripts/
│   ├── setup/
│   ├── ingestion/
│   └── processing/
├── docker-compose.yml
└── README.md
```

## Prasyarat

- Docker dan Docker Compose
- Minimal 8GB RAM
- Minimal 40GB ruang disk kosong

## Instalasi

1. Clone repositori ini:
```bash
git clone https://github.com/username/flood-prediction-system.git
cd flood-prediction-system
```

2. Pindahkan file-file paket ke direktori packages/:
```bash
# Pastikan file-file berikut ada di direktori packages/:
# - apache-hive-4.0.1-bin.tar.gz
# - apache-zookeeper-3.8.4-bin.tar.gz
# - db-derby-10.14.2.0-bin.tar.gz
# - hadoop-3.4.1.tar.gz
# - hbase-2.5.10-bin.tar.gz
# - spark-3.5.4-bin-hadoop3.tgz
```

3. Bangun dan jalankan layanan Docker:
```bash
docker-compose up -d
```

4. Jalankan skrip inisialisasi sistem:
```bash
chmod +x scripts/setup/init_system.sh
./scripts/setup/init_system.sh
```

## Verifikasi Instalasi

Setelah semua layanan berjalan, Anda dapat mengakses UI web berikut:

- Hadoop NameNode: http://localhost:9870
- YARN Resource Manager: http://localhost:8088
- Spark Master: http://localhost:8080
- HBase Master: http://localhost:16010
- Hive Server Web UI: http://localhost:10002

## Penggunaan

### Mengakses Hadoop CLI
```bash
docker exec -it namenode hadoop fs -ls /
```

### Mengakses Hive CLI
```bash
docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000
```

### Mengakses Spark Shell
```bash
docker exec -it spark-master spark-shell --master spark://spark-master:7077
```

### Mengakses HBase Shell
```bash
docker exec -it hbase-master hbase shell
```

## Membersihkan Sistem
```bash
docker-compose down -v
```

## Lisensi
MIT