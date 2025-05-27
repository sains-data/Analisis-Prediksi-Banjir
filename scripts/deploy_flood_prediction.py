#!/usr/bin/env python3
"""
Script deployment untuk prediksi banjir real-time
menggunakan model yang telah dilatih.

"""

import pandas as pd
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

class FloodPredictionDeployment:
    """
    Class untuk deployment model prediksi banjir
    """
    
    def __init__(self, model_path='data/processed/flood_prediction_model.joblib'):
        """
        Initialize deployment dengan load model
        """
        print("🚀 Initializing Flood Prediction Deployment System...")
        
        # Load trained model
        self.model_data = joblib.load(model_path)
        self.model = self.model_data['model']
        self.model_name = self.model_data['model_name']
        self.scaler = self.model_data.get('scaler')
        self.feature_selector = self.model_data.get('feature_selector')
        self.selected_features = self.model_data.get('selected_features')
        
        print(f"✓ Model loaded: {self.model_name}")
        print(f"✓ Feature selector: {'Available' if self.feature_selector else 'Not available'}")
        print(f"✓ Scaler: {'Available' if self.scaler else 'Not available'}")
    
    def predict_flood_risk(self, input_data):
        """
        Prediksi risiko banjir untuk data input baru
        
        Args:
            input_data: DataFrame dengan fitur yang diperlukan
        
        Returns:
            DataFrame dengan prediksi risiko
        """
        print("\n🔮 Making flood risk predictions...")
        
        try:
            # Prepare features
            feature_cols = input_data.select_dtypes(include=[np.number]).columns
            features_numeric = input_data[feature_cols]
            
            # Apply feature selection if available
            if self.feature_selector is not None:
                features_selected = self.feature_selector.transform(features_numeric)
                print(f"✓ Applied feature selection: {features_selected.shape[1]} features")
            else:
                features_selected = features_numeric
                print("⚠️ No feature selector, using all features")
            
            # Apply scaling if needed
            if self.model_name in ['Logistic Regression', 'SVM'] and self.scaler is not None:
                features_scaled = self.scaler.transform(features_selected)
                features_final = features_scaled
                print("✓ Applied feature scaling")
            else:
                features_final = features_selected
            
            # Make predictions
            if hasattr(self.model, 'predict_proba') and len(self.model.classes_) > 1:
                probabilities = self.model.predict_proba(features_final)[:, 1]
            else:
                probabilities = self.model.predict(features_final).astype(float)
            
            predictions = self.model.predict(features_final)
            
            # Create risk categories
            risk_categories = pd.cut(
                probabilities,
                bins=[0, 0.3, 0.6, 0.8, 1.0],
                labels=['Low', 'Medium', 'High', 'Very High']
            )
            
            # Create results DataFrame
            results = pd.DataFrame({
                'flood_risk_probability': probabilities,
                'flood_risk_prediction': predictions,
                'flood_risk_category': risk_categories
            })
            
            # Add original data if has region info
            if 'kabupaten_kota' in input_data.columns:
                results['kabupaten_kota'] = input_data['kabupaten_kota'].values
            
            print(f"✓ Predictions completed for {len(results)} records")
            
            return results
            
        except Exception as e:
            print(f"❌ Error in prediction: {str(e)}")
            raise
    
    def predict_single_region(self, region_features):
        """
        Prediksi untuk satu region dengan input manual
        
        Args:
            region_features: dict dengan fitur-fitur region
        
        Returns:
            dict dengan hasil prediksi
        """
        # Convert to DataFrame
        input_df = pd.DataFrame([region_features])
        
        # Make prediction
        result = self.predict_flood_risk(input_df)
        
        # Return single result
        return {
            'probability': float(result['flood_risk_probability'].iloc[0]),
            'category': str(result['flood_risk_category'].iloc[0]),
            'binary_prediction': int(result['flood_risk_prediction'].iloc[0])
        }
    
    def batch_predict_from_file(self, input_file, output_file=None):
        """
        Prediksi batch dari file CSV
        
        Args:
            input_file: path ke file input CSV
            output_file: path ke file output (optional)
        
        Returns:
            DataFrame dengan hasil prediksi
        """
        print(f"\n📂 Loading data from: {input_file}")
        
        # Load input data
        input_data = pd.read_csv(input_file)
        print(f"✓ Loaded {len(input_data)} records")
        
        # Make predictions
        results = self.predict_flood_risk(input_data)
        
        # Combine with input data
        if 'kabupaten_kota' in input_data.columns:
            combined_results = pd.concat([
                input_data[['kabupaten_kota']], 
                results
            ], axis=1)
        else:
            combined_results = results
        
        # Save results if output file specified
        if output_file:
            combined_results.to_csv(output_file, index=False)
            print(f"✓ Results saved to: {output_file}")
        
        return combined_results
    
    def get_model_info(self):
        """
        Informasi tentang model yang digunakan
        """
        info = {
            'model_type': self.model_name,
            'model_class': str(type(self.model).__name__),
            'has_scaler': self.scaler is not None,
            'has_feature_selector': self.feature_selector is not None,
            'selected_features': list(self.selected_features) if self.selected_features is not None else None,
            'feature_count': len(self.selected_features) if self.selected_features is not None else 'Unknown'
        }
        return info
    
    def generate_prediction_report(self, results):
        """
        Generate laporan ringkas dari hasil prediksi
        """
        print("\n" + "="*60)
        print("             LAPORAN PREDIKSI BANJIR")
        print("="*60)
        
        if 'kabupaten_kota' in results.columns:
            print(f"\n📊 DISTRIBUSI RISIKO:")
            risk_counts = results['flood_risk_category'].value_counts()
            for category, count in risk_counts.items():
                percentage = count / len(results) * 100
                emoji = "🔴" if category == "Very High" else "🟠" if category == "High" else "🟡" if category == "Medium" else "🟢"
                print(f"   {emoji} {category}: {count} daerah ({percentage:.1f}%)")
            
            print(f"\n⚠️  DAERAH RISIKO TINGGI:")
            high_risk = results[results['flood_risk_category'].isin(['Very High', 'High'])]
            if len(high_risk) > 0:
                high_risk_sorted = high_risk.sort_values('flood_risk_probability', ascending=False)
                for _, row in high_risk_sorted.iterrows():
                    print(f"   • {row['kabupaten_kota']}: {row['flood_risk_probability']:.1%} ({row['flood_risk_category']})")
            else:
                print("   Tidak ada daerah dengan risiko tinggi")
        
        print(f"\n📈 STATISTIK PREDIKSI:")
        print(f"   • Total prediksi: {len(results)}")
        print(f"   • Rata-rata probabilitas: {results['flood_risk_probability'].mean():.3f}")
        print(f"   • Probabilitas tertinggi: {results['flood_risk_probability'].max():.3f}")
        print(f"   • Probabilitas terendah: {results['flood_risk_probability'].min():.3f}")
        
        print("="*60)

def main():
    """
    Contoh penggunaan deployment system
    """
    print("🌊 FLOOD PREDICTION DEPLOYMENT SYSTEM 🌊")
    print("="*50)
    
    try:
        # Initialize deployment
        deployment = FloodPredictionDeployment()
        
        # Show model info
        model_info = deployment.get_model_info()
        print(f"\n📋 MODEL INFO:")
        for key, value in model_info.items():
            print(f"   • {key}: {value}")
        
        # Example: Predict from existing regional data
        print(f"\n🔄 TESTING WITH EXISTING DATA:")
        regional_data = pd.read_csv('data/processed/regional_flood_risk_analysis.csv')
        
        # Select sample regions for prediction
        sample_regions = regional_data.head(5)
        predictions = deployment.predict_flood_risk(sample_regions)
        
        # Combine results
        sample_with_predictions = pd.concat([
            sample_regions[['kabupaten_kota']], 
            predictions
        ], axis=1)
        
        # Generate report
        deployment.generate_prediction_report(sample_with_predictions)
        
        print(f"\n✅ DEPLOYMENT SYSTEM READY!")
        print(f"📝 Use deployment.predict_flood_risk(data) for new predictions")
        print(f"📁 Use deployment.batch_predict_from_file() for batch processing")
        
        return deployment
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    deployment_system = main()
