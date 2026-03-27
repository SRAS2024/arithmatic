FROM node:20-bookworm-slim

# Install system dependencies for Python, OCR, and PDF processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libfontconfig1 \
    fonts-liberation \
    fonts-dejavu-core \
    curl \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Meteor
RUN curl https://install.meteor.com/ | sh

# Create app directory
WORKDIR /app

# Setup Python virtual environment and install dependencies
COPY python/requirements.txt /app/python/requirements.txt
RUN python3 -m venv /app/python/venv \
    && /app/python/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /app/python/venv/bin/pip install --no-cache-dir -r /app/python/requirements.txt

# Copy package files and install Node dependencies
COPY package.json /app/
COPY .meteor /app/.meteor/
RUN meteor npm install --production

# Copy application code
COPY . /app/

# Make scripts executable
RUN chmod +x scripts/*.sh

# Create temp directory
RUN mkdir -p /app/server/temp && chmod 777 /app/server/temp

# Expose port
ENV PORT=3000
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Start command
CMD ["bash", "scripts/railway-start.sh"]
