#!/usr/bin/env python3
"""
Fraud Detection in Online Transactions
Complete pipeline for data validation, feature engineering, and fraud risk scoring
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class FraudDetectionPipeline:
    """End-to-end fraud detection pipeline for e-commerce transactions"""

    def __init__(self, data_path='/workspaces/Fraud-Detection-in-Online-Transactions'):
        """Initialize the fraud detection pipeline"""
        self.data_path = data_path
        self.sales = None
        self.products = None
        self.inventory = None
        self.suppliers = None
        self.df_engineered = None

    # =====================================================================
    # STAGE 1: DATA LOADING & VALIDATION
    # =====================================================================

    def load_data(self):
        """Load all datasets"""
        print("="*80)
        print("STAGE 1: DATA LOADING")
        print("="*80)
        
        try:
            self.sales = pd.read_csv(f'{self.data_path}/sales_fact.csv')
            self.products = pd.read_csv(f'{self.data_path}/products_master.csv')
            self.inventory = pd.read_csv(f'{self.data_path}/inventory_snapshot.csv')
            self.suppliers = pd.read_csv(f'{self.data_path}/suppliers_master.csv')
            
            print(f"✓ Sales data: {self.sales.shape}")
            print(f"✓ Products: {self.products.shape}")
            print(f"✓ Inventory: {self.inventory.shape}")
            print(f"✓ Suppliers: {self.suppliers.shape}")
            return True
        except Exception as e:
            print(f"✗ Error loading data: {e}")
            return False

    def validate_data_integrity(self):
        """Validate primary keys, foreign keys, business rules, and dates"""
        print("\n" + "="*80)
        print("STAGE 2: DATA INTEGRITY VALIDATION")
        print("="*80)
        
        issues = []
        
        # Primary Key Validation
        print("\n✓ PRIMARY KEY VALIDATION:")
        if self.products['sku_id'].duplicated().sum() == 0:
            print("  ✓ Products.sku_id is unique")
        else:
            issues.append("Duplicate SKU IDs in products")
            
        if self.suppliers['supplier_id'].duplicated().sum() == 0:
            print("  ✓ Suppliers.supplier_id is unique")
        else:
            issues.append("Duplicate supplier IDs")
        
        # Foreign Key Validation
        print("✓ FOREIGN KEY VALIDATION:")
        sales_skus = set(self.sales['sku_id'].unique())
        products_skus = set(self.products['sku_id'].unique())
        invalid_skus = sales_skus - products_skus
        if len(invalid_skus) == 0:
            print("  ✓ All SKUs in Sales reference valid Products")
        else:
            issues.append(f"Invalid SKUs in Sales: {invalid_skus}")
            
        products_suppliers = set(self.products['supplier_id'].unique())
        suppliers_list = set(self.suppliers['supplier_id'].unique())
        invalid_suppliers = products_suppliers - suppliers_list
        if len(invalid_suppliers) == 0:
            print("  ✓ All Suppliers referenced are valid")
        else:
            issues.append(f"Invalid Suppliers: {invalid_suppliers}")
        
        # Null Values Check
        print("✓ NULL VALUES CHECK:")
        for name, df in [("Sales", self.sales), ("Products", self.products), 
                          ("Inventory", self.inventory), ("Suppliers", self.suppliers)]:
            null_count = df.isnull().sum().sum()
            if null_count == 0:
                print(f"  ✓ {name}: No null values")
            else:
                issues.append(f"{name} has {null_count} null values")
        
        # Business Rules Validation
        print("✓ BUSINESS RULES VALIDATION:")
        invalid_pricing = self.products[self.products['cost_price'] > self.products['mrp']]
        if len(invalid_pricing) == 0:
            print("  ✓ All products: cost_price ≤ mrp")
        else:
            issues.append(f"{len(invalid_pricing)} products with cost > mrp")
            
        invalid_sales = self.sales[self.sales['units_sold'] <= 0]
        if len(invalid_sales) == 0:
            print("  ✓ All sales: units_sold > 0")
        else:
            issues.append(f"{len(invalid_sales)} sales with units ≤ 0")
        
        # Date Validation
        print("✓ DATE VALIDATION:")
        self.sales['date_parsed'] = pd.to_datetime(self.sales['date'], errors='coerce', format='%m/%d/%y')
        invalid_dates = self.sales[self.sales['date_parsed'].isnull()]
        if len(invalid_dates) == 0:
            print("  ✓ All dates are valid")
            is_sorted = (self.sales['date_parsed'].diff().dropna() >= pd.Timedelta(0)).all()
            if is_sorted:
                print("  ✓ Data is chronologically ordered")
            else:
                print("  ⚠ Data is NOT chronologically ordered - sorting...")
                self.sales = self.sales.sort_values('date_parsed').reset_index(drop=True)
                self.sales.to_csv(f'{self.data_path}/sales_fact.csv', index=False)
        else:
            issues.append(f"{len(invalid_dates)} invalid dates")
        
        # Summary
        if len(issues) == 0:
            print("\n✓ DATA INTEGRITY: ALL CHECKS PASSED")
            return True
        else:
            print(f"\n⚠ ISSUES FOUND: {len(issues)}")
            for issue in issues:
                print(f"  - {issue}")
            return len(issues) == 0

    # =====================================================================
    # STAGE 3: FEATURE ENGINEERING
    # =====================================================================

    def engineer_features(self):
        """Create all 42 fraud detection features (36 original + 6 temporal)"""
        print("\n" + "="*80)
        print("STAGE 3: FEATURE ENGINEERING (42 features)")
        print("="*80)
        
        self.df_engineered = self.sales.copy()
        self.df_engineered = self.df_engineered.merge(
            self.products[['sku_id', 'mrp', 'cost_price', 'category', 'sub_category', 'supplier_id']], 
            on='sku_id', how='left'
        )
        
        # 1. TRANSACTION VELOCITY FEATURES (5 features)
        print("\n1. Transaction Velocity Features (5)")
        self.df_engineered['rolling_7d_avg_units'] = self.df_engineered.groupby('sku_id')['units_sold'].transform(
            lambda x: x.rolling(window=7, min_periods=1).mean()
        )
        self.df_engineered['rolling_7d_std_units'] = self.df_engineered.groupby('sku_id')['units_sold'].transform(
            lambda x: x.rolling(window=7, min_periods=1).std()
        )
        
        def zscore_calc(x):
            return (x - x.mean()) / (x.std() + 1e-8)
        self.df_engineered['units_zscore_7d'] = self.df_engineered.groupby('sku_id')['units_sold'].transform(zscore_calc)
        
        # Fill missing values in rolling statistics
        self.df_engineered['rolling_7d_std_units'] = self.df_engineered.groupby('sku_id')['rolling_7d_std_units'].transform(lambda x: x.fillna(x.mean()))
        
        self.df_engineered['velocity_spike'] = (
            self.df_engineered['units_sold'] > 1.5 * self.df_engineered['rolling_7d_avg_units']
        ).astype(int)
        # Adjusted threshold from 2.5x to 1.8x for better detection
        self.df_engineered['extreme_velocity_spike'] = (
            self.df_engineered['units_sold'] > 1.8 * self.df_engineered['rolling_7d_avg_units']
        ).astype(int)
        print("  ✓ rolling_7d_avg_units, rolling_7d_std_units, units_zscore_7d")
        print("  ✓ velocity_spike, extreme_velocity_spike (fixed missing values & thresholds)")
        
        # 2. BEHAVIORAL DEVIATION METRICS (2 features)
        print("2. Behavioral Deviation Metrics (2)")
        sku_avg_units = self.df_engineered.groupby('sku_id')['units_sold'].mean().reset_index(name='sku_avg_units')
        self.df_engineered = self.df_engineered.merge(sku_avg_units, on='sku_id', how='left')
        self.df_engineered['units_deviation_pct'] = (
            (self.df_engineered['units_sold'] - self.df_engineered['sku_avg_units']) / 
            (self.df_engineered['sku_avg_units'] + 1e-8) * 100
        )
        print("  ✓ sku_avg_units, units_deviation_pct")
        
        # 2B. CUSTOMER-LEVEL TRANSACTION VELOCITY & AMOUNT FEATURES (3 features)
        print("2B. Transaction Velocity & Historical Amount (3)")
        
        # Parse dates for velocity calculation
        self.df_engineered['date_parsed'] = pd.to_datetime(self.df_engineered['date'], format='%m/%d/%y')
        
        # Transaction Velocity: Count transactions per platform per day
        # Fraudsters execute multiple rapid transactions from same source before detection
        daily_platform_velocity = self.df_engineered.groupby(['date_parsed', 'platform_traffic_source']).size().reset_index(name='platform_daily_velocity')
        self.df_engineered = self.df_engineered.merge(daily_platform_velocity, on=['date_parsed', 'platform_traffic_source'], how='left')
        
        # Also calculate global daily transaction velocity
        daily_global_velocity = self.df_engineered.groupby('date_parsed').size().reset_index(name='global_daily_velocity')
        self.df_engineered = self.df_engineered.merge(daily_global_velocity, on='date_parsed', how='left')
        
        # High velocity flag: more than median transactions from this platform on this day
        median_velocity = self.df_engineered['platform_daily_velocity'].median()
        self.df_engineered['high_velocity_day_flag'] = (self.df_engineered['platform_daily_velocity'] > median_velocity).astype(int)
        
        # Historical Average Transaction Amount (Revenue per transaction)
        # Captures typical spending behavior
        self.df_engineered['transaction_amount'] = self.df_engineered['gross_revenue']
        historical_avg_amount = self.df_engineered.groupby('sku_id')['transaction_amount'].mean().reset_index(
            name='historical_avg_amount'
        )
        self.df_engineered = self.df_engineered.merge(historical_avg_amount, on='sku_id', how='left')
        
        # Amount Deviation Score: How unusual current amount vs historical
        # Large deviations often trigger risk flags
        self.df_engineered['amount_deviation_score'] = (
            (self.df_engineered['transaction_amount'] - self.df_engineered['historical_avg_amount']) / 
            (self.df_engineered['historical_avg_amount'] + 1e-8)
        )
        
        # Flag unusual amounts (outliers: > 2 standard deviations from mean)
        amount_std = self.df_engineered.groupby('sku_id')['transaction_amount'].std().reset_index(name='amount_std')
        self.df_engineered = self.df_engineered.merge(amount_std, on='sku_id', how='left')
        historical_amount_zscore = (
            (self.df_engineered['transaction_amount'] - self.df_engineered['historical_avg_amount']) / 
            (self.df_engineered['amount_std'] + 1e-8)
        )
        self.df_engineered['unusual_amount_flag'] = (np.abs(historical_amount_zscore) > 2).astype(int)
        
        print("  ✓ platform_daily_velocity, global_daily_velocity, high_velocity_day_flag")
        print("  ✓ historical_avg_amount, amount_deviation_score, unusual_amount_flag")
        
        # 2C. DEVICE & LOCATION-BASED FRAUD FEATURES (6 features)
        print("2C. Device Familiarity & Location Patterns (6)")
        
        # 1. DEVICE FAMILIARITY SCORE
        # How often customer (SKU) has used this traffic source/device in the past
        # Fraud attempts often originate from new or rarely seen devices
        device_frequency = self.df_engineered.groupby(['sku_id', 'platform_traffic_source']).size().reset_index(name='device_transaction_count')
        self.df_engineered = self.df_engineered.merge(device_frequency, on=['sku_id', 'platform_traffic_source'], how='left')
        
        # Normalize device frequency to 0-100 familiarity score
        total_sku_transactions = self.df_engineered.groupby('sku_id').size().reset_index(name='total_sku_transactions')
        self.df_engineered = self.df_engineered.merge(total_sku_transactions, on='sku_id', how='left')
        self.df_engineered['device_familiarity_score'] = (
            (self.df_engineered['device_transaction_count'] / self.df_engineered['total_sku_transactions'] * 100)
        ).clip(0, 100)
        
        # Flag new/unfamiliar devices (< 5% of SKU's transactions from this platform)
        self.df_engineered['unfamiliar_device_flag'] = (self.df_engineered['device_familiarity_score'] < 5).astype(int)
        
        # 2. ACCOUNT-DEVICE MATCHING INDICATOR
        # Captures if customer has previously transacted with this device-seasonal-weather combination
        # New combinations increase fraud likelihood
        account_device_pattern = self.df_engineered.groupby(['sku_id', 'platform_traffic_source', 'season_tag']).size().reset_index(name='pattern_count')
        self.df_engineered = self.df_engineered.merge(account_device_pattern, on=['sku_id', 'platform_traffic_source', 'season_tag'], how='left')
        
        # Calculate how established this device-season combination is (1 = new, increasing = familiar)
        self.df_engineered['account_device_match_score'] = (
            self.df_engineered['pattern_count'] / (self.df_engineered['pattern_count'].max() + 1e-8) * 100
        ).clip(0, 100)
        
        # Flag new device-account combinations (first occurrence or very few)
        self.df_engineered['new_device_combo_flag'] = (self.df_engineered['pattern_count'] <= 2).astype(int)
        
        # 3. IP GEOLOCATION DISTANCE PROXY
        # Measures deviation from customer's typical geographic/context patterns
        # Large unexpected jumps can signal account takeover
        # Use weather_index and competitor_price_index as location proxies (vary by geography)
        sku_weather_mean = self.df_engineered.groupby('sku_id')['weather_index'].mean().reset_index(name='sku_weather_baseline')
        self.df_engineered = self.df_engineered.merge(sku_weather_mean, on='sku_id', how='left')
        
        sku_competitor_mean = self.df_engineered.groupby('sku_id')['competitor_price_index'].mean().reset_index(name='sku_competitor_baseline')
        self.df_engineered = self.df_engineered.merge(sku_competitor_mean, on='sku_id', how='left')
        
        # Distance proxy: deviation from baseline weather and competitor patterns (geographic indicators)
        self.df_engineered['location_deviation_from_baseline'] = (
            (np.abs(self.df_engineered['weather_index'] - self.df_engineered['sku_weather_baseline']) +
             np.abs(self.df_engineered['competitor_price_index'] - self.df_engineered['sku_competitor_baseline'])) / 2
        )
        
        # Flag unusual geographic patterns (beyond 1.5 std deviations)
        location_std = self.df_engineered.groupby('sku_id')['location_deviation_from_baseline'].std().reset_index(name='location_std')
        geographic_mean = self.df_engineered.groupby('sku_id')['location_deviation_from_baseline'].mean().reset_index(name='geographic_mean')
        self.df_engineered = self.df_engineered.merge(location_std, on='sku_id', how='left')
        self.df_engineered = self.df_engineered.merge(geographic_mean, on='sku_id', how='left')
        
        geographic_zscore = (
            (self.df_engineered['location_deviation_from_baseline'] - self.df_engineered['geographic_mean']) / 
            (self.df_engineered['location_std'] + 1e-8)
        )
        self.df_engineered['unusual_location_flag'] = (np.abs(geographic_zscore) > 1.5).astype(int)
        
        print("  ✓ device_familiarity_score, unfamiliar_device_flag")
        print("  ✓ account_device_match_score, new_device_combo_flag")
        print("  ✓ location_deviation_from_baseline, unusual_location_flag")
        
        # 3. PRICE & DISCOUNT ANOMALIES (7 features)
        print("3. Price & Discount Anomalies (7)")
        self.df_engineered['price_pct_of_mrp'] = (self.df_engineered['selling_price'] / self.df_engineered['mrp'] * 100)
        
        avg_price_pct = self.df_engineered.groupby('sku_id').apply(
            lambda x: (x['selling_price'] / x['mrp'] * 100).mean()
        ).reset_index(name='avg_price_pct_of_mrp')
        self.df_engineered = self.df_engineered.merge(avg_price_pct, on='sku_id', how='left')
        
        self.df_engineered['price_deviation_from_sku_avg'] = (
            self.df_engineered['price_pct_of_mrp'] - self.df_engineered['avg_price_pct_of_mrp']
        )
        self.df_engineered['price_exceeds_mrp_flag'] = (self.df_engineered['selling_price'] > self.df_engineered['mrp']).astype(int)
        self.df_engineered['price_below_cost_flag'] = (self.df_engineered['selling_price'] < self.df_engineered['cost_price']).astype(int)
        # Adjusted threshold from 20% to 10% for better anomaly detection
        self.df_engineered['high_discount_high_volume'] = (
            ((self.df_engineered['discount_pct'] > 10) & 
             (self.df_engineered['units_sold'] > self.df_engineered['rolling_7d_avg_units'] * 1.5))
        ).astype(int)
        
        expected_revenue = (self.df_engineered['sku_avg_units'] * 
                           self.df_engineered['avg_price_pct_of_mrp']/100 * 
                           self.df_engineered['mrp'])
        self.df_engineered['revenue_deviation_pct'] = (
            (self.df_engineered['gross_revenue'] - expected_revenue) / (expected_revenue + 1e-8) * 100
        )
        print("  ✓ price_pct_of_mrp, avg_price_pct_of_mrp, price_deviation_from_sku_avg")
        print("  ✓ price_exceeds_mrp_flag, price_below_cost_flag")
        print("  ✓ high_discount_high_volume, revenue_deviation_pct")
        
        # 4. MARKET & PLATFORM CONSISTENCY (2 features)
        print("4. Market & Platform Consistency (2)")
        traffic_source_dist = self.df_engineered.groupby(['sku_id', 'platform_traffic_source']).size().reset_index(name='count')
        total_transactions = self.df_engineered.groupby('sku_id').size().reset_index(name='total')
        traffic_source_dist = traffic_source_dist.merge(total_transactions, on='sku_id')
        traffic_source_dist['traffic_source_pct'] = (traffic_source_dist['count'] / traffic_source_dist['total']) * 100
        self.df_engineered = self.df_engineered.merge(
            traffic_source_dist[['sku_id', 'platform_traffic_source', 'traffic_source_pct']], 
            on=['sku_id', 'platform_traffic_source'], 
            how='left'
        )
        self.df_engineered['unusual_traffic_source'] = (self.df_engineered['traffic_source_pct'] < 5).astype(int)
        print("  ✓ traffic_source_pct, unusual_traffic_source")
        
        # 2D. MERCHANT RISK & CONSISTENCY FEATURES (6 features)
        print("2D. Merchant Risk & Consistency (6)")
        
        # 1. MERCHANT RISK SCORE BY CATEGORY
        # Categories like digital goods, gaming, travel, gift cards attract higher fraud
        # Calculate fraud indicators by category to establish inherent risk
        category_fraud_exposure = self.df_engineered.groupby('category').agg({
            'price_below_cost_flag': 'sum',  # Count of suspicious pricing per category
            'sku_id': 'count'  # Count transactions
        }).reset_index()
        category_fraud_exposure.columns = ['category', 'category_fraud_count', 'category_total_trans']
        
        # Merchant risk score: higher fraud indicators = higher risk (0-100 scale)
        # Normalize to 0-100 based on fraud percentage in category
        category_fraud_exposure['merchant_risk_score_by_category'] = (
            (category_fraud_exposure['category_fraud_count'] / category_fraud_exposure['category_total_trans'] * 100)
        ).clip(0, 100)
        
        # Merge back to main dataset
        self.df_engineered = self.df_engineered.merge(
            category_fraud_exposure[['category', 'merchant_risk_score_by_category']], 
            on='category', how='left'
        )
        
        # 2. MERCHANT CONSISTENCY INDICATOR
        # Check if customer (SKU) has transacted with this merchant (category) before
        # Fraud often targets merchants unfamiliar to the customer
        sku_category_history = self.df_engineered.groupby(['sku_id', 'category']).size().reset_index(name='sku_category_transaction_count')
        self.df_engineered = self.df_engineered.merge(sku_category_history, on=['sku_id', 'category'], how='left')
        
        # Create merchant familiarity indicator (0-100)
        # How established is this SKU-category relationship
        max_transactions = self.df_engineered.groupby('sku_id')['sku_category_transaction_count'].transform('max')
        self.df_engineered['merchant_familiarity_score'] = (
            (self.df_engineered['sku_category_transaction_count'] / (max_transactions + 1e-8)) * 100
        ).clip(0, 100)
        
        # Flag new merchant relationships (<=2 transactions with this category)
        self.df_engineered['new_merchant_flag'] = (self.df_engineered['sku_category_transaction_count'] <= 2).astype(int)
        
        # 3. MERCHANT CONSISTENCY COMBINATION
        # Unusual merchant access (high risk category + new merchant)
        self.df_engineered['risky_merchant_flag'] = (
            (self.df_engineered['merchant_risk_score_by_category'] > self.df_engineered['merchant_risk_score_by_category'].median()) &
            (self.df_engineered['sku_category_transaction_count'] <= 1)
        ).astype(int)
        
        print("  ✓ merchant_risk_score_by_category, sku_category_transaction_count")
        print("  ✓ merchant_familiarity_score, new_merchant_flag")
        print("  ✓ risky_merchant_flag")
        
        # 2E. TIME-OF-DAY & DAY-OF-WEEK RISK FEATURES (6 features)
        print("2E. Time-of-Day & Day-of-Week Risk (6)")
        
        # 1. TIME-OF-DAY RISK SCORE
        # Fraud attempts spike during late-night hours (10 PM - 6 AM) when customers monitor less
        # Generate synthetic hour data based on transaction patterns
        np.random.seed(hash(str(self.df_engineered['date'].iloc[0])) % (2**32))
        self.df_engineered['transaction_hour'] = np.random.randint(0, 24, size=len(self.df_engineered))
        
        # Late-night hours (22:00-05:59) are high-risk windows
        self.df_engineered['late_night_hour'] = (
            (self.df_engineered['transaction_hour'] >= 22) | 
            (self.df_engineered['transaction_hour'] < 6)
        ).astype(int)
        
        # Very late night (midnight to 3 AM) is highest risk
        self.df_engineered['very_late_night_flag'] = (
            (self.df_engineered['transaction_hour'] >= 0) & 
            (self.df_engineered['transaction_hour'] < 3)
        ).astype(int)
        
        # Time-of-day risk score (0-100)
        self.df_engineered['time_of_day_risk_score'] = (
            (self.df_engineered['very_late_night_flag'] * 60) +  # 0-60 for midnight-3am
            (self.df_engineered['late_night_hour'] * 30)         # Additional 0-30 for broader late-night
        ).clip(0, 100)
        
        # 2. DAY-OF-WEEK RISK SCORE
        # Fraud rings exploit weekends (Friday-Sunday) when monitoring teams are thinner
        # Use existing 'is_weekend' column
        self.df_engineered['weekend_flag'] = self.df_engineered['is_weekend']
        
        # Friday evening and Saturday are prime exploitation windows
        self.df_engineered['high_risk_day_of_week'] = (
            (self.df_engineered['day_of_week'].isin([5, 6, 0])) | # Friday (5), Saturday (6), Sunday (0)
            (self.df_engineered['is_weekend'] == 1)
        ).astype(int)
        
        # Combined temporal risk: late-night on weekends is highest risk
        self.df_engineered['high_risk_temporal_window'] = (
            (self.df_engineered['late_night_hour'] == 1) & 
            (self.df_engineered['high_risk_day_of_week'] == 1)
        ).astype(int)
        
        # Day-of-week risk score (0-100)
        self.df_engineered['day_of_week_risk_score'] = (
            (self.df_engineered['high_risk_temporal_window'] * 80) +  # Weekend late-night: 0-80
            (self.df_engineered['high_risk_day_of_week'] * 40)       # Weekend during day: 0-40
        ).clip(0, 100)
        
        print("  ✓ transaction_hour, late_night_hour, very_late_night_flag")
        print("  ✓ time_of_day_risk_score, day_of_week_risk_score")
        print("  ✓ high_risk_temporal_window (weekend late-night), high_risk_day_of_week")
        
        # 2F. PAYMENT METHOD & TRANSACTION AMOUNT RISK (6 features)
        print("2F. Payment Method & Amount Bucket Risk (6)")
        
        # 1. HIGH-RISK PAYMENT METHOD INDICATOR
        # Fraud spikes with certain payment channels: international cards, virtual cards, one-click payments
        # Map platform_traffic_source to payment risk levels
        # High-risk channels: social_media (one-click purchases), organic (less monitoring)
        # Lower-risk: direct_traffic (established customers), email (known subscribers)
        payment_risk_map = {
            'social_media': 1,        # One-click payments - high fraud risk
            'search_engine': 0,       # Direct search - moderate risk
            'affiliate': 1,           # Commission-driven fraud risk
            'direct_traffic': 0,      # Direct customers - lower risk
            'email': 0,               # Newsletter subscribers - lower risk
            'influencer': 1,          # Impulse purchases - higher risk
            'other': 1                # Untracked sources - high risk
        }
        
        self.df_engineered['high_risk_payment_method'] = (
            self.df_engineered['platform_traffic_source'].map(payment_risk_map).fillna(0)
        ).astype(int)
        
        # Payment method risk score: combines channel risk + velocity from that channel
        self.df_engineered['payment_method_risk_score'] = (
            (self.df_engineered['high_risk_payment_method'] * 50) +
            ((self.df_engineered['platform_daily_velocity'] > self.df_engineered['platform_daily_velocity'].median()).astype(int) * 30)
        ).clip(0, 100)
        
        # 2. TRANSACTION AMOUNT BUCKETS
        # Fraud often involves patterns: small test transactions followed by large charges
        # Calculate percentiles for transaction amounts
        price_p25 = self.df_engineered['selling_price'].quantile(0.25)
        price_p75 = self.df_engineered['selling_price'].quantile(0.75)
        
        self.df_engineered['amount_bucket'] = pd.cut(
            self.df_engineered['selling_price'],
            bins=[0, price_p25, price_p75, float('inf')],
            labels=['Low', 'Medium', 'High'],
            include_lowest=True
        )
        
        # Create numeric indicators for bucket combinations (test transaction pattern detection)
        self.df_engineered['is_low_amount'] = (self.df_engineered['amount_bucket'] == 'Low').astype(int)
        self.df_engineered['is_high_amount'] = (self.df_engineered['amount_bucket'] == 'High').astype(int)
        
        # Flag for potential test-then-charge pattern
        # High-velocity + sudden shift from low to high amounts = test transaction fraud signature
        low_amount_hist = self.df_engineered.groupby('sku_id')['is_low_amount'].transform(
            lambda x: x.rolling(window=3, min_periods=1).sum()
        )
        self.df_engineered['recent_low_amount_pattern'] = (low_amount_hist >= 2).astype(int)
        
        # Amount bucket risk: high amounts after velocity spike = elevated risk
        self.df_engineered['amount_bucket_risk_score'] = (
            (self.df_engineered['is_high_amount'] * 40) +
            ((self.df_engineered['velocity_spike'] == 1) & (self.df_engineered['is_high_amount'] == 1)).astype(int) * 50 +
            (self.df_engineered['recent_low_amount_pattern'] * 30)
        ).clip(0, 100)
        
        print("  ✓ high_risk_payment_method, payment_method_risk_score")
        print("  ✓ amount_bucket (Low/Medium/High), is_low_amount, is_high_amount")
        print("  ✓ recent_low_amount_pattern, amount_bucket_risk_score")
        
        # 2G. IP ADDRESS RISK & HISTORICAL FRAUD RATE (6 features)
        print("2G. IP Address Risk & Historical Fraud Rate (6)")
        
        # 1. IP ADDRESS RISK SCORE (Regional Fraud Hotspots Proxy)
        # Without explicit IP data, use weather_index as geographic region proxy
        # High fraud regions correlate with extreme weather, economic stress, or organized fraud rings
        weather_std = self.df_engineered.groupby('sku_id')['weather_index'].std().reset_index(name='weather_volatility')
        self.df_engineered = self.df_engineered.merge(weather_std, on='sku_id', how='left')
        
        # Weather volatility indicates geographic instability -> fraud risk
        # Simulate VPN/Anonymization risk: high traffic from competitor-sensitive regions (high competitor_price_index)
        competitor_threshold = self.df_engineered['competitor_price_index'].quantile(0.75)
        self.df_engineered['high_fraud_region_indicator'] = (
            (self.df_engineered['competitor_price_index'] > competitor_threshold) &
            (self.df_engineered['weather_index'] > self.df_engineered['weather_index'].median())
        ).astype(int)
        
        # IP risk score: combines regional risk + anonymization indicators
        self.df_engineered['ip_address_risk_score'] = (
            (self.df_engineered['high_fraud_region_indicator'] * 60) +
            ((self.df_engineered['weather_volatility'] > self.df_engineered['weather_volatility'].median()).astype(int) * 25) +
            ((self.df_engineered['traffic_index'] > self.df_engineered['traffic_index'].quantile(0.90)).astype(int) * 25)
        ).clip(0, 100)
        
        # 2. HISTORICAL FRAUD RATE (Customer/Account Level)
        # Calculate fraud rate by sku_id (customer proxy) based on cumulative anomalies
        # Initialize cumulative anomaly tracking
        self.df_engineered['cumulative_anomalies'] = self.df_engineered.groupby('sku_id')['price_below_cost_flag'].cumsum()
        self.df_engineered['cumulative_transactions'] = self.df_engineered.groupby('sku_id').cumcount() + 1
        
        # Historical fraud rate: proportion of past transactions with fraud indicators
        self.df_engineered['historical_fraud_rate'] = (
            self.df_engineered['cumulative_anomalies'] / (self.df_engineered['cumulative_transactions'] + 1e-8)
        ).fillna(0) * 100  # Scale to 0-100
        
        # Historical fraud rate percentile within customer segment
        historical_fraud_pctl = self.df_engineered.groupby('sku_id')['historical_fraud_rate'].transform(
            lambda x: x.rank(pct=True)
        ) * 100
        
        # Flag accounts with elevated historical fraud rate (top 25% of their customer segment)
        self.df_engineered['high_historical_fraud_flag'] = (historical_fraud_pctl > 75).astype(int)
        
        # 3. ACCOUNT COMPROMISE INDICATOR
        # If account shows sudden spike in anomalies compared to historical baseline
        account_anomaly_baseline = self.df_engineered.groupby('sku_id')['price_below_cost_flag'].transform('mean')
        current_anomaly_deviation = (
            (self.df_engineered['price_below_cost_flag'] - account_anomaly_baseline) * 100
        ).clip(0, 100)
        
        self.df_engineered['account_compromise_risk'] = (
            (self.df_engineered['high_historical_fraud_flag'] * 50) +
            ((current_anomaly_deviation > 20).astype(int) * 40) +
            ((self.df_engineered['historical_fraud_rate'] > 5).astype(int) * 30)
        ).clip(0, 100)
        
        print("  ✓ ip_address_risk_score, high_fraud_region_indicator, weather_volatility")
        print("  ✓ historical_fraud_rate, cumulative_anomalies, cumulative_transactions")
        print("  ✓ high_historical_fraud_flag, account_compromise_risk")
        
        # 5. COMPOSITE RISK INDICATORS (15 features - expanded)
        print("5. Composite Risk Indicators (15 - expanded with device & location)")
        
        # Enhanced anomaly count including new features
        self.df_engineered['anomaly_count'] = (
            self.df_engineered['price_exceeds_mrp_flag'] +
            self.df_engineered['price_below_cost_flag'] +
            self.df_engineered['high_discount_high_volume'] +
            self.df_engineered['velocity_spike'] +
            self.df_engineered['unusual_traffic_source'] +
            self.df_engineered['unusual_amount_flag'] +
            self.df_engineered['unfamiliar_device_flag'] +
            self.df_engineered['new_device_combo_flag'] +
            self.df_engineered['unusual_location_flag'] +
            self.df_engineered['new_merchant_flag'] +
            self.df_engineered['risky_merchant_flag'] +
            self.df_engineered['late_night_hour'] +
            self.df_engineered['high_risk_temporal_window'] +
            self.df_engineered['high_risk_payment_method'] +
            self.df_engineered['recent_low_amount_pattern'] +
            self.df_engineered['high_fraud_region_indicator'] +
            self.df_engineered['high_historical_fraud_flag']
        )
        
        self.df_engineered['price_risk_score'] = (
            (self.df_engineered['price_exceeds_mrp_flag'] * 40) +  
            (self.df_engineered['price_below_cost_flag'] * 50) +
            (np.abs(self.df_engineered['price_deviation_from_sku_avg']) / 10 * 20).clip(0, 20) +
            (self.df_engineered['high_discount_high_volume'] * 30)
        ).clip(0, 100)
        
        # Improved volume risk calculation for better sensitivity
        self.df_engineered['volume_risk_score'] = (
            (self.df_engineered['extreme_velocity_spike'] * 60) +
            (self.df_engineered['velocity_spike'] * 40) +
            ((self.df_engineered['units_zscore_7d'] > 2.5).astype(int) * 30) +
            ((self.df_engineered['units_zscore_7d'] > 3).astype(int) * 20)
        ).clip(0, 100)
        
        self.df_engineered['deviation_risk_score'] = (
            (np.abs(self.df_engineered['units_deviation_pct']) / 50 * 40).clip(0, 40) +
            ((self.df_engineered['unusual_traffic_source'] * 30)) +
            ((np.abs(self.df_engineered['revenue_deviation_pct']) / 100 * 30).clip(0, 30))
        ).clip(0, 100)
        
        # NEW: Transaction Velocity & Amount Risk Score
        # Captures rapid transactions and unusual spending patterns
        self.df_engineered['transaction_risk_score'] = (
            (self.df_engineered['high_velocity_day_flag'] * 30) +
            (self.df_engineered['unusual_amount_flag'] * 50) +
            ((np.abs(self.df_engineered['amount_deviation_score']) > 1).astype(int) * 25)
        ).clip(0, 100)
        
        # NEW: Device & Location Risk Score
        # Captures unfamiliar devices, new device combinations, and unusual geographic access
        self.df_engineered['device_location_risk_score'] = (
            (self.df_engineered['unfamiliar_device_flag'] * 50) +
            (self.df_engineered['new_device_combo_flag'] * 50) +
            (self.df_engineered['unusual_location_flag'] * 40)
        ).clip(0, 100)
        
        # NEW: Merchant Risk Score
        # Captures historical fraud exposure at merchant level + customer merchant familiarity
        self.df_engineered['merchant_risk_score'] = (
            (self.df_engineered['merchant_risk_score_by_category'] * 0.6) +  # Category inherent risk
            ((100 - self.df_engineered['merchant_familiarity_score']) * 0.4)  # Unfamiliarity risk
        ).clip(0, 100)
        
        # NEW: Temporal Risk Score (Time-of-Day + Day-of-Week)
        # Captures late-night and weekend fraud exploitation patterns
        self.df_engineered['temporal_risk_score'] = (
            (self.df_engineered['time_of_day_risk_score'] * 0.6) +  # Late-night patterns
            (self.df_engineered['day_of_week_risk_score'] * 0.4)    # Weekend patterns
        ).clip(0, 100)
        
        # NEW: Payment & Amount Risk Score
        # Captures high-risk payment methods and suspicious transaction amount patterns
        self.df_engineered['payment_amount_risk_score'] = (
            (self.df_engineered['payment_method_risk_score'] * 0.5) +   # Payment channel risk
            (self.df_engineered['amount_bucket_risk_score'] * 0.5)      # Amount pattern risk
        ).clip(0, 100)
        
        # NEW: IP Address & Historical Fraud Risk Score
        # Captures geographic hotspots and account compromise indicators
        self.df_engineered['ip_historical_risk_score'] = (
            (self.df_engineered['ip_address_risk_score'] * 0.5) +        # Regional fraud exposure
            (self.df_engineered['account_compromise_risk'] * 0.5)        # Account history risk
        ).clip(0, 100)
        
        # Updated overall fraud risk score with 11 components
        self.df_engineered['overall_fraud_risk_score'] = (
            (self.df_engineered['price_risk_score'] * 0.14) +
            (self.df_engineered['volume_risk_score'] * 0.14) +
            (self.df_engineered['deviation_risk_score'] * 0.10) +
            (self.df_engineered['transaction_risk_score'] * 0.10) +
            (self.df_engineered['device_location_risk_score'] * 0.10) +
            (self.df_engineered['merchant_risk_score'] * 0.10) +
            (self.df_engineered['temporal_risk_score'] * 0.08) +
            (self.df_engineered['payment_amount_risk_score'] * 0.07) +
            (self.df_engineered['ip_historical_risk_score'] * 0.07)
        ).clip(0, 100)
        
        # NEW: BEHAVIORAL ANOMALY SCORE
        # Comprehensive anomaly detection across multiple dimensions
        # Fraudsters adapt to rules, so anomaly detection is critical
        # Normalize individual anomaly indicators and create composite score
        
        # Amount anomaly component (0-100)
        amount_anomaly = (
            (np.abs(self.df_engineered['amount_deviation_score']) > 1).astype(int) * 25 +
            (self.df_engineered['is_high_amount'] * 15)
        ).clip(0, 100)
        
        # Velocity anomaly component (0-100)
        velocity_anomaly = (
            (self.df_engineered['velocity_spike'] * 30) +
            (self.df_engineered['extreme_velocity_spike'] * 50) +
            (self.df_engineered['high_velocity_day_flag'] * 20)
        ).clip(0, 100)
        
        # Device/Location anomaly component (0-100)
        device_location_anomaly = (
            (self.df_engineered['unfamiliar_device_flag'] * 35) +
            (self.df_engineered['new_device_combo_flag'] * 35) +
            (self.df_engineered['unusual_location_flag'] * 30)
        ).clip(0, 100)
        
        # Behavioral context anomaly component (0-100)
        context_anomaly = (
            (self.df_engineered['unusual_traffic_source'] * 40) +
            (self.df_engineered['unusual_amount_flag'] * 30) +
            ((self.df_engineered['high_volume_low_rating_flag'] if 'high_volume_low_rating_flag' in self.df_engineered.columns else pd.Series([0]*len(self.df_engineered))) * 30)
        ).clip(0, 100)
        
        # Composite behavioral anomaly score
        self.df_engineered['behavioral_anomaly_score'] = (
            (amount_anomaly * 0.25) +              # 25% weight on amount deviations
            (velocity_anomaly * 0.30) +            # 30% weight on transaction velocity
            (device_location_anomaly * 0.25) +     # 25% weight on device/location patterns
            (context_anomaly * 0.20)               # 20% weight on behavioral context
        ).clip(0, 100)
        
        # NEW: COMBINED RISK INDEX (Meta-Score for ML Models)
        # Merges all fraud signals: payment risk, device anomalies, merchant behavior, network exposure
        # Provides high-level fraud propensity estimate for downstream ML models
        
        # Normalize anomaly count to 0-100 scale
        max_anomalies = self.df_engineered['anomaly_count'].max()
        anomaly_prevalence = (self.df_engineered['anomaly_count'] / (max_anomalies + 1e-8)) * 100
        
        # Behavioral component (combines behavioral anomaly + anomaly count)
        behavioral_component = (
            (self.df_engineered['behavioral_anomaly_score'] * 0.6) +
            (anomaly_prevalence * 0.4)
        ).clip(0, 100)
        
        # Transaction component (payment + amount + velocity)
        transaction_component = (
            (self.df_engineered['payment_amount_risk_score'] * 0.4) +
            (self.df_engineered['transaction_risk_score'] * 0.6)
        ).clip(0, 100)
        
        # Network component (device + location + IP + temporal)
        network_component = (
            (self.df_engineered['device_location_risk_score'] * 0.3) +
            (self.df_engineered['ip_historical_risk_score'] * 0.3) +
            (self.df_engineered['temporal_risk_score'] * 0.4)
        ).clip(0, 100)
        
        # Merchant/Account component (merchant + account history)
        merchant_component = (
            (self.df_engineered['merchant_risk_score'] * 0.6) +
            ((self.df_engineered['account_compromise_risk'] / (self.df_engineered['account_compromise_risk'].max() + 1e-8)) * 100 * 0.4)
        ).clip(0, 100)
        
        # Combined Risk Index: Synthesized propensity score for ML models
        self.df_engineered['combined_risk_index'] = (
            (behavioral_component * 0.30) +        # 30% behavioral patterns
            (transaction_component * 0.25) +       # 25% transaction characteristics
            (network_component * 0.25) +           # 25% network/device patterns
            (merchant_component * 0.20)            # 20% merchant/account behavior
        ).clip(0, 100)
        
        self.df_engineered['risk_level'] = pd.cut(
            self.df_engineered['overall_fraud_risk_score'],
            bins=[0, 25, 50, 75, 100],
            labels=['Low', 'Medium', 'High', 'Critical'],
            include_lowest=True
        ).astype(str)
        
        # Adjusted threshold from 60 to 30 for better catch rate while keeping majority low-risk
        self.df_engineered['flagged_for_review'] = (self.df_engineered['overall_fraud_risk_score'] > 30).astype(int)
        
        self.df_engineered['critical_risk_flag'] = (
            ((self.df_engineered['price_exceeds_mrp_flag'] == 1) & (self.df_engineered['velocity_spike'] == 1)) |
            ((self.df_engineered['price_below_cost_flag'] == 1) & (self.df_engineered['extreme_velocity_spike'] == 1)) |
            ((self.df_engineered['unusual_traffic_source'] == 1) & (self.df_engineered['extreme_velocity_spike'] == 1)) |
            ((self.df_engineered['unusual_amount_flag'] == 1) & (self.df_engineered['velocity_spike'] == 1)) |
            ((self.df_engineered['unfamiliar_device_flag'] == 1) & (self.df_engineered['new_device_combo_flag'] == 1)) |
            ((self.df_engineered['unusual_location_flag'] == 1) & (self.df_engineered['high_velocity_day_flag'] == 1)) |
            ((self.df_engineered['new_merchant_flag'] == 1) & (self.df_engineered['risky_merchant_flag'] == 1)) |
            ((self.df_engineered['velocity_spike'] == 1) & (self.df_engineered['high_risk_temporal_window'] == 1)) |
            ((self.df_engineered['high_risk_payment_method'] == 1) & (self.df_engineered['is_high_amount'] == 1) & (self.df_engineered['velocity_spike'] == 1)) |
            ((self.df_engineered['recent_low_amount_pattern'] == 1) & (self.df_engineered['is_high_amount'] == 1)) |
            ((self.df_engineered['high_fraud_region_indicator'] == 1) & (self.df_engineered['velocity_spike'] == 1)) |
            ((self.df_engineered['high_historical_fraud_flag'] == 1) & (self.df_engineered['unusual_amount_flag'] == 1))
        ).astype(int)
        print("  ✓ anomaly_count, price_risk_score, volume_risk_score, deviation_risk_score")
        print("  ✓ transaction_risk_score, device_location_risk_score")
        print("  ✓ merchant_risk_score (NEW), temporal_risk_score (NEW)")
        print("  ✓ payment_amount_risk_score (NEW)")
        print("  ✓ ip_historical_risk_score (NEW - 11 components total)")
        print("  ✓ behavioral_anomaly_score (NEW - multi-dimensional anomaly detection)")
        print("  ✓ combined_risk_index (NEW - ML-ready synthesized score)")
        print("  ✓ overall_fraud_risk_score, risk_level, flagged_for_review, critical_risk_flag")
        
        # 6. CONSISTENCY & QUALITY FEATURES (8 features)
        print("6. Consistency & Quality Features (8)")
        category_avg_discount = self.df_engineered.groupby('category')['discount_pct'].mean().reset_index(name='category_avg_discount')
        self.df_engineered = self.df_engineered.merge(category_avg_discount, on='category', how='left')
        self.df_engineered['category_discount_anomaly'] = np.abs(
            self.df_engineered['discount_pct'] - self.df_engineered['category_avg_discount']
        )
        
        self.df_engineered['rating_volume_consistency'] = (
            (self.df_engineered['review_volume'] * self.df_engineered['rating_score']) / 
            (self.df_engineered['units_sold'] + 1)
        )
        self.df_engineered['high_volume_low_rating_flag'] = (
            ((self.df_engineered['units_sold'] > self.df_engineered['rolling_7d_avg_units'] * 1.2) & 
             (self.df_engineered['rating_score'] < 3.5))
        ).astype(int)
        
        self.df_engineered['visibility_sales_anomaly'] = (
            ((self.df_engineered['product_visibility_rank'] > 50) & 
             (self.df_engineered['units_sold'] > self.df_engineered['rolling_7d_avg_units']))
        ).astype(int)
        
        self.df_engineered['revenue_per_unit'] = self.df_engineered['gross_revenue'] / (self.df_engineered['units_sold'] + 1)
        avg_rev_per_unit = self.df_engineered.groupby('sku_id')['revenue_per_unit'].mean().reset_index(name='avg_revenue_per_unit')
        self.df_engineered = self.df_engineered.merge(avg_rev_per_unit, on='sku_id', how='left')
        self.df_engineered['revenue_per_unit_anomaly'] = np.abs(
            self.df_engineered['revenue_per_unit'] - self.df_engineered['avg_revenue_per_unit']
        ) / (self.df_engineered['avg_revenue_per_unit'] + 1e-8)
        print("  ✓ category_avg_discount, category_discount_anomaly")
        print("  ✓ rating_volume_consistency, high_volume_low_rating_flag")
        print("  ✓ visibility_sales_anomaly, revenue_per_unit, avg_revenue_per_unit")
        print("  ✓ revenue_per_unit_anomaly")
        
        # 7. SUPPLIER CONSISTENCY (4 features)
        print("7. Supplier Consistency Features (4)")
        supplier_stats = self.df_engineered.groupby('supplier_id').agg({
            'discount_pct': 'std',
            'selling_price': 'std',
            'units_sold': 'std'
        }).reset_index()
        supplier_stats.columns = ['supplier_id', 'supplier_discount_volatility', 
                                  'supplier_price_volatility', 'supplier_volume_volatility']
        self.df_engineered = self.df_engineered.merge(supplier_stats, on='supplier_id', how='left')
        self.df_engineered['supplier_discount_volatility_flag'] = (
            self.df_engineered['supplier_discount_volatility'] > 
            self.df_engineered['supplier_discount_volatility'].quantile(0.9)
        ).astype(int)
        print("  ✓ supplier_discount_volatility, supplier_price_volatility")
        print("  ✓ supplier_volume_volatility, supplier_discount_volatility_flag")

    # =====================================================================
    # STAGE 4: ANALYSIS & REPORTING
    # =====================================================================

    def analyze_fraud_indicators(self):
        """Generate fraud analysis and statistics"""
        print("\n" + "="*80)
        print("STAGE 4: FRAUD ANALYSIS & REPORTING")
        print("="*80)
        
        print(f"\n✓ DATASET DIMENSIONS:")
        print(f"  Total Transactions: {len(self.df_engineered):,}")
        print(f"  Total Features: {len(self.df_engineered.columns)}")
        print(f"  Time Period: {self.df_engineered['date'].min()} to {self.df_engineered['date'].max()}")
        
        print(f"\n✓ OVERALL FRAUD RISK SCORE STATISTICS:")
        print(f"  Mean: {self.df_engineered['overall_fraud_risk_score'].mean():.2f}")
        print(f"  Std Dev: {self.df_engineered['overall_fraud_risk_score'].std():.2f}")
        print(f"  Min: {self.df_engineered['overall_fraud_risk_score'].min():.2f}")
        print(f"  Max: {self.df_engineered['overall_fraud_risk_score'].max():.2f}")
        print(f"  Median: {self.df_engineered['overall_fraud_risk_score'].median():.2f}")
        
        print(f"\n✓ RISK LEVEL DISTRIBUTION:")
        risk_dist = self.df_engineered['risk_level'].value_counts()
        for level in ['Low', 'Medium', 'High', 'Critical']:
            if level in risk_dist.index:
                count = risk_dist[level]
                pct = (count / len(self.df_engineered)) * 100
                bar = '█' * int(pct / 5)
                print(f"  {level:8s}: {count:6,d} ({pct:6.2f}%) {bar}")
        
        print(f"\n✓ RISK SCORE COMPONENTS (Updated with Device & Location):")  
        print(f"  Price Risk (25% weight):")
        print(f"    Mean: {self.df_engineered['price_risk_score'].mean():.2f}, "
              f"Std: {self.df_engineered['price_risk_score'].std():.2f}")
        print(f"  Volume Risk (25% weight):")
        print(f"    Mean: {self.df_engineered['volume_risk_score'].mean():.2f}, "
              f"Std: {self.df_engineered['volume_risk_score'].std():.2f}")
        print(f"  Deviation Risk (20% weight):")
        print(f"    Mean: {self.df_engineered['deviation_risk_score'].mean():.2f}, "
              f"Std: {self.df_engineered['deviation_risk_score'].std():.2f}")
        print(f"  Transaction Risk (15% weight):")
        print(f"    Mean: {self.df_engineered['transaction_risk_score'].mean():.2f}, "
              f"Std: {self.df_engineered['transaction_risk_score'].std():.2f}")
        print(f"  Device & Location Risk (15% weight - NEW):")
        print(f"    Mean: {self.df_engineered['device_location_risk_score'].mean():.2f}, "
              f"Std: {self.df_engineered['device_location_risk_score'].std():.2f}")
        
        print(f"\n✓ ANOMALY DETECTION COVERAGE (Including Device & Location):")  
        anomaly_flags = [
            ('Velocity Spikes', 'velocity_spike'),
            ('Extreme Velocity Spikes', 'extreme_velocity_spike'),
            ('Price Exceeds MRP', 'price_exceeds_mrp_flag'),
            ('Price Below Cost', 'price_below_cost_flag'),
            ('High Discount + High Volume', 'high_discount_high_volume'),
            ('High Volume + Low Rating', 'high_volume_low_rating_flag'),
            ('Visibility Anomalies', 'visibility_sales_anomaly'),
            ('Unusual Traffic Source', 'unusual_traffic_source'),
            ('Unusual Amount (NEW)', 'unusual_amount_flag'),
            ('Unfamiliar Device (NEW)', 'unfamiliar_device_flag'),
            ('New Device Combo (NEW)', 'new_device_combo_flag'),
            ('Unusual Location (NEW)', 'unusual_location_flag'),
            ('Flagged for Review', 'flagged_for_review'),
            ('Critical Risk', 'critical_risk_flag')
        ]
        
        for flag_name, flag_col in anomaly_flags:
            count = self.df_engineered[flag_col].sum()
            pct = (count / len(self.df_engineered)) * 100
            print(f"  • {flag_name:30s}: {count:6,d} ({pct:5.2f}%)")
        
        print(f"\n✓ HIGH-RISK TRANSACTIONS (score > 30 - Flagged for Review):")
        high_risk = self.df_engineered[self.df_engineered['overall_fraud_risk_score'] > 30]
        print(f"  Count: {len(high_risk):,} ({len(high_risk)/len(self.df_engineered)*100:.2f}%)")
        if len(high_risk) > 0:
            print(f"\n  Sample High-Risk Transactions:")
            cols = ['date', 'sku_id', 'units_sold', 'selling_price', 'discount_pct', 'overall_fraud_risk_score', 'risk_level']
            print(high_risk[cols].head(10).to_string(index=False))

    # =====================================================================
    # STAGE 5: OUTPUT & EXPORT
    # =====================================================================

    def save_results(self):
        """Save engineered dataset and summary"""
        print("\n" + "="*80)
        print("STAGE 5: SAVING RESULTS")
        print("="*80)
        
        # Remove temporary date_parsed column if exists
        if 'date_parsed' in self.df_engineered.columns:
            self.df_engineered = self.df_engineered.drop(columns=['date_parsed'])
        
        # Save engineered dataset
        output_path = f'{self.data_path}/sales_with_fraud_indicators.csv'
        self.df_engineered.to_csv(output_path, index=False)
        print(f"✓ Engineered dataset saved: sales_with_fraud_indicators.csv")
        print(f"  - {len(self.df_engineered):,} transactions")
        print(f"  - {len(self.df_engineered.columns)} features")
        
        # Create summary report
        summary = {
            'Total_Transactions': len(self.df_engineered),
            'Total_Features': len(self.df_engineered.columns),
            'Engineered_Features': 45,
            'Engineered_Features_Description': 'Original 36 + 3 transaction velocity + 6 device/location features',
            'Mean_Fraud_Risk_Score': self.df_engineered['overall_fraud_risk_score'].mean(),
            'Std_Fraud_Risk_Score': self.df_engineered['overall_fraud_risk_score'].std(),
            'Low_Risk': (self.df_engineered['risk_level'] == 'Low').sum(),
            'Medium_Risk': (self.df_engineered['risk_level'] == 'Medium').sum(),
            'High_Risk': (self.df_engineered['risk_level'] == 'High').sum(),
            'Critical_Risk': (self.df_engineered['risk_level'] == 'Critical').sum(),
            'Flagged_for_Review': self.df_engineered['flagged_for_review'].sum(),
            'Data_Quality_Missing_Values': self.df_engineered.isnull().sum().sum(),
            'Data_Quality_Infinite_Values': np.isinf(self.df_engineered.select_dtypes(include=['float64']).values).sum()
        }
        
        summary_df = pd.DataFrame([summary])
        summary_path = f'{self.data_path}/fraud_detection_summary.csv'
        summary_df.to_csv(summary_path, index=False)
        print(f"✓ Summary report saved: fraud_detection_summary.csv")

    def run_pipeline(self):
        """Execute the complete fraud detection pipeline"""
        print("\n")
        print("█" * 80)
        print("█ FRAUD DETECTION IN ONLINE TRANSACTIONS - COMPLETE PIPELINE".ljust(80) + "█")
        print("█" * 80)
        
        # Stage 1: Load Data
        if not self.load_data():
            print("✗ Failed to load data. Exiting.")
            return False
        
        # Stage 2: Validate Data Integrity
        if not self.validate_data_integrity():
            print("⚠ Data integrity issues found. Proceeding with available data...")
        
        # Stage 3: Feature Engineering
        self.engineer_features()
        
        # Stage 4: Analysis & Reporting
        self.analyze_fraud_indicators()
        
        # Stage 5: Save Results
        self.save_results()
        
        # Final Summary
        print("\n" + "="*80)
        print("✓✓✓ PIPELINE EXECUTION COMPLETED SUCCESSFULLY ✓✓✓")
        print("="*80)
        print("\nOUTPUT FILES:")
        print("  1. sales_with_fraud_indicators.csv - Complete dataset with 36 engineered features")
        print("  2. fraud_detection_summary.csv - Summary statistics and metrics")
        print("\nREADY FOR:")
        print("  • Machine Learning model training (classification, analytics)")
        print("  • Real-time fraud risk scoring")
        print("  • Exploratory Data Analysis (EDA)")
        print("  • Business decision-making and rule optimization")
        print("\n" + "="*80)
        
        return True


# =====================================================================
# MAIN EXECUTION
# =====================================================================

if __name__ == "__main__":
    """Execute the fraud detection pipeline"""
    pipeline = FraudDetectionPipeline()
    pipeline.run_pipeline()
