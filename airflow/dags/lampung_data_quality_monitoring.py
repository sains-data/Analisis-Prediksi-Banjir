"""
Data Quality Monitoring DAG for Lampung Flood Prediction System
Monitors data quality, completeness, and accuracy from various sources
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.dates import days_ago
import pandas as pd
import numpy as np
import json
import logging

# Default arguments
default_args = {
    'owner': 'flood-prediction-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email': ['admin@lampung-flood-system.com']
}

# Create DAG
dag = DAG(
    'lampung_data_quality_monitoring',
    default_args=default_args,
    description='Monitor data quality for flood prediction system',
    schedule_interval=timedelta(hours=6),  # Run every 6 hours
    max_active_runs=1,
    catchup=False,
    tags=['flood-prediction', 'data-quality', 'monitoring', 'lampung']
)

def check_bmkg_data_quality(**context):
    """Check BMKG weather data quality and completeness"""
    try:
        logging.info("Starting BMKG data quality check...")
        
        # Simulate BMKG data quality metrics
        stations = [
            'Lampung_Tengah', 'Bandar_Lampung', 'Metro',
            'Tulang_Bawang', 'Lampung_Timur'
        ]
        
        quality_metrics = {}
        issues = []
        
        for station in stations:
            # Simulate data quality checks
            data_completeness = np.random.uniform(85, 100)  # Percentage
            data_accuracy = np.random.uniform(90, 100)      # Percentage
            missing_records = np.random.randint(0, 10)      # Count
            outliers = np.random.randint(0, 5)              # Count
            
            quality_metrics[station] = {
                'data_completeness': round(data_completeness, 2),
                'data_accuracy': round(data_accuracy, 2),
                'missing_records': missing_records,
                'outliers': outliers,
                'last_update': datetime.now().isoformat(),
                'status': 'GOOD' if data_completeness > 95 and data_accuracy > 95 else 'WARNING'
            }
            
            # Flag issues
            if data_completeness < 90:
                issues.append(f"Low data completeness for {station}: {data_completeness}%")
            if missing_records > 5:
                issues.append(f"High missing records for {station}: {missing_records}")
            if outliers > 3:
                issues.append(f"Many outliers detected for {station}: {outliers}")
        
        # Calculate overall quality score
        overall_completeness = np.mean([m['data_completeness'] for m in quality_metrics.values()])
        overall_accuracy = np.mean([m['data_accuracy'] for m in quality_metrics.values()])
        total_issues = len(issues)
        
        result = {
            'check_time': datetime.now().isoformat(),
            'overall_completeness': round(overall_completeness, 2),
            'overall_accuracy': round(overall_accuracy, 2),
            'stations_checked': len(stations),
            'total_issues': total_issues,
            'issues': issues,
            'station_metrics': quality_metrics,
            'status': 'HEALTHY' if total_issues == 0 else 'NEEDS_ATTENTION'
        }
        
        logging.info(f"BMKG Data Quality Check Results: {json.dumps(result, indent=2)}")
        
        # Store results for downstream tasks
        context['task_instance'].xcom_push(key='bmkg_quality', value=result)
        
        return result
        
    except Exception as e:
        logging.error(f"Error in BMKG data quality check: {str(e)}")
        raise

def check_iot_sensor_quality(**context):
    """Check IoT sensor data quality and availability"""
    try:
        logging.info("Starting IoT sensor data quality check...")
        
        # Simulate IoT sensor locations in Lampung
        sensor_locations = [
            'Sungai_Sekampung_Hulu', 'Sungai_Sekampung_Hilir',
            'Sungai_Way_Ratai', 'Sungai_Way_Seputih',
            'Bendungan_Batutegi', 'Pantai_Lampung'
        ]
        
        sensor_metrics = {}
        critical_issues = []
        
        for location in sensor_locations:
            # Simulate sensor health checks
            connectivity = np.random.uniform(88, 100)       # Percentage
            battery_level = np.random.uniform(20, 100)      # Percentage
            data_frequency = np.random.uniform(85, 100)     # Expected frequency
            calibration_status = np.random.choice(['OK', 'NEEDS_CALIBRATION'], p=[0.8, 0.2])
            
            sensor_metrics[location] = {
                'connectivity': round(connectivity, 2),
                'battery_level': round(battery_level, 2),
                'data_frequency': round(data_frequency, 2),
                'calibration_status': calibration_status,
                'last_reading': datetime.now().isoformat(),
                'sensor_type': 'water_level' if 'Sungai' in location else 'weather'
            }
            
            # Flag critical issues
            if connectivity < 90:
                critical_issues.append(f"Poor connectivity for {location}: {connectivity}%")
            if battery_level < 30:
                critical_issues.append(f"Low battery for {location}: {battery_level}%")
            if calibration_status == 'NEEDS_CALIBRATION':
                critical_issues.append(f"Calibration needed for {location}")
        
        # Calculate overall sensor health
        avg_connectivity = np.mean([m['connectivity'] for m in sensor_metrics.values()])
        avg_battery = np.mean([m['battery_level'] for m in sensor_metrics.values()])
        sensors_needing_calibration = sum(1 for m in sensor_metrics.values() if m['calibration_status'] == 'NEEDS_CALIBRATION')
        
        result = {
            'check_time': datetime.now().isoformat(),
            'avg_connectivity': round(avg_connectivity, 2),
            'avg_battery_level': round(avg_battery, 2),
            'sensors_checked': len(sensor_locations),
            'sensors_needing_calibration': sensors_needing_calibration,
            'critical_issues': critical_issues,
            'sensor_metrics': sensor_metrics,
            'status': 'HEALTHY' if len(critical_issues) == 0 else 'CRITICAL' if len(critical_issues) > 3 else 'WARNING'
        }
        
        logging.info(f"IoT Sensor Quality Check Results: {json.dumps(result, indent=2)}")
        
        # Store results for downstream tasks
        context['task_instance'].xcom_push(key='iot_quality', value=result)
        
        return result
        
    except Exception as e:
        logging.error(f"Error in IoT sensor quality check: {str(e)}")
        raise

def check_data_pipeline_health(**context):
    """Check the health of data processing pipelines"""
    try:
        logging.info("Starting data pipeline health check...")
        
        # Simulate pipeline health metrics
        pipelines = [
            'data_ingestion', 'data_cleaning', 'feature_engineering',
            'model_prediction', 'alert_system', 'dashboard_update'
        ]
        
        pipeline_metrics = {}
        failed_pipelines = []
        
        for pipeline in pipelines:
            # Simulate pipeline health
            success_rate = np.random.uniform(90, 100)       # Percentage
            avg_processing_time = np.random.uniform(30, 300) # Seconds
            last_run_status = np.random.choice(['SUCCESS', 'FAILED', 'RUNNING'], p=[0.85, 0.1, 0.05])
            queue_size = np.random.randint(0, 20)           # Number of pending tasks
            
            pipeline_metrics[pipeline] = {
                'success_rate_24h': round(success_rate, 2),
                'avg_processing_time_sec': round(avg_processing_time, 2),
                'last_run_status': last_run_status,
                'queue_size': queue_size,
                'last_run_time': datetime.now().isoformat(),
                'health_status': 'HEALTHY' if success_rate > 95 and last_run_status == 'SUCCESS' else 'DEGRADED'
            }
            
            # Flag failed pipelines
            if last_run_status == 'FAILED' or success_rate < 90:
                failed_pipelines.append(pipeline)
        
        # Calculate overall pipeline health
        avg_success_rate = np.mean([m['success_rate_24h'] for m in pipeline_metrics.values()])
        avg_processing_time = np.mean([m['avg_processing_time_sec'] for m in pipeline_metrics.values()])
        total_queue_size = sum([m['queue_size'] for m in pipeline_metrics.values()])
        
        result = {
            'check_time': datetime.now().isoformat(),
            'avg_success_rate': round(avg_success_rate, 2),
            'avg_processing_time': round(avg_processing_time, 2),
            'total_queue_size': total_queue_size,
            'pipelines_checked': len(pipelines),
            'failed_pipelines': failed_pipelines,
            'pipeline_metrics': pipeline_metrics,
            'overall_status': 'HEALTHY' if len(failed_pipelines) == 0 else 'CRITICAL'
        }
        
        logging.info(f"Pipeline Health Check Results: {json.dumps(result, indent=2)}")
        
        # Store results for downstream tasks
        context['task_instance'].xcom_push(key='pipeline_health', value=result)
        
        return result
        
    except Exception as e:
        logging.error(f"Error in pipeline health check: {str(e)}")
        raise

def generate_quality_report(**context):
    """Generate comprehensive data quality report"""
    try:
        logging.info("Generating comprehensive data quality report...")
        
        # Get results from previous tasks
        bmkg_quality = context['task_instance'].xcom_pull(key='bmkg_quality', task_ids='check_bmkg_data_quality')
        iot_quality = context['task_instance'].xcom_pull(key='iot_quality', task_ids='check_iot_sensor_quality')
        pipeline_health = context['task_instance'].xcom_pull(key='pipeline_health', task_ids='check_data_pipeline_health')
        
        # Generate comprehensive report
        report = {
            'report_time': datetime.now().isoformat(),
            'report_period': '6_hours',
            'bmkg_data': bmkg_quality,
            'iot_sensors': iot_quality,
            'data_pipelines': pipeline_health,
            'summary': {
                'overall_status': 'HEALTHY',
                'critical_issues': 0,
                'warnings': 0,
                'recommendations': []
            }
        }
        
        # Determine overall status and recommendations
        critical_issues = 0
        warnings = 0
        recommendations = []
        
        # Check BMKG status
        if bmkg_quality['status'] == 'NEEDS_ATTENTION':
            warnings += 1
            recommendations.append("Review BMKG data sources for completeness issues")
        
        # Check IoT status
        if iot_quality['status'] == 'CRITICAL':
            critical_issues += 1
            recommendations.append("Immediate attention needed for IoT sensor maintenance")
        elif iot_quality['status'] == 'WARNING':
            warnings += 1
            recommendations.append("Schedule IoT sensor maintenance and calibration")
        
        # Check pipeline status
        if pipeline_health['overall_status'] == 'CRITICAL':
            critical_issues += 1
            recommendations.append("Investigate and fix failed data pipelines immediately")
        
        # Update summary
        report['summary']['critical_issues'] = critical_issues
        report['summary']['warnings'] = warnings
        report['summary']['recommendations'] = recommendations
        
        if critical_issues > 0:
            report['summary']['overall_status'] = 'CRITICAL'
        elif warnings > 0:
            report['summary']['overall_status'] = 'WARNING'
        else:
            report['summary']['overall_status'] = 'HEALTHY'
        
        logging.info(f"Data Quality Report Generated: {json.dumps(report['summary'], indent=2)}")
        
        # Store report for dashboard
        context['task_instance'].xcom_push(key='quality_report', value=report)
        
        return report
        
    except Exception as e:
        logging.error(f"Error generating quality report: {str(e)}")
        raise

def send_quality_alerts(**context):
    """Send alerts based on quality check results"""
    try:
        logging.info("Processing quality alerts...")
        
        # Get quality report
        quality_report = context['task_instance'].xcom_pull(key='quality_report', task_ids='generate_quality_report')
        
        alerts_sent = []
        
        if quality_report['summary']['overall_status'] == 'CRITICAL':
            alert_message = f"""
🚨 CRITICAL: Lampung Flood Prediction System Alert 🚨

Time: {quality_report['report_time']}
Status: {quality_report['summary']['overall_status']}
Critical Issues: {quality_report['summary']['critical_issues']}

Immediate Actions Required:
{chr(10).join(['• ' + rec for rec in quality_report['summary']['recommendations']])}

Please check the system dashboard immediately.
            """
            
            logging.warning("CRITICAL ALERT: " + alert_message)
            alerts_sent.append("CRITICAL_SYSTEM_ALERT")
            
        elif quality_report['summary']['overall_status'] == 'WARNING':
            alert_message = f"""
⚠️  WARNING: Lampung Flood Prediction System Alert ⚠️ 

Time: {quality_report['report_time']}
Status: {quality_report['summary']['overall_status']}
Warnings: {quality_report['summary']['warnings']}

Recommended Actions:
{chr(10).join(['• ' + rec for rec in quality_report['summary']['recommendations']])}

Please review system status.
            """
            
            logging.warning("WARNING ALERT: " + alert_message)
            alerts_sent.append("WARNING_SYSTEM_ALERT")
        
        else:
            logging.info("✅ System status is HEALTHY - no alerts needed")
            alerts_sent.append("HEALTHY_STATUS_CONFIRMED")
        
        return {'alerts_sent': alerts_sent, 'status': quality_report['summary']['overall_status']}
        
    except Exception as e:
        logging.error(f"Error sending quality alerts: {str(e)}")
        raise

# Define tasks
start_task = DummyOperator(
    task_id='start_quality_monitoring',
    dag=dag
)

bmkg_check = PythonOperator(
    task_id='check_bmkg_data_quality',
    python_callable=check_bmkg_data_quality,
    dag=dag
)

iot_check = PythonOperator(
    task_id='check_iot_sensor_quality',
    python_callable=check_iot_sensor_quality,
    dag=dag
)

pipeline_check = PythonOperator(
    task_id='check_data_pipeline_health',
    python_callable=check_data_pipeline_health,
    dag=dag
)

generate_report = PythonOperator(
    task_id='generate_quality_report',
    python_callable=generate_quality_report,
    dag=dag
)

send_alerts = PythonOperator(
    task_id='send_quality_alerts',
    python_callable=send_quality_alerts,
    dag=dag
)

update_dashboard = BashOperator(
    task_id='update_quality_dashboard',
    bash_command="""
    echo "Updating quality monitoring dashboard..."
    echo "Quality report updated at $(date)"
    echo "Dashboard available at: http://localhost:8088/superset/dashboard/quality-monitoring"
    """,
    dag=dag
)

end_task = DummyOperator(
    task_id='end_quality_monitoring',
    dag=dag
)

# Define task dependencies
start_task >> [bmkg_check, iot_check, pipeline_check]
[bmkg_check, iot_check, pipeline_check] >> generate_report
generate_report >> [send_alerts, update_dashboard]
[send_alerts, update_dashboard] >> end_task
