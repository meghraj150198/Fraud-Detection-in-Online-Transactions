# 🎯 Dashboard Quick Start

**Fraud Detection Dashboard** is an interactive real-time analytics platform for monitoring fraud detection model performance and scoring transactions.

---

## ⚡ 60-Second Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements_dashboard.txt
```

### Step 2: Make Script Executable
```bash
chmod +x start_dashboard.sh
```

### Step 3: Start Dashboard
```bash
./start_dashboard.sh
# or directly:
streamlit run dashboard.py
```

### Step 4: Open in Browser
The dashboard will automatically open at `http://localhost:8501`

---

## 🎨 Dashboard Pages Overview

### 📊 **Dashboard (Main Overview)**
- **Real-time metrics**: Total transactions, fraud rate, risk scores
- **Risk charts**: Distribution of Low/Medium/High risk transactions
- **Statistical summary**: Risk score percentiles

**Perfect for**: Daily monitoring, quick status checks

---

### 🔍 **Scoring (Make Predictions)**
**Single Transaction:**
1. Fill in transaction details
2. Click "Score Transaction"
3. Get instant fraud prediction with confidence score

**Batch Upload:**
1. Upload CSV file with transactions
2. Click "Score Batch"
3. Download results with fraud predictions

**Perfect for**: Real-time fraud checking, batch processing

---

### 📈 **Analytics (Deep Dive)**
3 advanced analysis tabs:

**Risk Analysis Tab:**
- Confidence distribution histogram
- Risk statistics by category
- Feature correlation heatmap

**Feature Importance Tab:**
- Feature statistics
- Top risk indicators
- High-risk transaction details

**High Risk Tab:**
- Detailed list of flagged transactions
- Filter by risk score and level
- Export high-risk transactions to CSV

**Perfect for**: Fraud investigation, pattern analysis, reporting

---

### ⚙️ **System Info (Health Check)**
- Model metadata and performance metrics
- Component status (✅ Ready indicators)
- Deployment options
- Quick links to documentation

**Perfect for**: System verification, deployment reference

---

## 🎯 Common Tasks

### Task 1: Score a Single Transaction
```
Dashboard → Scoring (page) → Single Transaction
1. Enter details (price, quantity, hour, flags, scores)
2. Click "🎯 Score Transaction"
3. View result (Green/Yellow/Red with score)
```

**Example:** Find if a $500 purchase at 2 AM on unfamiliar device is fraud
- Set Selling Price: 500
- Set Transaction Hour: 2
- Set Device Familiarity: 10
- Result: Shows risk level and confidence

---

### Task 2: Check Daily Fraud Trends
```
Dashboard → Dashboard (main)
1. Review "Key Metrics" card
2. Check "Risk Distribution" charts
3. Look for changes from previous day
```

**What to watch:** Fraud rate should stay ~30-35%, any sudden spike indicates issue

---

### Task 3: Export High-Risk Transactions
```
Dashboard → Analytics → High Risk (tab)
1. Set "Minimum Risk Score" filter
2. Click "📥 Download Flagged Transactions"
3. Save CSV file for investigation
```

**Output:** CSV with columns: transaction_id, risk_score, risk_level, confidence, probabilities

---

### Task 4: Verify System Health
```
Dashboard → System Info (page)
1. Check all components show "✅ Ready"
2. Review Model Performance metrics
3. Note deployment options
```

**All Green?** System is production-ready!

---

## 📱 Browser Tips

- **Recommended**: Chrome, Firefox, Edge (latest versions)
- **Mobile**: Works on mobile browsers but better on desktop
- **Performance**: Dashboard updates in seconds with cached data
- **Refresh**: Use F5 or Ctrl+R to reload dashboard safely

---

## 🔧 Customization

### Change Dashboard Title
Edit `dashboard.py`, find line with `st.title()` and change text

### Adjust Color Scheme  
Modify color definitions around line 40:
```python
colors = {'Low': '#2ecc71', 'Medium': '#f39c12', 'High': '#e74c3c'}
```

### Hide Sidebar Elements
Comment out sidebar sections in `dashboard.py` between `with st.sidebar:` blocks

### Add Your Logo
Add HTML/CSS in the header section to display custom branding

---

## 🐛 Troubleshooting

### Dashboard crashes on startup
```bash
# Check Python syntax
python -m py_compile dashboard.py

# Check dependencies
python -c "import streamlit; import plotly; print('✓ OK')"
```

### "No scored data available" message
```bash
# Generate scored data first
python fraud_system_integration.py

# Then restart dashboard
streamlit run dashboard.py
```

### Charts not displaying
```bash
# Clear browser cache: Ctrl+Shift+Delete
# Reload page: F5
# Reinstall plotly: pip install --upgrade plotly
```

### Performance is slow
- Dashboard works best with <100k row datasets
- Use filters in Analytics tab to reduce data
- Close other browser tabs

---

## 📊 Example Workflow

**Daily Morning Routine (5 minutes):**

1. **Open dashboard** → `streamlit run dashboard.py`
2. **Check Dashboard tab** → Review Key Metrics
3. **Check for spikes** → Look at Risk Distribution
4. **Export high-risk** → Analytics → High Risk → Download
5. **Review data** → Open CSV, investigate flagged transactions
6. **Close dashboard** → Ctrl+C

---

## 🚀 Advanced Features

### Keyboard Shortcuts
- `R` - Rerun entire script
- `C` - Clear cache
- `V` - Toggle theme (dark/light)

### URL Parameters
```
# Add to dashboard URL to customize
?page=analytics  # Load specific page
```

### Caching
Dashboard caches data for performance:
- Force refresh: `st.cache_data.clear()`
- Disable cache: Remove `@st.cache_data` decorators

---

## 📚 Full Documentation

See **[DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)** for:
- Detailed feature descriptions
- Analytics deep dive
- Deployment options
- Integration patterns
- SQL query examples
- Docker setup

---

## 🎓 Learning Path

1. **Start**: Read this Quick Start guide
2. **Explore**: Try Dashboard page → Click around
3. **Score**: Score a transaction in Scoring page
4. **Analyze**: Review Analytics tab
5. **Reference**: Check System Info for deployment options
6. **Master**: Read full DASHBOARD_GUIDE.md

---

## ✅ Verification Checklist

Before using in production:

- [ ] Dashboard starts without errors
- [ ] All 4 pages load (Dashboard, Scoring, Analytics, System Info)
- [ ] Metrics display actual data (not placeholder)
- [ ] Can score a single transaction
- [ ] Can upload and score batch CSV
- [ ] Can export high-risk transactions
- [ ] System Info shows all components as Ready
- [ ] Charts render properly

---

## 💡 Pro Tips

1. **Bookmark dashboard URL** for quick access each day
2. **Set alerts** based on fraud rate metrics
3. **Schedule batch scoring** during off-peak hours
4. **Export daily reports** for audit trail
5. **Monitor confidence scores** - low confidence means uncertain predictions
6. **Check feature correlation** to understand what drives fraud signals

---

## 🔗 Related Files

- [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) - Full feature documentation
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - API reference
- [fraud_scoring_service_api.py](fraud_scoring_service_api.py) - REST API
- [fraud_scoring_service.py](fraud_scoring_service.py) - Core library

---

**Ready to start?** Run: `streamlit run dashboard.py` 🚀

Last Updated: 2026-02-09
