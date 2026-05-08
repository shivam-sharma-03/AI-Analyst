# 1. Standard Lightweight Image
FROM python:3.11-slim

# 2. Install system dependencies (For PostgreSQL connectivity)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Set working directory
WORKDIR /app

# 4. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copy the entire project
COPY . .

# 6. Set Environment Path (Taki folders mil jayein)
ENV PYTHONPATH=/app