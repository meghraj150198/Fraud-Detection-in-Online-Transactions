"""
Flask REST API for Fraud Detection Service
============================================
Deployment-ready API with comprehensive endpoints
"""

from flask import Flask, request, jsonify
from fraud_scoring_service import FraudScoringService
import logging
from datetime import datetime
import pandas as pd
import json

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize fraud detection service
try:
    service = FraudScoringService()
    logger.info("✓ Fraud Detection Service initialized")
except Exception as e:
    logger.error(f"Failed to initialize service: {e}")
    service = None

# ============================================================================
# HEALTH & INFO ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Fraud Detection Scoring API',
        'version': '1.0',
        'timestamp': datetime.now().isoformat(),
        'service_ready': service is not None
    }), 200


@app.route('/info', methods=['GET'])
def get_info():
    """Get API and model information"""
    if not service:
        return jsonify({'status': 'error', 'message': 'Service not initialized'}), 503
    
    try:
        stats = service.get_model_stats()
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'api_version': '1.0',
            'model': stats['model_info'],
            'training_performance': stats['training_metrics'],
            'service_stats': stats['service_stats']
        }), 200
    except Exception as e:
        logger.error(f"Info endpoint error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# SCORING ENDPOINTS
# ============================================================================

@app.route('/score', methods=['POST'])
def score_transaction():
    """
    Score a single transaction
    
    Request JSON:
    {
        "selling_price": 450.0,
        "quantity_ordered": 2,
        ... (all 49 required features)
    }
    
    Response:
    {
        "status": "success",
        "prediction": {
            "risk_level": "Low",
            "risk_score": 99.71,
            "confidence": 99.71,
            "is_flagged": false,
            "class_probabilities": {...}
        }
    }
    """
    if not service:
        return jsonify({'status': 'error', 'message': 'Service not available'}), 503
    
    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        response = service.score_single_transaction(data)
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Scoring error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 400


@app.route('/score-batch', methods=['POST'])
def score_batch():
    """
    Score multiple transactions in a batch
    
    Request JSON:
    {
        "transactions": [
            {"selling_price": 450.0, "quantity_ordered": 2, ...},
            {"selling_price": 250.0, "quantity_ordered": 1, ...},
            ...
        ]
    }
    
    Response:
    {
        "status": "success",
        "total_scored": 2,
        "fraud_flagged": 0,
        "results": [
            {"transaction_id": 0, "predicted_risk_level": "Low", ...},
            {"transaction_id": 1, "predicted_risk_level": "Medium", ...}
        ]
    }
    """
    if not service:
        return jsonify({'status': 'error', 'message': 'Service not available'}), 503
    
    try:
        data = request.json
        transactions_list = data.get('transactions', [])
        
        if not transactions_list:
            return jsonify({'status': 'error', 'message': 'No transactions provided'}), 400
        
        if len(transactions_list) > 10000:
            return jsonify({
                'status': 'error',
                'message': 'Batch too large (max 10000 transactions)'
            }), 400
        
        # Convert to DataFrame
        tx_df = pd.DataFrame(transactions_list)
        
        # Score
        logger.info(f"Scoring batch of {len(tx_df)} transactions")
        results = service.score_transactions(tx_df, return_details=False)
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'total_scored': len(results),
            'fraud_flagged': int(results['is_fraud_flagged'].sum()),
            'fraud_flag_rate': float(results['is_fraud_flagged'].mean() * 100),
            'average_risk_score': float(results['risk_score'].mean()),
            'results': results.to_dict(orient='records')
        }), 200
    
    except Exception as e:
        logger.error(f"Batch scoring error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 400


# ============================================================================
# ANALYSIS ENDPOINTS
# ============================================================================

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get model and service statistics"""
    if not service:
        return jsonify({'status': 'error', 'message': 'Service not available'}), 503
    
    try:
        stats = service.get_model_stats()
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            **stats
        }), 200
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/report', methods=['POST'])
def generate_report():
    """
    Generate risk analysis report for transactions
    
    Request JSON:
    {
        "transactions": [...]
    }
    """
    if not service:
        return jsonify({'status': 'error', 'message': 'Service not available'}), 503
    
    try:
        data = request.json
        transactions_list = data.get('transactions', [])
        
        if not transactions_list:
            return jsonify({'status': 'error', 'message': 'No transactions provided'}), 400
        
        # Convert to DataFrame
        tx_df = pd.DataFrame(transactions_list)
        
        # Score
        results = service.score_transactions(tx_df, return_details=False)
        
        # Generate report
        report = service.generate_risk_report(results)
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'report': report
        }), 200
    
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'timestamp': datetime.now().isoformat()
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500


# ============================================================================
# API DOCUMENTATION
# ============================================================================

@app.route('/', methods=['GET'])
def index():
    """API documentation"""
    return jsonify({
        'service': 'Fraud Detection Scoring API',
        'version': '1.0',
        'endpoints': {
            'health': {
                'method': 'GET',
                'endpoint': '/health',
                'description': 'Health check'
            },
            'info': {
                'method': 'GET',
                'endpoint': '/info',
                'description': 'Get API and model information'
            },
            'score_single': {
                'method': 'POST',
                'endpoint': '/score',
                'description': 'Score a single transaction',
                'example_request': {
                    'selling_price': 450.0,
                    'quantity_ordered': 2,
                    'note': 'Include all 49 required features'
                }
            },
            'score_batch': {
                'method': 'POST',
                'endpoint': '/score-batch',
                'description': 'Score multiple transactions',
                'example_request': {
                    'transactions': [
                        {'selling_price': 450.0, 'quantity_ordered': 2},
                        {'selling_price': 250.0, 'quantity_ordered': 1}
                    ]
                }
            },
            'stats': {
                'method': 'GET',
                'endpoint': '/stats',
                'description': 'Get model statistics'
            },
            'report': {
                'method': 'POST',
                'endpoint': '/report',
                'description': 'Generate risk analysis report'
            }
        },
        'documentation': 'See DEPLOYMENT_GUIDE.md for detailed API documentation'
    }), 200


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting Fraud Detection API...")
    logger.info("API Documentation available at http://localhost:5000/")
    
    # Development
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
    
    # Production (uncomment and use with Gunicorn):
    # gunicorn -w 4 -b 0.0.0.0:5000 fraud_scoring_service_api:app
