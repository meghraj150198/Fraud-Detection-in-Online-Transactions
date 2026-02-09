"""
Fraud Detection System - Landing/Home Page
Showcases all key features and provides navigation to dashboard
"""

import streamlit as st
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Fraud Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0 !important;
    }
    .block-container {
        padding: 2rem !important;
    }
    h1 {
        text-align: center;
        color: #667eea;
    }
    h2 {
        color: #667eea;
        margin-top: 2rem;
    }
    .feature-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-size: 1.2em;
    }
    .cta-button {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        text-decoration: none;
        margin: 1rem 0.5rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="text-align: center; padding: 3rem 0;">
    <h1 style="font-size: 3em; margin: 0;">🛡️ Fraud Detection System</h1>
    <p style="font-size: 1.3em; color: #666; margin-top: 1rem;">
        Advanced Real-Time Fraud Detection with Interactive Analytics
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# Main CTA
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: #f0f1ff; border-radius: 15px; border-left: 4px solid #667eea;">
        <h3 style="color: #667eea; margin: 0 0 1rem 0;">🚀 Ready to Get Started?</h3>
        <p style="color: #666; margin: 0 0 1.5rem 0;">Launch the interactive dashboard to monitor, analyze, and score transactions in real-time.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📊 Open Dashboard", use_container_width=True, key="dashboard_btn"):
            st.switch_page("pages/dashboard.py")
    
    with col_btn2:
        st.link_button("📖 View Docs", "https://github.com/meghraj150198/Fraud-Detection-in-Online-Transactions", use_container_width=True)

st.divider()

# Model Performance
st.markdown("## 🎯 Model Performance")
metric_cols = st.columns(4)
with metric_cols[0]:
    st.metric("Accuracy", "92.85%", delta=None)
with metric_cols[1]:
    st.metric("Fraud Recall", "87.71%", delta=None)
with metric_cols[2]:
    st.metric("False Alarms", "3.01%", delta=None, delta_color="inverse")
with metric_cols[3]:
    st.metric("Speed", "~200 tx/sec", delta=None)

st.divider()

# System Metrics
st.markdown("## 📊 System Metrics")
metric_cols = st.columns(4)
with metric_cols[0]:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 2em;">14,640</div>
        <div>Transactions</div>
    </div>
    """, unsafe_allow_html=True)
with metric_cols[1]:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 2em;">5,132</div>
        <div>Fraud Cases</div>
    </div>
    """, unsafe_allow_html=True)
with metric_cols[2]:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 2em;">124</div>
        <div>Features</div>
    </div>
    """, unsafe_allow_html=True)
with metric_cols[3]:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 2em;">8</div>
        <div>Base Models</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Dashboard Pages
st.markdown("## 📱 Dashboard Pages")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📊 Dashboard Page
    Real-time fraud metrics and visualizations
    
    - 5 key metric cards
    - Risk distribution charts
    - Score histograms
    - Statistical percentiles
    """)

with col2:
    st.markdown("""
    ### 🔍 Scoring Page
    Score transactions instantly or in batches
    
    - Single transaction scoring
    - CSV batch upload
    - Instant predictions
    - Confidence scores
    """)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📈 Analytics Page
    Advanced fraud pattern analysis
    
    - Risk analysis tab
    - Feature importance
    - High-risk explorer
    - CSV export
    """)

with col2:
    st.markdown("""
    ### ⚙️ System Info Page
    Health check & deployment reference
    
    - Component status
    - Model metrics
    - Deployment options
    - Quick references
    """)

st.divider()

# Key Features
st.markdown("## ✨ Key Features")

feature_cols = st.columns(3)

with feature_cols[0]:
    st.markdown("""
    **🎯 Real-Time Monitoring**
    - Live transaction metrics
    - Fraud rate tracking
    - Risk visualization
    - Health indicators
    """)

with feature_cols[1]:
    st.markdown("""
    **🔍 Interactive Scoring**
    - Single transaction scoring
    - Batch processing
    - Instant predictions
    - Confidence scores
    """)

with feature_cols[2]:
    st.markdown("""
    **📊 Advanced Analytics**
    - Pattern analysis
    - Correlations
    - Risk breakdown
    - Export to CSV
    """)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    📚 **Data Export**
    - Download predictions
    - Export reports
    - CSV format
    
    ✅ **Production Ready**
    - Error handling
    - Caching
    - Docker support
    """)

with col2:
    st.markdown("""
    🎨 **Beautiful UI**
    - Interactive charts
    - Color-coded levels
    - Mobile responsive
    - Theme support
    """)

st.divider()

# Technology Stack
st.markdown("## 🛠️ Technology Stack")

tech_cols = st.columns(4)
tech_stack = [
    ("Python 3.12", "🐍"),
    ("Streamlit", "📊"),
    ("Plotly", "📈"),
    ("Scikit-Learn", "🤖"),
    ("XGBoost", "⚡"),
    ("Pandas", "📋"),
    ("Flask API", "🌐"),
    ("Docker", "🐳"),
]

for i, (tech, icon) in enumerate(tech_stack):
    st.write(f"{icon} {tech}")

st.divider()

# ML Model Info
st.markdown("## 🤖 Machine Learning Model")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Architecture**
    
    Stacked ensemble with:
    - 8 signal-specific RF models
    - Gradient Boosting meta-learner
    - Multi-class classification
    """)

with col2:
    st.markdown("""
    **Feature Engineering**
    
    96 engineered features across:
    - Velocity patterns
    - Amount anomalies
    - Device behavior
    - Merchant patterns
    - Temporal signals
    """)

with col3:
    st.markdown("""
    **Training Data**
    
    - 14,640 transactions
    - 124 total features
    - 0 missing values
    - Fully validated
    """)

st.divider()

# Quick Start
st.markdown("## 🚀 Quick Start")

st.info("""
**Get running in 30 seconds:**

```bash
# Step 1: Install dependencies
pip install streamlit plotly

# Step 2: Launch dashboard
streamlit run dashboard.py

# Step 3: Open browser
→ http://localhost:8501
```

Or use the automated startup script:
```bash
./start_dashboard.sh
```
""")

st.divider()

# Deployment Options
st.markdown("## 📦 Deployment Options")

deploy_cols = st.columns(2)

with deploy_cols[0]:
    st.markdown("""
    **Python Library**
    ```python
    from fraud_scoring_service import FraudScoringService
    service = FraudScoringService()
    results = service.score_transactions(df)
    ```
    
    **Docker Container**
    ```bash
    docker-compose up -d
    ```
    """)

with deploy_cols[1]:
    st.markdown("""
    **REST API**
    ```bash
    python fraud_scoring_service_api.py
    ```
    
    **Python Client**
    ```python
    from fraud_detection_client import FraudDetectionClient
    client = FraudDetectionClient('http://api:5000')
    ```
    """)

st.divider()

# Documentation Links
st.markdown("## 📚 Documentation")

doc_cols = st.columns(2)

with doc_cols[0]:
    st.markdown("""
    - **DASHBOARD_QUICKSTART.md** - 60-second setup
    - **DASHBOARD_GUIDE.md** - Complete features
    - **DASHBOARD_REFERENCE.md** - Quick reference
    """)

with doc_cols[1]:
    st.markdown("""
    - **DASHBOARD_SUMMARY.md** - Full overview
    - **SYSTEM_OVERVIEW.md** - System integration
    - **DEPLOYMENT_GUIDE.md** - API reference
    """)

st.divider()

# Final CTA
st.markdown("""
<div style="text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin: 2rem 0;">
    <h2 style="color: white; margin: 0 0 1rem 0;">Ready to Detect Fraud?</h2>
    <p style="margin: 0 0 1.5rem 0; font-size: 1.1em;">Launch the interactive dashboard now and start monitoring transactions in real-time.</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 Launch Dashboard Now", use_container_width=True, key="launch_now"):
        st.switch_page("pages/dashboard.py")
    
    st.link_button("📖 View Full Guides", "https://github.com/meghraj150198/Fraud-Detection-in-Online-Transactions", use_container_width=True)

st.divider()

# Footer
st.markdown("""
<div style="text-align: center; color: #999; padding: 2rem 0; font-size: 0.9em;">
    <p><strong>🛡️ Fraud Detection System v1.0</strong></p>
    <p>Production-Ready • 92.85% Accuracy • Real-Time Monitoring</p>
    <p>Last Updated: February 9, 2026</p>
</div>
""", unsafe_allow_html=True)
