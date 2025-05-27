"""
DAG untuk Pipeline Prediksi Banjir Lampung
Mengintegrasikan data dari BMKG, IoT sensors, dan DEMNAS untuk prediksi banjir real-time

Author: Lampung Flood Prediction Team
Date: 2025-05-26
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta
import json
import pandas as pd
import requests
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
    'lampung_flood_prediction_pipeline',
    default_args=default_args,
    description='Pipeline prediksi banjir Lampung dengan integrasi multi-source data',
    schedule_interval=timedelta(hours=1),  # Eksekusi setiap jam
    catchup=False,
    max_active_runs=1,
    tags=['flood-prediction', 'lampung', 'real-time', 'machine-learning']
)

# ==================== TASK FUNCTIONS ====================

def extract_bmkg_weather_data(**context):
    """
    Extract real-time weather data dari BMKG API
    Fokus pada stasiun weather di Provinsi Lampung
    """
    print("🌦️ Starting BMKG weather data extraction...")
    
    # Stasiun BMKG di Lampung
    lampung_stations = {
        '96747': 'Bandar Lampung (Radin Inten II)',
        '96749': 'Lampung Tengah (Lampung Timur)',
        '96751': 'Lampung Utara (Kotabumi)',
        '96753': 'Lampung Selatan (Kalianda)',
        '96755': 'Lampung Barat (Liwa)'
    }
    
    weather_data = []
    current_time = datetime.now()
    
    for station_id, station_name in lampung_stations.items():
        try:
            # Simulasi data BMKG (dalam implementasi nyata, gunakan API BMKG)
            # URL: https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={kode_wilayah}
            
            # Simulate realistic weather data
            import random
            
            # Generate realistic weather patterns for Lampung
            base_temp = 28 + random.uniform(-3, 5)  # 25-33°C
            base_humidity = 80 + random.uniform(-15, 20)  # 65-100%
            
            # Seasonal rainfall patterns (May = rainy season ending)
            if current_time.month in [11, 12, 1, 2, 3, 4]:  # Rainy season
                rainfall = random.uniform(0, 80)  # Higher chance of rain
            else:  # Dry season
                rainfall = random.uniform(0, 20)  # Lower rainfall
            
            weather_record = {
                'station_id': station_id,
                'station_name': station_name,
                'timestamp': current_time.isoformat(),
                'temperature': round(base_temp, 1),
                'humidity': round(min(100, max(0, base_humidity)), 1),
                'rainfall_1h': round(rainfall, 1),
                'rainfall_3h': round(rainfall * 2.5, 1),
                'rainfall_24h': round(rainfall * 8, 1),
                'wind_speed': round(random.uniform(5, 25), 1),
                'wind_direction': random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']),
                'pressure': round(1013 + random.uniform(-10, 10), 1),
                'visibility': round(random.uniform(5, 15), 1),
                'weather_condition': random.choice(['cerah', 'berawan', 'hujan ringan', 'hujan sedang', 'hujan lebat'])
            }
            
            weather_data.append(weather_record)
            print(f"✅ Data extracted from {station_name}: {weather_record['weather_condition']}, "
                  f"Rainfall: {weather_record['rainfall_1h']}mm")
            
        except Exception as e:
            print(f"❌ Error extracting from station {station_id} ({station_name}): {e}")
            # Log error tapi jangan stop pipeline
            continue
    
    print(f"🌦️ BMKG extraction completed: {len(weather_data)} stations processed")
    
    # Save raw data to HDFS (simulasi)
    raw_data_path = f"/opt/airflow/data/raw/bmkg/weather_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(raw_data_path, 'w') as f:
        json.dump(weather_data, f, indent=2)
    
    return weather_data

def extract_iot_sensor_data(**context):
    """
    Extract data dari IoT water level sensors dan weather stations
    Di sepanjang sungai-sungai utama di Lampung
    """
    print("🌊 Starting IoT sensor data extraction...")
    
    # IoT sensors deployed di lokasi strategis Lampung
    iot_sensors = {
        'WL001': {'location': 'Sungai Way Sekampung - Bandar Lampung', 'type': 'water_level'},
        'WL002': {'location': 'Sungai Way Seputih - Lampung Tengah', 'type': 'water_level'},
        'WL003': {'location': 'Sungai Way Tulang Bawang - Tulang Bawang', 'type': 'water_level'},
        'WL004': {'location': 'Sungai Way Pengubuan - Lampung Tengah', 'type': 'water_level'},
        'WL005': {'location': 'Sungai Way Besai - Pesawaran', 'type': 'water_level'},
        'WS001': {'location': 'Weather Station - Metro', 'type': 'weather'},
        'WS002': {'location': 'Weather Station - Pringsewu', 'type': 'weather'},
        'WS003': {'location': 'Weather Station - Tanggamus', 'type': 'weather'}
    }
    
    sensor_data = []
    current_time = datetime.now()
    
    for sensor_id, sensor_info in iot_sensors.items():
        try:
            import random
            
            if sensor_info['type'] == 'water_level':
                # Water level sensor data
                normal_level = 150  # cm (normal water level)
                current_level = normal_level + random.uniform(-50, 100)
                
                # Determine flood risk based on water level
                if current_level > 250:
                    flood_risk = "VERY_HIGH"
                elif current_level > 200:
                    flood_risk = "HIGH"
                elif current_level > 180:
                    flood_risk = "MEDIUM"
                else:
                    flood_risk = "LOW"
                
                sensor_record = {
                    'sensor_id': sensor_id,
                    'location': sensor_info['location'],
                    'sensor_type': 'water_level',
                    'timestamp': current_time.isoformat(),
                    'water_level_cm': round(current_level, 1),
                    'water_level_normal': round(current_level / normal_level, 2),
                    'flow_rate': round(random.uniform(0.5, 5.0), 2),  # m³/s
                    'turbidity': round(random.uniform(10, 100), 1),  # NTU
                    'temperature': round(25 + random.uniform(-2, 5), 1),
                    'flood_risk': flood_risk,
                    'battery_level': round(random.uniform(70, 100), 1),
                    'signal_strength': round(random.uniform(-80, -40), 1),  # dBm
                    'status': 'ACTIVE'
                }
                
            else:  # weather sensor
                sensor_record = {
                    'sensor_id': sensor_id,
                    'location': sensor_info['location'],
                    'sensor_type': 'weather',
                    'timestamp': current_time.isoformat(),
                    'temperature': round(27 + random.uniform(-3, 6), 1),
                    'humidity': round(random.uniform(60, 95), 1),
                    'rainfall_rate': round(random.uniform(0, 50), 1),  # mm/h
                    'wind_speed': round(random.uniform(3, 20), 1),
                    'soil_moisture': round(random.uniform(20, 80), 1),  # %
                    'battery_level': round(random.uniform(75, 100), 1),
                    'signal_strength': round(random.uniform(-75, -45), 1),
                    'status': 'ACTIVE'
                }
            
            sensor_data.append(sensor_record)
            print(f"✅ Data extracted from {sensor_id}: {sensor_info['location']}")
            
        except Exception as e:
            print(f"❌ Error extracting from sensor {sensor_id}: {e}")
            continue
    
    print(f"🌊 IoT extraction completed: {len(sensor_data)} sensors processed")
    
    # Save raw sensor data
    raw_data_path = f"/opt/airflow/data/raw/iot/sensors_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(raw_data_path, 'w') as f:
        json.dump(sensor_data, f, indent=2)
    
    return sensor_data

def validate_and_clean_data(**context):
    """
    Validasi dan pembersihan data dari BMKG dan IoT sensors
    Deteksi anomali dan missing values
    """
    print("🔍 Starting data validation and cleaning...")
    
    # Get data dari previous tasks
    weather_data = context['task_instance'].xcom_pull(task_ids='extract_bmkg_weather')
    sensor_data = context['task_instance'].xcom_pull(task_ids='extract_iot_sensors')
    
    validated_data = {'weather': [], 'sensors': []}
    
    # Validate weather data
    print("🌦️ Validating BMKG weather data...")
    for record in weather_data:
        is_valid = True
        validation_errors = []
        
        # Temperature validation (10-40°C range for Lampung)
        if not (10 <= record['temperature'] <= 40):
            validation_errors.append(f"Temperature out of range: {record['temperature']}°C")
            is_valid = False
        
        # Humidity validation (0-100%)
        if not (0 <= record['humidity'] <= 100):
            validation_errors.append(f"Humidity out of range: {record['humidity']}%")
            is_valid = False
        
        # Rainfall validation (non-negative)
        if record['rainfall_1h'] < 0:
            validation_errors.append(f"Negative rainfall: {record['rainfall_1h']}mm")
            is_valid = False
        
        if is_valid:
            validated_data['weather'].append(record)
        else:
            print(f"⚠️ Invalid weather data from {record['station_name']}: {validation_errors}")
    
    # Validate sensor data
    print("🌊 Validating IoT sensor data...")
    for record in sensor_data:
        is_valid = True
        validation_errors = []
        
        if record['sensor_type'] == 'water_level':
            # Water level validation (0-500cm reasonable range)
            if not (0 <= record['water_level_cm'] <= 500):
                validation_errors.append(f"Water level out of range: {record['water_level_cm']}cm")
                is_valid = False
            
            # Flow rate validation
            if record['flow_rate'] < 0:
                validation_errors.append(f"Negative flow rate: {record['flow_rate']}m³/s")
                is_valid = False
        
        # Battery level validation
        if not (0 <= record['battery_level'] <= 100):
            validation_errors.append(f"Battery level out of range: {record['battery_level']}%")
            is_valid = False
        
        if is_valid:
            validated_data['sensors'].append(record)
        else:
            print(f"⚠️ Invalid sensor data from {record['sensor_id']}: {validation_errors}")
    
    # Data quality report
    weather_valid_rate = len(validated_data['weather']) / len(weather_data) * 100
    sensor_valid_rate = len(validated_data['sensors']) / len(sensor_data) * 100
    
    print(f"📊 Data Quality Report:")
    print(f"   Weather data: {len(validated_data['weather'])}/{len(weather_data)} valid ({weather_valid_rate:.1f}%)")
    print(f"   Sensor data: {len(validated_data['sensors'])}/{len(sensor_data)} valid ({sensor_valid_rate:.1f}%)")
    
    # Save cleaned data
    current_time = datetime.now()
    clean_data_path = f"/opt/airflow/data/processing/clean/validated_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(clean_data_path, 'w') as f:
        json.dump(validated_data, f, indent=2)
    
    return validated_data

def feature_engineering(**context):
    """
    Feature engineering untuk machine learning model
    Menggabungkan data weather dan sensor untuk prediction features
    """
    print("⚙️ Starting feature engineering...")
    
    validated_data = context['task_instance'].xcom_pull(task_ids='validate_clean_data')
    current_time = datetime.now()
    
    features_list = []
    
    # Combine weather and sensor data by location proximity
    weather_data = validated_data['weather']
    sensor_data = validated_data['sensors']
    
    for weather in weather_data:
        # Find matching sensors near this weather station
        water_sensors = [s for s in sensor_data if s['sensor_type'] == 'water_level']
        weather_sensors = [s for s in sensor_data if s['sensor_type'] == 'weather']
        
        # Create feature record
        feature_record = {
            'timestamp': current_time.isoformat(),
            'location_id': weather['station_id'],
            'location_name': weather['station_name'],
            
            # Weather features
            'temperature': weather['temperature'],
            'humidity': weather['humidity'],
            'rainfall_1h': weather['rainfall_1h'],
            'rainfall_3h': weather['rainfall_3h'],
            'rainfall_24h': weather['rainfall_24h'],
            'wind_speed': weather['wind_speed'],
            'pressure': weather['pressure'],
            'visibility': weather['visibility'],
            
            # Derived weather features
            'heat_index': weather['temperature'] + (weather['humidity'] * 0.1),
            'rainfall_intensity': 'low' if weather['rainfall_1h'] < 5 else 'medium' if weather['rainfall_1h'] < 20 else 'high',
            'humidity_category': 'low' if weather['humidity'] < 60 else 'medium' if weather['humidity'] < 80 else 'high',
            
            # Temporal features
            'hour_of_day': current_time.hour,
            'day_of_week': current_time.weekday(),
            'month': current_time.month,
            'is_rainy_season': int(current_time.month in [11, 12, 1, 2, 3, 4]),
            'is_peak_hours': int(current_time.hour in [6, 7, 8, 17, 18, 19]),  # Peak flood risk hours
            
            # Geographic features (simplified)
            'elevation_category': 'lowland',  # Most of Lampung is lowland
            'distance_to_coast': 50,  # km (average)
            'river_density': 'high',  # Lampung has many rivers
            
            # Default water level features (will be updated if sensor data available)
            'water_level_cm': 150,  # Default normal level
            'water_level_risk': 'LOW',
            'flow_rate': 2.0,
            'has_sensor_data': False
        }
        
        # Update with actual sensor data if available
        for sensor in water_sensors:
            # Simple proximity matching (in real implementation, use proper geo-matching)
            if any(keyword in sensor['location'].lower() for keyword in ['bandar', 'lampung', 'metro', 'way']):
                feature_record.update({
                    'water_level_cm': sensor['water_level_cm'],
                    'water_level_risk': sensor['flood_risk'],
                    'flow_rate': sensor['flow_rate'],
                    'turbidity': sensor['turbidity'],
                    'water_temp': sensor['temperature'],
                    'has_sensor_data': True
                })
                break
        
        # Calculate composite risk indicators
        risk_score = 0.0
        
        # Rainfall contribution (40% weight)
        if feature_record['rainfall_1h'] > 50:
            risk_score += 0.4
        elif feature_record['rainfall_1h'] > 20:
            risk_score += 0.2
        elif feature_record['rainfall_1h'] > 10:
            risk_score += 0.1
        
        # Water level contribution (30% weight)
        if feature_record['water_level_cm'] > 250:
            risk_score += 0.3
        elif feature_record['water_level_cm'] > 200:
            risk_score += 0.2
        elif feature_record['water_level_cm'] > 180:
            risk_score += 0.1
        
        # Seasonal/temporal contribution (20% weight)
        if feature_record['is_rainy_season']:
            risk_score += 0.1
        if feature_record['is_peak_hours']:
            risk_score += 0.05
        if feature_record['month'] in [12, 1, 2]:  # Peak rainy months
            risk_score += 0.05
        
        # Environmental contribution (10% weight)
        if feature_record['humidity'] > 85:
            risk_score += 0.05
        if feature_record['wind_speed'] < 5:  # Low wind can indicate storm
            risk_score += 0.05
        
        # Determine final risk level
        if risk_score >= 0.7:
            risk_level = "VERY_HIGH"
        elif risk_score >= 0.5:
            risk_level = "HIGH"
        elif risk_score >= 0.3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        feature_record.update({
            'risk_score': round(risk_score, 3),
            'predicted_risk_level': risk_level
        })
        
        features_list.append(feature_record)
    
    print(f"⚙️ Feature engineering completed: {len(features_list)} feature records created")
    
    # Save features
    features_path = f"/opt/airflow/data/processing/transformed/features_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(features_path, 'w') as f:
        json.dump(features_list, f, indent=2)
    
    return features_list

def predict_flood_risk(**context):
    """
    Machine Learning prediction untuk flood risk
    Menggunakan trained model untuk prediksi real-time
    """
    print("🤖 Starting flood risk prediction...")
    
    features = context['task_instance'].xcom_pull(task_ids='feature_engineering')
    current_time = datetime.now()
    
    predictions = []
    
    for feature in features:
        # Enhanced ML-like prediction logic
        # (Dalam implementasi nyata, gunakan model yang sudah di-train dengan Spark MLlib)
        
        risk_score = feature['risk_score']
        
        # Adjust prediction based on historical patterns
        historical_factor = 1.0
        
        # Higher risk during peak rainy season
        if feature['month'] in [12, 1, 2]:
            historical_factor += 0.1
        
        # Higher risk during certain hours
        if feature['hour_of_day'] in [2, 3, 4, 5]:  # Early morning hours
            historical_factor += 0.05
        
        # Adjust based on multiple weather indicators
        weather_pattern_risk = 0.0
        if feature['rainfall_1h'] > 30 and feature['humidity'] > 90:
            weather_pattern_risk += 0.15
        if feature['rainfall_3h'] > 50:
            weather_pattern_risk += 0.1
        if feature['pressure'] < 1005:  # Low pressure system
            weather_pattern_risk += 0.05
        
        # Final adjusted risk score
        adjusted_risk_score = min(1.0, (risk_score + weather_pattern_risk) * historical_factor)
        
        # Confidence calculation
        confidence = 0.8  # Base confidence
        if feature['has_sensor_data']:
            confidence += 0.15  # Higher confidence with sensor data
        if feature['rainfall_1h'] > 0:  # Active weather
            confidence += 0.05
        
        confidence = min(1.0, confidence)
        
        # Generate prediction
        if adjusted_risk_score >= 0.75:
            prediction_level = "VERY_HIGH"
            alert_priority = "CRITICAL"
        elif adjusted_risk_score >= 0.55:
            prediction_level = "HIGH"
            alert_priority = "HIGH"
        elif adjusted_risk_score >= 0.35:
            prediction_level = "MEDIUM"
            alert_priority = "MEDIUM"
        else:
            prediction_level = "LOW"
            alert_priority = "LOW"
        
        # Estimated flood probability (%)
        flood_probability = min(100, adjusted_risk_score * 100)
        
        # Time to potential flood (hours) - simplified calculation
        if prediction_level in ["VERY_HIGH", "HIGH"]:
            time_to_flood = max(1, 6 - (adjusted_risk_score * 6))
        else:
            time_to_flood = None
        
        prediction = {
            'prediction_id': f"PRED_{current_time.strftime('%Y%m%d_%H%M%S')}_{feature['location_id']}",
            'timestamp': current_time.isoformat(),
            'location_id': feature['location_id'],
            'location_name': feature['location_name'],
            'risk_score': round(adjusted_risk_score, 3),
            'risk_level': prediction_level,
            'flood_probability_percent': round(flood_probability, 1),
            'confidence': round(confidence, 2),
            'alert_priority': alert_priority,
            'time_to_flood_hours': time_to_flood,
            'contributing_factors': [],
            'recommendations': [],
            'input_features': feature
        }
        
        # Add contributing factors
        if feature['rainfall_1h'] > 20:
            prediction['contributing_factors'].append(f"High rainfall: {feature['rainfall_1h']}mm/h")
        if feature['has_sensor_data'] and feature['water_level_cm'] > 200:
            prediction['contributing_factors'].append(f"High water level: {feature['water_level_cm']}cm")
        if feature['humidity'] > 90:
            prediction['contributing_factors'].append(f"Very high humidity: {feature['humidity']}%")
        if feature['is_rainy_season']:
            prediction['contributing_factors'].append("Rainy season period")
        
        # Add recommendations
        if prediction_level in ["HIGH", "VERY_HIGH"]:
            prediction['recommendations'].extend([
                "Monitor water levels closely",
                "Prepare evacuation routes",
                "Alert emergency services",
                "Issue public warnings"
            ])
        elif prediction_level == "MEDIUM":
            prediction['recommendations'].extend([
                "Increase monitoring frequency",
                "Prepare emergency equipment",
                "Inform local authorities"
            ])
        else:
            prediction['recommendations'].append("Continue normal monitoring")
        
        predictions.append(prediction)
    
    print(f"🤖 Flood prediction completed: {len(predictions)} predictions generated")
    
    # Summary statistics
    high_risk_count = len([p for p in predictions if p['risk_level'] in ['HIGH', 'VERY_HIGH']])
    avg_flood_probability = sum(p['flood_probability_percent'] for p in predictions) / len(predictions)
    
    print(f"📊 Prediction Summary:")
    print(f"   High risk areas: {high_risk_count}/{len(predictions)}")
    print(f"   Average flood probability: {avg_flood_probability:.1f}%")
    
    # Save predictions
    predictions_path = f"/opt/airflow/data/analytics/predictions/realtime/predictions_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(predictions_path, 'w') as f:
        json.dump(predictions, f, indent=2)
    
    return predictions

def send_flood_alerts(**context):
    """
    Send alerts untuk high-risk flood predictions
    Notifikasi ke emergency services dan masyarakat
    """
    print("🚨 Processing flood alerts...")
    
    predictions = context['task_instance'].xcom_pull(task_ids='predict_flood_risk')
    current_time = datetime.now()
    
    # Filter predictions yang memerlukan alert
    critical_alerts = [p for p in predictions if p['alert_priority'] == 'CRITICAL']
    high_alerts = [p for p in predictions if p['alert_priority'] == 'HIGH']
    medium_alerts = [p for p in predictions if p['alert_priority'] == 'MEDIUM']
    
    alerts_sent = []
    
    # Process critical alerts
    if critical_alerts:
        print(f"🚨 CRITICAL FLOOD ALERT - {len(critical_alerts)} area(s) at very high risk!")
        for alert in critical_alerts:
            alert_message = {
                'alert_id': f"CRITICAL_{current_time.strftime('%Y%m%d_%H%M%S')}_{alert['location_id']}",
                'alert_level': 'CRITICAL',
                'location': alert['location_name'],
                'flood_probability': alert['flood_probability_percent'],
                'time_to_flood': alert['time_to_flood_hours'],
                'message': f"CRITICAL FLOOD WARNING for {alert['location_name']}! "
                          f"Flood probability: {alert['flood_probability_percent']}%. "
                          f"Estimated time to flood: {alert['time_to_flood_hours']} hours. "
                          f"IMMEDIATE ACTION REQUIRED!",
                'recipients': ['emergency_services', 'local_government', 'public_warning_system'],
                'actions_required': [
                    'Activate emergency response protocol',
                    'Begin evacuation procedures',
                    'Deploy emergency teams',
                    'Issue public evacuation orders'
                ]
            }
            alerts_sent.append(alert_message)
            print(f"   📍 {alert['location_name']}: {alert['flood_probability_percent']}% probability")
    
    # Process high priority alerts
    if high_alerts:
        print(f"⚠️ HIGH FLOOD ALERT - {len(high_alerts)} area(s) at high risk!")
        for alert in high_alerts:
            alert_message = {
                'alert_id': f"HIGH_{current_time.strftime('%Y%m%d_%H%M%S')}_{alert['location_id']}",
                'alert_level': 'HIGH',
                'location': alert['location_name'],
                'flood_probability': alert['flood_probability_percent'],
                'message': f"HIGH FLOOD WARNING for {alert['location_name']}! "
                          f"Flood probability: {alert['flood_probability_percent']}%. "
                          f"PREPARE FOR POTENTIAL FLOODING!",
                'recipients': ['emergency_services', 'local_government'],
                'actions_required': [
                    'Prepare emergency response teams',
                    'Alert evacuation centers',
                    'Increase monitoring frequency',
                    'Prepare public warnings'
                ]
            }
            alerts_sent.append(alert_message)
            print(f"   📍 {alert['location_name']}: {alert['flood_probability_percent']}% probability")
    
    # Process medium priority alerts
    if medium_alerts:
        print(f"📢 MEDIUM FLOOD ALERT - {len(medium_alerts)} area(s) at medium risk")
        for alert in medium_alerts:
            alert_message = {
                'alert_id': f"MEDIUM_{current_time.strftime('%Y%m%d_%H%M%S')}_{alert['location_id']}",
                'alert_level': 'MEDIUM',
                'location': alert['location_name'],
                'flood_probability': alert['flood_probability_percent'],
                'message': f"MEDIUM FLOOD WATCH for {alert['location_name']}. "
                          f"Flood probability: {alert['flood_probability_percent']}%. "
                          f"Monitor conditions closely.",
                'recipients': ['local_government', 'monitoring_teams'],
                'actions_required': [
                    'Increase monitoring',
                    'Prepare equipment',
                    'Brief response teams'
                ]
            }
            alerts_sent.append(alert_message)
    
    # If no high-risk areas
    if not critical_alerts and not high_alerts and not medium_alerts:
        print("✅ No flood alerts required - All areas at low risk")
        summary_message = {
            'alert_id': f"SUMMARY_{current_time.strftime('%Y%m%d_%H%M%S')}",
            'alert_level': 'INFO',
            'message': "Flood monitoring update: All monitored areas at low flood risk.",
            'total_areas_monitored': len(predictions),
            'avg_flood_probability': sum(p['flood_probability_percent'] for p in predictions) / len(predictions)
        }
        alerts_sent.append(summary_message)
    
    # Simulate sending alerts (in production, integrate with actual alert systems)
    print("\n📱 Alert Distribution:")
    for alert in alerts_sent:
        if alert['alert_level'] in ['CRITICAL', 'HIGH']:
            # Critical alerts: SMS, Push notifications, Email, Radio
            print(f"   🚨 {alert['alert_level']} Alert sent to Emergency Services")
            print(f"   📱 SMS alerts sent to residents in {alert.get('location', 'all areas')}")
            print(f"   📻 Radio broadcast initiated")
            print(f"   📧 Email alerts sent to authorities")
        elif alert['alert_level'] == 'MEDIUM':
            # Medium alerts: Email, Dashboard updates
            print(f"   📧 Medium alert sent to monitoring teams")
            print(f"   📊 Dashboard updated")
        else:
            # Info updates: Dashboard only
            print(f"   📊 Status update: Normal conditions")
    
    # Save alert logs
    alerts_path = f"/opt/airflow/data/analytics/alerts/alerts_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(alerts_path, 'w') as f:
        json.dump(alerts_sent, f, indent=2)
    
    print(f"\n🚨 Alert processing completed: {len(alerts_sent)} alerts generated")
    
    return {
        'total_alerts': len(alerts_sent),
        'critical_alerts': len(critical_alerts),
        'high_alerts': len(high_alerts),
        'medium_alerts': len(medium_alerts),
        'alerts_detail': alerts_sent
    }

# ==================== DAG TASKS DEFINITION ====================

# Task 1: Extract BMKG Weather Data
extract_bmkg_task = PythonOperator(
    task_id='extract_bmkg_weather',
    python_callable=extract_bmkg_weather_data,
    dag=dag,
    doc_md="Extract real-time weather data dari stasiun BMKG di Provinsi Lampung"
)

# Task 2: Extract IoT Sensor Data
extract_iot_task = PythonOperator(
    task_id='extract_iot_sensors',
    python_callable=extract_iot_sensor_data,
    dag=dag,
    doc_md="Extract data dari IoT water level sensors dan weather stations"
)

# Task 3: Data Validation & Cleaning
validate_data_task = PythonOperator(
    task_id='validate_clean_data',
    python_callable=validate_and_clean_data,
    dag=dag,
    doc_md="Validasi dan pembersihan data, deteksi anomali dan missing values"
)

# Task 4: Feature Engineering
feature_engineering_task = PythonOperator(
    task_id='feature_engineering',
    python_callable=feature_engineering,
    dag=dag,
    doc_md="Feature engineering untuk machine learning model"
)

# Task 5: Flood Risk Prediction
predict_risk_task = PythonOperator(
    task_id='predict_flood_risk',
    python_callable=predict_flood_risk,
    dag=dag,
    doc_md="Machine Learning prediction untuk flood risk assessment"
)

# Task 6: Send Flood Alerts
send_alerts_task = PythonOperator(
    task_id='send_flood_alerts',
    python_callable=send_flood_alerts,
    dag=dag,
    doc_md="Send alerts untuk high-risk flood predictions"
)

# Task 7: Store Results to HDFS/Hive (Bash task for Spark job)
store_results_task = BashOperator(
    task_id='store_results_to_hdfs',
    bash_command='''
    echo "🗄️ Storing flood prediction results to HDFS/Hive..."
    
    # Create HDFS directories if not exist
    # hdfs dfs -mkdir -p /data/analytics/predictions/realtime
    # hdfs dfs -mkdir -p /data/analytics/alerts
    
    # In production: Submit Spark job to process and store data
    # /opt/spark/bin/spark-submit \
    #   --master spark://spark-master:7077 \
    #   --class FloodDataProcessor \
    #   /opt/spark-apps/flood_data_processor.py
    
    echo "✅ Data storage task completed (simulated)"
    echo "📊 Results available in:"
    echo "   - HDFS: /data/analytics/predictions/"
    echo "   - Hive tables: flood_predictions, flood_alerts"
    echo "   - HBase: real-time flood data"
    ''',
    dag=dag
)

# Task 8: Update Superset Dashboard
update_dashboard_task = BashOperator(
    task_id='update_superset_dashboard',
    bash_command='''
    echo "📊 Updating Superset dashboard with latest predictions..."
    
    # In production: Refresh Superset dashboard cache
    # curl -X POST "http://superset:8088/api/v1/dashboard/refresh" \
    #   -H "Authorization: Bearer $SUPERSET_TOKEN"
    
    echo "✅ Dashboard update completed"
    echo "🌐 Dashboard available at: http://localhost:8089"
    echo "📈 Updated flood monitoring dashboard with:"
    echo "   - Real-time flood risk maps"
    echo "   - Alert status indicators"
    echo "   - Historical trend analysis"
    echo "   - Sensor status monitoring"
    ''',
    dag=dag
)

# ==================== TASK DEPENDENCIES ====================

# Define pipeline flow
# Parallel data extraction
[extract_bmkg_task, extract_iot_task] >> validate_data_task

# Sequential processing
validate_data_task >> feature_engineering_task
feature_engineering_task >> predict_risk_task
predict_risk_task >> send_alerts_task

# Parallel storage and dashboard update
send_alerts_task >> [store_results_task, update_dashboard_task]

# Optional: Add task groups for better organization
from airflow.utils.task_group import TaskGroup

# You can organize tasks into groups like this:
# with TaskGroup("data_extraction", dag=dag) as extraction_group:
#     extract_bmkg_task
#     extract_iot_task

# with TaskGroup("data_processing", dag=dag) as processing_group:
#     validate_data_task
#     feature_engineering_task

# with TaskGroup("ml_prediction", dag=dag) as prediction_group:
#     predict_risk_task
#     send_alerts_task

# with TaskGroup("data_storage", dag=dag) as storage_group:
#     store_results_task
#     update_dashboard_task
