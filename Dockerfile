# Multi-stage Docker build for Product Processing Cron Job
FROM python:3.10-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV TZ=Asia/Ho_Chi_Minh

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM base as production

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Copy application code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p /app/data /app/images /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "cron_job.py"]





