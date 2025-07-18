FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libxss1 \
    libasound2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    xdg-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and its browser dependencies
RUN pip install --no-cache-dir playwright && playwright install --with-deps

# Copy environment files early (so they can be overridden in Docker run)
COPY .env.logging .env.logging
COPY .env .env

# Copy source code
COPY . .

# Install editable package
RUN pip install --no-cache-dir -e src/

# Set PYTHONPATH so src modules are accessible
ENV PYTHONPATH=/app/src

# Default command
CMD ["python", "src/sragent_crewai/main.py"]
