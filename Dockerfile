# Use official Python 3.11 slim image for smaller size and better security
FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory inside the container
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code (excluding files in .dockerignore)
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs

# Health check to ensure the application is running properly
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command (optional – overridden by docker-compose)
CMD ["python", "bot.py"]
