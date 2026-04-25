# ── Build stage ────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ── Runtime stage ───────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Install runtime system dependencies (LibreOffice for slide → PNG conversion)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r learnforge && useradd -r -g learnforge learnforge

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/learnforge/.local

# Copy application code
COPY --chown=learnforge:learnforge . .

# Create temp directories for video processing and local data storage
RUN mkdir -p /tmp/learnforge /app/data && chown -R learnforge:learnforge /tmp/learnforge /app/data

USER learnforge

ENV PATH=/home/learnforge/.local/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
