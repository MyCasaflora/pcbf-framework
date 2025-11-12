# PCBF 2.1 - Production Deployment Guide

## 🚀 Dauerhafte Bereitstellung als Systemd-Service

---

## 📋 Übersicht

Die PCBF 2.1 CSV Validation UI ist jetzt als **dauerhafter Systemd-Service** konfiguriert und läuft automatisch:

- ✅ **Automatischer Start** beim System-Boot
- ✅ **Automatischer Neustart** bei Abstürzen
- ✅ **Logging** in Systemd-Journal und Dateien
- ✅ **Ressourcen-Limits** (2GB RAM, 200% CPU)
- ✅ **Health-Checks** mit automatischer Wiederherstellung
- ✅ **Management-Scripts** für einfache Verwaltung

---

## 🎯 Schnellstart

### Service-Status prüfen

```bash
cd /home/ubuntu/pcbf_framework
./manage.sh status
```

**Ausgabe:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PCBF 2.1 CSV Validation UI Manager
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Service Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Service: ✅ Läuft
Gestartet: Wed 2025-11-12 13:03:59 EST
Port 8002: ✅ Erreichbar
Logs: 4.0K (2 Zeilen)
```

---

## 🔧 Management-Befehle

### 1. Status anzeigen

```bash
./manage.sh status
```

Zeigt:
- Service-Status (läuft/gestoppt)
- Uptime
- Port-Erreichbarkeit
- Log-Größe

---

### 2. Service starten

```bash
./manage.sh start
```

Startet den Service (falls gestoppt).

---

### 3. Service stoppen

```bash
./manage.sh stop
```

Stoppt den Service.

---

### 4. Service neu starten

```bash
./manage.sh restart
```

Stoppt und startet den Service neu (z.B. nach Code-Änderungen).

---

### 5. Logs anzeigen

```bash
./manage.sh logs
```

Zeigt die letzten 50 Log-Zeilen.

---

### 6. Logs in Echtzeit folgen

```bash
./manage.sh follow
```

Folgt den Logs in Echtzeit (Ctrl+C zum Beenden).

---

## 📦 Deployment-Workflow

### Erstmaliges Deployment

```bash
cd /home/ubuntu/pcbf_framework
./deploy.sh
```

**Das Script:**
1. ✅ Prüft Arbeitsverzeichnis
2. ✅ Prüft Python-Dependencies
3. ✅ Erstellt Logs-Verzeichnis
4. ✅ Stoppt alte Prozesse
5. ✅ Installiert Systemd-Service
6. ✅ Aktiviert und startet Service
7. ✅ Führt Health-Check durch

**Ausgabe:**
```
🚀 PCBF 2.1 CSV Validation UI - Deployment
==========================================

1. Prüfe Arbeitsverzeichnis...
✅ Arbeitsverzeichnis OK

2. Prüfe Python-Dependencies...
✅ Dependencies OK

3. Erstelle Logs-Verzeichnis...
✅ Logs-Verzeichnis erstellt

4. Stoppe alte Prozesse...
✅ Alte Prozesse gestoppt

5. Installiere Systemd-Service...
✅ Service-Datei installiert

6. Aktiviere und starte Service...
✅ Service läuft

7. Führe Health-Check durch...
✅ Server antwortet auf Port 8002

==========================================
✅ Deployment erfolgreich!

📊 Service-Informationen:
  - Name: pcbf-csv-ui
  - Port: 8002
  - Logs: /home/ubuntu/pcbf_framework/logs/

🔧 Nützliche Befehle:
  - Status: sudo systemctl status pcbf-csv-ui
  - Logs: sudo journalctl -u pcbf-csv-ui -f
  - Neustart: sudo systemctl restart pcbf-csv-ui
  - Stoppen: sudo systemctl stop pcbf-csv-ui

🌐 Zugriff:
  - Lokal: http://localhost:8002
  - Öffentlich: https://8002-i10gec5oawwi59ab9yrf5-2da1d099.manusvm.computer
```

---

### Code-Updates deployen

```bash
cd /home/ubuntu/pcbf_framework

# 1. Code aktualisieren (z.B. via Git)
git pull

# 2. Dependencies aktualisieren (falls nötig)
pip3 install -r requirements.txt

# 3. Service neu starten
./manage.sh restart

# 4. Status prüfen
./manage.sh status
```

---

## 🏥 Health-Checks & Monitoring

### Manueller Health-Check

```bash
./healthcheck.sh
```

**Funktionsweise:**
- Prüft ob Server auf Port 8002 antwortet
- Bei Fehler: Automatischer Neustart (max. 3x)
- Logging in `logs/healthcheck.log`

**Exit Codes:**
- `0` - Health check OK
- `1` - Health check failed

---

### Automatische Health-Checks (Cronjob)

**Empfehlung:** Alle 5 Minuten prüfen

```bash
# Cronjob hinzufügen
crontab -e
```

**Eintrag:**
```
*/5 * * * * /home/ubuntu/pcbf_framework/healthcheck.sh >> /home/ubuntu/pcbf_framework/logs/cron.log 2>&1
```

**Vorteile:**
- ✅ Automatische Wiederherstellung bei Ausfällen
- ✅ Logging aller Health-Checks
- ✅ Max. 3 Restart-Versuche (verhindert Boot-Loops)

---

## 📊 Systemd-Service Details

### Service-Datei

**Pfad:** `/etc/systemd/system/pcbf-csv-ui.service`

**Inhalt:**
```ini
[Unit]
Description=PCBF 2.1 CSV Validation UI
After=network.target
Documentation=https://github.com/your-org/pcbf-framework

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/pcbf_framework
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="PYTHONUNBUFFERED=1"
Environment="OPENROUTER_API_KEY=sk-or-v1-***"

# Hauptprozess
ExecStart=/usr/bin/python3 /home/ubuntu/pcbf_framework/validation_ui_csv.py

# Restart-Konfiguration
Restart=always
RestartSec=10
StartLimitInterval=200
StartLimitBurst=5

# Logging
StandardOutput=append:/home/ubuntu/pcbf_framework/logs/service.log
StandardError=append:/home/ubuntu/pcbf_framework/logs/service-error.log

# Sicherheit
NoNewPrivileges=true
PrivateTmp=true

# Ressourcen-Limits
LimitNOFILE=65536
MemoryMax=2G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

---

### Systemd-Befehle

#### Status prüfen
```bash
sudo systemctl status pcbf-csv-ui
```

#### Service starten
```bash
sudo systemctl start pcbf-csv-ui
```

#### Service stoppen
```bash
sudo systemctl stop pcbf-csv-ui
```

#### Service neu starten
```bash
sudo systemctl restart pcbf-csv-ui
```

#### Service aktivieren (Autostart)
```bash
sudo systemctl enable pcbf-csv-ui
```

#### Service deaktivieren (kein Autostart)
```bash
sudo systemctl disable pcbf-csv-ui
```

#### Logs anzeigen
```bash
sudo journalctl -u pcbf-csv-ui -f
```

#### Logs der letzten Stunde
```bash
sudo journalctl -u pcbf-csv-ui --since "1 hour ago"
```

---

## 📁 Verzeichnisstruktur

```
/home/ubuntu/pcbf_framework/
├── validation_ui_csv.py          # Hauptanwendung
├── csv_processor.py              # CSV-Verarbeitung
├── analyzer.py                   # Analyse-Orchestrierung
├── models.py                     # Datenmodelle
├── agents/                       # Analyse-Agenten
│   ├── disc_agent.py
│   ├── neo_agent.py
│   ├── riasec_agent.py
│   └── persuasion_agent.py
├── logs/                         # Log-Dateien
│   ├── service.log               # Systemd stdout
│   ├── service-error.log         # Systemd stderr
│   ├── healthcheck.log           # Health-Check-Logs
│   └── cron.log                  # Cronjob-Logs
├── pcbf-csv-ui.service           # Systemd-Service-Datei
├── deploy.sh                     # Deployment-Script
├── manage.sh                     # Management-Script
├── healthcheck.sh                # Health-Check-Script
└── PRODUCTION_DEPLOYMENT.md      # Diese Dokumentation
```

---

## 🔒 Sicherheit

### API-Keys

**Wichtig:** API-Keys sind in der Service-Datei gespeichert!

**Berechtigungen prüfen:**
```bash
ls -l /etc/systemd/system/pcbf-csv-ui.service
```

**Sollte sein:**
```
-rw-r--r-- 1 root root ... pcbf-csv-ui.service
```

**Nur root kann schreiben, aber alle können lesen.**

**Für Produktion:** Verwende Secrets-Management (z.B. HashiCorp Vault, AWS Secrets Manager)

---

### Ressourcen-Limits

**Konfiguriert:**
- **Memory:** Max. 2GB
- **CPU:** Max. 200% (2 Kerne)
- **File Descriptors:** 65536

**Anpassen:**
```bash
sudo nano /etc/systemd/system/pcbf-csv-ui.service
# Ändere MemoryMax, CPUQuota, LimitNOFILE
sudo systemctl daemon-reload
sudo systemctl restart pcbf-csv-ui
```

---

## 📈 Performance-Optimierung

### 1. Worker-Anzahl erhöhen

**Datei:** `csv_processor.py`

```python
# Zeile ~75
results = self.analyzer.analyze_batch(
    profiles=profiles,
    max_workers=10  # Standard: 5, erhöhe auf 10
)
```

**Neustart:**
```bash
./manage.sh restart
```

---

### 2. Timeout anpassen

**Datei:** `csv_processor.py`

```python
# Zeile ~80
timeout=120  # Standard: 60, erhöhe auf 120
```

---

### 3. Caching aktivieren

**Für zukünftige Versionen:**
- Redis für LLM-Response-Caching
- Memcached für Profil-Caching

---

## 🐛 Troubleshooting

### Problem 1: Service startet nicht

**Symptome:**
```bash
./manage.sh status
# Service: ❌ Gestoppt
```

**Diagnose:**
```bash
sudo journalctl -u pcbf-csv-ui -n 50
```

**Häufige Ursachen:**
1. API-Key fehlt oder falsch
2. Port 8002 bereits belegt
3. Python-Dependencies fehlen

**Lösung:**
```bash
# 1. API-Key prüfen
sudo nano /etc/systemd/system/pcbf-csv-ui.service
# Prüfe Environment="OPENROUTER_API_KEY=..."

# 2. Port prüfen
sudo lsof -i :8002
# Falls belegt: Prozess killen

# 3. Dependencies installieren
pip3 install -r requirements.txt

# 4. Service neu starten
sudo systemctl daemon-reload
sudo systemctl restart pcbf-csv-ui
```

---

### Problem 2: Server antwortet nicht

**Symptome:**
```bash
curl http://localhost:8002/
# curl: (7) Failed to connect
```

**Diagnose:**
```bash
./manage.sh status
# Port 8002: ❌ Nicht erreichbar
```

**Lösung:**
```bash
# 1. Service-Status prüfen
sudo systemctl status pcbf-csv-ui

# 2. Logs prüfen
./manage.sh logs

# 3. Manuell starten (Test)
pkill -f validation_ui_csv.py
cd /home/ubuntu/pcbf_framework
python3 validation_ui_csv.py
# Fehler beobachten

# 4. Service neu deployen
./deploy.sh
```

---

### Problem 3: Hoher Speicherverbrauch

**Symptome:**
```bash
./manage.sh status
# Memory: 1.8G / 2.0G
```

**Lösung:**
```bash
# 1. Memory-Limit erhöhen
sudo nano /etc/systemd/system/pcbf-csv-ui.service
# Ändere: MemoryMax=4G

# 2. Reload und Restart
sudo systemctl daemon-reload
sudo systemctl restart pcbf-csv-ui

# 3. Oder: Worker reduzieren
# In csv_processor.py: max_workers=3
```

---

### Problem 4: Langsame Analyse

**Symptome:**
- Analyse dauert >5 Sekunden pro Profil

**Diagnose:**
```bash
# Logs prüfen
./manage.sh logs | grep "Analyse-Zeit"
```

**Lösung:**
```bash
# 1. Worker erhöhen (siehe Performance-Optimierung)
# 2. Timeout erhöhen
# 3. LLM-API-Status prüfen (OpenRouter)
```

---

## 📊 Monitoring & Alerting

### Log-Rotation

**Empfehlung:** Logrotate konfigurieren

```bash
sudo nano /etc/logrotate.d/pcbf-csv-ui
```

**Inhalt:**
```
/home/ubuntu/pcbf_framework/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    create 0644 ubuntu ubuntu
}
```

**Test:**
```bash
sudo logrotate -f /etc/logrotate.d/pcbf-csv-ui
```

---

### Prometheus-Metriken (optional)

**Für zukünftige Versionen:**
- `/metrics` Endpoint
- Prometheus-Exporter
- Grafana-Dashboard

---

## 🚀 Production Checklist

### Vor dem Go-Live

- [ ] Service läuft stabil (./manage.sh status)
- [ ] Health-Checks funktionieren (./healthcheck.sh)
- [ ] Cronjob für Health-Checks eingerichtet
- [ ] Logs-Rotation konfiguriert
- [ ] Ressourcen-Limits angepasst
- [ ] API-Keys gesichert
- [ ] Backup-Strategie definiert
- [ ] Monitoring eingerichtet
- [ ] Dokumentation aktualisiert

---

### Nach dem Go-Live

- [ ] Tägliche Health-Check-Logs prüfen
- [ ] Wöchentliche Performance-Analyse
- [ ] Monatliche Sicherheits-Updates
- [ ] Quartalsweise Kapazitäts-Planung

---

## 📚 Weiterführende Dokumentation

- **CSV_UPLOAD_GUIDE.md** - Anleitung für CSV-Upload und Analyse
- **VALIDATION_GUIDE.md** - Validierungs-Protokoll
- **TECHNICAL_DOCUMENTATION.md** - Technische Architektur
- **UPDATE_V2.1.4.md** - Letzte Änderungen

---

## 🆘 Support

### Bei Problemen

1. **Logs prüfen:** `./manage.sh logs`
2. **Status prüfen:** `./manage.sh status`
3. **Health-Check:** `./healthcheck.sh`
4. **Service neu starten:** `./manage.sh restart`

### Kontakt

- **GitHub Issues:** https://github.com/your-org/pcbf-framework/issues
- **Email:** support@your-org.com
- **Slack:** #pcbf-support

---

## ✅ Zusammenfassung

### Implementiert

✅ **Systemd-Service** - Automatischer Start und Neustart  
✅ **Management-Scripts** - Einfache Verwaltung  
✅ **Health-Checks** - Automatische Wiederherstellung  
✅ **Logging** - Systemd-Journal + Dateien  
✅ **Ressourcen-Limits** - 2GB RAM, 200% CPU  
✅ **Deployment-Script** - One-Click-Deployment

### Vorteile

- 🚀 **Dauerhaft:** Läuft permanent, auch nach Neustart
- 🔄 **Robust:** Automatischer Neustart bei Abstürzen
- 📊 **Überwacht:** Health-Checks alle 5 Minuten
- 🔧 **Wartbar:** Einfache Management-Befehle
- 📈 **Skalierbar:** Ressourcen-Limits anpassbar

---

**Die PCBF 2.1 CSV Validation UI ist jetzt produktionsbereit!** 🎉

**URL:** https://8002-i10gec5oawwi59ab9yrf5-2da1d099.manusvm.computer

**Service:** `pcbf-csv-ui` (läuft dauerhaft)

