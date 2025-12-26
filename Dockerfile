# SeedVR2 Video Upscaler - Docker Image
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv \
    ffmpeg libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev \
    curl git && \
    rm -rf /var/lib/apt/lists/* && \
    ln -sf /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir flask flask-cors flasgger gunicorn fastmcp werkzeug

# Copy application code
COPY . .

# Create directories
RUN mkdir -p /app/models/SEEDVR2 /app/uploads /app/outputs /app/static /app/templates

# Expose port
EXPOSE 8200

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8200/health || exit 1

# Default command
CMD ["python", "server.py"]