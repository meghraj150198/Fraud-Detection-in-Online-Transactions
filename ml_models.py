"""
Stacked Ensemble Fraud Detection Model
=====================================
Multi-class risk classification with base models per signal type and meta-learner
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score, 
    precision_score, recall_score, f1_score, roc_auc_score,
    roc_curve, auc
)
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
import lightgbm as lgb
import pickle
from datetime import datetime

# ============================================================================
# SECTION 1: DATA LOADING & PREPARATION
# ============================================================================

print("=" * 80)
print("STACKED ENSEMBLE FRAUD DETECTION MODEL - MULTI-CLASS CLASSIFICATION")
print("=" * 80)
print("\n[1] Loading data and preparing features...")

df = pd.read_csv('sales_with_fraud_indicators.csv')

print(f"✓ Loaded {len(df):,} transactions with {len(df.columns)} features")

# ============================================================================
# SECTION 2: TARGET VARIABLE PREPARATION
# ============================================================================

# Create multi-class target: Low, Medium, High, Critical
def create_risk_category(row):
    """Map fraud risk score to risk categories optimized for recall"""
    score = row['overall_fraud_risk_score']
    
    if score >= 50:
        return 'Critical'
    elif score >= 25:
        return 'High'
    elif score >= 10:
        return 'Medium'
    else:
        return 'Low'

df['risk_category'] = df.apply(create_risk_category, axis=1)

# Distribution
print("\n[2] Target Distribution (Multi-Class Risk Categories):")
risk_dist = df['risk_category'].value_counts().sort_index()
for risk, count in risk_dist.items():
    pct = count / len(df) * 100
    print(f"   {risk:10s}: {count:6,} transactions ({pct:5.2f}%)")

# ============================================================================
# SECTION 3: SIGNAL GROUP FEATURE SELECTION
# ============================================================================

print("\n[3] Organizing features into signal groups...")

# Define feature groups for base models
feature_groups = {
    'velocity': [
        'velocity_spike', 'extreme_velocity_spike', 'units_zscore_7d',
        'rolling_7d_avg_units', 'rolling_7d_std_units',
        'platform_daily_velocity', 'global_daily_velocity', 'high_velocity_day_flag'
    ],
    'amount': [
        'historical_avg_amount', 'amount_deviation_score', 'unusual_amount_flag',
        'price_pct_of_mrp', 'avg_price_pct_of_mrp', 'price_deviation_from_sku_avg',
        'price_exceeds_mrp_flag', 'price_below_cost_flag'
    ],
    'device_location': [
        'device_familiarity_score', 'unfamiliar_device_flag', 'account_device_match_score',
        'new_device_combo_flag', 'location_deviation_from_baseline', 'unusual_location_flag'
    ],
    'merchant': [
        'merchant_risk_score_by_category', 'sku_category_transaction_count',
        'merchant_familiarity_score', 'new_merchant_flag', 'risky_merchant_flag',
        'merchant_risk_score'
    ],
    'temporal': [
        'transaction_hour', 'late_night_hour', 'very_late_night_flag',
        'time_of_day_risk_score', 'day_of_week_risk_score', 'high_risk_temporal_window'
    ],
    'payment_method': [
        'high_risk_payment_method', 'payment_method_risk_score',
        'is_low_amount', 'is_high_amount', 'recent_low_amount_pattern'
    ],
    'ip_historical': [
        'ip_address_risk_score', 'high_fraud_region_indicator', 'weather_volatility',
        'historical_fraud_rate', 'high_historical_fraud_flag', 'account_compromise_risk'
    ],
    'behavioral_meta': [
        'behavioral_anomaly_score', 'combined_risk_index', 'anomaly_count',
        'cumulative_anomalies'
    ]
}

print(f"\n   Signal Groups and Feature Counts:")
for group, features in feature_groups.items():
    valid_features = [f for f in features if f in df.columns]
    print(f"   • {group:20s}: {len(valid_features):2d} features")

# Combine all features for full model
all_features = []
for features in feature_groups.values():
    all_features.extend([f for f in features if f in df.columns])
all_features = list(set(all_features))  # Remove duplicates

# Filter to only numeric features
numeric_features = [f for f in all_features if df[f].dtype in ['float64', 'int64', 'float32', 'int32']]
all_features = numeric_features

print(f"\n   Total Numeric Features for Models: {len(all_features)}")

# ============================================================================
# SECTION 4: TRAIN-TEST SPLIT
# ============================================================================

print("\n[4] Splitting data (70% train, 30% test, stratified)...")

X = df[all_features].copy()
y = df['risk_category'].copy()

# Handle missing values
X = X.fillna(X.mean(numeric_only=True))

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.30, random_state=42, stratify=y
)

print(f"   Training set: {len(X_train):,} transactions")
print(f"   Test set: {len(X_test):,} transactions")

# Encode target
label_encoder = LabelEncoder()
y_train_encoded = label_encoder.fit_transform(y_train)
y_test_encoded = label_encoder.transform(y_test)

print(f"   Classes: {list(label_encoder.classes_)}")

# Standardize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ============================================================================
# SECTION 5: BASE MODELS (ONE PER SIGNAL GROUP)
# ============================================================================

print("\n[5] Training base models for each signal group...")
print("   (Optimized for Recall - catching all fraud cases)")

base_models = {}
base_predictions_train = []  # For meta-learner training
base_predictions_test = []   # For meta-learner testing

for group_name, features in feature_groups.items():
    # Filter to valid features in this group
    valid_features = [f for f in features if f in df.columns]
    
    if len(valid_features) == 0 or not any(df[f].dtype in ['float64', 'int64', 'float32', 'int32'] for f in valid_features):
        print(f"   ! {group_name:20s}: No valid features, skipping")
        continue
    
    print(f"\n   {group_name.upper()}")
    print(f"   ─────────────────────────────────────────")
    
    # Get group features
    X_train_group = X_train[valid_features].fillna(X_train[valid_features].mean(numeric_only=True))
    X_test_group = X_test[valid_features].fillna(X_train[valid_features].mean(numeric_only=True))
    
    # Scale
    scaler_group = StandardScaler()
    X_train_group_scaled = scaler_group.fit_transform(X_train_group)
    X_test_group_scaled = scaler_group.transform(X_test_group)
    
    # Train Random Forest (optimized for recall)
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=20,
        min_samples_leaf=10,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'  # Handle class imbalance
    )
    
    model.fit(X_train_group_scaled, y_train_encoded)
    base_models[group_name] = {
        'model': model,
        'scaler': scaler_group,
        'features': valid_features
    }
    
    # Predictions for meta-learner
    train_pred = model.predict_proba(X_train_group_scaled)
    test_pred = model.predict_proba(X_test_group_scaled)
    
    base_predictions_train.append(train_pred)
    base_predictions_test.append(test_pred)
    
    # Evaluate
    y_pred_test = model.predict(X_test_group_scaled)
    recall = recall_score(y_test_encoded, y_pred_test, average='weighted', zero_division=0)
    f1 = f1_score(y_test_encoded, y_pred_test, average='weighted', zero_division=0)
    
    print(f"   Features: {len(valid_features)}")
    print(f"   Recall:   {recall:.4f}")
    print(f"   F1-Score: {f1:.4f}")

# Create meta-features
X_train_meta = np.hstack(base_predictions_train)
X_test_meta = np.hstack(base_predictions_test)

print(f"\n   Meta-Features Shape: {X_train_meta.shape}")
print(f"   (Each class probability from {len(base_models)} base models)")

# ============================================================================
# SECTION 6: META-LEARNER (GRADIENT BOOSTING)
# ============================================================================

print("\n[6] Training Meta-Learner (Gradient Boosting on base predictions)...")
print("   ─────────────────────────────────────────")

meta_model = GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=5,
    min_samples_split=20,
    min_samples_leaf=10,
    random_state=42,
    subsample=0.8,
    validation_fraction=0.1,
    n_iter_no_change=20
)

meta_model.fit(X_train_meta, y_train_encoded)

print("   ✓ Meta-learner trained on base model predictions")

# ============================================================================
# SECTION 7: MODEL EVALUATION
# ============================================================================

print("\n[7] MODEL EVALUATION - TEST SET")
print("   " + "=" * 76)

# Predictions
y_pred_meta = meta_model.predict(X_test_meta)
y_pred_proba_meta = meta_model.predict_proba(X_test_meta)

# Metrics
accuracy = accuracy_score(y_test_encoded, y_pred_meta)
recall_weighted = recall_score(y_test_encoded, y_pred_meta, average='weighted', zero_division=0)
recall_macro = recall_score(y_test_encoded, y_pred_meta, average='macro', zero_division=0)
precision_weighted = precision_score(y_test_encoded, y_pred_meta, average='weighted', zero_division=0)
f1_weighted = f1_score(y_test_encoded, y_pred_meta, average='weighted', zero_division=0)

print(f"\n   OVERALL PERFORMANCE:")
print(f"   Accuracy:           {accuracy:.4f}")
print(f"   Precision (weighted): {precision_weighted:.4f}")
print(f"   Recall (weighted):  {recall_weighted:.4f}  ← Primary metric")
print(f"   Recall (macro):     {recall_macro:.4f}  ← Balanced across classes")
print(f"   F1-Score (weighted):{f1_weighted:.4f}")

# Per-class metrics
print(f"\n   PER-CLASS DETAILED REPORT:")
print(f"   " + "─" * 76)

y_test_labels = label_encoder.inverse_transform(y_test_encoded)
y_pred_labels = label_encoder.inverse_transform(y_pred_meta)

print(classification_report(y_test_labels, y_pred_labels, digits=4))

# Confusion Matrix
print(f"\n   CONFUSION MATRIX:")
print(f"   " + "─" * 76)
cm = confusion_matrix(y_test_encoded, y_pred_meta)
class_names = label_encoder.classes_

print(f"\n   {'Actual→ / Predicted↓':15s}", end="")
for name in class_names:
    print(f"{name:>12s}", end="")
print()
print(f"   {'-' * 76}")

for i, actual_class in enumerate(class_names):
    print(f"   {actual_class:15s}", end="")
    for j in range(len(class_names)):
        count = cm[i, j]
        pct = count / cm[i].sum() * 100 if cm[i].sum() > 0 else 0
        print(f"{count:6d}({pct:5.1f}%)", end="")
    print()

# ============================================================================
# SECTION 8: RISK DISTRIBUTION IN PREDICTIONS
# ============================================================================

print(f"\n[8] PREDICTION DISTRIBUTION VS ACTUAL")
print(f"   " + "=" * 76)

actual_dist = pd.Series(y_test_labels).value_counts().sort_index()
pred_dist = pd.Series(y_pred_labels).value_counts().sort_index()

print(f"\n   {'Risk Level':12s} | {'Actual':>10s} | {'Predicted':>10s} | {'Difference':>10s}")
print(f"   {'-' * 76}")

for risk_level in label_encoder.classes_:
    actual_count = actual_dist.get(risk_level, 0)
    pred_count = pred_dist.get(risk_level, 0)
    diff = pred_count - actual_count
    
    print(f"   {risk_level:12s} | {actual_count:10,d} | {pred_count:10,d} | {diff:+10,d}")

# ============================================================================
# SECTION 9: BASE MODEL FEATURE IMPORTANCE
# ============================================================================

print(f"\n[9] FEATURE IMPORTANCE - TOP SIGNALS BY GROUP")
print(f"   " + "=" * 76)

for group_name in sorted(base_models.keys()):
    model_info = base_models[group_name]
    model = model_info['model']
    features = model_info['features']
    
    importances = model.feature_importances_
    feature_importance_df = pd.DataFrame({
        'feature': features,
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    print(f"\n   {group_name.upper()}")
    print(f"   {'-' * 76}")
    for idx, row in feature_importance_df.head(3).iterrows():
        print(f"   • {row['feature']:40s}: {row['importance']:.4f}")

# ============================================================================
# SECTION 10: DETECTION EFFECTIVENESS
# ============================================================================

print(f"\n[10] FRAUD DETECTION EFFECTIVENESS")
print(f"   " + "=" * 76)

# Identify fraud cases (Medium, High, Critical)
is_actual_fraud = y_test_labels != 'Low'
is_pred_fraud = y_pred_labels != 'Low'

fraud_detected = (is_actual_fraud & is_pred_fraud).sum()
fraud_missed = (is_actual_fraud & ~is_pred_fraud).sum()
false_alarms = (~is_actual_fraud & is_pred_fraud).sum()
true_negatives = (~is_actual_fraud & ~is_pred_fraud).sum()

print(f"\n   Actual Fraud Cases:     {is_actual_fraud.sum():6,d} transactions")
print(f"   Detected Fraud:         {fraud_detected:6,d} ({fraud_detected/is_actual_fraud.sum()*100:.2f}% recall)")
print(f"   Missed Fraud:           {fraud_missed:6,d} ({fraud_missed/is_actual_fraud.sum()*100:.2f}% miss rate)")
print(f"\n   Predicted as Normal:    {(~is_pred_fraud).sum():6,d} transactions")
print(f"   Correctly Identified:   {true_negatives:6,d} ({true_negatives/((~is_actual_fraud).sum())*100:.2f}% specificity)")
print(f"   False Alarms:           {false_alarms:6,d} ({false_alarms/((~is_actual_fraud).sum())*100:.2f}% false positive rate)")

# ============================================================================
# SECTION 11: MODEL SAVE & SERIALIZATION
# ============================================================================

print(f"\n[11] SAVING MODELS & ARTIFACTS")
print(f"   " + "=" * 76)

# Save all components
model_artifacts = {
    'meta_model': meta_model,
    'base_models': base_models,
    'label_encoder': label_encoder,
    'scaler': scaler,
    'all_features': all_features,
    'feature_groups': feature_groups,
    'training_date': datetime.now().isoformat(),
    'metrics': {
        'accuracy': accuracy,
        'recall_weighted': recall_weighted,
        'precision_weighted': precision_weighted,
        'f1_weighted': f1_weighted
    }
}

with open('ml_model_artifacts.pkl', 'wb') as f:
    pickle.dump(model_artifacts, f)

print(f"   ✓ Saved: ml_model_artifacts.pkl")

# ============================================================================
# SECTION 12: SUMMARY & RECOMMENDATIONS
# ============================================================================

print(f"\n[12] MODEL SUMMARY & DEPLOYABILITY")
print(f"   " + "=" * 76)

print(f"\n   Architecture:")
print(f"   • Base Models:  {len(base_models)} signal-specific Random Forests")
print(f"   • Meta-Learner: Gradient Boosting on probability predictions")
print(f"   • Target:       Multi-class (Low, Medium, High, Critical)")
print(f"   • Optimization: Recall (catch all fraud) > Precision")

print(f"\n   Data Split:")
print(f"   • Training:     {len(X_train):,} transactions")
print(f"   • Testing:      {len(X_test):,} transactions")

print(f"\n   Model Performance:")
print(f"   • Multi-class Recall:   {recall_macro:.4f}")
print(f"   • Fraud Detection Rate: {fraud_detected/is_actual_fraud.sum()*100:.2f}%")
print(f"   • False Alarm Rate:     {false_alarms/((~is_actual_fraud).sum())*100:.2f}%")

print(f"\n   Recommended Next Steps:")
print(f"   1. Deploy meta-model for real-time scoring")
print(f"   2. Monitor recall on new fraud patterns")
print(f"   3. Calibrate decision thresholds by business cost")
print(f"   4. A/B test against rule-based system")
print(f"   5. Retrain quarterly with new data")

print("\n" + "=" * 80)
print("STACKED ENSEMBLE MODEL TRAINING COMPLETE")
print("=" * 80)
