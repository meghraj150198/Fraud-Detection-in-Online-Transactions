"""
Fraud Detection API Client Examples
====================================
Usage examples for integrating with the fraud detection service
"""

import requests
import pandas as pd
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Base URL (update for your deployment)
API_BASE_URL = 'http://localhost:5000'

# ============================================================================
# EXAMPLE 1: Health Check
# ============================================================================

def check_api_health():
    """Verify API is running and healthy"""
    try:
        response = requests.get(f'{API_BASE_URL}/health')
        if response.status_code == 200:
            logger.info("✓ API is healthy")
            print(json.dumps(response.json(), indent=2))
        else:
            logger.error(f"✗ API health check failed: {response.status_code}")
    except Exception as e:
        logger.error(f"✗ Cannot reach API: {e}")


# ============================================================================
# EXAMPLE 2: Score Single Transaction
# ============================================================================

def score_single_transaction(transaction_data):
    """
    Score a single transaction
    
    Args:
        transaction_data: Dictionary with transaction features
    
    Returns:
        Fraud risk prediction with probability scores
    """
    try:
        response = requests.post(
            f'{API_BASE_URL}/score',
            json=transaction_data,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "="*60)
            print("SINGLE TRANSACTION FRAUD RISK ASSESSMENT")
            print("="*60)
            print(f"\nRisk Level: {result['prediction']['risk_level']}")
            print(f"Risk Score: {result['prediction']['risk_score']:.2f}/100")
            print(f"Confidence: {result['prediction']['confidence']:.2f}%")
            print(f"Flagged: {'Yes' if result['prediction']['is_flagged'] else 'No'}")
            
            print("\nClass Probabilities:")
            for cls, prob in result['prediction']['class_probabilities'].items():
                print(f"  • {cls.capitalize():10s}: {prob:.2f}%")
            
            return result
        else:
            logger.error(f"Scoring failed: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error scoring transaction: {e}")
        return None


# ============================================================================
# EXAMPLE 3: Batch Score Transactions
# ============================================================================

def score_batch_transactions(df):
    """
    Score multiple transactions in batch
    
    Args:
        df: DataFrame with transaction features
    
    Returns:
        DataFrame with fraud predictions
    """
    try:
        # Convert DataFrame to list of dicts
        transactions_list = df.to_dict(orient='records')
        
        response = requests.post(
            f'{API_BASE_URL}/score-batch',
            json={'transactions': transactions_list},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "="*60)
            print("BATCH FRAUD DETECTION RESULTS")
            print("="*60)
            print(f"\nTotal Transactions: {result['total_scored']:,}")
            print(f"Fraud Flagged: {result['fraud_flagged']} ({result['fraud_flag_rate']:.2f}%)")
            print(f"Average Risk Score: {result['average_risk_score']:.2f}/100")
            
            print("\nRisk Distribution:")
            results_df = pd.DataFrame(result['results'])
            print(results_df['predicted_risk_level'].value_counts().to_string())
            
            return pd.DataFrame(result['results'])
        else:
            logger.error(f"Batch scoring failed: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error batch scoring: {e}")
        return None


# ============================================================================
# EXAMPLE 4: Generate Risk Report
# ============================================================================

def generate_risk_report(df):
    """
    Generate comprehensive fraud analysis report
    
    Args:
        df: DataFrame with transaction features
    
    Returns:
        Dictionary with analysis report
    """
    try:
        transactions_list = df.to_dict(orient='records')
        
        response = requests.post(
            f'{API_BASE_URL}/report',
            json={'transactions': transactions_list},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()['report']
            
            print("\n" + "="*60)
            print("FRAUD RISK ANALYSIS REPORT")
            print("="*60)
            
            print(f"\nTransaction Summary:")
            print(f"  • Total: {result['total_transactions']:,}")
            print(f"  • Fraud Flagged: {result['fraud_flagged']} ({result['fraud_flag_rate']})")
            print(f"  • High Risk: {result['high_risk_transactions']}")
            
            print(f"\nRisk Distribution:")
            for risk_level, count in result['risk_distribution'].items():
                print(f"  • {risk_level:10s}: {count:6,}")
            
            print(f"\nRisk Score Percentiles:")
            for pct, score in result['percentile_risk_scores'].items():
                print(f"  • {pct:3s}: {score:6.2f}")
            
            return result
        else:
            logger.error(f"Report generation failed: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return None


# ============================================================================
# EXAMPLE 5: Integration with Real-time System
# ============================================================================

class FraudDetectionClient:
    """
    Production client for fraud detection API integration
    
    Usage:
        client = FraudDetectionClient('http://localhost:5000')
        
        # Score transaction
        result = client.score(transaction_dict)
        
        if result['prediction']['is_flagged']:
            # Handle fraud case
            send_alert(transaction_dict)
        else:
            # Process normally
            process_transaction(transaction_dict)
    """
    
    def __init__(self, api_url, timeout=5):
        self.api_url = api_url
        self.timeout = timeout
        self.stats = {
            'total_scored': 0,
            'fraud_detected': 0,
            'errors': 0
        }
    
    def score(self, transaction_dict):
        """Score a single transaction with retry logic"""
        try:
            response = requests.post(
                f'{self.api_url}/score',
                json=transaction_dict,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                self.stats['total_scored'] += 1
                result = response.json()
                
                if result['prediction']['is_flagged']:
                    self.stats['fraud_detected'] += 1
                
                return result['prediction']
            else:
                self.stats['errors'] += 1
                logger.warning(f"API error: {response.status_code}")
                # Graceful degradation: flag for manual review
                return {'risk_level': 'Medium', 'error': True}
        
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Scoring error: {e}")
            # Graceful degradation
            return {'risk_level': 'Medium', 'error': True}
    
    def score_batch(self, transactions_list):
        """Score multiple transactions"""
        try:
            response = requests.post(
                f'{self.api_url}/score-batch',
                json={'transactions': transactions_list},
                timeout=self.timeout * len(transactions_list)
            )
            
            if response.status_code == 200:
                result = response.json()
                self.stats['total_scored'] += result['total_scored']
                self.stats['fraud_detected'] += result['fraud_flagged']
                return pd.DataFrame(result['results'])
            else:
                self.stats['errors'] += 1
                logger.warning(f"Batch API error: {response.status_code}")
                return None
        
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Batch scoring error: {e}")
            return None
    
    def get_stats(self):
        """Get API client statistics"""
        return {
            **self.stats,
            'fraud_detection_rate': f"{(self.stats['fraud_detected']/max(self.stats['total_scored'],1)*100):.2f}%"
        }


# ============================================================================
# EXAMPLE 6: Decision Logic Integration
# ============================================================================

def apply_business_rules(fraud_prediction):
    """
    Apply business rules based on fraud prediction
    
    Args:
        fraud_prediction: Output from score() or score_single_transaction()
    
    Returns:
        Decision tuple: (action, reason, risk_level)
    """
    
    risk_level = fraud_prediction['risk_level']
    risk_score = fraud_prediction['risk_score']
    confidence = fraud_prediction['confidence']
    
    # Decision logic
    if risk_level == 'High':
        if confidence > 90:
            return ('block', 'High confidence fraud detected', risk_level)
        else:
            return ('manual_review', 'High risk with moderate confidence', risk_level)
    
    elif risk_level == 'Medium':
        if risk_score > 70:
            return ('require_verification', 'Medium-high risk - require OTP', risk_level)
        else:
            return ('monitor', 'Medium risk - allow with monitoring', risk_level)
    
    else:  # Low risk
        if confidence > 95:
            return ('approve', 'Low risk with high confidence', risk_level)
        else:
            return ('monitor', 'Low risk with moderate confidence', risk_level)


# ============================================================================
# MAIN: DEMONSTRATION
# ============================================================================

if __name__ == '__main__':
    
    print("\n" + "="*60)
    print("FRAUD DETECTION API CLIENT - EXAMPLES")
    print("="*60)
    
    # 1. Health check
    print("\n[1] Health Check")
    print("   " + "-"*56)
    check_api_health()
    
    # 2. Score single transaction
    print("\n[2] Score Single Transaction")
    print("   " + "-"*56)
    single_tx = {
        'selling_price': 450.0,
        'quantity_ordered': 2,
        'velocity_spike': 0,
        'unusual_amount_flag': 0,
        # ... add all 49 required features
    }
    result = score_single_transaction(single_tx)
    
    # 3. Batch scoring
    print("\n[3] Batch Score Transactions")
    print("   " + "-"*56)
    try:
        batch_df = pd.read_csv('sales_with_fraud_indicators.csv').head(50)
        results_df = score_batch_transactions(batch_df)
    except:
        print("(Batch data not available for this example)")
    
    # 4. Generate report
    print("\n[4] Generate Risk Report")
    print("   " + "-"*56)
    try:
        generate_risk_report(batch_df)
    except:
        print("(Report generation example skipped)")
    
    # 5. Client integration example
    print("\n[5] Production Client Integration")
    print("   " + "-"*56)
    client = FraudDetectionClient(API_BASE_URL)
    print(f"   Initialized fraud detection client")
    print(f"   Client stats: {client.get_stats()}")
    
    print("\n" + "="*60)
    print("EXAMPLES COMPLETE")
    print("="*60)
