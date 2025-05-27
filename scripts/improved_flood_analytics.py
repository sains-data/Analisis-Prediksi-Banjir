#!/usr/bin/env python3

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.functions import countDistinct, count, avg, sum, max, min, desc, asc, col, when, to_date, month, year, regexp_extract, round
from pyspark.sql.types import *

def create_spark_session():
    """Create Spark session with optimal configuration"""
    return SparkSession.builder \
        .appName("Improved Flood Analytics Pipeline") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.sql.catalogImplementation", "in-memory") \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .getOrCreate()

def load_csv_data(spark, hdfs_path, schema=None):
    """Load CSV data from HDFS with error handling"""
    try:
        print(f"Loading CSV from: {hdfs_path}")
        if schema:
            df = spark.read.option("header", "true").schema(schema).csv(hdfs_path)
        else:
            df = spark.read.option("header", "true").option("inferSchema", "true").csv(hdfs_path)
        
        record_count = df.count()
        print(f"Successfully loaded {record_count} records from {hdfs_path}")
        return df
    except Exception as e:
        print(f"Error loading {hdfs_path}: {str(e)}")
        return None

def load_json_array_data(spark, hdfs_path):
    """Load JSON array data from HDFS - specifically for sensor data"""
    try:
        print(f"Loading JSON array from: {hdfs_path}")
        
        # Define explicit schema for sensor data
        sensor_schema = ArrayType(StructType([
            StructField("sensor_id", StringType(), True),
            StructField("timestamp", StringType(), True),
            StructField("location", StringType(), True),
            StructField("water_level", DoubleType(), True),
            StructField("flow_rate", DoubleType(), True),
            StructField("temperature", DoubleType(), True),
            StructField("humidity", IntegerType(), True),
            StructField("battery", IntegerType(), True)
        ]))
        
        # Read the JSON as text first
        json_text = spark.read.text(hdfs_path)
        
        # Parse JSON using from_json function
        from pyspark.sql.functions import from_json, explode, col
        
        # Read the entire JSON file as a single row
        df = spark.read.option("multiline", "true").json(hdfs_path)
        
        # Check the structure
        print("JSON structure analysis:")
        df.printSchema()
        df.show(truncate=False)
        
        # If it's an array in the root, we need to handle it differently
        # Try reading with RDD approach for array JSON
        json_rdd = spark.sparkContext.textFile(hdfs_path)
        json_string = json_rdd.collect()[0]  # Get the entire JSON string
        
        # Parse the JSON string directly
        import json
        json_data = json.loads(json_string)
        
        # Convert to DataFrame
        sensor_df = spark.createDataFrame(json_data)
        
        record_count = sensor_df.count()
        print(f"Successfully loaded {record_count} sensor records")
        
        # Show sample data
        print("Sample sensor data:")
        sensor_df.show(5)
        
        return sensor_df
        
    except Exception as e:
        print(f"Error loading JSON array from {hdfs_path}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def analyze_weather_data(weather_df):
    """Comprehensive weather data analysis"""
    print("\n" + "="*50)
    print("WEATHER DATA ANALYSIS")
    print("="*50)
    
    if not weather_df:
        print("❌ No weather data available")
        return None
    
    record_count = weather_df.count()
    print(f"📊 Total weather records: {record_count:,}")
    
    if record_count == 0:
        print("❌ Weather dataset is empty")
        return None
    
    # Show schema and sample data
    print("\n🔍 Weather data structure:")
    weather_df.printSchema()
    
    print("\n📋 Sample weather data:")
    weather_df.show(5, truncate=False)
    
    # Basic statistics
    print("\n📈 Weather data statistics:")
    weather_df.describe().show()
      # High rainfall analysis
    high_rainfall_threshold = 50.0
    high_rainfall = weather_df.filter(col("rainfall") > high_rainfall_threshold)
    high_rainfall_count = high_rainfall.count()
    print(f"🌧️  High rainfall days (>{high_rainfall_threshold}mm): {high_rainfall_count:,}")
    
    if high_rainfall_count > 0:
        print("\n☔ Extreme rainfall events:")
        high_rainfall.select("location", "timestamp", "rainfall") \
            .orderBy(desc("rainfall")) \
            .show(10)
    
    # Location-based analysis
    print("\n🗺️  Weather analysis by location:")
    location_stats = weather_df.groupBy("location") \
        .agg(
            count("*").alias("record_count"),
            round(avg("rainfall"), 2).alias("avg_rainfall_mm"),
            round(max("rainfall"), 2).alias("max_rainfall_mm"),
            round(avg("humidity"), 1).alias("avg_humidity_pct"),
            round(avg("temperature"), 1).alias("avg_temp_celsius"),
            round(avg("wind_speed"), 1).alias("avg_wind_speed_kmh")
        ) \
        .orderBy(desc("avg_rainfall_mm"))
    
    location_stats.show(20, truncate=False)
      # Monthly rainfall patterns
    print("\n📅 Monthly rainfall patterns:")
    monthly_rainfall = weather_df.withColumn("month", month(to_date(col("timestamp")))) \
        .groupBy("month") \
        .agg(
            round(avg("rainfall"), 2).alias("avg_rainfall"),
            round(sum("rainfall"), 2).alias("total_rainfall"),
            count("*").alias("day_count")
        ) \
        .orderBy("month")
    
    monthly_rainfall.show(12)
    
    return location_stats

def analyze_elevation_data(elevation_df):
    """Comprehensive elevation and topography analysis"""
    print("\n" + "="*50)
    print("ELEVATION & TOPOGRAPHY ANALYSIS")
    print("="*50)
    
    if not elevation_df:
        print("❌ No elevation data available")
        return None
    
    record_count = elevation_df.count()
    print(f"📊 Total elevation grid points: {record_count:,}")
    
    if record_count == 0:
        print("❌ Elevation dataset is empty")
        return None
    
    # Show schema and sample data
    print("\n🔍 Elevation data structure:")
    elevation_df.printSchema()
    
    print("\n📋 Sample elevation data:")
    elevation_df.show(5, truncate=False)
    
    # Basic elevation statistics
    print("\n📈 Elevation statistics:")
    elevation_df.describe().show()
    
    # Flood risk areas (low elevation)
    low_elevation_threshold = 100.0  # meters
    low_elevation = elevation_df.filter(col("elevation_m") < low_elevation_threshold)
    low_elevation_count = low_elevation.count()
    percentage = (low_elevation_count / record_count) * 100
    
    print(f"⚠️  Low elevation areas (<{low_elevation_threshold}m): {low_elevation_count:,} ({percentage:.1f}%)")
    
    # High flood risk areas (low elevation + flat terrain)
    high_risk_areas = elevation_df.filter(
        (col("elevation_m") < 200) & (col("slope_deg") < 5)
    )
    high_risk_count = high_risk_areas.count()
    risk_percentage = (high_risk_count / record_count) * 100
    
    print(f"🚨 High flood risk areas (low & flat): {high_risk_count:,} ({risk_percentage:.1f}%)")
    
    # Land cover analysis
    print("\n🌍 Flood risk by land cover type:")
    landcover_risk = elevation_df.groupBy("land_cover") \
        .agg(
            count("*").alias("total_areas"),
            round(avg("elevation_m"), 1).alias("avg_elevation_m"),
            round(avg("slope_deg"), 1).alias("avg_slope_deg"),
            round(min("elevation_m"), 1).alias("min_elevation_m"),
            round(max("elevation_m"), 1).alias("max_elevation_m"),
            sum(when(col("elevation_m") < 100, 1).otherwise(0)).alias("low_elevation_count")
        ) \
        .withColumn("flood_risk_pct", round((col("low_elevation_count") / col("total_areas")) * 100, 1)) \
        .orderBy(desc("flood_risk_pct"))
    
    landcover_risk.show(20, truncate=False)
    
    # Slope analysis for drainage assessment
    print("\n⛰️  Slope analysis for drainage:")
    slope_analysis = elevation_df.groupBy("land_cover") \
        .agg(
            round(avg("slope_deg"), 1).alias("avg_slope"),
            sum(when(col("slope_deg") < 2, 1).otherwise(0)).alias("very_flat_areas"),
            sum(when((col("slope_deg") >= 2) & (col("slope_deg") < 5), 1).otherwise(0)).alias("gentle_slope_areas"),
            sum(when(col("slope_deg") >= 5, 1).otherwise(0)).alias("steep_areas")
        ) \
        .orderBy("avg_slope")
    
    slope_analysis.show(20, truncate=False)
    
    return landcover_risk

def analyze_flood_history(flood_df):
    """Comprehensive historical flood analysis"""
    print("\n" + "="*50)
    print("HISTORICAL FLOOD DATA ANALYSIS")
    print("="*50)
    
    if not flood_df:
        print("❌ No flood history data available")
        return None
    
    record_count = flood_df.count()
    print(f"📊 Total flood incidents: {record_count:,}")
    
    if record_count == 0:
        print("❌ Flood history dataset is empty")
        return None
    
    # Show schema and sample data
    print("\n🔍 Flood history data structure:")
    flood_df.printSchema()
    
    print("\n📋 Sample flood history data:")
    flood_df.show(5, truncate=False)
    
    # Basic flood statistics
    print("\n📈 Flood incident statistics:")
    flood_df.describe().show()
    
    # Flood frequency by location
    print("\n🗺️  Flood frequency by location:")
    location_floods = flood_df.groupBy("lokasi") \
        .agg(
            count("*").alias("flood_incidents"),
            round(avg("tinggi_air_cm"), 1).alias("avg_water_height_cm"),
            round(max("tinggi_air_cm"), 1).alias("max_water_height_cm"),
            round(avg("area_terdampak_ha"), 1).alias("avg_affected_area_ha"),
            round(sum("area_terdampak_ha"), 1).alias("total_affected_area_ha"),
            round(avg("durasi_jam"), 1).alias("avg_duration_hours"),
            round(sum("jumlah_pengungsi"), 0).alias("total_refugees")
        ) \
        .orderBy(desc("flood_incidents"))
    
    location_floods.show(20, truncate=False)
    
    # Temporal analysis
    print("\n📅 Flood incidents by year:")
    yearly_floods = flood_df.withColumn("year", year(to_date(col("tanggal"), "yyyy-MM-dd"))) \
        .groupBy("year") \
        .agg(
            count("*").alias("flood_count"),
            round(avg("tinggi_air_cm"), 1).alias("avg_water_height"),
            round(sum("jumlah_pengungsi"), 0).alias("total_refugees")
        ) \
        .orderBy("year")
    
    yearly_floods.show()
    
    # Severity analysis
    print("\n⚠️  Flood severity analysis:")
    severity_analysis = flood_df \
        .withColumn("severity_category", 
                   when(col("tinggi_air_cm") > 200, "Extreme (>2m)")
                   .when(col("tinggi_air_cm") > 100, "High (1-2m)")
                   .when(col("tinggi_air_cm") > 50, "Moderate (0.5-1m)")
                   .otherwise("Low (<0.5m)")) \
        .groupBy("severity_category") \
        .agg(
            count("*").alias("incident_count"),
            round(avg("area_terdampak_ha"), 1).alias("avg_affected_area"),
            round(sum("jumlah_pengungsi"), 0).alias("total_refugees")
        ) \
        .orderBy(desc("incident_count"))
    
    severity_analysis.show()
    
    return location_floods

def analyze_sensor_data(sensor_df):
    """Comprehensive IoT sensor data analysis"""
    print("\n" + "="*50)
    print("IoT SENSOR DATA ANALYSIS")
    print("="*50)
    
    if not sensor_df:
        print("❌ No sensor data available")
        return None
    
    record_count = sensor_df.count()
    print(f"📊 Total sensor readings: {record_count:,}")
    
    if record_count == 0:
        print("❌ Sensor dataset is empty")
        return None
    
    # Show schema and sample data
    print("\n🔍 Sensor data structure:")
    sensor_df.printSchema()
    
    print("\n📋 Sample sensor data:")
    sensor_df.show(10, truncate=False)
    
    # Basic sensor statistics
    print("\n📈 Sensor readings statistics:")
    sensor_df.describe().show()
    
    # Critical water level analysis
    critical_threshold = 2.0  # meters
    warning_threshold = 1.5   # meters
    
    critical_readings = sensor_df.filter(col("water_level") > critical_threshold)
    warning_readings = sensor_df.filter(
        (col("water_level") > warning_threshold) & (col("water_level") <= critical_threshold)
    )
    
    print(f"🚨 Critical water levels (>{critical_threshold}m): {critical_readings.count()}")
    print(f"⚠️  Warning water levels ({warning_threshold}-{critical_threshold}m): {warning_readings.count()}")
    
    if critical_readings.count() > 0:
        print("\n🚨 Critical flood conditions:")
        critical_readings.select("sensor_id", "location", "timestamp", "water_level", "flow_rate") \
            .orderBy(desc("water_level")) \
            .show(10, truncate=False)
    
    # Location-based sensor analysis
    print("\n🗺️  Sensor readings by location:")
    location_sensors = sensor_df.groupBy("location") \
        .agg(
            count("*").alias("reading_count"),
            countDistinct("sensor_id").alias("sensor_count"),
            round(avg("water_level"), 2).alias("avg_water_level_m"),
            round(max("water_level"), 2).alias("max_water_level_m"),
            round(avg("flow_rate"), 2).alias("avg_flow_rate"),
            round(max("flow_rate"), 2).alias("max_flow_rate"),
            round(avg("temperature"), 1).alias("avg_temperature"),
            round(avg("humidity"), 0).alias("avg_humidity"),
            round(avg("battery"), 0).alias("avg_battery_pct")
        ) \
        .orderBy(desc("max_water_level_m"))
    
    location_sensors.show(20, truncate=False)
    
    # Sensor health monitoring
    print("\n🔋 Sensor health status:")
    low_battery_threshold = 30
    low_battery_sensors = sensor_df.filter(col("battery") < low_battery_threshold)
    
    print(f"⚠️  Sensors with low battery (<{low_battery_threshold}%): {low_battery_sensors.count()}")
    
    if low_battery_sensors.count() > 0:
        low_battery_sensors.select("sensor_id", "location", "battery", "timestamp") \
            .orderBy("battery") \
            .show(10, truncate=False)
    
    # Flow rate analysis
    print("\n🌊 Flow rate analysis:")
    high_flow_threshold = 20.0  # m³/s
    high_flow_readings = sensor_df.filter(col("flow_rate") > high_flow_threshold)
    
    print(f"💨 High flow rate readings (>{high_flow_threshold} m³/s): {high_flow_readings.count()}")
    
    return location_sensors

def integrated_flood_risk_assessment(weather_df, elevation_df, flood_df, sensor_df):
    """Comprehensive integrated flood risk assessment"""
    print("\n" + "="*60)
    print("INTEGRATED FLOOD RISK ASSESSMENT")
    print("="*60)
    
    try:
        risk_factors = []
        
        # 1. Weather-based risk assessment
        if weather_df:
            print("\n🌧️  Weather-based risk factors:")
            high_rainfall_locations = weather_df.filter(col("rainfall") > 30) \
                .groupBy("location") \
                .agg(
                    count("*").alias("high_rainfall_days"),
                    round(avg("rainfall"), 2).alias("avg_high_rainfall")
                ) \
                .withColumn("weather_risk_score", 
                           round((col("high_rainfall_days") * col("avg_high_rainfall")) / 100, 2))
            
            print("High rainfall risk by location:")
            high_rainfall_locations.orderBy(desc("weather_risk_score")).show(10)
            risk_factors.append("weather")
        
        # 2. Topographic risk assessment
        if elevation_df:
            print("\n⛰️  Topographic risk factors:")
            topo_risk = elevation_df.groupBy("land_cover") \
                .agg(
                    count("*").alias("total_areas"),
                    round(avg("elevation_m"), 1).alias("avg_elevation"),
                    round(avg("slope_deg"), 1).alias("avg_slope"),
                    sum(when((col("elevation_m") < 100) & (col("slope_deg") < 3), 1).otherwise(0)).alias("high_risk_areas")
                ) \
                .withColumn("topo_risk_pct", 
                           round((col("high_risk_areas") / col("total_areas")) * 100, 1)) \
                .orderBy(desc("topo_risk_pct"))
            
            print("Topographic flood risk by land cover:")
            topo_risk.show(15, truncate=False)
            risk_factors.append("topography")
        
        # 3. Historical flood risk
        if flood_df:
            print("\n📜 Historical flood risk:")
            historical_risk = flood_df.groupBy("lokasi") \
                .agg(
                    count("*").alias("flood_frequency"),
                    round(avg("tinggi_air_cm"), 1).alias("avg_water_height"),
                    round(max("tinggi_air_cm"), 1).alias("max_water_height")
                ) \
                .withColumn("historical_risk_score", 
                           round((col("flood_frequency") * col("avg_water_height")) / 50, 2)) \
                .orderBy(desc("historical_risk_score"))
            
            print("Historical flood risk by location:")
            historical_risk.show(15, truncate=False)
            risk_factors.append("historical")
        
        # 4. Real-time sensor risk
        if sensor_df:
            print("\n📡 Real-time sensor risk assessment:")
            current_risk = sensor_df.groupBy("location") \
                .agg(
                    round(max("water_level"), 2).alias("current_max_water_level"),
                    round(avg("water_level"), 2).alias("avg_water_level"),
                    round(max("flow_rate"), 2).alias("max_flow_rate"),
                    count("*").alias("sensor_readings")
                ) \
                .withColumn("current_risk_level",
                           when(col("current_max_water_level") > 2.0, "CRITICAL")
                           .when(col("current_max_water_level") > 1.5, "HIGH")
                           .when(col("current_max_water_level") > 1.0, "MODERATE")
                           .otherwise("LOW")) \
                .orderBy(desc("current_max_water_level"))
            
            print("Current flood risk by location:")
            current_risk.show(20, truncate=False)
            risk_factors.append("real-time sensors")
        
        # Summary
        print("\n📊 FLOOD RISK ASSESSMENT SUMMARY:")
        print("=" * 50)
        print(f"✅ Analysis completed using {len(risk_factors)} data sources:")
        for i, factor in enumerate(risk_factors, 1):
            print(f"   {i}. {factor.title()}")
        
        # Recommendations
        print("\n🎯 FLOOD RISK MITIGATION RECOMMENDATIONS:")
        print("=" * 50)
        print("1. 🚨 Monitor high-risk locations with critical water levels")
        print("2. 🏗️  Implement drainage improvements in low-lying flat areas")
        print("3. 📡 Maintain sensor network - replace low battery sensors")
        print("4. 🌧️  Establish rainfall early warning systems")
        print("5. 📋 Update evacuation plans for historically flood-prone areas")
        print("6. 🌊 Improve river channel capacity in high flow rate areas")
        
    except Exception as e:
        print(f"❌ Integrated analysis error: {str(e)}")
        import traceback
        traceback.print_exc()

def save_analysis_results(spark, df, output_path, analysis_name):
    """Save analysis results to HDFS with improved error handling"""
    try:
        if not df or df.count() == 0:
            print(f"⚠️  No data to save for {analysis_name}")
            return False
        
        full_path = f"{output_path}/{analysis_name}"
        print(f"💾 Saving {analysis_name} results to: {full_path}")
        
        # Save as CSV with header
        df.coalesce(1).write.mode("overwrite").option("header", "true").csv(full_path)
        
        record_count = df.count()
        print(f"✅ Successfully saved {record_count} records to {full_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving {analysis_name} to {output_path}: {str(e)}")
        return False

def main():
    """Main analytics pipeline execution"""
    print("🚀 STARTING IMPROVED FLOOD ANALYTICS PIPELINE")
    print("=" * 60)
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        # Configuration
        hdfs_base = "hdfs://namenode:8020"
        input_path = f"{hdfs_base}/data/input"
        output_path = f"{hdfs_base}/data/processed"
        
        print(f"📁 Input path: {input_path}")
        print(f"📁 Output path: {output_path}")
        
        # Data loading phase
        print("\n🔄 DATA LOADING PHASE")
        print("-" * 30)
        
        print("1️⃣  Loading weather data...")
        weather_df = load_csv_data(spark, f"{input_path}/data_cuaca_bmkg.csv")
        
        print("2️⃣  Loading elevation data...")
        elevation_df = load_csv_data(spark, f"{input_path}/regional_elevation_summary.csv")
        
        print("3️⃣  Loading flood history...")
        flood_df = load_csv_data(spark, f"{input_path}/data_banjir_historis.csv")
        
        print("4️⃣  Loading sensor data...")
        sensor_df = load_json_array_data(spark, f"{input_path}/data_sensor_iot.json")
        
        # Analysis phase
        print("\n🔬 DATA ANALYSIS PHASE")
        print("-" * 30)
        
        # Individual analyses
        weather_results = analyze_weather_data(weather_df) if weather_df else None
        elevation_results = analyze_elevation_data(elevation_df) if elevation_df else None
        flood_results = analyze_flood_history(flood_df) if flood_df else None
        sensor_results = analyze_sensor_data(sensor_df) if sensor_df else None
        
        # Save results phase
        print("\n💾 SAVING RESULTS PHASE")
        print("-" * 30)
        
        saved_analyses = []
        
        if save_analysis_results(spark, weather_results, output_path, "weather_analysis"):
            saved_analyses.append("Weather Analysis")
        
        if save_analysis_results(spark, elevation_results, output_path, "elevation_analysis"):
            saved_analyses.append("Elevation Analysis")
        
        if save_analysis_results(spark, flood_results, output_path, "flood_analysis"):
            saved_analyses.append("Flood History Analysis")
        
        if save_analysis_results(spark, sensor_results, output_path, "sensor_analysis"):
            saved_analyses.append("Sensor Analysis")
        
        # Integrated analysis phase
        print("\n🔗 INTEGRATED ANALYSIS PHASE")
        print("-" * 30)
        
        integrated_flood_risk_assessment(weather_df, elevation_df, flood_df, sensor_df)
        
        # Final summary
        print("\n🎉 PIPELINE COMPLETION SUMMARY")
        print("=" * 60)
        
        # Count successfully loaded datasets
        loaded_datasets = []
        if weather_df: loaded_datasets.append(f"Weather Data ({weather_df.count():,} records)")
        if elevation_df: loaded_datasets.append(f"Elevation Data ({elevation_df.count():,} records)")
        if flood_df: loaded_datasets.append(f"Flood History ({flood_df.count():,} records)")
        if sensor_df: loaded_datasets.append(f"Sensor Data ({sensor_df.count():,} records)")
        
        print(f"✅ Successfully processed {len(loaded_datasets)} datasets:")
        for dataset in loaded_datasets:
            print(f"   📊 {dataset}")
        
        print(f"\n✅ Successfully saved {len(saved_analyses)} analysis results:")
        for analysis in saved_analyses:
            print(f"   💾 {analysis}")
        
        print("\n🎯 FLOOD RISK ANALYTICS PIPELINE COMPLETED SUCCESSFULLY!")
        print("📋 Comprehensive flood risk assessment completed for Lampung region")
        print("📊 All results saved to HDFS for further visualization and reporting")
          # Performance metrics
        total_records = 0
        for df in [weather_df, elevation_df, flood_df, sensor_df]:
            if df:
                total_records += df.count()
        print(f"📈 Total records processed: {total_records:,}")
        
    except Exception as e:
        print(f"❌ PIPELINE ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🔚 Stopping Spark session...")
        spark.stop()
        print("✅ Spark session stopped successfully")

if __name__ == "__main__":
    main()
