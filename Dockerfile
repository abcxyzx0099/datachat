# =============================================================================
# DataChat SPSS Analyzer - Dockerfile
# =============================================================================
# Multi-stage build for optimized image size
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Base image with system dependencies
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Prevent Python from creating .pyc files
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # PSPP statistical analysis tool
    pspp \
    # Build essentials for Python packages
    gcc \
    g++ \
    # Required for some Python packages
    libc-dev \
    # Clean up to reduce image size
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# -----------------------------------------------------------------------------
# Stage 2: Dependencies installation
# -----------------------------------------------------------------------------
FROM base AS dependencies

# Set working directory
WORKDIR /app

# Copy requirements file first for Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 3: Application
# -----------------------------------------------------------------------------
FROM base AS app

# Copy Python dependencies from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Set working directory
WORKDIR /app

# Copy application code
COPY agent/ ./agent/
COPY config/ ./config/
COPY utils/ ./utils/

# Copy requirements file (for reference)
COPY requirements.txt .

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/output /app/temp /app/logs /app/checkpoints

# Create non-root user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 -m -d /app appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose ports
# 8123: LangGraph server
# 3000: Agent Chat UI (if running in same container)
EXPOSE 8123 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import agent.graph; print('OK')" || exit 1

# Default command - start LangGraph development server
CMD ["python", "-m", "langgraph", "dev", "--port", "8123", "--host", "0.0.0.0"]
