"""
Model Prediktif Banjir menggunakan Spark MLlib
Sesuai dengan Proposal: Model Prediktif dengan Spark MLlib
"""

from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.regression import GBTRegressor
from pyspark.ml.evaluation import BinaryClassificationEvaluator, RegressionEvaluator
from pyspark.ml import Pipeline
from pyspark.sql.functions import col, when

class FloodPredictionModel:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("LampungFloodPrediction") \
            .config("spark.sql.adaptive.enabled", "true") \
            .getOrCreate()
    
    def load_training_data(self):
        """Load data dari Hive tables"""
        # Data cuaca dari BMKG
        weather_df = self.spark.sql("""
            SELECT * FROM flood_data.weather_history 
            WHERE province = 'Lampung'
        """)
        
        # Data kejadian banjir dari BNPB
        flood_events_df = self.spark.sql("""
            SELECT * FROM flood_data.flood_events 
            WHERE province = 'Lampung'
        """)
        
        # Join data untuk training
        training_data = weather_df.join(
            flood_events_df, 
            on=['date', 'location'], 
            how='left'
        ).fillna({'flood_occurred': 0})
        
        return training_data
    
    def create_features(self, df):
        """Feature engineering sesuai proposal"""
        # Fitur cuaca
        weather_features = [
            'rainfall_1day', 'rainfall_3day', 'rainfall_7day',
            'temperature', 'humidity', 'wind_speed'
        ]
        
        # Fitur geografis
        geo_features = [
            'elevation', 'slope', 'distance_to_river',
            'drainage_density', 'land_use_type'
        ]
        
        # Fitur historis
        historical_features = [
            'flood_history_1year', 'flood_history_5year',
            'seasonal_pattern'
        ]
        
        all_features = weather_features + geo_features + historical_features
        
        # Vector assembler
        assembler = VectorAssembler(
            inputCols=all_features,
            outputCol="features"
        )
        
        return assembler
    
    def train_classification_model(self, training_data):
        """Model klasifikasi tingkat risiko banjir"""
        # Random Forest untuk klasifikasi risiko (rendah, sedang, tinggi)
        rf_classifier = RandomForestClassifier(
            featuresCol="scaled_features",
            labelCol="risk_level",
            numTrees=100,
            maxDepth=10,
            seed=42
        )
        
        return rf_classifier
    
    def train_regression_model(self, training_data):
        """Model regresi untuk prediksi kedalaman banjir"""
        # Gradient Boosting Trees untuk prediksi kedalaman
        gbt_regressor = GBTRegressor(
            featuresCol="scaled_features",
            labelCol="flood_depth",
            maxIter=100,
            maxDepth=8,
            seed=42
        )
        
        return gbt_regressor
    
    def create_pipeline(self):
        """Create ML Pipeline sesuai proposal"""
        # Feature engineering
        assembler = self.create_features(None)  # Will be configured later
        
        # Scaling
        scaler = StandardScaler(
            inputCol="features",
            outputCol="scaled_features"
        )
        
        # Models
        rf_classifier = self.train_classification_model(None)
        gbt_regressor = self.train_regression_model(None)
        
        # Pipeline
        pipeline = Pipeline(stages=[
            assembler,
            scaler,
            rf_classifier
        ])
        
        return pipeline
    
    def evaluate_model(self, predictions, model_type="classification"):
        """Evaluasi model sesuai target akurasi minimal 75%"""
        if model_type == "classification":
            evaluator = BinaryClassificationEvaluator(
                labelCol="flood_occurred",
                rawPredictionCol="rawPrediction",
                metricName="areaUnderROC"
            )
            auc = evaluator.evaluate(predictions)
            print(f"Model Classification AUC: {auc:.4f}")
            
            if auc >= 0.75:
                print("✅ Model memenuhi target akurasi minimal 75%")
            else:
                print("❌ Model belum memenuhi target akurasi minimal 75%")
                
        elif model_type == "regression":
            evaluator = RegressionEvaluator(
                labelCol="flood_depth",
                predictionCol="prediction",
                metricName="rmse"
            )
            rmse = evaluator.evaluate(predictions)
            print(f"Model Regression RMSE: {rmse:.4f}")
    
    def save_model(self, model, model_path):
        """Simpan model untuk deployment"""
        model.write().overwrite().save(model_path)
        print(f"Model saved to: {model_path}")

if __name__ == "__main__":
    print("Training Flood Prediction Model for Lampung Province...")
    
    model = FloodPredictionModel()
    
    # Load dan training
    training_data = model.load_training_data()
    pipeline = model.create_pipeline()
    
    # Fit model
    trained_model = pipeline.fit(training_data)
    
    # Evaluasi
    predictions = trained_model.transform(training_data)
    model.evaluate_model(predictions)
    
    # Save model
    model.save_model(trained_model, "/data/analytics/models/deployed/flood_prediction_v1")
    
    print("Model training completed!")
