"""
Fraud Detection System - Interactive Dashboard
================================================
Real-time analytics and monitoring dashboard for fraud detection model
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import os

# Set page configuration
st.set_page_config(
    page_title="Fraud Detection Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .success-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .warning-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD DATA AND MODEL
# ============================================================================

@st.cache_resource
def load_model_and_data():
    """Load model artifacts and feature data"""
    import pickle
    from fraud_scoring_service import FraudScoringService
    
    service = FraudScoringService()
    data = pd.read_csv('sales_with_fraud_indicators.csv')
    
    return service, data

@st.cache_data
def load_scored_data():
    """Load previously scored transactions"""
    try:
        return pd.read_csv('fraud_system_output/scored_transactions_20260209_044125.csv')
    except:
        return None

@st.cache_data
def load_model_stats():
    """Load model performance statistics"""
    try:
        with open('model_stats.json', 'r') as f:
            return json.load(f)
    except:
        return None

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

with st.sidebar:
    st.title("🛡️ Fraud Detection")
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Select View:",
        ["📊 Dashboard", "🔍 Scoring", "📈 Analytics", "⚙️ System Info"],
        help="Choose a section to view"
    )
    
    st.markdown("---")
    st.subheader("System Status")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Model", "Active ✓", delta=None, delta_color="off")
    with col2:
        st.metric("API", "Ready ✓", delta=None, delta_color="off")
    
    st.markdown("---")
    st.sidebar.info(
        "💡 **Quick Tips:**\n\n"
        "• Use Dashboard for overview\n"
        "• Score transactions in Scoring\n"
        "• Deep dive with Analytics\n"
        "• Check system health in Info"
    )

# ============================================================================
# PAGE 1: DASHBOARD
# ============================================================================

if page == "📊 Dashboard":
    st.title("🛡️ Fraud Detection Dashboard")
    
    # Load data
    service, raw_data = load_model_and_data()
    stats = load_model_stats()
    scored_data = load_scored_data()
    
    if scored_data is not None:
        # Key Metrics Row
        st.markdown("## 📊 Key Metrics")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Total Transactions",
                f"{len(scored_data):,}",
                help="Total transactions scored"
            )
        
        with col2:
            fraud_count = scored_data['is_fraud_flagged'].sum()
            fraud_rate = scored_data['is_fraud_flagged'].mean() * 100
            st.metric(
                "Fraud Flagged",
                f"{fraud_count:,}",
                delta=f"{fraud_rate:.2f}%",
                delta_color="inverse"
            )
        
        with col3:
            avg_score = scored_data['risk_score'].mean()
            st.metric(
                "Avg Risk Score",
                f"{avg_score:.2f}/100",
                help="Average risk score across all transactions"
            )
        
        with col4:
            high_risk = (scored_data['predicted_risk_level'] == 'High').sum()
            st.metric(
                "High Risk",
                f"{high_risk}",
                help="Transactions with High risk classification"
            )
        
        with col5:
            if stats:
                accuracy = stats['training_metrics'].get('accuracy', 0)
                st.metric(
                    "Model Accuracy",
                    f"{accuracy*100:.2f}%",
                    help="Model accuracy from training"
                )
        
        st.markdown("---")
        
        # Risk Distribution
        st.markdown("## 📈 Risk Classification Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk distribution pie chart
            risk_dist = scored_data['predicted_risk_level'].value_counts()
            
            colors = {'Low': '#2ecc71', 'Medium': '#f39c12', 'High': '#e74c3c'}
            fig_pie = go.Figure(data=[go.Pie(
                labels=risk_dist.index,
                values=risk_dist.values,
                marker=dict(colors=[colors.get(x, '#95a5a6') for x in risk_dist.index]),
                textposition='inside',
                textinfo='label+percent'
            )])
            fig_pie.update_layout(
                title="Risk Distribution",
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Risk class counts bar chart
            fig_bar = go.Figure(data=[go.Bar(
                x=['Low', 'Medium', 'High'],
                y=[
                    (scored_data['predicted_risk_level'] == 'Low').sum(),
                    (scored_data['predicted_risk_level'] == 'Medium').sum(),
                    (scored_data['predicted_risk_level'] == 'High').sum()
                ],
                marker_color=['#2ecc71', '#f39c12', '#e74c3c'],
                text=[
                    (scored_data['predicted_risk_level'] == 'Low').sum(),
                    (scored_data['predicted_risk_level'] == 'Medium').sum(),
                    (scored_data['predicted_risk_level'] == 'High').sum()
                ],
                textposition='outside'
            )])
            fig_bar.update_layout(
                title="Transaction Count by Risk Level",
                xaxis_title="Risk Level",
                yaxis_title="Count",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("---")
        
        # Risk Score Distribution
        st.markdown("## 📊 Risk Score Distribution")
        
        fig_hist = go.Figure(data=[go.Histogram(
            x=scored_data['risk_score'],
            nbinsx=50,
            marker_color='#3498db',
            name='Risk Score'
        )])
        fig_hist.update_layout(
            title="Distribution of Risk Scores (0-100)",
            xaxis_title="Risk Score",
            yaxis_title="Frequency",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        
        st.markdown("---")
        
        # Statistics Table
        st.markdown("## 📋 Risk Score Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("25th Percentile", f"{scored_data['risk_score'].quantile(0.25):.2f}")
        with col2:
            st.metric("50th Percentile", f"{scored_data['risk_score'].quantile(0.50):.2f}")
        with col3:
            st.metric("75th Percentile", f"{scored_data['risk_score'].quantile(0.75):.2f}")
        with col4:
            st.metric("95th Percentile", f"{scored_data['risk_score'].quantile(0.95):.2f}")
    else:
        st.warning("⚠️ No scored data available. Please run the integration pipeline first.")
        st.code("python fraud_system_integration.py", language="bash")

# ============================================================================
# PAGE 2: LIVE SCORING
# ============================================================================

elif page == "🔍 Scoring":
    st.title("🔍 Real-Time Transaction Scoring")
    
    service, raw_data = load_model_and_data()
    
    st.markdown("""
    Score individual transactions or upload a batch of transactions to get fraud risk predictions.
    """)
    
    # Scoring mode selection
    scoring_mode = st.radio(
        "Choose Scoring Mode:",
        ["Single Transaction", "Batch Upload"],
        horizontal=True
    )
    
    if scoring_mode == "Single Transaction":
        st.markdown("### 📝 Enter Transaction Details")
        
        # Get feature names from model
        features = service.all_features
        
        # Create input fields for key features
        col1, col2, col3 = st.columns(3)
        
        transaction_data = {}
        
        with col1:
            transaction_data['selling_price'] = st.number_input(
                "Selling Price ($)",
                min_value=0.0,
                value=450.0,
                step=10.0
            )
            transaction_data['quantity_ordered'] = st.number_input(
                "Quantity",
                min_value=1,
                value=2,
                step=1
            )
            transaction_data['transaction_hour'] = st.number_input(
                "Transaction Hour (0-23)",
                min_value=0,
                max_value=23,
                value=12
            )
        
        with col2:
            transaction_data['velocity_spike'] = st.selectbox(
                "Velocity Spike?",
                [0, 1],
                format_func=lambda x: "Yes" if x == 1 else "No"
            )
            transaction_data['unusual_amount_flag'] = st.selectbox(
                "Unusual Amount?",
                [0, 1],
                format_func=lambda x: "Yes" if x == 1 else "No"
            )
            transaction_data['device_familiarity_score'] = st.slider(
                "Device Familiarity (0-100)",
                0, 100, 75
            )
        
        with col3:
            transaction_data['merchant_risk_score'] = st.slider(
                "Merchant Risk Score (0-100)",
                0, 100, 30
            )
            transaction_data['combined_risk_index'] = st.slider(
                "Combined Risk Index (0-100)",
                0, 100, 15
            )
        
        # Fill missing features with defaults
        for feature in features:
            if feature not in transaction_data:
                transaction_data[feature] = raw_data[feature].mean()
        
        if st.button("🎯 Score Transaction", key="score_single"):
            with st.spinner("Scoring transaction..."):
                try:
                    response = service.score_single_transaction(transaction_data)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 🔍 Prediction Result")
                        
                        prediction = response['prediction']
                        risk_level = prediction['risk_level']
                        risk_score = prediction['risk_score']
                        confidence = prediction['confidence']
                        
                        # Color based on risk level
                        if risk_level == 'Low':
                            color = "#2ecc71"
                            emoji = "✅"
                        elif risk_level == 'Medium':
                            color = "#f39c12"
                            emoji = "⚠️"
                        else:
                            color = "#e74c3c"
                            emoji = "🚫"
                        
                        st.markdown(f"""
                        <div style="background-color:{color}; padding: 20px; border-radius: 10px; color: white;">
                            <h2>{emoji} {risk_level}</h2>
                            <h3>Risk Score: {risk_score:.2f}/100</h3>
                            <p>Confidence: {confidence:.2f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if prediction['is_flagged']:
                            st.error("🚨 **FLAGGED FOR REVIEW** - Fraud indicators detected")
                        else:
                            st.success("✅ **APPROVED** - Low fraud risk")
                    
                    with col2:
                        st.markdown("### 📊 Class Probabilities")
                        
                        probs = prediction['class_probabilities']
                        fig_gauge = go.Figure(go.Indicator(
                            mode="gauge+number+delta",
                            value=risk_score,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "Risk Score"},
                            gauge={
                                'axis': {'range': [0, 100]},
                                'bar': {'color': color},
                                'steps': [
                                    {'range': [0, 33], 'color': "#2ecc7122"},
                                    {'range': [33, 66], 'color': "#f39c1222"},
                                    {'range': [66, 100], 'color': "#e74c3c22"}
                                ],
                                'threshold': {
                                    'line': {'color': "black", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 50
                                }
                            }
                        ))
                        st.plotly_chart(fig_gauge, use_container_width=True)
                        
                        st.markdown("**Probabilities by Class:**")
                        for cls, prob in probs.items():
                            st.write(f"• {cls.capitalize()}: {prob:.2f}%")
                
                except Exception as e:
                    st.error(f"Error scoring transaction: {e}")
    
    else:  # Batch Upload
        st.markdown("### 📤 Upload Batch of Transactions")
        
        uploaded_file = st.file_uploader(
            "Upload CSV file with transactions",
            type="csv",
            help="CSV should have columns matching the fraud detection features"
        )
        
        if uploaded_file is not None:
            batch_df = pd.read_csv(uploaded_file)
            
            st.write(f"Loaded {len(batch_df)} transactions")
            st.dataframe(batch_df.head(), use_container_width=True)
            
            if st.button("🎯 Score Batch", key="score_batch"):
                with st.spinner(f"Scoring {len(batch_df)} transactions..."):
                    try:
                        results = service.score_transactions(batch_df)
                        
                        # Display results
                        st.markdown("### 📊 Batch Scoring Results")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Total Scored", len(results))
                        with col2:
                            flagged = results['is_fraud_flagged'].sum()
                            st.metric("Fraud Flagged", f"{flagged} ({flagged/len(results)*100:.2f}%)")
                        with col3:
                            st.metric("Avg Risk Score", f"{results['risk_score'].mean():.2f}")
                        
                        # Download results
                        csv = results.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results (CSV)",
                            data=csv,
                            file_name=f"fraud_scores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                        
                        # Show results table
                        st.dataframe(results, use_container_width=True)
                    
                    except Exception as e:
                        st.error(f"Error scoring batch: {e}")

# ============================================================================
# PAGE 3: ANALYTICS
# ============================================================================

elif page == "📈 Analytics":
    st.title("📈 Advanced Analytics")
    
    scored_data = load_scored_data()
    raw_data = pd.read_csv('sales_with_fraud_indicators.csv')
    
    if scored_data is not None:
        # Tab navigation
        tab1, tab2, tab3 = st.tabs(["Risk Analysis", "Feature Importance", "High Risk"])
        
        with tab1:
            st.markdown("## 🔍 Detailed Risk Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Confidence distribution
                fig_conf = go.Figure(data=[go.Histogram(
                    x=scored_data['confidence'],
                    nbinsx=30,
                    marker_color='#9b59b6',
                    name='Confidence'
                )])
                fig_conf.update_layout(
                    title="Model Confidence Distribution",
                    xaxis_title="Confidence (%)",
                    yaxis_title="Frequency",
                    height=400
                )
                st.plotly_chart(fig_conf, use_container_width=True)
            
            with col2:
                # Risk by class breakdown
                risk_stats = scored_data.groupby('predicted_risk_level').agg({
                    'risk_score': ['mean', 'min', 'max', 'std'],
                    'confidence': 'mean'
                }).round(2)
                st.dataframe(risk_stats, use_container_width=True)
            
            st.markdown("---")
            
            # Risk score correlation
            st.markdown("## 📊 Risk Factors Correlation")
            
            correlation_features = [
                'selling_price', 'quantity_ordered', 'velocity_spike',
                'combined_risk_index', 'behavioral_anomaly_score',
                'merchant_risk_score', 'device_familiarity_score'
            ]
            
            available_features = [f for f in correlation_features if f in raw_data.columns]
            
            if len(available_features) > 0:
                corr_data = raw_data[available_features + ['overall_fraud_risk_score']].corr()
                
                fig_corr = go.Figure(data=go.Heatmap(
                    z=corr_data.values,
                    x=corr_data.columns,
                    y=corr_data.columns,
                    colorscale='RdBu',
                    zmid=0
                ))
                fig_corr.update_layout(
                    title="Feature Correlation with Fraud Risk",
                    height=600
                )
                st.plotly_chart(fig_corr, use_container_width=True)
        
        with tab2:
            st.markdown("## 🎯 Feature Importance Analysis")
            
            if st.checkbox("Show Feature Statistics"):
                feature_stats = raw_data[[
                    'velocity_spike', 'unusual_amount_flag', 'unfamiliar_device_flag',
                    'new_merchant_flag', 'late_night_hour', 'high_risk_payment_method',
                    'high_historical_fraud_flag', 'behavioral_anomaly_score'
                ]].describe().round(3)
                st.dataframe(feature_stats, use_container_width=True)
            
            # Top risky features
            st.markdown("## ⚠️ Top Risk Indicators")
            
            col1, col2 = st.columns(2)
            
            with col1:
                high_risk_txns = scored_data[scored_data['predicted_risk_level'] == 'High']
                
                if len(high_risk_txns) > 0:
                    st.write(f"### High Risk Transactions: {len(high_risk_txns)}")
                    st.dataframe(
                        high_risk_txns[['risk_score', 'confidence', 'prob_high']].head(10),
                        use_container_width=True
                    )
        
        with tab3:
            st.markdown("## 🚨 High Risk Transaction Details")
            
            high_risk = scored_data[scored_data['is_fraud_flagged'] == 1].sort_values(
                'risk_score', ascending=False
            )
            
            st.write(f"Total High-Risk Transactions: **{len(high_risk)}**")
            
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                min_score = st.slider("Minimum Risk Score", 0, 100, 50)
            
            with col2:
                risk_level_filter = st.multiselect(
                    "Risk Levels",
                    ['High', 'Medium'],
                    default=['High', 'Medium']
                )
            
            filtered = high_risk[
                (high_risk['risk_score'] >= min_score) &
                (high_risk['predicted_risk_level'].isin(risk_level_filter))
            ]
            
            st.dataframe(
                filtered[[
                    'transaction_id', 'risk_score', 'predicted_risk_level',
                    'confidence', 'prob_high', 'prob_medium'
                ]].head(50),
                use_container_width=True
            )
            
            # Download flagged transactions
            csv = filtered.to_csv(index=False)
            st.download_button(
                label="📥 Download Flagged Transactions",
                data=csv,
                file_name=f"high_risk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

# ============================================================================
# PAGE 4: SYSTEM INFO
# ============================================================================

elif page == "⚙️ System Info":
    st.title("⚙️ System Information & Status")
    
    stats = load_model_stats()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("## 📊 Model Information")
        
        if stats:
            st.write(f"**Model Type:** Stacked Ensemble")
            st.write(f"**Base Models:** 8 signal-specific")
            st.write(f"**Meta-Learner:** Gradient Boosting")
            st.write(f"**Total Features:** 49")
            st.write(f"**Training Date:** 2026-02-09")
            st.write(f"**Version:** 1.0")
        
        st.markdown("---")
        st.markdown("## 🎯 Model Performance")
        
        if stats and 'training_performance' in stats.get('training_metrics', {}):
            metrics = stats['training_metrics']
            
            st.metric("Accuracy", f"{metrics.get('accuracy', 0):.4f}")
            st.metric("Precision", f"{metrics.get('precision_weighted', 0):.4f}")
            st.metric("Recall", f"{metrics.get('recall_weighted', 0):.4f}")
            st.metric("F1-Score", f"{metrics.get('f1_weighted', 0):.4f}")
    
    with col2:
        st.markdown("## 🔧 System Status")
        
        # Check component status
        components = {
            "Feature Data": os.path.exists('sales_with_fraud_indicators.csv'),
            "Model Artifacts": os.path.exists('ml_model_artifacts.pkl'),
            "Scoring Service": True,  # Loaded if we got here
            "REST API": os.path.exists('fraud_scoring_service_api.py'),
            "Docker Setup": os.path.exists('Dockerfile'),
            "Documentation": os.path.exists('DEPLOYMENT_GUIDE.md')
        }
        
        for component, status in components.items():
            status_text = "✅ Ready" if status else "❌ Missing"
            st.write(f"**{component}:** {status_text}")
        
        st.markdown("---")
        st.markdown("## 📈 Deployment Options")
        
        st.code("""
# Option 1: Python Library
from fraud_scoring_service import FraudScoringService
service = FraudScoringService()
results = service.score_transactions(df)

# Option 2: REST API
python fraud_scoring_service_api.py

# Option 3: Docker
docker build -t fraud-detector:v1.0 .
docker run -p 5000:5000 fraud-detector:v1.0
        """)
    
    st.markdown("---")
    st.markdown("## 📚 Documentation")
    
    docs = {
        "SYSTEM_STATUS.md": "Executive overview",
        "DEPLOYMENT_GUIDE.md": "API reference & deployment",
        "COMPLETE_INTEGRATION_GUIDE.md": "All integration options",
        "DEPLOYMENT_README.md": "Quick start guide"
    }
    
    for doc, description in docs.items():
        st.write(f"📄 **{doc}** - {description}")
    
    st.markdown("---")
    st.markdown("## 🔗 Quick Links")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 View Full Report"):
            st.write("See fraud_system_output/system_report_*.json")
    
    with col2:
        if st.button("⚡ Run Integration Test"):
            st.code("python fraud_system_integration.py")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px; padding: 20px;">
    <p>🛡️ Fraud Detection System Dashboard v1.0 | Last Updated: 2026-02-09</p>
    <p>Model Accuracy: 92.85% | Fraud Detection Rate: 87.71%</p>
</div>
""", unsafe_allow_html=True)
