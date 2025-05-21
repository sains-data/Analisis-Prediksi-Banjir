import requests
import json
import os
from datetime import datetime

def fetch_bmkg_data():
    """
    Fungsi simulasi untuk mengambil data BMKG.
    Dalam implementasi sebenarnya, ini akan mengambil dari API BMKG.
    """
    # Placeholder - dalam implementasi sebenarnya akan memanggil API BMKG
    # Gunakan data sample sebagai contoh
    with open('/app/data/sample/data_cuaca_bmkg.csv', 'r') as f:
        # Skip header
        next(f)
        data = []
        for line in f:
            fields = line.strip().split(',')
            data.append({
                "timestamp": fields[0],
                "location": fields[1],
                "rainfall": float(fields[2]),
                "humidity": float(fields[3]),
                "temperature": float(fields[4]),
                "wind_speed": float(fields[5])
            })
    return data

def save_to_hdfs(data):
    """Menyimpan data ke HDFS"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/tmp/weather_{timestamp}.json"
    
    # Simpan ke file lokal dulu
    with open(filename, 'w') as f:
        json.dump(data, f)
    
    # Upload ke HDFS
    hdfs_path = f"/data/raw/bmkg/weather_{timestamp}.json"
    os.system(f"hadoop fs -put {filename} {hdfs_path}")
    os.remove(filename)  # Hapus file lokal
    
    print(f"Data saved to HDFS: {hdfs_path}")

if __name__ == "__main__":
    print("Fetching BMKG weather data...")
    weather_data = fetch_bmkg_data()
    print(f"Retrieved {len(weather_data)} weather records")
    
    print("Saving data to HDFS...")
    save_to_hdfs(weather_data)
    
    print("Data ingestion complete")