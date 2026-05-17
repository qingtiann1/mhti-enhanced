# MHTI Enhanced - Standalone Docker Image
# ==========================================
# Build: docker build -t mhti-enhanced:latest .
# Run:   docker run -d -p 8000:8000 -v /your/data:/app/data -v /your/media:/media:ro -v /your/output:/output mhti-enhanced:latest
#
# OR use docker-compose.yml for one-click deployment.

FROM python:3.11-slim

LABEL org.opencontainers.image.title="MHTI Enhanced"
LABEL org.opencontainers.image.description="Multi-source TV series metadata scraper with Bangumi R18 support"
LABEL org.opencontainers.image.source="https://github.com/qingtiann1/mhti-enhanced"

# Install system dependencies including Caddy
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
    | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
    | tee /etc/apt/sources.list.d/caddy-stable.list \
    && apt-get update && apt-get install -y --no-install-recommends caddy \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server/ ./server/
COPY static/ ./static/

# Copy Caddy config and startup script
COPY Caddyfile /etc/caddy/Caddyfile
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Data directory for scraper database
VOLUME ["/app/data"]

# Expose main entry port (Caddy: 8000 -> API:8001)
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -sf http://localhost:8000/health || exit 1

ENTRYPOINT ["/app/start.sh"]
