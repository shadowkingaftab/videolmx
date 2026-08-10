# ==========================================
# Stage 1: Base
# ==========================================
FROM python:3.14-slim-bookworm AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    build-essential \
    libpq-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgbm1 \
    libasound2 \
    libatspi2.0-0 \
    libxshmfence1 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright dependencies
RUN apt-get update && apt-get install -y \
    libwoff1 \
    libopus0 \
    libwebp7 \
    libwebpdemux2 \
    libwebpmux3 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    libopenjp2-7 \
    libjpeg62-turbo \
    libpng16-16 \
    libavcodec58 \
    libavformat58 \
    libavutil56 \
    libavdevice58 \
    libavfilter7 \
    libavcodec-extra58 \
    && rm -rf /var/lib/apt/lists/*

# Install FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# ==========================================
# Stage 2: Development
# ==========================================
FROM base AS development

# Install dependencies with dev packages
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --with dev

# Install Playwright browsers
RUN playwright install --with-deps chromium firefox webkit
RUN playwright install-deps

# Copy source code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create necessary directories
RUN mkdir -p /app/uploads /app/exports /app/cache /app/logs

# Set permissions
RUN chmod -R 755 /app/uploads /app/exports /app/cache /app/logs

# Expose port
EXPOSE 8000

# Default command (will be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ==========================================
# Stage 3: Builder
# ==========================================
FROM base AS builder

# Install production dependencies only
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-dev

# Install Playwright browsers (production)
RUN playwright install --with-deps chromium firefox webkit
RUN playwright install-deps

# Copy source code
COPY . .

# Run type checking and linting
RUN mypy app/ --ignore-missing-imports || true
RUN ruff check app/ || true

# ==========================================
# Stage 4: Production
# ==========================================
FROM python:3.14-slim-bookworm AS production

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgbm1 \
    libasound2 \
    libatspi2.0-0 \
    libxshmfence1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --gid 1001 appuser

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy Playwright browsers from builder
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright
COPY --from=builder /usr/local/lib/python3.11/site-packages/playwright/driver /usr/local/lib/python3.11/site-packages/playwright/driver

# Copy application code
COPY --from=builder /app /app

# Create necessary directories
RUN mkdir -p /app/uploads /app/exports /app/cache /app/logs \
    && chown -R appuser:appgroup /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Production command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
