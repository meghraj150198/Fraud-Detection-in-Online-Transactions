"""
Fraud Detection Scoring Service - Production Deployment
========================================================
Real-time fraud risk prediction API for online transaction monitoring
"""

import pandas as pd
import numpy as np
import pickle
import warnings
warnings.filterwarnings('ignore')

from datetime import datetime
import json
import logging

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('fraud_scoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# FRAUD SCORING SERVICE CLASS
# ============================================================================

class FraudScoringService:
    """
    Production-ready fraud detection service for real-time scoring
    """
    
    def __init__(self, model_artifacts_path='ml_model_artifacts.pkl', feature_data_path='sales_with_fraud_indicators.csv'):
        """Initialize the scoring service with trained models"""
        
        logger.info("Initializing Fraud Scoring Service...")
        
        # Load model artifacts
        with open(model_artifacts_path, 'rb') as f:
            self.artifacts = pickle.load(f)
        
        self.meta_model = self.artifacts['meta_model']
        self.base_models = self.artifacts['base_models']
        self.label_encoder = self.artifacts['label_encoder']
        self.scaler = self.artifacts['scaler']
        self.all_features = self.artifacts['all_features']
        self.feature_groups = self.artifacts['feature_groups']
        
        # Load feature reference data for scaling context
        self.feature_data = pd.read_csv(feature_data_path)
        
        logger.info(f"✓ Model loaded with {len(self.all_features)} features")
        logger.info(f"✓ Risk classes: {list(self.label_encoder.classes_)}")
        logger.info(f"✓ Base models: {len(self.base_models)} signal groups")
        
        # Scoring statistics
        self.total_scored = 0
        self.fraud_count = 0
        self.last_scores = None
    
    def prepare_features(self, transaction_data):
        """
        Prepare transaction data for model input
        Handles missing values, scaling, and feature alignment
        """
        
        # Ensure all required features present
        for feature in self.all_features:
            if feature not in transaction_data.columns:
                # Use mean from training data if missing
                transaction_data[feature] = self.feature_data[feature].mean()
        
        # Select only required features
        X = transaction_data[self.all_features].copy()
        
        # Handle missing values
        X = X.fillna(X.mean(numeric_only=True))
        
        return X
    
    def get_base_predictions(self, X, return_probabilities=False):
        """
        Generate predictions from all base models
        Returns probability distributions for meta-learner input
        """
        
        base_predictions = []
        
        for group_name, model_info in self.base_models.items():
            model = model_info['model']
            scaler_group = model_info['scaler']
            features = model_info['features']
            
            # Filter features for this group
            X_group = X[features].copy()
            
            # Scale
            X_group_scaled = scaler_group.transform(X_group)
            
            # Get probability predictions
            proba = model.predict_proba(X_group_scaled)
            base_predictions.append(proba)
        
        # Stack all base predictions
        X_meta = np.hstack(base_predictions)
        
        if return_probabilities:
            return X_meta, base_predictions
        return X_meta
    
    def score_transactions(self, transaction_data, return_details=False):
        """
        Score transactions and return fraud risk classifications
        
        Parameters:
        - transaction_data: DataFrame with transaction features
        - return_details: If True, return detailed probability scores
        
        Returns:
        - DataFrame with risk classifications and scores
        """
        
        logger.info(f"Scoring {len(transaction_data)} transactions...")
        
        # Prepare features
        X = self.prepare_features(transaction_data)
        
        # Get base model predictions
        X_meta = self.get_base_predictions(X)
        
        # Meta-model prediction
        y_pred_encoded = self.meta_model.predict(X_meta)
        y_pred_proba = self.meta_model.predict_proba(X_meta)
        
        # Decode predictions
        y_pred_labels = self.label_encoder.inverse_transform(y_pred_encoded)
        
        # Get risk scores (max probability)
        risk_scores = y_pred_proba.max(axis=1) * 100  # Convert to 0-100 scale
        
        # Create results dataframe
        results = pd.DataFrame({
            'transaction_id': range(len(transaction_data)),
            'predicted_risk_level': y_pred_labels,
            'risk_score': risk_scores.round(2),
            'confidence': (y_pred_proba.max(axis=1) * 100).round(2)
        })
        
        # Add probability for each class
        for i, class_name in enumerate(self.label_encoder.classes_):
            results[f'prob_{class_name.lower()}'] = (y_pred_proba[:, i] * 100).round(2)
        
        # Fraud flag (Medium or High risk)
        results['is_fraud_flagged'] = results['predicted_risk_level'].isin(['Medium', 'High']).astype(int)
        
        # Update statistics
        self.total_scored += len(transaction_data)
        self.fraud_count += results['is_fraud_flagged'].sum()
        self.last_scores = results
        
        logger.info(f"✓ Scored {len(transaction_data)} transactions")
        logger.info(f"  • Fraud Flagged: {results['is_fraud_flagged'].sum()} ({results['is_fraud_flagged'].mean()*100:.2f}%)")
        logger.info(f"  • Average Risk Score: {results['risk_score'].mean():.2f}/100")
        
        if return_details:
            return results, y_pred_proba
        return results
    
    def score_single_transaction(self, transaction_dict):
        """Score a single transaction and return fraud risk
        
        Parameters:
        - transaction_dict: Dictionary with transaction features
        
        Returns:
        - Dictionary with risk classification and score
        """
        
        # Convert to DataFrame
        tx_data = pd.DataFrame([transaction_dict])
        
        # Score
        results = self.score_transactions(tx_data, return_details=False)
        result_row = results.iloc[0].to_dict()
        
        # Format response
        response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'prediction': {
                'risk_level': result_row['predicted_risk_level'],
                'risk_score': float(result_row['risk_score']),
                'confidence': float(result_row['confidence']),
                'is_flagged': bool(result_row['is_fraud_flagged']),
                'class_probabilities': {
                    'low': float(result_row['prob_low']),
                    'medium': float(result_row['prob_medium']),
                    'high': float(result_row['prob_high'])
                }
            }
        }
        
        return response
    
    def get_model_stats(self):
        """Return model performance statistics"""
        
        stats = {
            'model_info': {
                'base_models': len(self.base_models),
                'base_model_types': list(self.base_models.keys()),
                'total_features': len(self.all_features),
                'risk_classes': list(self.label_encoder.classes_),
                'training_date': self.artifacts.get('training_date', 'Unknown')
            },
            'training_metrics': self.artifacts.get('metrics', {}),
            'service_stats': {
                'total_transactions_scored': self.total_scored,
                'total_fraud_flagged': self.fraud_count,
                'fraud_flag_rate': f"{(self.fraud_count / max(self.total_scored, 1) * 100):.2f}%"
            }
        }
        
        return stats
    
    def generate_risk_report(self, results_df):
        """Generate summary report from scored transactions"""
        
        report = {
            'total_transactions': len(results_df),
            'risk_distribution': results_df['predicted_risk_level'].value_counts().to_dict(),
            'fraud_flagged': results_df['is_fraud_flagged'].sum(),
            'fraud_flag_rate': f"{results_df['is_fraud_flagged'].mean()*100:.2f}%",
            'average_risk_score': f"{results_df['risk_score'].mean():.2f}",
            'high_risk_transactions': len(results_df[results_df['predicted_risk_level'] == 'High']),
            'percentile_risk_scores': {
                '25th': float(results_df['risk_score'].quantile(0.25)),
                '50th': float(results_df['risk_score'].quantile(0.50)),
                '75th': float(results_df['risk_score'].quantile(0.75)),
                '95th': float(results_df['risk_score'].quantile(0.95))
            }
        }
        
        return report


# ============================================================================
# EXAMPLE DEPLOYMENT & TESTING
# ============================================================================

def main():
    """Initialize service and demonstrate scoring"""
    
    print("=" * 80)
    print("FRAUD DETECTION SCORING SERVICE - DEPLOYMENT")
    print("=" * 80)
    
    # Initialize service
    service = FraudScoringService()
    
    # Display model information
    print("\n[1] MODEL INFORMATION")
    print("   " + "=" * 76)
    stats = service.get_model_stats()
    print(f"\n   Architecture:")
    print(f"   • Base Models: {stats['model_info']['base_models']}")
    print(f"   • Signal Groups: {', '.join(stats['model_info']['base_model_types'])}")
    print(f"   • Total Features: {stats['model_info']['total_features']}")
    print(f"   • Risk Classes: {', '.join(stats['model_info']['risk_classes'])}")
    
    print(f"\n   Training Performance:")
    for metric, value in stats['training_metrics'].items():
        print(f"   • {metric.replace('_', ' ').title()}: {value:.4f}")
    
    # Load test data
    print("\n[2] LOADING TEST DATA")
    print("   " + "=" * 76)
    test_df = pd.read_csv('sales_with_fraud_indicators.csv').head(100)
    print(f"   ✓ Loaded {len(test_df)} transactions for testing")
    
    # Score batch
    print("\n[3] BATCH SCORING")
    print("   " + "=" * 76)
    results = service.score_transactions(test_df, return_details=False)
    
    print(f"\n   Results Preview:")
    print(results.head(10).to_string(index=False))
    
    # Risk report
    print("\n[4] RISK ANALYSIS REPORT")
    print("   " + "=" * 76)
    report = service.generate_risk_report(results)
    
    print(f"\n   Transaction Summary:")
    print(f"   • Total Scored: {report['total_transactions']:,}")
    print(f"   • Fraud Flagged: {report['fraud_flagged']} ({report['fraud_flag_rate']})")
    print(f"   • High Risk: {report['high_risk_transactions']}")
    
    print(f"\n   Risk Distribution:")
    for risk_level, count in report['risk_distribution'].items():
        pct = count / report['total_transactions'] * 100
        print(f"   • {risk_level:10s}: {count:6,d} ({pct:5.2f}%)")
    
    print(f"\n   Risk Score Percentiles:")
    for pct, score in report['percentile_risk_scores'].items():
        print(f"   • {pct:3s} percentile: {score:6.2f}")
    
    # Single transaction example
    print("\n[5] SINGLE TRANSACTION SCORING")
    print("   " + "=" * 76)
    
    # Get first transaction
    tx_dict = test_df.iloc[0].to_dict()
    response = service.score_single_transaction(tx_dict)
    
    print(f"\n   Transaction Response:")
    print(f"   • Risk Level: {response['prediction']['risk_level']}")
    print(f"   • Risk Score: {response['prediction']['risk_score']:.2f}/100")
    print(f"   • Confidence: {response['prediction']['confidence']:.2f}%")
    print(f"   • Flagged: {response['prediction']['is_flagged']}")
    print(f"\n   Class Probabilities:")
    for cls, prob in response['prediction']['class_probabilities'].items():
        print(f"   • {cls.capitalize():10s}: {prob:.2f}%")
    
    # High-risk transactions
    print("\n[6] HIGH-RISK TRANSACTIONS")
    print("   " + "=" * 76)
    
    high_risk = results[results['predicted_risk_level'] == 'High'].sort_values('risk_score', ascending=False)
    
    if len(high_risk) > 0:
        print(f"\n   Found {len(high_risk)} HIGH RISK transactions:")
        print(high_risk[['transaction_id', 'risk_score', 'confidence']].head(10).to_string(index=False))
    else:
        print("\n   No HIGH risk transactions in this batch")
    
    # Service statistics
    print("\n[7] SERVICE STATISTICS")
    print("   " + "=" * 76)
    
    final_stats = service.get_model_stats()
    print(f"\n   Scoring Service Stats (since initialization):")
    print(f"   • Total Transactions Scored: {final_stats['service_stats']['total_transactions_scored']:,}")
    print(f"   • Total Fraud Flagged: {final_stats['service_stats']['total_fraud_flagged']:,}")
    print(f"   • Fraud Flag Rate: {final_stats['service_stats']['fraud_flag_rate']}")
    
    # Save sample outputs
    print("\n[8] SAVING OUTPUTS")
    print("   " + "=" * 76)
    
    results.to_csv('fraud_scores_batch_sample.csv', index=False)
    print(f"   ✓ Saved: fraud_scores_batch_sample.csv")
    
    with open('model_stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"   ✓ Saved: model_stats.json")
    
    print("\n" + "=" * 80)
    print("DEPLOYMENT COMPLETE - Service Ready for Production")
    print("=" * 80)
    
    return service


# ============================================================================
# REST API DEPLOYMENT (OPTIONAL - Requires Flask)
# ============================================================================

def create_flask_api(service):
    """Create Flask REST API for fraud scoring service"""
    
    try:
        from flask import Flask, request, jsonify
    except ImportError:
        logger.warning("Flask not installed. Install with: pip install flask")
        return None
    
    app = Flask(__name__)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'Fraud Detection Scoring',
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/score', methods=['POST'])
    def score_transaction():
        """Score a single transaction"""
        try:
            data = request.json
            response = service.score_single_transaction(data)
            return jsonify(response), 200
        except Exception as e:
            logger.error(f"Scoring error: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 400
    
    @app.route('/score-batch', methods=['POST'])
    def score_batch():
        """Score multiple transactions"""
        try:
            data = request.json
            transactions_list = data.get('transactions', [])
            
            if not transactions_list:
                return jsonify({'status': 'error', 'message': 'No transactions provided'}), 400
            
            # Convert to DataFrame
            tx_df = pd.DataFrame(transactions_list)
            
            # Score
            results = service.score_transactions(tx_df, return_details=False)
            
            return jsonify({
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'total_scored': len(results),
                'fraud_flagged': int(results['is_fraud_flagged'].sum()),
                'results': results.to_dict(orient='records')
            }), 200
        
        except Exception as e:
            logger.error(f"Batch scoring error: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 400
    
    @app.route('/stats', methods=['GET'])
    def get_stats():
        """Get model statistics"""
        try:
            stats = service.get_model_stats()
            return jsonify(stats), 200
        except Exception as e:
            logger.error(f"Stats error: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 400
    
    return app


if __name__ == '__main__':
    # Initialize service and run deployment demo
    service = main()
    
    # Uncomment to start Flask API (requires Flask)
    # app = create_flask_api(service)
    # app.run(host='0.0.0.0', port=5000, debug=False)
