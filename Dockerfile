FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt domain-requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r domain-requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose API port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.stockalpha.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
