# Fraud Detection Service - Docker Deployment

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_deployment.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_deployment.txt

# Copy application files
COPY ml_model_artifacts.pkl .
COPY sales_with_fraud_indicators.csv .
COPY fraud_scoring_service.py .
COPY fraud_scoring_service_api.py .

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Start API
CMD ["python", "fraud_scoring_service_api.py"]

# Build: docker build -t fraud-detector:v1.0 .
# Run:   docker run -p 5000:5000 fraud-detector:v1.0
