"""
Test script untuk memverifikasi data pipeline
"""

import subprocess
import time
import requests

def test_hdfs_connection():
    """Test HDFS connectivity"""
    try:
        result = subprocess.run([
            "docker", "exec", "namenode", 
            "hdfs", "dfs", "-ls", "/"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ HDFS connection: OK")
            return True
        else:
            print("❌ HDFS connection: FAILED")
            return False
    except Exception as e:
        print(f"❌ HDFS connection error: {e}")
        return False

def test_hive_connection():
    """Test Hive connectivity"""
    try:
        result = subprocess.run([
            "docker", "exec", "hive-server",
            "beeline", "-u", "jdbc:hive2://localhost:10000",
            "-e", "SHOW DATABASES;"
        ], capture_output=True, text=True)
        
        if "flood_data" in result.stdout:
            print("✅ Hive connection: OK")
            return True
        else:
            print("❌ Hive connection: FAILED")
            return False
    except Exception as e:
        print(f"❌ Hive connection error: {e}")
        return False

def test_kafka_connectivity():
    """Test Kafka connectivity"""
    try:
        result = subprocess.run([
            "docker", "exec", "kafka",
            "kafka-topics", "--list",
            "--bootstrap-server", "localhost:9092"
        ], capture_output=True, text=True)
        
        if "bmkg-weather-realtime" in result.stdout:
            print("✅ Kafka connection: OK")
            return True
        else:
            print("❌ Kafka connection: FAILED")
            return False
    except Exception as e:
        print(f"❌ Kafka connection error: {e}")
        return False

def test_superset_api():
    """Test Superset API"""
    try:
        response = requests.get("http://localhost:8088/health", timeout=10)
        if response.status_code == 200:
            print("✅ Superset API: OK")
            return True
        else:
            print("❌ Superset API: FAILED")
            return False
    except Exception as e:
        print(f"❌ Superset API error: {e}")
        return False

def main():
    print("=== Big Data Pipeline Test ===")
    print()
    
    tests = [
        test_hdfs_connection,
        test_hive_connection,
        test_kafka_connectivity,
        test_superset_api
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print()
    print("=== Test Summary ===")
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Pipeline is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the logs.")
        return 1

if __name__ == "__main__":
    exit(main())
