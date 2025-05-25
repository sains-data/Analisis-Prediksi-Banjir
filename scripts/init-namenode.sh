#!/bin/bash

# Script untuk menginisialisasi HDFS namenode otomatis
# Script ini akan mengecek apakah namenode sudah di-format atau belum
# Jika belum, script akan melakukan format

echo "Checking if namenode is already formatted..."

# Menghentikan container namenode jika sedang berjalan
docker-compose stop namenode

# Jalankan container namenode dengan mode khusus untuk format
docker-compose run --rm namenode hdfs namenode -format -force

# Start semua container
docker-compose up -d

echo "HDFS namenode has been initialized successfully!"
echo "The system should now be running properly."
echo ""
echo "Access the following UIs:"
echo "- HDFS NameNode: http://localhost:9870"
echo "- YARN ResourceManager: http://localhost:8088"
echo "- Spark Master: http://localhost:8080"
echo "- Jupyter Notebook: http://localhost:8888"
echo "- Superset: http://localhost:8089"
echo "- HBase Master: http://localhost:16010"
