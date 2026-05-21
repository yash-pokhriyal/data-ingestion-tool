# =========================================================
# Production Grade Log Analyzer Container
# =========================================================

# Lightweight stable Python runtime
FROM python:3.9-slim

# Prevent .pyc generation
ENV PYTHONDONTWRITEBYTECODE=1

# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1

# Internal workspace
WORKDIR /app

# Copy dependency manifest first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Default analyzer entrypoint
ENTRYPOINT ["python", "log-analyzer.py"]