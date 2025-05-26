"""
Simplified System Validation for Lampung Flood Prediction Platform
Focuses on critical functionality with better error handling
"""

import subprocess
import requests
import json
import time
import os
from datetime import datetime

def run_command(cmd, timeout=30):
    """Run a command with timeout and return success status"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_hdfs_operations():
    """Test basic HDFS operations"""
    print("🔄 Testing HDFS Operations...")
    
    # Clean up any existing test data
    run_command(["docker-compose", "exec", "-T", "namenode", "hdfs", "dfs", "-rm", "-r", "/test"])
    
    # Create test directory
    success, stdout, stderr = run_command([
        "docker-compose", "exec", "-T", "namenode", 
        "hdfs", "dfs", "-mkdir", "-p", "/test/validation"
    ])
    
    if success:
        print("✅ HDFS Operations: SUCCESS")
        return True
    else:
        print(f"❌ HDFS Operations: FAILED - {stderr}")
        return False

def test_spark_master():
    """Test Spark Master connectivity"""
    print("🔄 Testing Spark Master...")
    
    success, stdout, stderr = run_command([
        "docker-compose", "exec", "-T", "spark-master", 
        "/opt/spark/bin/spark-submit", "--version"
    ], timeout=15)
    
    # Check both stdout and stderr as Spark version info might go to stderr
    if success and ("version" in stdout.lower() or "version" in stderr.lower()):
        print("✅ Spark Master: SUCCESS")
        return True
    else:
        print(f"❌ Spark Master: FAILED")
        return False

def test_hive_basic():
    """Test basic Hive operations"""
    print("🔄 Testing Hive Basic Operations...")
    
    success, stdout, stderr = run_command([
        "docker-compose", "exec", "-T", "hive-server", 
        "beeline", "-u", "jdbc:hive2://localhost:10000", 
        "-e", "SHOW DATABASES;"
    ], timeout=30)
    
    if success and "default" in stdout:
        print("✅ Hive Operations: SUCCESS")
        return True
    else:
        print(f"❌ Hive Operations: FAILED")
        return False

def test_kafka_basic():
    """Test basic Kafka operations"""
    print("🔄 Testing Kafka Operations...")
    
    # First, try to list existing topics
    success, stdout, stderr = run_command([
        "docker-compose", "exec", "-T", "kafka", 
        "/opt/kafka/bin/kafka-topics.sh", "--list", 
        "--bootstrap-server", "localhost:9092"
    ], timeout=15)
    
    if success:
        print("✅ Kafka Operations: SUCCESS")
        return True
    else:
        print(f"❌ Kafka Operations: FAILED")
        return False

def test_web_interfaces():
    """Test all web interfaces"""
    print("🔄 Testing Web Interfaces...")
    
    interfaces = [
        ("Hadoop NameNode", "http://localhost:9870"),
        ("Hadoop ResourceManager", "http://localhost:8088"),
        ("Spark Master", "http://localhost:8080"),
        ("HBase Master", "http://localhost:16010"),
        ("Jupyter", "http://localhost:8888"),
        ("Superset", "http://localhost:8089"),
        ("Airflow", "http://localhost:8085")
    ]
    
    successful = 0
    for name, url in interfaces:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"  ✅ {name}: Accessible")
                successful += 1
            else:
                print(f"  ❌ {name}: Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ {name}: Connection failed")
    
    if successful >= len(interfaces) * 0.8:  # 80% success rate
        print("✅ Web Interfaces: SUCCESS")
        return True
    else:
        print("❌ Web Interfaces: FAILED")
        return False

def test_airflow_health():
    """Test Airflow health and basic functionality"""
    print("🔄 Testing Airflow Health...")
    
    try:
        response = requests.get("http://localhost:8085/health", timeout=10)
        if response.status_code == 200:
            print("✅ Airflow Health: SUCCESS")
            return True
        else:
            print(f"❌ Airflow Health: FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Airflow Health: FAILED - {str(e)}")
        return False

def main():
    """Run simplified system validation"""
    print("🚀 Lampung Flood Prediction Platform - System Validation")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")
    print()
    
    # Change to the correct directory
    os.chdir("m:\\ITERA\\Semester 6\\Analisis Big Data\\Tugas Besar\\Analisis-Prediksi-Banjir")
    
    tests = [
        ("HDFS Operations", test_hdfs_operations),
        ("Spark Master", test_spark_master),
        ("Hive Basic Operations", test_hive_basic),
        ("Kafka Operations", test_kafka_basic),
        ("Web Interfaces", test_web_interfaces),
        ("Airflow Health", test_airflow_health)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
            results.append(False)
    
    # Calculate results
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Overall assessment
    if success_rate >= 85:
        status = "🎉 EXCELLENT"
        message = "System is fully operational and ready for production!"
    elif success_rate >= 70:
        status = "✅ GOOD"
        message = "System is operational with minor issues."
    elif success_rate >= 50:
        status = "⚠️  MODERATE"
        message = "System has some functional components but needs attention."
    else:
        status = "❌ CRITICAL"
        message = "System requires immediate attention."
    
    print(f"\nStatus: {status}")
    print(f"Assessment: {message}")
    
    # Detailed component status
    print(f"\n📋 Component Status:")
    for i, (test_name, _) in enumerate(tests):
        status_icon = "✅" if results[i] else "❌"
        print(f"  {status_icon} {test_name}")
    
    # Save results
    validation_data = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "passed": passed,
            "total": total,
            "success_rate": success_rate,
            "status": status.split()[1] if len(status.split()) > 1 else status
        },
        "component_results": {test_name: results[i] for i, (test_name, _) in enumerate(tests)}
    }
    
    with open("validation_results.json", "w") as f:
        json.dump(validation_data, f, indent=2)
    
    print(f"\n📁 Results saved to: validation_results.json")
    print(f"🕒 Completed at: {datetime.now()}")
    
    return success_rate >= 70

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
