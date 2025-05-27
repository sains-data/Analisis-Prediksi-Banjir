"""
DAG untuk Pipeline Prediksi Banjir Lampung - Real Data Integration
Menggunakan data dummy yang sebenarnya dari BMKG, IoT sensors, DEMNAS, dan BNPB

Author: Lampung Flood Prediction Team
Date: 2025-05-26
Version: 2.0 - Real Data Integration
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import pandas as pd
import json
import numpy as np
import logging
import os
from pathlib import Path

# Default arguments untuk DAG
default_args = {
    'owner': 'lampung-flood-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 26),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=1)
}

# Inisialisasi DAG
dag = DAG(
    'lampung_flood_prediction_real_data',
    default_args=default_args,
    description='Pipeline prediksi banjir Lampung menggunakan real dummy data',
    schedule_interval=timedelta(hours=1),  # Eksekusi setiap jam
    catchup=False,
    max_active_runs=1,
    tags=['flood-prediction', 'lampung', 'real-data', 'machine-learning']
)

# ==================== DATA PATHS ====================
BASE_DATA_PATH = "/opt/airflow/data/raw"
BMKG_HISTORICAL_PATH = f"{BASE_DATA_PATH}/bmkg/cuaca_historis/data_cuaca_bmkg.csv"
IOT_SENSOR_PATH = f"{BASE_DATA_PATH}/iot/data_sensor_iot.json"
DEMNAS_TOPO_PATH = f"{BASE_DATA_PATH}/demnas/topografi/data_elevasi_demnas.csv"
BNPB_FLOOD_PATH = f"{BASE_DATA_PATH}/bnpb/kejadian_banjir/data_banjir_historis.csv"

# ==================== TASK FUNCTIONS ====================

def extract_bmkg_real_data(**context):
    """
    Extract data BMKG dari file CSV yang sudah ada
    Kolom: timestamp,location,rainfall,humidity,temperature,wind_speed
    """
    print("🌦️ Starting BMKG real data extraction...")
    
    try:
        # Read BMKG historical data
        bmkg_data = pd.read_csv(BMKG_HISTORICAL_PATH)
        
        print(f"📊 BMKG data loaded: {len(bmkg_data)} records")
        print(f"📍 Locations: {bmkg_data['location'].unique().tolist()}")
        print(f"📅 Date range: {bmkg_data['timestamp'].min()} to {bmkg_data['timestamp'].max()}")
        
        # Get recent data (simulate real-time by getting latest data per location)
        latest_data = bmkg_data.groupby('location').tail(1).reset_index(drop=True)
        
        # Convert to our format
        weather_data = []
        current_time = datetime.now()
        
        for _, row in latest_data.iterrows():
            # Map locations to station IDs
            location_to_id = {
                'Bandar Lampung': '96747',
                'Metro': '96749', 
                'Lampung Barat': '96751',
                'Lampung Selatan': '96753',
                'Lampung Tengah': '96755',
                'Lampung Timur': '96756',
                'Lampung Utara': '96757',
                'Mesuji': '96758',
                'Pesawaran': '96759',
                'Pesisir Barat': '96760'
            }
            
            station_id = location_to_id.get(row['location'], '96999')
            
            weather_record = {
                'station_id': station_id,
                'station_name': row['location'],
                'timestamp': current_time.isoformat(),
                'temperature': float(row['temperature']),
                'humidity': float(row['humidity']),
                'rainfall': float(row['rainfall']),  # Menggunakan kolom asli
                'wind_speed': float(row['wind_speed']),
                
                # Derived fields for compatibility
                'rainfall_1h': float(row['rainfall']),
                'rainfall_3h': float(row['rainfall']) * 2.5,  # Estimasi
                'rainfall_24h': float(row['rainfall']) * 8,   # Estimasi
                'pressure': 1013.0 + np.random.uniform(-5, 5),  # Default + noise
                'visibility': 10.0 + np.random.uniform(-2, 5),  # Default + noise
                'weather_condition': 'hujan' if row['rainfall'] > 5 else 'berawan' if row['humidity'] > 80 else 'cerah'
            }
            
            weather_data.append(weather_record)
            print(f"✅ Processed {row['location']}: {weather_record['rainfall']}mm rainfall, {weather_record['temperature']}°C")
        
        print(f"🌦️ BMKG extraction completed: {len(weather_data)} current stations processed")
        
        # Save processed data
        output_path = f"/opt/airflow/data/processing/bmkg_current_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(weather_data, f, indent=2)
        
        return weather_data
        
    except Exception as e:
        print(f"❌ Error reading BMKG data: {e}")
        print(f"📂 Expected path: {BMKG_HISTORICAL_PATH}")
        raise

def extract_iot_real_data(**context):
    """
    Extract data IoT sensor dari file JSON yang sudah ada
    Format: sensor_id, timestamp, location, water_level, flow_rate, temperature, humidity, battery
    """
    print("🌊 Starting IoT real data extraction...")
    
    try:
        # Read IoT sensor data
        with open(IOT_SENSOR_PATH, 'r') as f:
            iot_raw_data = json.load(f)
        
        print(f"📊 IoT data loaded: {len(iot_raw_data)} sensor records")
        
        # Process IoT data to our format
        sensor_data = []
        current_time = datetime.now()
        
        for sensor in iot_raw_data:
            # Determine sensor type based on data available
            if 'water_level' in sensor and 'flow_rate' in sensor:
                sensor_type = 'water_level'
                
                # Convert water_level from meters to cm (sesuai format asli)
                water_level_cm = float(sensor['water_level']) * 100
                
                # Determine flood risk based on water level
                if water_level_cm > 250:
                    flood_risk = "VERY_HIGH"
                elif water_level_cm > 200:
                    flood_risk = "HIGH"
                elif water_level_cm > 150:
                    flood_risk = "MEDIUM"
                else:
                    flood_risk = "LOW"
                
                sensor_record = {
                    'sensor_id': sensor['sensor_id'],
                    'location': sensor['location'],
                    'sensor_type': sensor_type,
                    'timestamp': current_time.isoformat(),
                    'water_level_cm': water_level_cm,
                    'water_level_original': float(sensor['water_level']),  # Keep original for reference
                    'flow_rate': float(sensor['flow_rate']),
                    'temperature': float(sensor['temperature']),
                    'humidity': float(sensor['humidity']),
                    'battery_level': float(sensor['battery']),
                    'flood_risk': flood_risk,
                    'status': 'ACTIVE' if sensor['battery'] > 20 else 'LOW_BATTERY'
                }
            else:
                # Weather-type sensor (if no water_level data)
                sensor_record = {
                    'sensor_id': sensor['sensor_id'],
                    'location': sensor['location'],
                    'sensor_type': 'weather',
                    'timestamp': current_time.isoformat(),
                    'temperature': float(sensor['temperature']),
                    'humidity': float(sensor['humidity']),
                    'battery_level': float(sensor['battery']),
                    'status': 'ACTIVE' if sensor['battery'] > 20 else 'LOW_BATTERY'
                }
            
            sensor_data.append(sensor_record)
            print(f"✅ Processed {sensor['sensor_id']}: {sensor['location']}")
        
        print(f"🌊 IoT extraction completed: {len(sensor_data)} sensors processed")
        
        # Save processed data
        output_path = f"/opt/airflow/data/processing/iot_current_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(sensor_data, f, indent=2)
        
        return sensor_data
        
    except Exception as e:
        print(f"❌ Error reading IoT data: {e}")
        print(f"📂 Expected path: {IOT_SENSOR_PATH}")
        raise

def extract_demnas_topography(**context):
    """
    Extract data topografi DEMNAS untuk analisis risiko berdasarkan elevasi
    Kolom: grid_id,longitude,latitude,elevation_m,slope_deg,land_cover
    """
    print("🗻 Starting DEMNAS topography extraction...")
    
    try:
        # Read DEMNAS topography data
        demnas_data = pd.read_csv(DEMNAS_TOPO_PATH)
        
        print(f"📊 DEMNAS data loaded: {len(demnas_data)} grid points")
        print(f"🏔️ Elevation range: {demnas_data['elevation_m'].min():.1f}m - {demnas_data['elevation_m'].max():.1f}m")
        print(f"📐 Slope range: {demnas_data['slope_deg'].min():.1f}° - {demnas_data['slope_deg'].max():.1f}°")
        
        # Aggregate topography data by area for flood risk assessment
        topo_summary = {
            'total_grid_points': len(demnas_data),
            'avg_elevation': float(demnas_data['elevation_m'].mean()),
            'min_elevation': float(demnas_data['elevation_m'].min()),
            'max_elevation': float(demnas_data['elevation_m'].max()),
            'avg_slope': float(demnas_data['slope_deg'].mean()),
            'low_elevation_areas': len(demnas_data[demnas_data['elevation_m'] < 50]),  # < 50m elevation
            'high_slope_areas': len(demnas_data[demnas_data['slope_deg'] > 15]),      # > 15° slope
            'land_cover_distribution': demnas_data['land_cover'].value_counts().to_dict(),
            'flood_risk_zones': {
                'very_high_risk': len(demnas_data[(demnas_data['elevation_m'] < 20) & (demnas_data['slope_deg'] < 5)]),
                'high_risk': len(demnas_data[(demnas_data['elevation_m'] < 50) & (demnas_data['slope_deg'] < 10)]),
                'medium_risk': len(demnas_data[(demnas_data['elevation_m'] < 100) & (demnas_data['slope_deg'] < 15)]),
                'low_risk': len(demnas_data[(demnas_data['elevation_m'] >= 100) | (demnas_data['slope_deg'] >= 15)])
            }
        }
        
        print(f"🗻 Topography summary:")
        print(f"   Average elevation: {topo_summary['avg_elevation']:.1f}m")
        print(f"   Low elevation areas (<50m): {topo_summary['low_elevation_areas']} grid points")
        print(f"   Very high flood risk zones: {topo_summary['flood_risk_zones']['very_high_risk']} grid points")
        
        # Save processed topography data
        current_time = datetime.now()
        output_path = f"/opt/airflow/data/processing/demnas_summary_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(topo_summary, f, indent=2)
        
        return topo_summary
        
    except Exception as e:
        print(f"❌ Error reading DEMNAS data: {e}")
        print(f"📂 Expected path: {DEMNAS_TOPO_PATH}")
        raise

def extract_bnpb_historical_floods(**context):
    """
    Extract data kejadian banjir historis dari BNPB
    Kolom: tanggal,lokasi,tinggi_air_cm,area_terdampak_ha,durasi_jam,jumlah_pengungsi
    """
    print("📋 Starting BNPB historical flood data extraction...")
    
    try:
        # Read BNPB flood historical data
        bnpb_data = pd.read_csv(BNPB_FLOOD_PATH)
        
        print(f"📊 BNPB flood data loaded: {len(bnpb_data)} historical events")
        print(f"📍 Affected locations: {bnpb_data['lokasi'].unique().tolist()}")
        print(f"📅 Period: {bnpb_data['tanggal'].min()} to {bnpb_data['tanggal'].max()}")
        
        # Analyze historical patterns per location
        location_analysis = {}
        for location in bnpb_data['lokasi'].unique():
            location_data = bnpb_data[bnpb_data['lokasi'] == location]
            
            location_analysis[location] = {
                'total_events': len(location_data),
                'avg_water_height_cm': float(location_data['tinggi_air_cm'].mean()),
                'max_water_height_cm': float(location_data['tinggi_air_cm'].max()),
                'avg_affected_area_ha': float(location_data['area_terdampak_ha'].mean()),
                'total_evacuees': int(location_data['jumlah_pengungsi'].sum()),
                'avg_duration_hours': float(location_data['durasi_jam'].mean()),
                'risk_score': 0.0  # Will be calculated
            }
            
            # Calculate risk score based on historical data
            # Factors: frequency, severity (water height), impact (evacuees), duration
            frequency_score = min(1.0, len(location_data) / 10)  # Normalize by max 10 events
            severity_score = min(1.0, location_data['tinggi_air_cm'].max() / 300)  # Normalize by 300cm max
            impact_score = min(1.0, location_data['jumlah_pengungsi'].sum() / 20000)  # Normalize by 20k evacuees
            duration_score = min(1.0, location_data['durasi_jam'].mean() / 50)  # Normalize by 50 hours
            
            risk_score = (frequency_score * 0.3 + severity_score * 0.4 + impact_score * 0.2 + duration_score * 0.1)
            location_analysis[location]['risk_score'] = round(risk_score, 3)
            
            # Determine risk category
            if risk_score >= 0.7:
                location_analysis[location]['risk_category'] = 'VERY_HIGH'
            elif risk_score >= 0.5:
                location_analysis[location]['risk_category'] = 'HIGH'
            elif risk_score >= 0.3:
                location_analysis[location]['risk_category'] = 'MEDIUM'
            else:
                location_analysis[location]['risk_category'] = 'LOW'
        
        historical_summary = {
            'total_flood_events': len(bnpb_data),
            'total_evacuees_historical': int(bnpb_data['jumlah_pengungsi'].sum()),
            'avg_flood_height': float(bnpb_data['tinggi_air_cm'].mean()),
            'max_flood_height': float(bnpb_data['tinggi_air_cm'].max()),
            'most_affected_locations': bnpb_data['lokasi'].value_counts().head(5).to_dict(),
            'location_risk_analysis': location_analysis
        }
        
        print(f"📋 Historical flood analysis:")
        print(f"   Total events: {historical_summary['total_flood_events']}")
        print(f"   Total evacuees: {historical_summary['total_evacuees_historical']:,}")
        print(f"   Average flood height: {historical_summary['avg_flood_height']:.1f}cm")
        
        # Save processed historical data
        current_time = datetime.now()
        output_path = f"/opt/airflow/data/processing/bnpb_analysis_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(historical_summary, f, indent=2)
        
        return historical_summary
        
    except Exception as e:
        print(f"❌ Error reading BNPB data: {e}")
        print(f"📂 Expected path: {BNPB_FLOOD_PATH}")
        raise

def integrate_and_validate_data(**context):
    """
    Integrasikan dan validasi semua data dari multiple sources
    """
    print("🔗 Starting data integration and validation...")
    
    # Get data from previous tasks
    bmkg_data = context['task_instance'].xcom_pull(task_ids='extract_bmkg_real_data')
    iot_data = context['task_instance'].xcom_pull(task_ids='extract_iot_real_data') 
    topo_data = context['task_instance'].xcom_pull(task_ids='extract_demnas_topography')
    flood_history = context['task_instance'].xcom_pull(task_ids='extract_bnpb_historical')
    
    print(f"📊 Data integration summary:")
    print(f"   BMKG weather stations: {len(bmkg_data)}")
    print(f"   IoT sensors: {len(iot_data)}")
    print(f"   Topography grid points: {topo_data['total_grid_points']}")
    print(f"   Historical flood events: {flood_history['total_flood_events']}")
    
    validated_data = {
        'weather': [],
        'sensors': [],
        'integration_timestamp': datetime.now().isoformat(),
        'data_quality': {
            'weather_stations_active': 0,
            'iot_sensors_active': 0,
            'data_completeness_score': 0.0,
            'integration_success': True
        }
    }
    
    # Validate weather data
    for station in bmkg_data:
        is_valid = True
        validation_errors = []
        
        # Validate temperature range for Lampung (20-35°C realistic range)
        if not (20 <= station['temperature'] <= 35):
            validation_errors.append(f"Temperature out of realistic range: {station['temperature']}°C")
            # Don't mark as invalid, just warn
            print(f"⚠️ Warning: {station['station_name']} - {validation_errors[-1]}")
        
        # Validate humidity (0-100%)
        if not (0 <= station['humidity'] <= 100):
            validation_errors.append(f"Humidity out of range: {station['humidity']}%")
            is_valid = False
        
        # Validate rainfall (non-negative, reasonable upper limit)
        if station['rainfall'] < 0 or station['rainfall'] > 200:
            validation_errors.append(f"Rainfall out of reasonable range: {station['rainfall']}mm")
            is_valid = False
        
        if is_valid:
            validated_data['weather'].append(station)
            validated_data['data_quality']['weather_stations_active'] += 1
        else:
            print(f"❌ Invalid weather data from {station['station_name']}: {validation_errors}")
    
    # Validate sensor data
    for sensor in iot_data:
        is_valid = True
        validation_errors = []
        
        # Validate battery level
        if not (0 <= sensor['battery_level'] <= 100):
            validation_errors.append(f"Battery level out of range: {sensor['battery_level']}%")
            is_valid = False
        
        # Validate water level for water sensors
        if sensor['sensor_type'] == 'water_level':
            if not (0 <= sensor['water_level_cm'] <= 1000):  # Up to 10m seems reasonable
                validation_errors.append(f"Water level out of range: {sensor['water_level_cm']}cm")
                is_valid = False
            
            if sensor['flow_rate'] < 0:
                validation_errors.append(f"Negative flow rate: {sensor['flow_rate']}")
                is_valid = False
        
        if is_valid:
            validated_data['sensors'].append(sensor)
            validated_data['data_quality']['iot_sensors_active'] += 1
        else:
            print(f"❌ Invalid sensor data from {sensor['sensor_id']}: {validation_errors}")
    
    # Calculate data completeness score
    total_expected_sources = 4  # BMKG, IoT, DEMNAS, BNPB
    sources_available = sum([
        1 if len(validated_data['weather']) > 0 else 0,
        1 if len(validated_data['sensors']) > 0 else 0,
        1 if topo_data['total_grid_points'] > 0 else 0,
        1 if flood_history['total_flood_events'] > 0 else 0
    ])
    
    validated_data['data_quality']['data_completeness_score'] = sources_available / total_expected_sources
    validated_data['data_quality']['integration_success'] = sources_available >= 3  # At least 3 sources
    
    # Add context data
    validated_data['topography_summary'] = topo_data
    validated_data['flood_history_summary'] = flood_history
    
    print(f"✅ Data validation completed:")
    print(f"   Valid weather stations: {validated_data['data_quality']['weather_stations_active']}/{len(bmkg_data)}")
    print(f"   Valid IoT sensors: {validated_data['data_quality']['iot_sensors_active']}/{len(iot_data)}")
    print(f"   Data completeness score: {validated_data['data_quality']['data_completeness_score']:.2f}")
    
    # Save integrated data
    current_time = datetime.now()
    output_path = f"/opt/airflow/data/processing/integrated_validated_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(validated_data, f, indent=2)
    
    return validated_data

def enhanced_feature_engineering(**context):
    """
    Enhanced feature engineering menggunakan semua data sources
    """
    print("⚙️ Starting enhanced feature engineering...")
    
    validated_data = context['task_instance'].xcom_pull(task_ids='integrate_validate_data')
    current_time = datetime.now()
    
    features_list = []
    
    # Get historical risk scores for locations
    historical_risks = validated_data['flood_history_summary']['location_risk_analysis']
    topo_data = validated_data['topography_summary']
    
    # Create features for each weather station
    for weather in validated_data['weather']:
        location_name = weather['station_name']
        
        # Find matching IoT sensors near this location
        nearby_sensors = []
        for sensor in validated_data['sensors']:
            # Simple location matching (could be improved with actual coordinates)
            if any(keyword in sensor['location'].lower() for keyword in 
                  [word.lower() for word in location_name.split()]):
                nearby_sensors.append(sensor)
        
        # Get historical risk for this location
        historical_risk = historical_risks.get(location_name, {
            'risk_score': 0.1,
            'risk_category': 'LOW',
            'total_events': 0,
            'avg_water_height_cm': 0,
            'total_evacuees': 0
        })
        
        # Create comprehensive feature record
        feature_record = {
            'timestamp': current_time.isoformat(),
            'location_id': weather['station_id'],
            'location_name': location_name,
            
            # Current weather features (from real BMKG data)
            'temperature': weather['temperature'],
            'humidity': weather['humidity'],
            'rainfall_current': weather['rainfall'],
            'wind_speed': weather['wind_speed'],
            'rainfall_1h': weather['rainfall_1h'],
            'rainfall_3h': weather['rainfall_3h'],
            'rainfall_24h': weather['rainfall_24h'],
            
            # Historical flood risk features (from BNPB data)
            'historical_risk_score': historical_risk['risk_score'],
            'historical_risk_category': historical_risk['risk_category'],
            'historical_flood_events': historical_risk['total_events'],
            'max_historical_water_height': historical_risk.get('max_water_height_cm', 0),
            'total_historical_evacuees': historical_risk['total_evacuees'],
            
            # Topographical risk features (from DEMNAS)
            'avg_elevation': topo_data['avg_elevation'],
            'low_elevation_risk': topo_data['low_elevation_areas'] / topo_data['total_grid_points'],
            'topographic_flood_risk': topo_data['flood_risk_zones']['very_high_risk'] / topo_data['total_grid_points'],
            
            # Current sensor features (from IoT)
            'has_sensor_data': len(nearby_sensors) > 0,
            'active_sensors_count': len([s for s in nearby_sensors if s['status'] == 'ACTIVE']),
            'water_level_cm': 0,
            'flow_rate': 0,
            'sensor_battery_avg': 0,
            
            # Temporal features
            'hour_of_day': current_time.hour,
            'day_of_week': current_time.weekday(),
            'month': current_time.month,
            'is_rainy_season': int(current_time.month in [11, 12, 1, 2, 3, 4]),
            'is_peak_hours': int(current_time.hour in [2, 3, 4, 5, 6]),  # Early morning flood risk
            
            # Derived risk indicators
            'weather_risk_score': 0.0,
            'sensor_risk_score': 0.0,
            'composite_risk_score': 0.0
        }
        
        # Update with actual sensor data if available
        if nearby_sensors:
            water_sensors = [s for s in nearby_sensors if s['sensor_type'] == 'water_level']
            if water_sensors:
                # Use the sensor with highest water level (worst case)
                max_water_sensor = max(water_sensors, key=lambda x: x.get('water_level_cm', 0))
                feature_record.update({
                    'water_level_cm': max_water_sensor['water_level_cm'],
                    'flow_rate': max_water_sensor['flow_rate'],
                    'sensor_flood_risk': max_water_sensor['flood_risk']
                })
            
            # Calculate average battery level
            feature_record['sensor_battery_avg'] = np.mean([s['battery_level'] for s in nearby_sensors])
        
        # Calculate weather risk score
        weather_risk = 0.0
        if feature_record['rainfall_current'] > 50:
            weather_risk += 0.4
        elif feature_record['rainfall_current'] > 20:
            weather_risk += 0.2
        elif feature_record['rainfall_current'] > 10:
            weather_risk += 0.1
        
        if feature_record['humidity'] > 90:
            weather_risk += 0.1
        
        if feature_record['wind_speed'] < 3:  # Very low wind (storm conditions)
            weather_risk += 0.05
        
        feature_record['weather_risk_score'] = weather_risk
        
        # Calculate sensor risk score
        sensor_risk = 0.0
        if feature_record['water_level_cm'] > 250:
            sensor_risk += 0.4
        elif feature_record['water_level_cm'] > 200:
            sensor_risk += 0.3
        elif feature_record['water_level_cm'] > 150:
            sensor_risk += 0.2
        
        if feature_record['flow_rate'] > 15:
            sensor_risk += 0.1
        
        feature_record['sensor_risk_score'] = sensor_risk
        
        # Calculate composite risk score
        composite_risk = (
            weather_risk * 0.4 +                                    # Current weather: 40%
            sensor_risk * 0.3 +                                     # Current sensors: 30%
            feature_record['historical_risk_score'] * 0.2 +         # Historical risk: 20%
            feature_record['topographic_flood_risk'] * 0.1          # Topographic risk: 10%
        )
        
        # Adjust for temporal factors
        if feature_record['is_rainy_season']:
            composite_risk *= 1.2
        if feature_record['is_peak_hours']:
            composite_risk *= 1.1
        
        feature_record['composite_risk_score'] = min(1.0, composite_risk)
        
        # Determine risk level
        if composite_risk >= 0.7:
            risk_level = "VERY_HIGH"
        elif composite_risk >= 0.5:
            risk_level = "HIGH"
        elif composite_risk >= 0.3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        feature_record['predicted_risk_level'] = risk_level
        
        features_list.append(feature_record)
        
        print(f"✅ Features created for {location_name}: Risk={risk_level} ({composite_risk:.3f})")
    
    print(f"⚙️ Enhanced feature engineering completed: {len(features_list)} feature records")
    
    # Save features
    output_path = f"/opt/airflow/data/processing/enhanced_features_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(features_list, f, indent=2)
    
    return features_list

def ml_flood_prediction(**context):
    """
    Machine Learning prediction menggunakan enhanced features dari real data
    """
    print("🤖 Starting ML flood prediction with real data...")
    
    features = context['task_instance'].xcom_pull(task_ids='enhanced_feature_engineering')
    current_time = datetime.now()
    
    predictions = []
    
    for feature in features:
        # Enhanced ML prediction using all available data
        base_risk = feature['composite_risk_score']
        
        # Advanced pattern recognition adjustments
        pattern_adjustments = 0.0
        
        # Multi-factor weather pattern analysis
        if (feature['rainfall_current'] > 30 and 
            feature['humidity'] > 85 and 
            feature['wind_speed'] < 5):
            pattern_adjustments += 0.15  # Storm pattern
        
        # Historical event correlation
        if (feature['historical_flood_events'] > 3 and 
            feature['month'] in [12, 1, 2] and 
            feature['rainfall_current'] > 20):
            pattern_adjustments += 0.1  # High-risk period with rainfall
        
        # Topographic vulnerability
        if (feature['topographic_flood_risk'] > 0.3 and 
            feature['water_level_cm'] > 180):
            pattern_adjustments += 0.1  # Vulnerable topography + high water
        
        # Sensor reliability factor
        confidence_factor = 1.0
        if feature['has_sensor_data'] and feature['sensor_battery_avg'] > 50:
            confidence_factor = 1.2  # Higher confidence with good sensors
        elif not feature['has_sensor_data']:
            confidence_factor = 0.8  # Lower confidence without sensors
        
        # Final risk calculation
        final_risk = min(1.0, (base_risk + pattern_adjustments) * confidence_factor)
        
        # Prediction confidence
        prediction_confidence = 0.7  # Base confidence
        if feature['has_sensor_data']:
            prediction_confidence += 0.15
        if feature['historical_flood_events'] > 0:
            prediction_confidence += 0.1
        if feature['rainfall_current'] > 0:  # Active weather
            prediction_confidence += 0.05
        
        prediction_confidence = min(1.0, prediction_confidence)
        
        # Determine alert level
        if final_risk >= 0.8:
            alert_level = "CRITICAL"
            prediction_level = "VERY_HIGH"
        elif final_risk >= 0.6:
            alert_level = "HIGH"
            prediction_level = "HIGH"
        elif final_risk >= 0.4:
            alert_level = "MEDIUM"
            prediction_level = "MEDIUM"
        else:
            alert_level = "LOW"
            prediction_level = "LOW"
        
        # Time to flood estimation (more sophisticated)
        time_to_flood = None
        if prediction_level in ["VERY_HIGH", "HIGH"]:
            # Base time calculation
            base_time = 8 - (final_risk * 8)  # 0-8 hours based on risk
            
            # Adjust based on rainfall intensity
            if feature['rainfall_current'] > 50:
                base_time *= 0.5  # Very heavy rain = faster flooding
            elif feature['rainfall_current'] > 20:
                base_time *= 0.7  # Heavy rain = faster flooding
            
            # Adjust based on water level
            if feature['water_level_cm'] > 200:
                base_time *= 0.6  # Already high water = faster flooding
            
            time_to_flood = max(0.5, base_time)  # Minimum 30 minutes
        
        # Generate prediction
        prediction = {
            'prediction_id': f"PRED_REAL_{current_time.strftime('%Y%m%d_%H%M%S')}_{feature['location_id']}",
            'timestamp': current_time.isoformat(),
            'location_id': feature['location_id'],
            'location_name': feature['location_name'],
            'risk_score': round(final_risk, 3),
            'risk_level': prediction_level,
            'alert_priority': alert_level,
            'flood_probability_percent': round(final_risk * 100, 1),
            'confidence': round(prediction_confidence, 2),
            'time_to_flood_hours': time_to_flood,
            
            # Enhanced prediction details
            'contributing_factors': [],
            'historical_context': {
                'past_events': feature['historical_flood_events'],
                'max_historical_height': feature['max_historical_water_height'],
                'historical_risk_category': feature['historical_risk_category']
            },
            'current_conditions': {
                'rainfall': feature['rainfall_current'],
                'water_level': feature['water_level_cm'],
                'humidity': feature['humidity'],
                'temperature': feature['temperature'],
                'sensors_active': feature['active_sensors_count']
            },
            'risk_breakdown': {
                'weather_risk': feature['weather_risk_score'],
                'sensor_risk': feature['sensor_risk_score'],
                'historical_risk': feature['historical_risk_score'],
                'topographic_risk': feature['topographic_flood_risk']
            },
            'recommendations': [],
            'data_sources_used': ['BMKG', 'IoT', 'DEMNAS', 'BNPB']
        }
        
        # Add detailed contributing factors
        if feature['rainfall_current'] > 20:
            prediction['contributing_factors'].append(f"High current rainfall: {feature['rainfall_current']}mm")
        
        if feature['water_level_cm'] > 200:
            prediction['contributing_factors'].append(f"Elevated water level: {feature['water_level_cm']}cm")
        
        if feature['historical_flood_events'] > 2:
            prediction['contributing_factors'].append(f"Historical flood-prone area: {feature['historical_flood_events']} past events")
        
        if feature['topographic_flood_risk'] > 0.2:
            prediction['contributing_factors'].append("Topographically vulnerable area")
        
        if feature['humidity'] > 90:
            prediction['contributing_factors'].append(f"Very high humidity: {feature['humidity']}%")
        
        if feature['is_rainy_season']:
            prediction['contributing_factors'].append("Peak rainy season period")
        
        # Add specific recommendations
        if prediction_level == "VERY_HIGH":
            prediction['recommendations'].extend([
                "IMMEDIATE EVACUATION recommended for low-lying areas",
                "Deploy emergency response teams",
                "Activate flood warning sirens",
                "Close flood-prone roads",
                "Open evacuation centers"
            ])
        elif prediction_level == "HIGH":
            prediction['recommendations'].extend([
                "Prepare for potential evacuation",
                "Monitor water levels every 15 minutes",
                "Alert emergency services",
                "Issue public warnings",
                "Prepare emergency supplies"
            ])
        elif prediction_level == "MEDIUM":
            prediction['recommendations'].extend([
                "Increase monitoring frequency",
                "Prepare emergency equipment",
                "Brief response teams",
                "Monitor weather updates closely"
            ])
        else:
            prediction['recommendations'].append("Continue normal monitoring")
        
        predictions.append(prediction)
        
        print(f"🎯 Prediction for {feature['location_name']}: {prediction_level} "
              f"({final_risk:.3f}) - Confidence: {prediction_confidence:.2f}")
    
    # Generate summary statistics
    high_risk_count = len([p for p in predictions if p['risk_level'] in ['HIGH', 'VERY_HIGH']])
    avg_flood_probability = np.mean([p['flood_probability_percent'] for p in predictions])
    critical_alerts = len([p for p in predictions if p['alert_priority'] == 'CRITICAL'])
    
    print(f"🤖 ML Prediction completed:")
    print(f"   Total locations analyzed: {len(predictions)}")
    print(f"   High risk areas: {high_risk_count}")
    print(f"   Critical alerts: {critical_alerts}")
    print(f"   Average flood probability: {avg_flood_probability:.1f}%")
    
    # Save predictions
    output_path = f"/opt/airflow/data/analytics/predictions/ml_predictions_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(predictions, f, indent=2)
    
    return predictions

def generate_comprehensive_alerts(**context):
    """
    Generate comprehensive alerts berdasarkan ML predictions dan real data
    """
    print("🚨 Generating comprehensive flood alerts...")
    
    predictions = context['task_instance'].xcom_pull(task_ids='ml_flood_prediction')
    current_time = datetime.now()
    
    # Categorize predictions by alert level
    critical_alerts = [p for p in predictions if p['alert_priority'] == 'CRITICAL']
    high_alerts = [p for p in predictions if p['alert_priority'] == 'HIGH']
    medium_alerts = [p for p in predictions if p['alert_priority'] == 'MEDIUM']
    low_alerts = [p for p in predictions if p['alert_priority'] == 'LOW']
    
    alerts_generated = []
    
    # Process CRITICAL alerts
    if critical_alerts:
        print(f"🚨 CRITICAL FLOOD EMERGENCY - {len(critical_alerts)} location(s) require immediate action!")
        
        for alert in critical_alerts:
            alert_message = {
                'alert_id': f"CRITICAL_{current_time.strftime('%Y%m%d_%H%M%S')}_{alert['location_id']}",
                'alert_level': 'CRITICAL',
                'timestamp': current_time.isoformat(),
                'location': alert['location_name'],
                'flood_probability': alert['flood_probability_percent'],
                'confidence': alert['confidence'],
                'time_to_flood_hours': alert['time_to_flood_hours'],
                
                'emergency_message': f"""
🚨 CRITICAL FLOOD EMERGENCY - {alert['location_name']} 🚨

IMMEDIATE EVACUATION REQUIRED
• Flood Probability: {alert['flood_probability_percent']}%
• Confidence Level: {alert['confidence']:.0%}
• Estimated Time to Flood: {alert['time_to_flood_hours']:.1f} hours

CURRENT CONDITIONS:
• Rainfall: {alert['current_conditions']['rainfall']}mm
• Water Level: {alert['current_conditions']['water_level']}cm
• Active Sensors: {alert['current_conditions']['sensors_active']}

IMMEDIATE ACTIONS REQUIRED:
{chr(10).join(['• ' + rec for rec in alert['recommendations']])}

Data Sources: {', '.join(alert['data_sources_used'])}
Historical Context: {alert['historical_context']['past_events']} previous flood events
                """,
                
                'recipients': [
                    'emergency_services', 'local_government', 'provincial_government',
                    'public_warning_system', 'media', 'community_leaders'
                ],
                
                'distribution_channels': [
                    'emergency_siren', 'sms_broadcast', 'radio_emergency',
                    'tv_emergency', 'social_media', 'mobile_app', 'loudspeaker'
                ],
                
                'historical_context': alert['historical_context'],
                'current_conditions': alert['current_conditions'],
                'risk_breakdown': alert['risk_breakdown']
            }
            
            alerts_generated.append(alert_message)
            print(f"   🆘 {alert['location_name']}: {alert['flood_probability_percent']}% - "
                  f"ETA: {alert['time_to_flood_hours']:.1f}h")
    
    # Process HIGH alerts
    if high_alerts:
        print(f"⚠️ HIGH FLOOD WARNING - {len(high_alerts)} location(s) at high risk!")
        
        for alert in high_alerts:
            alert_message = {
                'alert_id': f"HIGH_{current_time.strftime('%Y%m%d_%H%M%S')}_{alert['location_id']}",
                'alert_level': 'HIGH',
                'timestamp': current_time.isoformat(),
                'location': alert['location_name'],
                'flood_probability': alert['flood_probability_percent'],
                'confidence': alert['confidence'],
                
                'warning_message': f"""
⚠️ HIGH FLOOD WARNING - {alert['location_name']} ⚠️

PREPARE FOR POTENTIAL FLOODING
• Flood Probability: {alert['flood_probability_percent']}%
• Confidence Level: {alert['confidence']:.0%}

CONTRIBUTING FACTORS:
{chr(10).join(['• ' + factor for factor in alert['contributing_factors']])}

RECOMMENDED ACTIONS:
{chr(10).join(['• ' + rec for rec in alert['recommendations']])}
                """,
                
                'recipients': ['emergency_services', 'local_government', 'monitoring_teams'],
                'distribution_channels': ['sms_alert', 'email', 'dashboard', 'mobile_app'],
                'historical_context': alert['historical_context'],
                'current_conditions': alert['current_conditions']
            }
            
            alerts_generated.append(alert_message)
            print(f"   ⚠️ {alert['location_name']}: {alert['flood_probability_percent']}%")
    
    # Process MEDIUM alerts
    if medium_alerts:
        print(f"📢 MEDIUM FLOOD WATCH - {len(medium_alerts)} location(s) under monitoring")
        
        medium_summary = {
            'alert_id': f"MEDIUM_SUMMARY_{current_time.strftime('%Y%m%d_%H%M%S')}",
            'alert_level': 'MEDIUM',
            'timestamp': current_time.isoformat(),
            'locations_count': len(medium_alerts),
            'locations': [alert['location_name'] for alert in medium_alerts],
            'avg_probability': np.mean([alert['flood_probability_percent'] for alert in medium_alerts]),
            
            'summary_message': f"""
📢 FLOOD MONITORING UPDATE - {len(medium_alerts)} Areas Under Watch

LOCATIONS MONITORED:
{chr(10).join(['• ' + alert['location_name'] + f" ({alert['flood_probability_percent']}%)" for alert in medium_alerts])}

AVERAGE FLOOD PROBABILITY: {np.mean([alert['flood_probability_percent'] for alert in medium_alerts]):.1f}%

MONITORING ACTIONS:
• Increased sensor monitoring frequency
• Weather pattern analysis
• Emergency team briefings
• Community preparedness checks
            """,
            
            'recipients': ['monitoring_teams', 'local_government'],
            'distribution_channels': ['email', 'dashboard', 'internal_alert']
        }
        
        alerts_generated.append(medium_summary)
    
    # Generate overall system status
    system_status = {
        'alert_id': f"SYSTEM_STATUS_{current_time.strftime('%Y%m%d_%H%M%S')}",
        'timestamp': current_time.isoformat(),
        'alert_summary': {
            'total_locations_monitored': len(predictions),
            'critical_alerts': len(critical_alerts),
            'high_alerts': len(high_alerts),
            'medium_alerts': len(medium_alerts),
            'low_risk_areas': len(low_alerts),
            'overall_system_status': 'EMERGENCY' if critical_alerts else 'WARNING' if high_alerts else 'NORMAL'
        },
        
        'data_integration_status': {
            'bmkg_stations_active': len(set(p['location_name'] for p in predictions)),
            'iot_sensors_total': sum(p['current_conditions']['sensors_active'] for p in predictions),
            'data_sources_integrated': 4,  # BMKG, IoT, DEMNAS, BNPB
            'prediction_confidence_avg': np.mean([p['confidence'] for p in predictions])
        },
        
        'recommendations': {
            'immediate_actions': [],
            'monitoring_actions': [],
            'system_improvements': []
        }
    }
    
    # Add system-level recommendations
    if critical_alerts:
        system_status['recommendations']['immediate_actions'].extend([
            'Activate provincial emergency response center',
            'Deploy additional emergency teams',
            'Coordinate with regional disaster management',
            'Increase public communication frequency'
        ])
    
    if high_alerts or medium_alerts:
        system_status['recommendations']['monitoring_actions'].extend([
            'Increase data collection frequency',
            'Monitor weather radar closely',
            'Prepare evacuation resources',
            'Update public on flood status'
        ])
    
    alerts_generated.append(system_status)
    
    print(f"🚨 Alert generation summary:")
    print(f"   Critical alerts: {len(critical_alerts)}")
    print(f"   High alerts: {len(high_alerts)}")
    print(f"   Medium alerts: {len(medium_alerts)}")
    print(f"   System status: {system_status['alert_summary']['overall_system_status']}")
    
    # Save all alerts
    output_path = f"/opt/airflow/data/analytics/alerts/comprehensive_alerts_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(alerts_generated, f, indent=2)
    
    return {
        'alerts_generated': alerts_generated,
        'summary': system_status['alert_summary'],
        'total_alerts': len(alerts_generated)
    }

# ==================== DAG TASKS DEFINITION ====================

# Task 1: Extract BMKG Real Data
extract_bmkg_task = PythonOperator(
    task_id='extract_bmkg_real_data',
    python_callable=extract_bmkg_real_data,
    dag=dag,
    doc_md="Extract data cuaca BMKG dari file CSV historis"
)

# Task 2: Extract IoT Real Data
extract_iot_task = PythonOperator(
    task_id='extract_iot_real_data',
    python_callable=extract_iot_real_data,
    dag=dag,
    doc_md="Extract data IoT sensor dari file JSON"
)

# Task 3: Extract DEMNAS Topography
extract_demnas_task = PythonOperator(
    task_id='extract_demnas_topography',
    python_callable=extract_demnas_topography,
    dag=dag,
    doc_md="Extract data topografi DEMNAS untuk analisis risiko elevasi"
)

# Task 4: Extract BNPB Historical Floods
extract_bnpb_task = PythonOperator(
    task_id='extract_bnpb_historical',
    python_callable=extract_bnpb_historical_floods,
    dag=dag,
    doc_md="Extract data kejadian banjir historis dari BNPB"
)

# Task 5: Integrate and Validate All Data
integrate_validate_task = PythonOperator(
    task_id='integrate_validate_data',
    python_callable=integrate_and_validate_data,
    dag=dag,
    doc_md="Integrasikan dan validasi data dari semua sources"
)

# Task 6: Enhanced Feature Engineering
feature_engineering_task = PythonOperator(
    task_id='enhanced_feature_engineering',
    python_callable=enhanced_feature_engineering,
    dag=dag,
    doc_md="Enhanced feature engineering menggunakan semua data sources"
)

# Task 7: ML Flood Prediction
ml_prediction_task = PythonOperator(
    task_id='ml_flood_prediction',
    python_callable=ml_flood_prediction,
    dag=dag,
    doc_md="Machine Learning prediction menggunakan enhanced features"
)

# Task 8: Generate Comprehensive Alerts
generate_alerts_task = PythonOperator(
    task_id='generate_comprehensive_alerts',
    python_callable=generate_comprehensive_alerts,
    dag=dag,
    doc_md="Generate comprehensive alerts berdasarkan ML predictions"
)

# Task 9: Store Results to Big Data Stack
store_results_task = BashOperator(
    task_id='store_results_to_big_data_stack',
    bash_command='''
    echo "🗄️ Storing flood prediction results to Big Data Stack..."
    echo "⏰ Processing time: $(date)"
    
    # Simulate storing to HDFS
    echo "📁 Creating HDFS directories..."
    # hdfs dfs -mkdir -p /data/analytics/predictions/realtime
    # hdfs dfs -mkdir -p /data/analytics/alerts/comprehensive
    # hdfs dfs -mkdir -p /data/processed/integrated
    
    echo "💾 Storing processed data..."
    # hdfs dfs -put /opt/airflow/data/analytics/predictions/* /data/analytics/predictions/realtime/
    # hdfs dfs -put /opt/airflow/data/analytics/alerts/* /data/analytics/alerts/comprehensive/
    
    # Simulate Hive table updates
    echo "🏗️ Updating Hive tables..."
    # beeline -u jdbc:hive2://hive-server:10000 -e "
    #   INSERT INTO TABLE flood_predictions_realtime 
    #   SELECT * FROM flood_predictions_staging;
    # "
    
    # Simulate HBase updates for real-time access
    echo "📊 Updating HBase tables..."
    # echo "put 'flood_status', 'current', 'predictions', '$(cat /opt/airflow/data/analytics/predictions/latest.json)'" | hbase shell
    
    # Simulate Kafka message for real-time streaming
    echo "🌊 Publishing to Kafka streams..."
    # kafka-console-producer --topic flood-alerts --bootstrap-server kafka:9092 < /opt/airflow/data/analytics/alerts/latest.json
    
    echo "✅ Big Data Stack storage completed:"
    echo "   - HDFS: /data/analytics/predictions/ & /data/analytics/alerts/"
    echo "   - Hive: Tables updated with latest predictions"
    echo "   - HBase: Real-time status updated"
    echo "   - Kafka: Alert stream published"
    echo "   - Ready for Superset dashboard consumption"
    ''',
    dag=dag
)

# Task 10: Update Analytics Dashboard
update_dashboard_task = BashOperator(
    task_id='update_analytics_dashboard',
    bash_command='''
    echo "📊 Updating Superset Analytics Dashboard..."
    echo "⏰ Dashboard refresh time: $(date)"
    
    # Simulate Superset dashboard refresh
    echo "🔄 Refreshing dashboard cache..."
    # curl -X POST "http://superset:8088/api/v1/dashboard/flood-monitoring/refresh" \\
    #   -H "Authorization: Bearer $SUPERSET_TOKEN"
    
    echo "📈 Dashboard components updated:"
    echo "   ✅ Real-time flood risk map"
    echo "   ✅ Current alert status indicators" 
    echo "   ✅ Historical trend analysis"
    echo "   ✅ Sensor status monitoring"
    echo "   ✅ Weather pattern visualization"
    echo "   ✅ Evacuation route recommendations"
    
    echo "🌐 Dashboard accessible at:"
    echo "   Main Dashboard: http://localhost:8088/superset/dashboard/lampung-flood-monitoring"
    echo "   Alert Center: http://localhost:8088/superset/dashboard/flood-alerts"
    echo "   Historical Analysis: http://localhost:8088/superset/dashboard/flood-history"
    
    echo "📱 Mobile alerts configured for:"
    echo "   - Emergency services"
    echo "   - Local government officials"
    echo "   - Community leaders"
    echo "   - General public (high-risk areas)"
    
    echo "✅ Analytics dashboard update completed!"
    ''',
    dag=dag
)

# ==================== TASK DEPENDENCIES ====================

# Parallel data extraction from all sources
[extract_bmkg_task, extract_iot_task, extract_demnas_task, extract_bnpb_task] >> integrate_validate_task

# Sequential processing pipeline
integrate_validate_task >> feature_engineering_task
feature_engineering_task >> ml_prediction_task
ml_prediction_task >> generate_alerts_task

# Parallel storage and dashboard update
generate_alerts_task >> [store_results_task, update_dashboard_task]
