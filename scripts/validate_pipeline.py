#!/usr/bin/env python3
"""
Validation script for the improved flood analytics pipeline
This script checks if all dependencies are available and the script can be imported
"""

import sys
import traceback

def validate_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Validating dependencies...")
    
    try:
        import pyspark
        print(f"✅ PySpark: {pyspark.__version__}")
    except ImportError:
        print("❌ PySpark not found")
        return False
    
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import col, when, count, countDistinct
        print("✅ PySpark SQL functions imported successfully")
    except ImportError as e:
        print(f"❌ PySpark SQL import error: {e}")
        return False
    
    return True

def validate_script_syntax():
    """Check if the improved flood analytics script has valid syntax"""
    print("\n🔍 Validating script syntax...")
    
    try:
        # Try to compile the script
        with open('/opt/spark/work-dir/improved_flood_analytics.py', 'r') as f:
            script_content = f.read()
        
        compile(script_content, 'improved_flood_analytics.py', 'exec')
        print("✅ Script syntax is valid")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in script: {e}")
        return False
    except FileNotFoundError:
        print("❌ improved_flood_analytics.py not found")
        return False
    except Exception as e:
        print(f"❌ Error validating script: {e}")
        return False

def validate_spark_session():
    """Check if Spark session can be created"""
    print("\n🔍 Validating Spark session...")
    
    try:
        from pyspark.sql import SparkSession
        
        spark = SparkSession.builder \
            .appName("ValidationTest") \
            .config("spark.sql.adaptive.enabled", "true") \
            .getOrCreate()
        
        print("✅ Spark session created successfully")
        
        # Test basic functionality
        test_data = [("test", 1), ("data", 2)]
        test_df = spark.createDataFrame(test_data, ["name", "value"])
        count = test_df.count()
        
        print(f"✅ Basic DataFrame operations work (count: {count})")
        
        spark.stop()
        return True
        
    except Exception as e:
        print(f"❌ Spark session error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all validations"""
    print("🚀 Starting Flood Analytics Pipeline Validation\n")
    
    # Track validation results
    results = []
    
    # Run validations
    results.append(validate_dependencies())
    results.append(validate_script_syntax())
    results.append(validate_spark_session())
    
    # Summary
    print("\n" + "="*50)
    print("📊 VALIDATION SUMMARY")
    print("="*50)
    
    if all(results):
        print("🎉 ALL VALIDATIONS PASSED!")
        print("✅ The flood analytics pipeline is ready to run")
        print("\nTo run the analytics:")
        print("docker exec -it spark-master /opt/spark/bin/spark-submit \\")
        print("  --master spark://spark-master:7077 \\")
        print("  /opt/spark/work-dir/improved_flood_analytics.py")
        return 0
    else:
        print("❌ SOME VALIDATIONS FAILED")
        print("Please check the errors above and fix them before running the pipeline")
        return 1

if __name__ == "__main__":
    sys.exit(main())
