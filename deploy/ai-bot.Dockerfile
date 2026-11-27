# The ai engine's Discord bot. Built by deploy/docker-compose.yml (context: the repository root).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ai ./ai
RUN useradd --create-home --uid 1000 kogane && mkdir -p /data && chown kogane /data
USER kogane
CMD ["python", "-m", "ai.bot"]
