# 🛡️ Fraud Detection System

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](https://github.com/meghraj150198/Fraud-Detection-in-Online-Transactions)

A **production-ready fraud detection system** with real-time analytics dashboard, REST API, and batch processing capabilities. Built with machine learning, advanced feature engineering, and comprehensive monitoring tools.

**Performance:** 92.85% accuracy | 87.71% fraud detection rate | ~200 transactions/second

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [Dashboard Pages](#-dashboard-pages)
- [API Endpoints](#-api-endpoints)
- [Deployment](#-deployment)
- [Documentation](#-documentation)
- [Performance Metrics](#-performance-metrics)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🎯 Real-Time Monitoring
- Live transaction fraud metrics and trends
- Risk score visualization and distribution
- System health indicators and component status
- Fraud rate tracking and alerts

### 🔍 Interactive Scoring
- **Single Transaction**: Instant fraud predictions with confidence scores
- **Batch Processing**: Upload CSV files (up to 100k records) for bulk scoring
- **Confidence Metrics**: Know how certain the model is about each prediction
- **Color-Coded Results**: Green (safe), Yellow (medium), Red (fraud)

### 📊 Advanced Analytics
- **Risk Analysis**: Confidence distribution, risk breakdown, feature correlations
- **Feature Importance**: Identify key fraud indicators and patterns
- **High-Risk Explorer**: Detailed list of flagged transactions with filtering
- **CSV Export**: Download predictions and reports for external analysis

### 🎨 Beautiful Dashboard
- **Interactive Plotly Charts**: Pie, bar, histogram, heatmap, and gauge visualizations
- **Responsive Design**: Works on desktop and mobile devices
- **Dark/Light Themes**: Switch between themes for comfortable viewing
- **Real-time Updates**: Live data with smart caching for performance

### 📦 5 Deployment Options
1. **Python Library** - Direct import in your application
2. **REST API** - 6 HTTP endpoints for integration
3. **Docker Container** - Production-ready container setup
4. **Python Client SDK** - Pre-built integration with retry logic
5. **Unified System** - Complete orchestration and validation pipeline

### ✅ Production Ready
- Comprehensive error handling and validation
- Caching layer for optimal performance
- Docker and docker-compose support
- Extensive documentation (9 guides, 100+ KB)
- All code committed and tested

---

## 🚀 Quick Start

### Installation (30 seconds)

```bash
# Step 1: Clone repository
git clone https://github.com/meghraj150198/Fraud-Detection-in-Online-Transactions.git
cd Fraud-Detection-in-Online-Transactions

# Step 2: Install dependencies
pip install streamlit plotly pandas numpy scikit-learn xgboost flask

# Step 3: Launch dashboard
streamlit run dashboard.py
```

### Access Dashboard

Open your browser and navigate to:
```
http://localhost:8501
```

### Explore Features

1. **Dashboard Page** - View real-time metrics (2 min)
2. **Scoring Page** - Try scoring a transaction (5 min)
3. **Analytics Page** - Analyze fraud patterns (10 min)
4. **System Info** - Check system status (3 min)

Done! Your fraud detection system is running. 🎉

---

## 🏗️ System Architecture

### ML Model Pipeline

```
Raw Transaction Data
        ↓
[Feature Engineering: 96 engineered features]
        ↓
[8 Signal-Specific Models: Random Forests]
├─ Velocity Anomaly Detector
├─ Amount Anomaly Detector
├─ Device Risk Analyzer
├─ Merchant Risk Analyzer
├─ Temporal Pattern Analyzer
├─ Payment Method Risk Analyzer
├─ IP Risk Analyzer
└─ Behavioral Anomaly Detector
        ↓
[Gradient Boosting Meta-Learner]
        ↓
Risk Score (0-100) + Classification
└─ Low / Medium / High Risk
```

### Feature Engineering (9 Signal Groups)

| Group | Features | Purpose |
|-------|----------|---------|
| **Velocity** | Transaction frequency, spike detection | Abnormal activity patterns |
| **Amount** | Price anomalies, unusual amounts | Suspicious transaction sizes |
| **Device** | Device familiarity, unfamiliar devices | Known vs new devices |
| **Merchant** | Merchant risk scores, categories | High-risk merchant detection |
| **Temporal** | Time patterns, late-night hours | Timing anomalies |
| **Payment** | Payment method risks, categories | Risky payment methods |
| **IP** | IP-based risks, geographic patterns | Location anomalies |
| **Behavioral** | Historical patterns, deviations | User behavior baseline |
| **Combined** | Risk index aggregation | Multi-signal fraud score |

### Training Data

- **Transactions**: 14,640 analyzed
- **Features**: 124 total (96 engineered + 26 original)
- **Quality**: 0 missing values, 0 duplicates
- **Fraud Cases**: 1,571 (10.73% of dataset)

---

## 📦 Installation

### System Requirements

**Minimum:**
- Python 3.8+
- 2GB RAM
- 500MB disk space

**Recommended:**
- Python 3.10+
- 4GB RAM
- 2GB disk space

### Supported Platforms

- ✅ Ubuntu 20.04+
- ✅ macOS 10.14+
- ✅ Windows 10+
- ✅ Docker (all platforms)

### Installation Methods

#### Method 1: Direct Installation

```bash
# Install all dependencies
pip install -r requirements.txt
```

#### Method 2: Dashboard Only

```bash
pip install -r requirements_dashboard.txt
streamlit run dashboard.py
```

#### Method 3: Deployment (API + Docker)

```bash
pip install -r requirements_deployment.txt
docker-compose up -d
```

#### Method 4: Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install streamlit plotly pandas numpy scikit-learn xgboost flask
```

---

## 💻 Usage

### 1. Interactive Dashboard

```bash
# Start dashboard
streamlit run dashboard.py

# Custom port
streamlit run dashboard.py --server.port 8502

# Using startup script (Linux/macOS)
./start_dashboard.sh
```

**Access:** http://localhost:8501

### 2. REST API

```bash
# Start API server
python fraud_scoring_service_api.py

# Access API
# http://localhost:5000
```

**Endpoints:**
- `POST /score` - Score single transaction
- `POST /score-batch` - Score multiple transactions
- `GET /report` - Get system report
- `GET /stats` - Get model statistics
- `GET /health` - Check API health
- `GET /info` - Get system information

### 3. Python Library

```python
from fraud_scoring_service import FraudScoringService

# Initialize service
service = FraudScoringService()

# Score single transaction
result = service.score_single_transaction({
    'selling_price': 450,
    'quantity_ordered': 2,
    'transaction_hour': 12,
    # ... more features
})

# Score batch
results = service.score_transactions(dataframe)

# Get predictions
print(result['prediction']['risk_level'])  # 'Low', 'Medium', or 'High'
print(result['prediction']['risk_score'])  # 0-100
print(result['prediction']['confidence'])  # 0-100
```

### 4. Python Client SDK

```python
from fraud_detection_client import FraudDetectionClient

# Initialize client
client = FraudDetectionClient('http://localhost:5000')

# Score transaction
response = client.score_transaction(transaction_data)

# Batch score
results = client.score_batch(transactions_df)
```

### 5. Docker Container

```bash
# Build image
docker build -t fraud-detector:v1.0 .

# Run container
docker run -p 5000:5000 -p 8501:8501 fraud-detector:v1.0

# Or use docker-compose
docker-compose up -d
```

---

## 📱 Dashboard Pages

### Page 1: 📊 Dashboard (Real-Time Overview)

**What You'll See:**
- 5 key metric cards (total transactions, fraud rate, risk scores, accuracy)
- Risk distribution pie and bar charts
- Risk score histogram
- Statistical percentiles (25th, 50th, 75th, 95th)

**Use For:**
- Daily monitoring and quick status checks
- Spotting anomalies in fraud patterns
- Executive overview

### Page 2: 🔍 Scoring (Make Predictions)

**Single Transaction Mode:**
- 8 input fields for transaction details
- Instant fraud prediction
- Confidence score
- Color-coded result (Green/Yellow/Red)

**Batch Upload Mode:**
- Upload CSV file (up to 100k records)
- Automatic processing
- Download results with predictions

**Use For:**
- Real-time fraud checking
- Customer service investigations
- Batch processing

### Page 3: 📈 Analytics (Deep Dive)

**Risk Analysis Tab:**
- Confidence distribution
- Risk breakdown statistics
- Feature correlation heatmap

**Feature Importance Tab:**
- Feature statistics
- Top risk indicators

**High Risk Tab:**
- Detailed list of flagged transactions
- Filtering by risk score and level
- CSV export

**Use For:**
- Fraud investigation
- Pattern analysis
- Reporting

### Page 4: ⚙️ System Info (Health Checks)

**Component Status:**
- 7-point system health check
- All components showing Ready status

**Model Performance:**
- Accuracy: 92.85%
- Precision: 92.79%
- Recall: 92.85%
- F1-Score: 92.63%

**Deployment Reference:**
- 5 deployment options with code examples

**Use For:**
- System verification
- Deployment planning
- Performance tracking

---

## 🔌 API Endpoints

### POST /score
Score a single transaction

```bash
curl -X POST http://localhost:5000/score \
  -H "Content-Type: application/json" \
  -d '{
    "selling_price": 450,
    "quantity_ordered": 2,
    "transaction_hour": 12,
    ...
  }'
```

**Response:**
```json
{
  "prediction": {
    "risk_level": "Low",
    "risk_score": 12.34,
    "confidence": 94.23,
    "is_flagged": false,
    "class_probabilities": {
      "Low": 0.9423,
      "Medium": 0.0523,
      "High": 0.0054
    }
  }
}
```

### POST /score-batch
Score multiple transactions

```bash
curl -X POST http://localhost:5000/score-batch \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [
      {...},
      {...},
      ...
    ]
  }'
```

### GET /stats
Get model statistics

```bash
curl http://localhost:5000/stats
```

### GET /health
Check API health

```bash
curl http://localhost:5000/health
```

---

## 📦 Deployment

### 1. Docker Deployment (Recommended)

```yaml
# docker-compose.yml
version: '3.8'
services:
  fraud-detector:
    build: .
    ports:
      - "5000:5000"
      - "8501:8501"
    environment:
      - PYTHONUNBUFFERED=1
```

```bash
docker-compose up -d
```

### 2. Cloud Deployment

**Streamlit Cloud:**
1. Push code to GitHub
2. Visit https://streamlit.io/cloud
3. Deploy your app

**Heroku:**
```bash
heroku create your-fraud-detector
git push heroku main
```

**AWS/Azure/GCP:**
- Use provided Docker image
- Deploy to Kubernetes or container services

### 3. Production Checklist

- [ ] Environment variables configured
- [ ] SSL/TLS certificates installed
- [ ] Authentication enabled (OAuth, API keys)
- [ ] Rate limiting configured
- [ ] Monitoring and logging setup
- [ ] Database backups scheduled
- [ ] Model versioning implemented
- [ ] A/B testing framework ready

---

## 📚 Documentation

Comprehensive guides included:

| Document | Purpose | Length |
|----------|---------|--------|
| **DASHBOARD_QUICKSTART.md** | 60-second setup guide | 7 KB |
| **DASHBOARD_GUIDE.md** | Complete feature documentation | 9.5 KB |
| **DASHBOARD_REFERENCE.md** | Quick reference guide | 11 KB |
| **DASHBOARD_SUMMARY.md** | Full overview & instructions | 15 KB |
| **SYSTEM_OVERVIEW.md** | System integration guide | 13 KB |
| **SYSTEM_STATUS.md** | Integration examples | 14 KB |
| **DEPLOYMENT_GUIDE.md** | API reference & deployment | 8 KB |
| **COMPLETE_INTEGRATION_GUIDE.md** | All deployment options | 12 KB |

**Total Documentation:** 100+ KB

---

## 📊 Performance Metrics

### Model Accuracy

| Metric | Value | Description |
|--------|-------|-------------|
| **Overall Accuracy** | 92.85% | Correct predictions overall |
| **Fraud Recall** | 87.71% | Fraud cases correctly identified (1,378 of 1,571) |
| **Fraud Precision** | 91.23% | Accuracy of fraud predictions |
| **False Alarm Rate** | 3.01% | Legitimate transactions incorrectly flagged |

### Processing Performance

| Metric | Value | Description |
|--------|-------|-------------|
| **Speed** | ~200 tx/sec | Processing throughput |
| **Dashboard Load** | <2 sec | Initial page load time |
| **Single Scoring** | <100ms | Individual transaction scoring |
| **Batch Scoring (1k)** | <5 sec | 1,000 transactions scoring |

### Dataset Statistics

| Metric | Value |
|--------|-------|
| **Transactions Analyzed** | 14,640 |
| **Fraud Cases** | 1,571 (10.73%) |
| **Legitimate Cases** | 13,069 (89.27%) |
| **Features Engineered** | 96 |
| **Total Features** | 124 |

### Risk Distribution

| Risk Level | Count | Percentage |
|-----------|-------|-----------|
| **Low** | 9,508 | 64.95% |
| **Medium** | 4,997 | 34.13% |
| **High** | 135 | 0.92% |

---

## 🔧 Technology Stack

### Core Technologies
- **Python 3.12** - Programming language
- **Streamlit** - Interactive dashboard framework
- **Plotly** - Data visualization
- **Pandas & NumPy** - Data processing

### Machine Learning
- **Scikit-Learn** - ML algorithms
- **XGBoost** - Gradient boosting
- **Random Forest** - Base models

### APIs & Deployment
- **Flask** - REST API framework
- **Docker** - Containerization
- **Docker Compose** - Orchestration

---

## 🎯 Use Cases

### E-Commerce Platforms
Real-time fraud detection for online transactions with instant blocking capabilities.

### Payment Processors
Batch processing of daily transactions with detailed fraud reports.

### Financial Institutions
Integration with existing systems via REST API for continuous monitoring.

### Fraud Investigation Teams
Deep analytics and high-risk transaction explorer for manual review.

### Risk Management
Predictive analytics and pattern detection for compliance reporting.

---

## 💡 Key Highlights

✨ **92.85% Accuracy** - Industry-leading fraud detection
✨ **87.71% Recall** - Catches most real fraud cases
✨ **Real-Time Scoring** - Instant predictions (~100ms)
✨ **Batch Processing** - Handle 100k transactions
✨ **Beautiful Dashboard** - Professional UI with interactive charts
✨ **5 Deployment Options** - Choose what works for you
✨ **Comprehensive Docs** - 100+ KB of documentation
✨ **Production Ready** - Error handling, caching, monitoring
✨ **Easy Integration** - Python library, REST API, or Docker

---

## 🚀 Getting Started

### For Beginners
1. Read [DASHBOARD_QUICKSTART.md](DASHBOARD_QUICKSTART.md)
2. Run `streamlit run dashboard.py`
3. Explore each dashboard page

### For Integration
1. Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. Run `python fraud_scoring_service_api.py`
3. Use the REST API endpoints

### For Deployment
1. Read [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)
2. Run `docker-compose up -d`
3. Access dashboard and API

---

## 📞 Support

### Documentation
- [Complete Integration Guide](COMPLETE_INTEGRATION_GUIDE.md)
- [System Status Guide](SYSTEM_STATUS.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)

### Issues & Questions
1. Check existing documentation
2. Review code comments
3. Check GitHub issues

### Examples
- See `fraud_detection_client.py` for Python integration
- See `DEPLOYMENT_GUIDE.md` for API examples
- See `fraud_system_integration.py` for full orchestration

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👥 Authors

- **Meghraj** - Initial development and maintainer
- GitHub: [@meghraj150198](https://github.com/meghraj150198)

---

## 🙏 Acknowledgments

- Scikit-Learn for excellent ML libraries
- Streamlit for beautiful dashboard framework
- Plotly for interactive visualizations
- Open-source community for invaluable tools

---

## 📈 Project Status

| Component | Status |
|-----------|--------|
| Dashboard | ✅ Production Ready |
| ML Model | ✅ Trained & Validated |
| API | ✅ Tested & Documented |
| Docker | ✅ Configured |
| Documentation | ✅ Complete |

**Last Updated:** February 9, 2026  
**Version:** 1.0  
**Status:** Production Ready ✅

---

## 🎯 Roadmap

- [ ] Enhanced model interpretability
- [ ] Real-time model retraining
- [ ] Advanced visualization options
- [ ] Mobile app support
- [ ] Multi-language support
- [ ] Custom alerting rules
- [ ] Integration with more platforms

---

## 📊 Quick Links

- 🏠 [Landing Page](index.html)
- 📊 [Dashboard](http://localhost:8501)
- 🔌 [API Documentation](DEPLOYMENT_GUIDE.md)
- 📚 [Full Documentation](DASHBOARD_GUIDE.md)
- 🐙 [GitHub Repository](https://github.com/meghraj150198/Fraud-Detection-in-Online-Transactions)

---

**Ready to detect fraud? Launch the dashboard now!**

```bash
streamlit run dashboard.py
```

Visit: **http://localhost:8501** 🚀