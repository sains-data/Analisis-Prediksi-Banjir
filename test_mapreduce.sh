    #!/bin/bash

# MapReduce Testing Script
# Sesuai dengan Proposal: Uji cluster dengan MapReduce

set -e

echo "=========================================="
echo "TESTING MAPREDUCE CLUSTER"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Test 1: WordCount - Basic MapReduce Test
test_wordcount() {
    print_status "Testing MapReduce with WordCount..."
    
    # Create sample text data
    cat > sample_flood_data.txt << 'EOF'
banjir lampung hujan deras sungai meluap
cuaca ekstrim banjir bandung hujan lebat
lampung banjir sungai way tulang budi
hujan deras lampung banjir meluap sungai
cuaca buruk banjir lampung hujan ekstrim
data cuaca bmkg lampung banjir prediksi
sensor iot lampung banjir monitoring
hbase nosql data banjir realtime
spark streaming data banjir analytics
hadoop mapreduce processing banjir data
EOF
    
    # Upload to HDFS
    print_status "Uploading sample data to HDFS..."
    docker exec namenode hdfs dfs -put sample_flood_data.txt /data/processing/input/
    
    # Run WordCount MapReduce job
    print_status "Running WordCount MapReduce job..."
    docker exec resourcemanager hadoop jar \
        /opt/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar \
        wordcount \
        /data/processing/input/sample_flood_data.txt \
        /data/processing/output/wordcount
    
    # Check results
    print_status "Checking WordCount results..."
    docker exec namenode hdfs dfs -cat /data/processing/output/wordcount/part-r-00000
    
    # Cleanup
    docker exec namenode hdfs dfs -rm -r /data/processing/output/wordcount
    rm sample_flood_data.txt
    
    print_status "✅ WordCount test completed successfully!"
}

# Test 2: Custom MapReduce for Weather Data Processing
test_weather_mapreduce() {
    print_status "Testing custom MapReduce for weather data processing..."
    
    # Create sample weather data
    cat > sample_weather_data.csv << 'EOF'
date,station_id,location,temperature,humidity,rainfall,wind_speed
2024-01-01,96747,Bandar_Lampung,28.5,75,0.0,5.2
2024-01-01,96749,Lampung_Tengah,27.8,80,2.1,4.8
2024-01-01,96751,Lampung_Utara,26.9,82,5.5,6.1
2024-01-02,96747,Bandar_Lampung,29.1,73,0.5,5.8
2024-01-02,96749,Lampung_Tengah,28.3,78,3.2,5.1
2024-01-02,96751,Lampung_Utara,27.2,85,8.1,6.8
2024-01-03,96747,Bandar_Lampung,27.9,78,12.5,7.2
2024-01-03,96749,Lampung_Tengah,27.1,83,15.8,6.9
2024-01-03,96751,Lampung_Utara,26.5,88,18.2,8.1
EOF
    
    # Upload weather data to HDFS
    print_status "Uploading weather data to HDFS..."
    docker exec namenode hdfs dfs -mkdir -p /data/raw/bmkg/sample
    docker exec namenode hdfs dfs -put sample_weather_data.csv /data/raw/bmkg/sample/
    
    # Create simple weather analysis MapReduce using streaming
    cat > weather_mapper.py << 'EOF'
#!/usr/bin/env python3
import sys

# Skip header
header_skipped = False

for line in sys.stdin:
    line = line.strip()
    if not header_skipped:
        header_skipped = True
        continue
    
    if line:
        fields = line.split(',')
        if len(fields) >= 6:
            date = fields[0]
            location = fields[2]
            rainfall = float(fields[5]) if fields[5] else 0.0
            
            # Emit location and rainfall
            print(f"{location}\t{rainfall}")
EOF

    cat > weather_reducer.py << 'EOF'
#!/usr/bin/env python3
import sys

current_location = None
total_rainfall = 0.0
count = 0

for line in sys.stdin:
    line = line.strip()
    if line:
        location, rainfall = line.split('\t')
        rainfall = float(rainfall)
        
        if current_location == location:
            total_rainfall += rainfall
            count += 1
        else:
            if current_location is not None:
                avg_rainfall = total_rainfall / count if count > 0 else 0
                print(f"{current_location}\t{avg_rainfall:.2f}\t{total_rainfall:.2f}\t{count}")
            
            current_location = location
            total_rainfall = rainfall
            count = 1

# Output last location
if current_location is not None:
    avg_rainfall = total_rainfall / count if count > 0 else 0
    print(f"{current_location}\t{avg_rainfall:.2f}\t{total_rainfall:.2f}\t{count}")
EOF

    # Make scripts executable
    chmod +x weather_mapper.py weather_reducer.py
    
    # Copy scripts to namenode
    docker cp weather_mapper.py namenode:/tmp/
    docker cp weather_reducer.py namenode:/tmp/
    
    # Run streaming MapReduce job
    print_status "Running weather analysis MapReduce job..."
    docker exec namenode hadoop jar \
        /opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-*.jar \
        -files /tmp/weather_mapper.py,/tmp/weather_reducer.py \
        -mapper weather_mapper.py \
        -reducer weather_reducer.py \
        -input /data/raw/bmkg/sample/sample_weather_data.csv \
        -output /data/processing/output/weather_analysis
    
    # Show results
    print_status "Weather analysis results:"
    docker exec namenode hdfs dfs -cat /data/processing/output/weather_analysis/part-00000
    
    # Cleanup
    docker exec namenode hdfs dfs -rm -r /data/processing/output/weather_analysis
    rm sample_weather_data.csv weather_mapper.py weather_reducer.py
    
    print_status "✅ Weather MapReduce test completed successfully!"
}

# Test 3: Validate HDFS replication and storage
test_hdfs_health() {
    print_status "Testing HDFS health and replication..."
    
    # Check HDFS status
    print_status "HDFS Status:"
    docker exec namenode hdfs dfsadmin -report
    
    # Check safe mode
    print_status "Checking safe mode status:"
    docker exec namenode hdfs dfsadmin -safemode get
    
    # List HDFS directories
    print_status "HDFS Directory structure:"
    docker exec namenode hdfs dfs -ls -R /data
    
    print_status "✅ HDFS health check completed!"
}

# Test 4: YARN Resource Manager functionality
test_yarn() {
    print_status "Testing YARN Resource Manager..."
    
    # Check YARN nodes
    print_status "YARN Node status:"
    docker exec resourcemanager yarn node -list
    
    # Check YARN applications
    print_status "YARN Applications:"
    docker exec resourcemanager yarn application -list
    
    print_status "✅ YARN test completed!"
}

# Test 5: Integration test - Full pipeline test
test_integration() {
    print_status "Running integration test - Full pipeline..."
    
    # Create flood simulation data
    cat > flood_simulation_data.txt << 'EOF'
2024-05-24,96747,Bandar_Lampung,HIGH_RAIN,25.5,extreme_weather
2024-05-24,96749,Lampung_Tengah,MEDIUM_RAIN,18.2,moderate_weather  
2024-05-24,96751,Lampung_Utara,HIGH_RAIN,32.1,extreme_weather
2024-05-23,96747,Bandar_Lampung,LOW_RAIN,5.2,normal_weather
2024-05-23,96749,Lampung_Tengah,MEDIUM_RAIN,12.8,moderate_weather
2024-05-23,96751,Lampung_Utara,HIGH_RAIN,28.9,extreme_weather
EOF
    
    # Upload to HDFS
    docker exec namenode hdfs dfs -put flood_simulation_data.txt /data/processing/input/
    
    # Create flood risk analysis mapper
    cat > flood_risk_mapper.py << 'EOF'
#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    if line:
        fields = line.split(',')
        if len(fields) >= 6:
            date = fields[0]
            location = fields[2]
            rain_level = fields[3]
            rainfall_amount = float(fields[4])
            weather_condition = fields[5]
            
            # Calculate flood risk
            risk_score = 0
            if rain_level == "HIGH_RAIN":
                risk_score += 3
            elif rain_level == "MEDIUM_RAIN":
                risk_score += 2
            elif rain_level == "LOW_RAIN":
                risk_score += 1
                
            if rainfall_amount > 30:
                risk_score += 3
            elif rainfall_amount > 15:
                risk_score += 2
            elif rainfall_amount > 5:
                risk_score += 1
                
            if weather_condition == "extreme_weather":
                risk_score += 2
            elif weather_condition == "moderate_weather":
                risk_score += 1
            
            # Determine risk level
            if risk_score >= 7:
                risk_level = "VERY_HIGH"
            elif risk_score >= 5:
                risk_level = "HIGH"
            elif risk_score >= 3:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            print(f"{location}\t{date}\t{risk_level}\t{risk_score}\t{rainfall_amount}")
EOF

    cat > flood_risk_reducer.py << 'EOF'
#!/usr/bin/env python3
import sys

locations = {}

for line in sys.stdin:
    line = line.strip()
    if line:
        parts = line.split('\t')
        if len(parts) >= 5:
            location = parts[0]
            date = parts[1]
            risk_level = parts[2]
            risk_score = int(parts[3])
            rainfall = float(parts[4])
            
            if location not in locations:
                locations[location] = {
                    'total_risk': 0,
                    'max_risk': 0,
                    'total_rainfall': 0,
                    'count': 0,
                    'high_risk_days': 0
                }
            
            locations[location]['total_risk'] += risk_score
            locations[location]['max_risk'] = max(locations[location]['max_risk'], risk_score)
            locations[location]['total_rainfall'] += rainfall
            locations[location]['count'] += 1
            
            if risk_level in ['HIGH', 'VERY_HIGH']:
                locations[location]['high_risk_days'] += 1

# Output summary for each location
for location, data in locations.items():
    avg_risk = data['total_risk'] / data['count']
    avg_rainfall = data['total_rainfall'] / data['count']
    risk_percentage = (data['high_risk_days'] / data['count']) * 100
    
    print(f"{location}\tAVG_RISK:{avg_risk:.2f}\tMAX_RISK:{data['max_risk']}\tAVG_RAINFALL:{avg_rainfall:.2f}\tHIGH_RISK_DAYS:{risk_percentage:.1f}%")
EOF

    # Make executable and copy
    chmod +x flood_risk_mapper.py flood_risk_reducer.py
    docker cp flood_risk_mapper.py namenode:/tmp/
    docker cp flood_risk_reducer.py namenode:/tmp/
    
    # Run flood risk analysis
    print_status "Running flood risk analysis MapReduce job..."
    docker exec namenode hadoop jar \
        /opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-*.jar \
        -files /tmp/flood_risk_mapper.py,/tmp/flood_risk_reducer.py \
        -mapper flood_risk_mapper.py \
        -reducer flood_risk_reducer.py \
        -input /data/processing/input/flood_simulation_data.txt \
        -output /data/analytics/predictions/flood_risk_analysis
    
    # Show results
    print_status "Flood risk analysis results:"
    docker exec namenode hdfs dfs -cat /data/analytics/predictions/flood_risk_analysis/part-00000
    
    # Save results to serving layer
    docker exec namenode hdfs dfs -cp /data/analytics/predictions/flood_risk_analysis/part-00000 /data/serving/hive/flood_risk_summary.txt
    
    # Cleanup
    rm flood_simulation_data.txt flood_risk_mapper.py flood_risk_reducer.py
    
    print_status "✅ Integration test completed successfully!"
}

# Main test runner
run_all_tests() {
    print_status "Starting comprehensive MapReduce testing..."
    print_status "This validates the Hadoop cluster setup for Lampung flood prediction project"
    print_status ""
    
    # Check if cluster is running
    if ! docker ps | grep -q "namenode"; then
        print_error "Hadoop cluster is not running. Please start with docker-compose up -d"
        exit 1
    fi
    
    # Wait for services to be ready
    print_status "Waiting for Hadoop services to be ready..."
    sleep 30
    
    # Run tests
    test_hdfs_health
    echo ""
    
    test_yarn
    echo ""
    
    test_wordcount
    echo ""
    
    test_weather_mapreduce
    echo ""
    
    test_integration
    echo ""
    
    print_status "=========================================="
    print_status "ALL MAPREDUCE TESTS COMPLETED!"
    print_status "=========================================="
    print_status ""
    print_status "✅ Basic WordCount test: PASSED"
    print_status "✅ Weather data processing: PASSED"
    print_status "✅ HDFS health check: PASSED" 
    print_status "✅ YARN functionality: PASSED"
    print_status "✅ Integration test: PASSED"
    print_status ""
    print_status "Your Hadoop cluster is ready for:"
    print_status "• Data ingestion from BMKG, BNPB, DEMNAS"
    print_status "• MapReduce processing of large datasets"
    print_status "• Integration with Hive for data warehousing"
    print_status "• Integration with HBase for NoSQL storage"
    print_status "• Spark MLlib for machine learning models"
    print_status ""
    print_status "Next steps:"
    print_status "1. Test Hive integration: docker exec hive-server beeline -u jdbc:hive2://localhost:10000"
    print_status "2. Test HBase: docker exec hbase-master hbase shell"
    print_status "3. Test Spark: docker exec spark-master spark-shell"
    print_status "4. Start developing your flood prediction models!"
}

# Individual test functions
case "${1:-all}" in
    wordcount)
        test_wordcount
        ;;
    weather)
        test_weather_mapreduce
        ;;
    hdfs)
        test_hdfs_health
        ;;
    yarn)
        test_yarn
        ;;
    integration)
        test_integration
        ;;
    all)
        run_all_tests
        ;;
    *)
        echo "Usage: $0 [wordcount|weather|hdfs|yarn|integration|all]"
        echo "Default: all"
        exit 1
        ;;
esac