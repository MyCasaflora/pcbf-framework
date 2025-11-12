# PCBF 2.1 Framework - Deployment Guide

## Schritt-für-Schritt-Anleitung zur Bereitstellung

---

## 🎯 Voraussetzungen

### System-Anforderungen

- **Betriebssystem**: Linux (Ubuntu 22.04+), macOS, oder Windows mit WSL
- **Python**: Version 3.11 oder höher
- **RAM**: Mindestens 2 GB (empfohlen: 4 GB)
- **CPU**: 2+ Cores empfohlen für parallele Verarbeitung
- **Festplatte**: 500 MB für Framework + Dependencies

### Externe Services

- **OpenRouter API-Key**: Erforderlich für LLM-Zugriff
  - Registrierung: https://openrouter.ai/
  - Kosten: Pay-per-use (ca. $0.10-0.20 pro 100 Profile)

---

## 📦 Installation

### Option 1: Lokale Installation (Entwicklung)

#### Schritt 1: Repository klonen oder Dateien kopieren

```bash
# Falls Git-Repository:
git clone <repository-url>
cd pcbf_framework

# Oder: Dateien manuell kopieren
cp -r /pfad/zum/framework /home/ubuntu/pcbf_framework
cd /home/ubuntu/pcbf_framework
```

#### Schritt 2: Python-Dependencies installieren

```bash
# Virtual Environment erstellen (empfohlen)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows

# Dependencies installieren
pip3 install -r requirements.txt
```

**Erwartete Ausgabe:**
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 pydantic-2.5.0 ...
```

#### Schritt 3: Umgebungsvariablen setzen

**Option A: Export (temporär)**

```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

**Option B: .env-Datei (persistent)**

```bash
# .env-Datei erstellen
cat > .env << EOF
OPENROUTER_API_KEY=sk-or-v1-...
EOF
```

**Option C: System-Environment (permanent)**

```bash
# Linux/Mac: In ~/.bashrc oder ~/.zshrc
echo 'export OPENROUTER_API_KEY="sk-or-v1-..."' >> ~/.bashrc
source ~/.bashrc

# Windows: Systemsteuerung → Umgebungsvariablen
```

#### Schritt 4: Logs-Verzeichnis erstellen

```bash
mkdir -p logs
```

#### Schritt 5: Server starten

```bash
python3 app.py
```

**Erwartete Ausgabe:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

#### Schritt 6: Testen

```bash
# In neuem Terminal:
curl http://localhost:8000/health

# Erwartete Antwort:
{"status":"healthy","timestamp":1729482000.123}
```

---

### Option 2: Docker-Deployment (Produktion)

#### Schritt 1: Dockerfile erstellen

```bash
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

# Arbeitsverzeichnis
WORKDIR /app

# Dependencies kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Framework-Dateien kopieren
COPY . .

# Logs-Verzeichnis erstellen
RUN mkdir -p /app/logs

# Port exponieren
EXPOSE 8000

# Server starten
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
```

#### Schritt 2: Docker-Image bauen

```bash
docker build -t pcbf-framework:2.1.0 .
```

#### Schritt 3: Container starten

```bash
docker run -d \
  --name pcbf-framework \
  -p 8000:8000 \
  -e OPENROUTER_API_KEY="sk-or-v1-..." \
  -v $(pwd)/logs:/app/logs \
  pcbf-framework:2.1.0
```

#### Schritt 4: Status prüfen

```bash
docker ps
docker logs pcbf-framework
curl http://localhost:8000/health
```

---

### Option 3: Docker Compose (Multi-Container)

#### Schritt 1: docker-compose.yml erstellen

```yaml
version: '3.8'

services:
  pcbf-api:
    build: .
    container_name: pcbf-framework
    ports:
      - "8000:8000"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: Nginx als Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: pcbf-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - pcbf-api
    restart: unless-stopped
```

#### Schritt 2: Starten

```bash
# .env-Datei mit API-Key erstellen
echo "OPENROUTER_API_KEY=sk-or-v1-..." > .env

# Services starten
docker-compose up -d

# Logs anzeigen
docker-compose logs -f pcbf-api
```

---

## 🌐 Produktion-Deployment

### Option 1: VPS/Cloud-Server (DigitalOcean, AWS EC2, etc.)

#### Schritt 1: Server vorbereiten

```bash
# SSH-Verbindung
ssh user@your-server-ip

# System aktualisieren
sudo apt update && sudo apt upgrade -y

# Python installieren
sudo apt install python3.11 python3.11-venv python3-pip -y

# Git installieren (falls benötigt)
sudo apt install git -y
```

#### Schritt 2: Framework deployen

```bash
# Framework-Dateien hochladen
scp -r /local/path/pcbf_framework user@server:/home/user/

# Oder via Git
git clone <repository-url> /home/user/pcbf_framework

# Auf Server:
cd /home/user/pcbf_framework
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Schritt 3: Systemd-Service erstellen

```bash
sudo nano /etc/systemd/system/pcbf-framework.service
```

**Inhalt:**

```ini
[Unit]
Description=PCBF 2.1 Framework API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/pcbf_framework
Environment="PATH=/home/ubuntu/pcbf_framework/venv/bin"
Environment="OPENROUTER_API_KEY=sk-or-v1-..."
ExecStart=/home/ubuntu/pcbf_framework/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Schritt 4: Service aktivieren

```bash
sudo systemctl daemon-reload
sudo systemctl enable pcbf-framework
sudo systemctl start pcbf-framework
sudo systemctl status pcbf-framework
```

#### Schritt 5: Nginx als Reverse Proxy

```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/pcbf-framework
```

**Inhalt:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Aktivieren:**

```bash
sudo ln -s /etc/nginx/sites-available/pcbf-framework /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Schritt 6: SSL mit Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

### Option 2: Kubernetes-Deployment

#### deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pcbf-framework
  labels:
    app: pcbf-framework
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pcbf-framework
  template:
    metadata:
      labels:
        app: pcbf-framework
    spec:
      containers:
      - name: pcbf-api
        image: your-registry/pcbf-framework:2.1.0
        ports:
        - containerPort: 8000
        env:
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: pcbf-secrets
              key: openrouter-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: pcbf-framework-service
spec:
  selector:
    app: pcbf-framework
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

**Deployen:**

```bash
# Secret erstellen
kubectl create secret generic pcbf-secrets \
  --from-literal=openrouter-api-key='sk-or-v1-...'

# Deployment
kubectl apply -f deployment.yaml

# Status prüfen
kubectl get pods
kubectl get services
```

---

## 🔧 Konfiguration

### Umgebungsvariablen

| Variable | Beschreibung | Erforderlich | Default |
|----------|--------------|--------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API-Key | Ja | - |
| `DATABASE_URL` | Datenbank-URL (optional) | Nein | `sqlite:///./pcbf.db` |

### config.py anpassen

Für produktionsspezifische Anpassungen:

```python
# config.py

# API-Einstellungen
API_HOST = "0.0.0.0"  # Alle Interfaces
API_PORT = 8000

# Model-Auswahl
DEFAULT_MODEL = "gpt-4.1-mini"  # Oder "gpt-4.1-nano" für niedrigere Kosten

# Confidence-Schwellenwerte anpassen
CONFIDENCE_THRESHOLDS = {
    "high": 75,    # Von 80 auf 75 senken für mehr "High"-Ergebnisse
    "medium": 55,  # Von 60 auf 55
    "low": 35      # Von 40 auf 35
}

# Logging
LOG_LEVEL = "INFO"  # "DEBUG" für Entwicklung, "INFO" für Produktion
```

---

## 📊 Monitoring & Logging

### Logs anzeigen

**Lokale Installation:**

```bash
tail -f logs/pcbf.log
```

**Docker:**

```bash
docker logs -f pcbf-framework
```

**Systemd:**

```bash
sudo journalctl -u pcbf-framework -f
```

### Log-Rotation einrichten

```bash
sudo nano /etc/logrotate.d/pcbf-framework
```

**Inhalt:**

```
/home/ubuntu/pcbf_framework/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
    postrotate
        systemctl reload pcbf-framework > /dev/null 2>&1 || true
    endscript
}
```

### Prometheus-Metriken (optional)

```python
# In app.py hinzufügen:
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(...)
Instrumentator().instrument(app).expose(app)
```

---

## 🔒 Sicherheit

### 1. API-Key-Sicherheit

✅ **Niemals** API-Keys im Code speichern  
✅ Umgebungsvariablen oder Secrets-Manager verwenden  
✅ API-Keys regelmäßig rotieren

### 2. HTTPS erzwingen

```nginx
# Nginx: HTTP → HTTPS Redirect
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### 3. Rate-Limiting

```python
# In app.py hinzufügen:
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/analyze")
@limiter.limit("10/minute")  # Max 10 Requests pro Minute
async def analyze_profiles(...):
    ...
```

### 4. Firewall-Regeln

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

---

## 🧪 Testing nach Deployment

### 1. Health-Check

```bash
curl https://your-domain.com/health
```

**Erwartete Antwort:**
```json
{"status":"healthy","timestamp":1729482000.123}
```

### 2. Vollständiger API-Test

```bash
# Test-Script ausführen
python3 test_api.py
```

### 3. Load-Testing

```bash
# Apache Bench
ab -n 100 -c 10 https://your-domain.com/health

# Oder: wrk
wrk -t4 -c100 -d30s https://your-domain.com/health
```

---

## 🔄 Updates & Wartung

### Framework aktualisieren

```bash
# Backup erstellen
cp -r /home/ubuntu/pcbf_framework /home/ubuntu/pcbf_framework.backup

# Neue Version deployen
cd /home/ubuntu/pcbf_framework
git pull  # Oder Dateien manuell kopieren

# Dependencies aktualisieren
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Service neu starten
sudo systemctl restart pcbf-framework
```

### Datenbank-Migration (falls verwendet)

```bash
# Alembic für Migrations
pip install alembic
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

---

## 📈 Skalierung

### Horizontale Skalierung

**Option 1: Load Balancer + mehrere Instanzen**

```nginx
# Nginx Load Balancer
upstream pcbf_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location / {
        proxy_pass http://pcbf_backend;
    }
}
```

**Option 2: Kubernetes Auto-Scaling**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: pcbf-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: pcbf-framework
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## 🆘 Troubleshooting

### Problem: Server startet nicht

**Prüfen:**

```bash
# Logs anzeigen
sudo journalctl -u pcbf-framework -n 50

# Port bereits belegt?
sudo lsof -i :8000

# Python-Version korrekt?
python3 --version  # Sollte 3.11+ sein
```

### Problem: API-Key-Fehler

**Prüfen:**

```bash
# Umgebungsvariable gesetzt?
echo $OPENROUTER_API_KEY

# In Service-File korrekt?
sudo systemctl show pcbf-framework | grep OPENROUTER
```

### Problem: Niedrige Performance

**Optimierungen:**

```bash
# Mehr Worker-Prozesse
uvicorn app:app --workers 4

# Gunicorn mit Uvicorn-Worker
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
```

---

## 📞 Support

Bei Deployment-Problemen:

1. Logs prüfen: `logs/pcbf.log`
2. Health-Endpoint testen: `/health`
3. Test-Script ausführen: `python3 test_api.py`
4. Entwicklungsteam kontaktieren

---

**PCBF 2.1 Framework** - Deployment Guide v1.0

