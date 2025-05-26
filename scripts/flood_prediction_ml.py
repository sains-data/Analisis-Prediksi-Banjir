#!/usr/bin/env python3
"""
Script untuk membuat model machine learning prediksi banjir 
berdasarkan data elevasi, cuaca, dan riwayat banjir Lampung.

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.feature_selection import SelectKBest, f_classif
import joblib
import warnings
warnings.filterwarnings('ignore')

class FloodPredictionModel:
    """
    Class untuk membuat model prediksi banjir
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}        
        self.feature_importance = {}
        self.best_model = None
        self.best_model_name = None
        self.feature_selector = None
        self.selected_features = None
    def load_integrated_data(self):
        """Load dan gabungkan semua data yang sudah diproses"""
        print("Loading integrated datasets...")
        
        # Load data elevasi dengan regions
        elevation_df = pd.read_csv('data/raw/demnas/topografi/data_elevasi_with_regions.csv', encoding='utf-8')
        print(f"✓ Elevation data: {len(elevation_df):,} points")
        
        # Load data banjir yang sudah enhanced
        flood_df = pd.read_csv('data/processed/flood_events_enhanced.csv', encoding='utf-8')
        print(f"✓ Flood events: {len(flood_df):,} records")
        
        # Load data cuaca yang sudah enhanced
        weather_df = pd.read_csv('data/processed/weather_data_enhanced.csv', encoding='utf-8')
        print(f"✓ Weather data: {len(weather_df):,} records")
        
        # Load analisis risiko regional
        risk_df = pd.read_csv('data/processed/regional_flood_risk_analysis.csv', encoding='utf-8')
        print(f"✓ Regional risk analysis: {len(risk_df):,} regions")
        
        return elevation_df, flood_df, weather_df, risk_df
    
    def prepare_features(self, elevation_df, flood_df, weather_df, risk_df):
        """Persiapkan features untuk machine learning"""
        print("\nPreparing features for machine learning...")
        
        # 1. Aggregate elevation features by region
        elevation_features = elevation_df.groupby('kabupaten_kota').agg({
            'elevation_m': ['mean', 'std', 'min', 'max'],
            'slope_deg': ['mean', 'std', 'max'],
            'region_confidence': 'mean',
            'grid_id': 'count'
        }).round(2)
        
        elevation_features.columns = [
            'elevation_mean', 'elevation_std', 'elevation_min', 'elevation_max',
            'slope_mean', 'slope_std', 'slope_max', 'region_confidence', 'grid_count'
        ]
        
        # 2. Aggregate weather features by region and season
        weather_features = weather_df.groupby(['location', 'musim']).agg({
            'rainfall': ['mean', 'sum', 'max', 'std'],
            'humidity': ['mean', 'max'],
            'temperature': ['mean', 'max'],
            'wind_speed': ['mean', 'max']
        }).round(2)
        
        weather_features.columns = [
            'rainfall_mean', 'rainfall_sum', 'rainfall_max', 'rainfall_std',
            'humidity_mean', 'humidity_max', 'temperature_mean', 'temperature_max',
            'wind_speed_mean', 'wind_speed_max'
        ]
        
        # Pivot weather data to get seasonal features
        weather_pivot = weather_features.reset_index().pivot(
            index='location', columns='musim'
        ).fillna(0)
        
        # Flatten column names
        weather_pivot.columns = [f"{col[0]}_{col[1].replace(' ', '_')}" for col in weather_pivot.columns]
        
        # 3. Prepare flood target and additional features
        flood_features = flood_df.groupby('lokasi').agg({
            'tinggi_air_cm': ['count', 'mean', 'max', 'sum'],
            'area_terdampak_ha': ['mean', 'max', 'sum'],
            'durasi_jam': ['mean', 'max', 'sum'],
            'jumlah_pengungsi': ['sum', 'max'],
            'bulan': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else x.median()
        }).round(2)
        
        flood_features.columns = [
            'flood_frequency', 'water_height_mean', 'water_height_max', 'water_height_total',
            'affected_area_mean', 'affected_area_max', 'affected_area_total',
            'duration_mean', 'duration_max', 'duration_total',
            'evacuees_total', 'evacuees_max', 'peak_flood_month'
        ]
        
        # 4. Combine all features
        master_features = elevation_features.copy()
        master_features = master_features.join(weather_pivot, how='left')
        master_features = master_features.join(flood_features, how='left')
        
        # Fill missing values
        master_features = master_features.fillna(0)
          # 5. Create target variables
        # Binary classification: High flood risk (based on frequency > median)
        median_frequency = master_features['flood_frequency'].median()
        master_features['has_high_flood_risk'] = (master_features['flood_frequency'] > median_frequency).astype(int)
        
        # Alternative target: Based on total impact
        master_features['total_impact_score'] = (
            master_features['water_height_total'] + 
            master_features['affected_area_total'] + 
            master_features['evacuees_total']
        )
        median_impact = master_features['total_impact_score'].median()
        master_features['has_high_impact'] = (master_features['total_impact_score'] > median_impact).astype(int)
        
        # Multi-class classification: Risk level based on quartiles
        master_features['risk_level'] = pd.qcut(
            master_features['flood_frequency'],
            q=4,
            labels=['Low Risk', 'Medium Risk', 'High Risk', 'Very High Risk']
        )
        
        # Add additional derived features
        master_features['elevation_risk_score'] = np.where(
            master_features['elevation_mean'] < 50, 3,
            np.where(master_features['elevation_mean'] < 100, 2,
                    np.where(master_features['elevation_mean'] < 200, 1, 0))
        )
        
        master_features['rainfall_intensity'] = (
            master_features['rainfall_mean_Musim_Hujan'] / 
            (master_features['rainfall_mean_Musim_Kemarau'] + 1)
        )
        
        master_features['topographic_vulnerability'] = (
            master_features['elevation_risk_score'] * master_features['slope_max'] / 10
        )
        
        print(f"✓ Created {len(master_features)} regional feature sets")
        print(f"✓ Feature dimensions: {master_features.shape}")
        
        return master_features
    
    def select_features(self, X, y, k=15):
        """Feature selection untuk mendapatkan fitur terbaik"""
        print(f"\nSelecting top {k} features...")
          # Remove non-numeric columns and target columns
        feature_cols = X.select_dtypes(include=[np.number]).columns
        feature_cols = feature_cols.drop(['has_high_flood_risk', 'has_high_impact', 'total_impact_score', 'risk_level'], errors='ignore')
        
        X_numeric = X[feature_cols]
        
        # Feature selection
        selector = SelectKBest(score_func=f_classif, k=min(k, len(feature_cols)))
        X_selected = selector.fit_transform(X_numeric, y)
        
        # Get selected feature names
        selected_features = feature_cols[selector.get_support()]
        print(f"✓ Selected features: {list(selected_features)}")
        
        # Store selector for later use
        self.feature_selector = selector
        self.selected_features = selected_features
        
        return X_selected, selected_features, selector
    
    def train_models(self, X, y, feature_names):
        """Train multiple models dan bandingkan performa"""
        print("\nTraining multiple models...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers['main'] = scaler
        
        # Define models
        models = {
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
            'SVM': SVC(probability=True, random_state=42)
        }
        
        # Train and evaluate models
        results = {}
        
        for name, model in models.items():
            print(f"\nTraining {name}...")
              # Train model
            if name in ['Logistic Regression', 'SVM']:
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                if hasattr(model, 'predict_proba') and len(model.classes_) > 1:
                    y_prob = model.predict_proba(X_test_scaled)[:, 1]
                else:
                    y_prob = y_pred.astype(float)  # Use predictions as probabilities
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                if hasattr(model, 'predict_proba') and len(model.classes_) > 1:
                    y_prob = model.predict_proba(X_test)[:, 1]
                else:
                    y_prob = y_pred.astype(float)  # Use predictions as probabilities
            
            # Evaluate
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
            
            results[name] = {
                'model': model,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'test_accuracy': (y_pred == y_test).mean(),
                'predictions': y_pred,
                'probabilities': y_prob
            }
            
            # Feature importance (if available)
            if hasattr(model, 'feature_importances_'):
                importance_df = pd.DataFrame({
                    'feature': feature_names,
                    'importance': model.feature_importances_
                }).sort_values('importance', ascending=False)
                
                self.feature_importance[name] = importance_df
                print(f"✓ Top 5 features: {list(importance_df['feature'].head())}")
            
            print(f"✓ CV Accuracy: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
            print(f"✓ Test Accuracy: {results[name]['test_accuracy']:.3f}")
        
        # Find best model
        best_model_name = max(results.keys(), key=lambda k: results[k]['cv_mean'])
        self.best_model = results[best_model_name]['model']
        self.best_model_name = best_model_name
        self.models = results
        
        print(f"\n🏆 Best model: {best_model_name}")
        print(f"🏆 Best CV accuracy: {results[best_model_name]['cv_mean']:.3f}")
        
        return X_train, X_test, y_train, y_test, results
    
    def evaluate_best_model(self, X_test, y_test):
        """Evaluasi detail model terbaik"""
        print(f"\n=== DETAILED EVALUATION: {self.best_model_name} ===")
          # Predictions
        if self.best_model_name in ['Logistic Regression', 'SVM']:
            scaler = self.scalers['main']
            X_test_scaled = scaler.transform(X_test)
            y_pred = self.best_model.predict(X_test_scaled)
            if hasattr(self.best_model, 'predict_proba') and len(self.best_model.classes_) > 1:
                y_prob = self.best_model.predict_proba(X_test_scaled)[:, 1]
            else:
                y_prob = y_pred.astype(float)
        else:
            y_pred = self.best_model.predict(X_test)
            if hasattr(self.best_model, 'predict_proba') and len(self.best_model.classes_) > 1:
                y_prob = self.best_model.predict_proba(X_test)[:, 1]
            else:
                y_prob = y_pred.astype(float)
        
        # Classification report
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        print(f"\nConfusion Matrix:")
        print(cm)
        
        # ROC AUC
        if y_prob is not None:
            auc_score = roc_auc_score(y_test, y_prob)
            print(f"\nROC AUC Score: {auc_score:.3f}")
        
        return y_pred, y_prob
    def create_flood_risk_predictions(self, elevation_df, features_df):
        """Buat prediksi risiko banjir untuk semua titik elevasi"""
        print("\nCreating flood risk predictions for all elevation points...")
        
        # Prepare features untuk prediksi - same as training
        regional_features = features_df.drop(['has_high_flood_risk', 'has_high_impact', 'total_impact_score', 'risk_level'], axis=1, errors='ignore')
        
        # Apply same feature selection as training
        feature_cols = regional_features.select_dtypes(include=[np.number]).columns
        regional_features_numeric = regional_features[feature_cols]
        
        # Use the saved feature selector to transform features
        if self.feature_selector is not None:
            regional_features_selected = self.feature_selector.transform(regional_features_numeric)
            print(f"✓ Applied feature selection: {regional_features_selected.shape[1]} features selected")
        else:
            regional_features_selected = regional_features_numeric
            print("⚠️ No feature selector found, using all numeric features")
        
        # Scale features jika perlu
        if self.best_model_name in ['Logistic Regression', 'SVM']:
            scaler = self.scalers['main']
            regional_features_scaled = scaler.transform(regional_features_selected)
            if hasattr(self.best_model, 'predict_proba') and len(self.best_model.classes_) > 1:
                flood_prob = self.best_model.predict_proba(regional_features_scaled)[:, 1]
            else:
                flood_prob = self.best_model.predict(regional_features_scaled).astype(float)
        else:
            if hasattr(self.best_model, 'predict_proba') and len(self.best_model.classes_) > 1:
                flood_prob = self.best_model.predict_proba(regional_features_selected)[:, 1]
            else:
                flood_prob = self.best_model.predict(regional_features_selected).astype(float)
        
        # Create prediction dataframe
        regional_predictions = pd.DataFrame({
            'kabupaten_kota': regional_features.index,
            'flood_risk_probability': flood_prob,
            'flood_risk_category': pd.cut(
                flood_prob,
                bins=[0, 0.3, 0.6, 0.8, 1.0],
                labels=['Low', 'Medium', 'High', 'Very High']
            )
        })
        
        # Merge with elevation data
        elevation_with_predictions = elevation_df.merge(
            regional_predictions, on='kabupaten_kota', how='left'
        )
        
        print(f"✓ Created predictions for {len(elevation_with_predictions):,} elevation points")
        
        return elevation_with_predictions, regional_predictions
    
    def save_model_and_results(self, features_df, elevation_predictions, regional_predictions):
        """Simpan model dan hasil prediksi"""
        print("\nSaving model and predictions...")
          # Save trained model
        model_path = 'data/processed/flood_prediction_model.joblib'
        joblib.dump({
            'model': self.best_model,
            'model_name': self.best_model_name,
            'scaler': self.scalers.get('main'),
            'feature_selector': self.feature_selector,
            'selected_features': self.selected_features,
            'feature_names': features_df.columns.tolist()
        }, model_path)
        print(f"✓ Model saved: {model_path}")
        
        # Save predictions
        elevation_predictions.to_csv('data/processed/elevation_flood_predictions.csv', index=False)
        print("✓ Elevation predictions saved")
        
        regional_predictions.to_csv('data/processed/regional_flood_predictions.csv', index=False)
        print("✓ Regional predictions saved")
        
        # Save feature importance
        if self.best_model_name in self.feature_importance:
            importance_df = self.feature_importance[self.best_model_name]
            importance_df.to_csv('data/processed/feature_importance.csv', index=False)
            print("✓ Feature importance saved")
    
    def generate_prediction_report(self, regional_predictions, features_df):
        """Generate laporan prediksi risiko banjir"""
        print("\n" + "="*80)
        print("                    LAPORAN PREDIKSI RISIKO BANJIR LAMPUNG")
        print("="*80)
        
        print(f"\nModel terbaik: {self.best_model_name}")
        print(f"Akurasi model: {self.models[self.best_model_name]['cv_mean']:.3f}")
        
        print(f"\n🔴 DAERAH RISIKO SANGAT TINGGI (>80%):")
        very_high = regional_predictions[regional_predictions['flood_risk_category'] == 'Very High']
        for _, row in very_high.iterrows():
            prob = row['flood_risk_probability']
            print(f"   • {row['kabupaten_kota']}: {prob:.1%} probability")
        
        print(f"\n🟠 DAERAH RISIKO TINGGI (60-80%):")
        high = regional_predictions[regional_predictions['flood_risk_category'] == 'High']
        for _, row in high.iterrows():
            prob = row['flood_risk_probability']
            print(f"   • {row['kabupaten_kota']}: {prob:.1%} probability")
        
        print(f"\n🟡 DAERAH RISIKO SEDANG (30-60%):")
        medium = regional_predictions[regional_predictions['flood_risk_category'] == 'Medium']
        for _, row in medium.iterrows():
            prob = row['flood_risk_probability']
            print(f"   • {row['kabupaten_kota']}: {prob:.1%} probability")
        
        print(f"\n🟢 DAERAH RISIKO RENDAH (<30%):")
        low = regional_predictions[regional_predictions['flood_risk_category'] == 'Low']
        for _, row in low.iterrows():
            prob = row['flood_risk_probability']
            print(f"   • {row['kabupaten_kota']}: {prob:.1%} probability")
        
        print(f"\n📊 STATISTIK PREDIKSI:")
        risk_counts = regional_predictions['flood_risk_category'].value_counts()
        for category, count in risk_counts.items():
            percentage = count / len(regional_predictions) * 100
            print(f"   • {category}: {count} daerah ({percentage:.1f}%)")
        
        print(f"\n🔧 FITUR TERPENTING:")
        if self.best_model_name in self.feature_importance:
            top_features = self.feature_importance[self.best_model_name].head()
            for _, row in top_features.iterrows():
                print(f"   • {row['feature']}: {row['importance']:.3f}")
        
        print(f"\n💡 REKOMENDASI BERDASARKAN MODEL:")
        print("   1. Fokus mitigasi pada daerah dengan prediksi risiko tinggi")
        print("   2. Monitor daerah risiko sedang untuk early warning")
        print("   3. Tingkatkan sistem drainase di daerah elevasi rendah")
        print("   4. Perhatikan pola curah hujan musiman untuk preparedness")

def main():
    """Fungsi utama untuk training model prediksi banjir"""
    print("🤖 SISTEM MACHINE LEARNING PREDIKSI BANJIR LAMPUNG 🤖")
    print("="*70)
    
    try:
        # Initialize model
        flood_model = FloodPredictionModel()
        
        # Load data
        elevation_df, flood_df, weather_df, risk_df = flood_model.load_integrated_data()
        
        # Prepare features
        features_df = flood_model.prepare_features(elevation_df, flood_df, weather_df, risk_df)
          # Feature selection
        X_selected, selected_features, selector = flood_model.select_features(
            features_df, features_df['has_high_flood_risk']
        )
        
        # Train models
        X_train, X_test, y_train, y_test, results = flood_model.train_models(
            X_selected, features_df['has_high_flood_risk'], selected_features
        )
        
        # Evaluate best model
        y_pred, y_prob = flood_model.evaluate_best_model(X_test, y_test)
        
        # Create predictions
        elevation_predictions, regional_predictions = flood_model.create_flood_risk_predictions(
            elevation_df, features_df
        )
        
        # Save results
        flood_model.save_model_and_results(
            features_df, elevation_predictions, regional_predictions
        )
        
        # Generate report
        flood_model.generate_prediction_report(regional_predictions, features_df)
        
        print("\n" + "="*70)
        print("✅ MACHINE LEARNING MODEL TRAINING COMPLETED!")
        print("📁 Model dan prediksi tersimpan di folder 'data/processed/'")
        print("🎯 Model siap untuk prediksi banjir real-time")
        
        return flood_model, elevation_predictions, regional_predictions
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = main()
