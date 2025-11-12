# PCBF 2.1 CSV Validation UI - Docker Image
FROM python:3.11-slim

# Metadaten
LABEL maintainer="your-email@example.com"
LABEL description="PCBF 2.1 CSV Validation UI - Psychologisierungs-Framework"
LABEL version="2.1.5"

# Arbeitsverzeichnis
WORKDIR /app

# System-Dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python-Dependencies kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungs-Code kopieren
COPY . .

# Logs-Verzeichnis erstellen
RUN mkdir -p logs

# Port exponieren
EXPOSE 8002

# Health-Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8002/ || exit 1

# Umgebungsvariablen (können überschrieben werden)
ENV PORT=8002
ENV PYTHONUNBUFFERED=1

# Startbefehl
CMD ["python3", "validation_ui_csv.py"]

