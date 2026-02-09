# 📊 Fraud Detection Dashboard

An interactive, real-time analytics dashboard for monitoring and analyzing fraud detection model performance, scoring individual transactions, and viewing system health metrics.

## 🎯 Quick Start

### Installation

```bash
# Install dashboard dependencies
pip install -r requirements_dashboard.txt

# Or install individual packages
pip install streamlit plotly
```

### Launch Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open in your default browser at `http://localhost:8501`

## 📋 Dashboard Sections

### 1. 📊 Dashboard (Home)
Main real-time analytics view with key metrics and visualizations.

**Features:**
- **Key Metrics**: Total transactions, fraud rate, average risk score, high-risk count, model accuracy
- **Risk Distribution**: Pie chart and bar chart showing the breakdown of Low/Medium/High risk transactions
- **Risk Score Distribution**: Histogram showing the distribution of risk scores across all transactions
- **Risk Score Statistics**: 25th, 50th, 75th, and 95th percentiles of risk scores

**What to Look For:**
- Red flags: High percentage of flagged transactions (>40% may indicate data quality issues)
- Normal: ~30-35% medium+high risk with ~1% truly high risk
- Risk score distribution: Should be bimodal (safe transactions near 100, risky near 0)

---

### 2. 🔍 Scoring (Real-Time Predictions)
Score individual transactions or upload batch files for predictions.

#### Single Transaction Scoring
1. Enter transaction details:
   - Selling Price ($)
   - Quantity Ordered
   - Transaction Hour (0-23)
   - Velocity Spike? (Yes/No)
   - Unusual Amount? (Yes/No)
   - Device Familiarity Score (0-100)
   - Merchant Risk Score (0-100)
   - Combined Risk Index (0-100)

2. Click "🎯 Score Transaction"

3. View results:
   - Risk Level (Low/Medium/High) with color coding
   - Risk Score (0-100)
   - Confidence percentage
   - Class probabilities for each risk level
   - Flag status (✅ APPROVED or 🚫 FLAGGED FOR REVIEW)

#### Batch Upload Scoring
1. Prepare CSV file with transaction data
2. Upload the CSV file
3. Click "🎯 Score Batch"
4. View results and download predictions

**Input CSV Format:**
Required columns should match model features:
```csv
selling_price,quantity_ordered,transaction_hour,velocity_spike,unusual_amount_flag,...
450,2,12,0,0,...
```

---

### 3. 📈 Analytics (Advanced Analysis)

#### Tab 1: Risk Analysis
- **Model Confidence Distribution**: Shows how confident predictions are across all transactions
- **Risk by Class Breakdown**: Min, max, mean, std deviation, and average confidence for each risk level
- **Feature Correlation Heatmap**: Visual correlation between features and fraud risk

**Insights:**
- High confidence transactions (>90%) are more reliable
- Correlation with overall_fraud_risk_score shows feature importance

#### Tab 2: Feature Importance
- **Feature Statistics**: Descriptive statistics for key fraud indicators
- **Top Risk Indicators**: List of transactions with highest fraud risk scores

**Key Statistics:**
- Velocity spike frequency
- Unusual amount flags
- Device familiarity patterns
- Behavioral anomaly scores

#### Tab 3: High Risk Transactions
- **Detailed view** of all flagged high-risk transactions
- **Filtering options**:
  - Minimum risk score threshold
  - Risk level selection (High/Medium)
- **Download functionality**: Export flagged transactions to CSV

---

### 4. ⚙️ System Information & Status
System health, model metadata, and deployment information.

**Components Monitored:**
✓ Feature Data - Training dataset availability
✓ Model Artifacts - Trained model file status
✓ Scoring Service - Service availability
✓ REST API - API deployment status
✓ Docker Setup - Container configuration
✓ Documentation - Guides and references

**Model Information Displayed:**
- Model type: Stacked Ensemble
- Base models: 8 signal-specific models
- Meta-learner: Gradient Boosting
- Total features: 49
- Training date & version

**Deployment Options:**
Quick reference for 5 deployment methods with code snippets

---

## 🎨 Dashboard Features

### Color Coding
- 🟢 **Green** (#2ecc71): Low Risk - Safe transactions
- 🟡 **Orange** (#f39c12): Medium Risk - Monitor closely
- 🔴 **Red** (#e74c3c): High Risk - Flag for review

### Real-Time Updates
- Sidebar status indicators show current system status
- Metrics refresh when data is reloaded
- Download buttons for exporting results

### Interactive Charts
- **Pie Charts**: Hover for percentages and counts
- **Bar Charts**: Hover for exact values
- **Histograms**: See distribution patterns
- **Heatmaps**: Identify feature correlations
- **Gauge Charts**: Visual risk score indicator

---

## 🚀 Usage Scenarios

### Scenario 1: Daily Fraud Monitoring
1. Open Dashboard tab
2. Check Key Metrics for daily fraud rate
3. Review Risk Distribution for anomalies
4. If >5% increase, investigate in Analytics tab

### Scenario 2: Transaction Investigation
1. Customer reports suspicious transaction
2. Go to Scoring tab → Single Transaction
3. Enter transaction details
4. View fraud score and confidence
5. Take appropriate action based on risk level

### Scenario 3: Batch Processing
1. Export transactions from your system
2. Go to Scoring tab → Batch Upload
3. Upload CSV file
4. Download scored results
5. Integrate scores into your system

### Scenario 4: Performance Audit
1. Go to System Info tab
2. Check component status
3. Review model metrics (92.85% accuracy)
4. Verify deployment options

### Scenario 5: Fraud Pattern Analysis
1. Go to Analytics tab
2. Review Risk Analysis for confidence patterns
3. Check Feature Importance statistics
4. Use correlation heatmap to identify drivers
5. Export high-risk transactions for investigation

---

## 📊 Key Metrics Explained

| Metric | Range | Interpretation |
|--------|-------|-----------------|
| **Total Transactions** | 0+ | Total scored in current view |
| **Fraud Flagged %** | 0-100% | Percentage flagged as fraud |
| **Avg Risk Score** | 0-100 | Average across all transactions |
| **High Risk Count** | 0+ | Transactions classified as High |
| **Model Accuracy** | 0-100% | Training accuracy (fixed at 92.85%) |

---

## 🔧 Configuration

### Customize Dashboard Title
Edit line in `dashboard.py`:
```python
st.title("🛡️ Fraud Detection Dashboard")
```

### Change Color Scheme
Modify colors in `dashboard.py`:
```python
colors = {'Low': '#2ecc71', 'Medium': '#f39c12', 'High': '#e74c3c'}
```

### Adjust Page Layout
```python
st.set_page_config(
    layout="wide",  # or "centered"
    initial_sidebar_state="expanded"  # or "collapsed"
)
```

---

## 🐛 Troubleshooting

### Dashboard Won't Start
```bash
# Check if streamlit is installed
pip install streamlit

# Check for syntax errors
python -m py_compile dashboard.py
```

### Data Files Not Found
Ensure these files exist in the workspace:
- `sales_with_fraud_indicators.csv` (training data)
- `fraud_system_output/scored_transactions_*.csv` (scored data)
- `ml_model_artifacts.pkl` (trained model)

### Performance Issues
- Dashboard is slow with large datasets (>100k rows)
- Use batch filtering in Analytics tab
- Consider time-based filtering

### Charts Not Displaying
- Clear browser cache: `Ctrl+Shift+Delete`
- Reload page: `F5`
- Check plotly installation: `pip install --upgrade plotly`

---

## 📈 Dashboard Analytics SQL Queries (for Reference)

If you want to query the underlying data:

```python
# Total fraud rate
fraud_rate = scored_data['is_fraud_flagged'].mean() * 100

# Average score by risk level
avg_by_level = scored_data.groupby('predicted_risk_level')['risk_score'].mean()

# Confidence by risk level
conf_by_level = scored_data.groupby('predicted_risk_level')['confidence'].mean()

# Top 10 highest risk transactions
top_risk = scored_data.nlargest(10, 'risk_score')
```

---

## 🚀 Deployment

### Local Development
```bash
streamlit run dashboard.py
```

### Streamlit Cloud (Free Hosting)
1. Push code to GitHub
2. Visit https://streamlit.io/cloud
3. Deploy your app
4. Share public URL

### Docker Container
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements_dashboard.txt .
RUN pip install -r requirements_dashboard.txt
COPY dashboard.py .
EXPOSE 8501
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501"]
```

### Run in Docker
```bash
docker build -t fraud-dashboard:v1.0 .
docker run -p 8501:8501 fraud-dashboard:v1.0
```

---

## 📚 Integration with Production Systems

### Option 1: Embed in Your App
Host dashboard on internal server for team access

### Option 2: Scheduled Reports
```python
# Generate daily report via cron job
streamlit run dashboard.py --logger.level=error
```

### Option 3: REST API + Dashboard
- Use `fraud_scoring_service_api.py` for real-time scoring
- Use dashboard for visualization and analysis

### Option 4: Real-Time Data Integration
Modify data loading section to pull from database:
```python
# Replace CSV loading
scored_data = pd.read_sql(
    "SELECT * FROM scored_transactions WHERE date = TODAY()",
    connection
)
```

---

## 📞 Support & Feedback

For issues or feature requests:
1. Check this documentation
2. Review error messages in browser console (F12)
3. Check terminal output where dashboard was launched

---

## 🎓 Learning Resources

**Streamlit Documentation:** https://docs.streamlit.io
**Plotly Documentation:** https://plotly.com/python
**Fraud Detection Best Practices:** See DEPLOYMENT_GUIDE.md

---

**Last Updated:** 2026-02-09
**Dashboard Version:** 1.0
**Compatible with:** Python 3.8+, Streamlit 1.28+
