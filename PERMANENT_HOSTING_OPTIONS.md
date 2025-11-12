# PCBF 2.1 - Permanente Hosting-Optionen

## 🌐 Website dauerhaft öffentlich erreichbar machen

---

## ❌ Problem

Die aktuelle URL (`https://8002-i10gec5oawwi59ab9yrf5-2da1d099.manusvm.computer`) ist nur **temporär** verfügbar:

- ✅ Funktioniert während der Sandbox-Session
- ❌ Nicht erreichbar wenn Sandbox schläft
- ❌ Nicht erreichbar nach Sandbox-Neustart
- ❌ URL ändert sich bei jedem Neustart

**Fehlermeldung:**
```
The temporary website is currently unavailable
This may be because Manus's computer is asleep or the link has expired.
```

---

## ✅ Lösungen für permanente Erreichbarkeit

### Übersicht

| Option | Kosten | Komplexität | Empfehlung |
|--------|--------|-------------|------------|
| **1. Railway.app** | $5-20/Monat | ⭐ Einfach | ✅ **Empfohlen** |
| **2. Render.com** | $7-25/Monat | ⭐ Einfach | ✅ Gut |
| **3. DigitalOcean** | $6-12/Monat | ⭐⭐ Mittel | ✅ Flexibel |
| **4. AWS Lightsail** | $5-10/Monat | ⭐⭐ Mittel | ⚠️ Komplex |
| **5. Hetzner Cloud** | €4-8/Monat | ⭐⭐ Mittel | ✅ Günstig |
| **6. Eigener Server** | Variabel | ⭐⭐⭐ Komplex | ⚠️ Nur für Experten |

---

## 🚀 Option 1: Railway.app (Empfohlen)

### Vorteile

- ✅ **Einfachstes Deployment** - Git Push genügt
- ✅ **Automatische HTTPS** - Kostenlose SSL-Zertifikate
- ✅ **Custom Domain** - Eigene Domain möglich
- ✅ **Automatische Skalierung** - Bei Bedarf
- ✅ **Umgebungsvariablen** - Einfache Konfiguration
- ✅ **Logs & Monitoring** - Integriert

### Kosten

- **Starter:** $5/Monat (500 Stunden)
- **Pro:** $20/Monat (unbegrenzt)

### Deployment-Schritte

#### 1. Repository erstellen

```bash
cd /home/ubuntu/pcbf_framework

# Git initialisieren
git init
git add .
git commit -m "Initial commit"

# GitHub Repository erstellen (über GitHub Web-UI)
# Dann:
git remote add origin https://github.com/your-username/pcbf-framework.git
git push -u origin main
```

#### 2. Railway-Projekt erstellen

1. Gehe zu https://railway.app
2. Klicke "Start a New Project"
3. Wähle "Deploy from GitHub repo"
4. Wähle dein Repository
5. Railway erkennt automatisch Python

#### 3. Umgebungsvariablen setzen

**In Railway Dashboard:**

```
OPENROUTER_API_KEY=sk-or-v1-***
PORT=8002
```

#### 4. Deploy-Konfiguration

**Erstelle `railway.json`:**

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python3 validation_ui_csv.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 5. Deployment

```bash
git add railway.json
git commit -m "Add Railway config"
git push
```

**Railway deployed automatisch!**

#### 6. Custom Domain (optional)

**In Railway Dashboard:**
- Settings → Domains
- Add Custom Domain
- DNS konfigurieren (A-Record oder CNAME)

**Fertig!** Website ist unter `https://your-app.railway.app` erreichbar

---

## 🎨 Option 2: Render.com

### Vorteile

- ✅ **Kostenloser Plan** verfügbar (mit Einschränkungen)
- ✅ **Automatische HTTPS**
- ✅ **Custom Domain**
- ✅ **Auto-Deploy** bei Git Push

### Kosten

- **Free:** $0/Monat (schläft nach 15 Min Inaktivität)
- **Starter:** $7/Monat (immer aktiv)
- **Standard:** $25/Monat (mehr Ressourcen)

### Deployment-Schritte

#### 1. Repository vorbereiten

**Erstelle `render.yaml`:**

```yaml
services:
  - type: web
    name: pcbf-csv-ui
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python3 validation_ui_csv.py
    envVars:
      - key: OPENROUTER_API_KEY
        sync: false
      - key: PORT
        value: 8002
```

```bash
git add render.yaml
git commit -m "Add Render config"
git push
```

#### 2. Render-Service erstellen

1. Gehe zu https://render.com
2. New → Web Service
3. Connect GitHub Repository
4. Render erkennt `render.yaml`
5. Klicke "Create Web Service"

#### 3. Umgebungsvariablen setzen

**In Render Dashboard:**
- Environment → Add Environment Variable
- `OPENROUTER_API_KEY`: `sk-or-v1-***`

**Fertig!** Website ist unter `https://your-app.onrender.com` erreichbar

---

## 💧 Option 3: DigitalOcean App Platform

### Vorteile

- ✅ **Einfaches Deployment**
- ✅ **Skalierbar**
- ✅ **Gute Dokumentation**
- ✅ **Integriertes Monitoring**

### Kosten

- **Basic:** $5/Monat (512MB RAM)
- **Professional:** $12/Monat (1GB RAM)

### Deployment-Schritte

#### 1. DigitalOcean App erstellen

1. Gehe zu https://cloud.digitalocean.com/apps
2. Create App
3. GitHub Repository verbinden
4. Branch auswählen (main)

#### 2. App konfigurieren

**Erkannte Einstellungen:**
- **Type:** Web Service
- **Build Command:** `pip install -r requirements.txt`
- **Run Command:** `python3 validation_ui_csv.py`

#### 3. Umgebungsvariablen

```
OPENROUTER_API_KEY=sk-or-v1-***
PORT=8002
```

#### 4. Ressourcen wählen

- **Basic:** $5/Monat
- **Professional:** $12/Monat (empfohlen)

**Fertig!** Website ist unter `https://your-app.ondigitalocean.app` erreichbar

---

## 🖥️ Option 4: VPS (Virtual Private Server)

### Anbieter

1. **Hetzner Cloud** - €4/Monat (2GB RAM, Deutschland)
2. **DigitalOcean Droplet** - $6/Monat (1GB RAM)
3. **Linode** - $5/Monat (1GB RAM)
4. **Vultr** - $6/Monat (1GB RAM)

### Vorteile

- ✅ **Volle Kontrolle**
- ✅ **Günstig** bei langfristiger Nutzung
- ✅ **Mehrere Apps** auf einem Server

### Nachteile

- ❌ **Mehr Aufwand** (Server-Administration)
- ❌ **Sicherheit** selbst verwalten
- ❌ **Updates** selbst durchführen

### Deployment-Schritte (Hetzner Cloud)

#### 1. Server erstellen

1. Gehe zu https://console.hetzner.cloud
2. New Project
3. Add Server
   - **Location:** Nürnberg (Deutschland)
   - **Image:** Ubuntu 22.04
   - **Type:** CX11 (2GB RAM, €4.51/Monat)
   - **SSH Key:** Hinzufügen

#### 2. Server konfigurieren

```bash
# SSH-Verbindung
ssh root@your-server-ip

# System aktualisieren
apt update && apt upgrade -y

# Python und Dependencies installieren
apt install -y python3 python3-pip git

# Projekt klonen
cd /opt
git clone https://github.com/your-username/pcbf-framework.git
cd pcbf-framework

# Dependencies installieren
pip3 install -r requirements.txt

# Umgebungsvariablen setzen
export OPENROUTER_API_KEY="sk-or-v1-***"

# Systemd-Service einrichten
cp pcbf-csv-ui.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable pcbf-csv-ui
systemctl start pcbf-csv-ui
```

#### 3. Firewall konfigurieren

```bash
# UFW installieren
apt install -y ufw

# Firewall-Regeln
ufw allow 22/tcp   # SSH
ufw allow 8002/tcp # PCBF App
ufw enable
```

#### 4. Nginx Reverse Proxy (optional, für HTTPS)

```bash
# Nginx installieren
apt install -y nginx certbot python3-certbot-nginx

# Nginx konfigurieren
nano /etc/nginx/sites-available/pcbf
```

**Inhalt:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Aktivieren
ln -s /etc/nginx/sites-available/pcbf /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# HTTPS mit Let's Encrypt
certbot --nginx -d your-domain.com
```

**Fertig!** Website ist unter `https://your-domain.com` erreichbar

---

## 🐳 Option 5: Docker + Cloud

### Vorteile

- ✅ **Portabel** - Läuft überall
- ✅ **Reproduzierbar** - Immer gleiche Umgebung
- ✅ **Skalierbar** - Einfach mehrere Container

### Deployment-Schritte

#### 1. Dockerfile erstellen

**Siehe `Dockerfile` im Projekt**

#### 2. Docker Hub

```bash
# Docker Image bauen
docker build -t your-username/pcbf-csv-ui:latest .

# Zu Docker Hub pushen
docker login
docker push your-username/pcbf-csv-ui:latest
```

#### 3. Auf Server deployen

```bash
# Auf Server
docker pull your-username/pcbf-csv-ui:latest
docker run -d \
  -p 8002:8002 \
  -e OPENROUTER_API_KEY="sk-or-v1-***" \
  --restart always \
  --name pcbf-csv-ui \
  your-username/pcbf-csv-ui:latest
```

---

## 📊 Vergleich der Optionen

### Kosten (pro Monat)

| Option | Kosten | Inkludiert |
|--------|--------|------------|
| Railway | $5-20 | HTTPS, Domain, Monitoring |
| Render | $7-25 | HTTPS, Domain, Auto-Deploy |
| DigitalOcean App | $5-12 | HTTPS, Domain, Monitoring |
| Hetzner VPS | €4-8 | Server, Traffic |
| AWS Lightsail | $5-10 | Server, Traffic |

### Aufwand

| Option | Setup | Wartung | Skalierung |
|--------|-------|---------|------------|
| Railway | ⭐ | ⭐ | ⭐ |
| Render | ⭐ | ⭐ | ⭐ |
| DigitalOcean App | ⭐ | ⭐ | ⭐⭐ |
| VPS | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

### Features

| Feature | Railway | Render | DO App | VPS |
|---------|---------|--------|--------|-----|
| Auto-Deploy | ✅ | ✅ | ✅ | ❌ |
| HTTPS | ✅ | ✅ | ✅ | ⚠️ (manuell) |
| Custom Domain | ✅ | ✅ | ✅ | ✅ |
| Monitoring | ✅ | ✅ | ✅ | ⚠️ (selbst) |
| Logs | ✅ | ✅ | ✅ | ⚠️ (selbst) |
| Skalierung | ✅ | ✅ | ✅ | ❌ |

---

## 🎯 Empfehlung

### Für Anfänger: Railway.app

**Warum:**
- ✅ Einfachstes Setup (5 Minuten)
- ✅ Git Push = Deploy
- ✅ Automatische HTTPS
- ✅ Gutes Monitoring

**Kosten:** $5/Monat

---

### Für Fortgeschrittene: Hetzner Cloud VPS

**Warum:**
- ✅ Günstig (€4/Monat)
- ✅ Volle Kontrolle
- ✅ Mehrere Apps möglich
- ✅ EU-Server (DSGVO)

**Kosten:** €4/Monat

**Aber:** Mehr Aufwand (Server-Administration)

---

### Für Unternehmen: DigitalOcean App Platform

**Warum:**
- ✅ Professionell
- ✅ Gute Skalierung
- ✅ Integriertes Monitoring
- ✅ 24/7 Support

**Kosten:** $12/Monat

---

## 🚀 Schnellstart-Anleitung

### Railway.app (Empfohlen)

#### Schritt 1: GitHub Repository

```bash
cd /home/ubuntu/pcbf_framework
git init
git add .
git commit -m "Initial commit"

# GitHub Repository erstellen (Web-UI)
# Dann:
git remote add origin https://github.com/YOUR-USERNAME/pcbf-framework.git
git push -u origin main
```

#### Schritt 2: Railway-Projekt

1. https://railway.app → Sign up (mit GitHub)
2. "New Project" → "Deploy from GitHub repo"
3. Repository auswählen
4. Environment Variables:
   - `OPENROUTER_API_KEY`: `sk-or-v1-***`
   - `PORT`: `8002`
5. Deploy!

#### Schritt 3: Fertig!

**URL:** `https://your-app.railway.app`

**Custom Domain (optional):**
- Settings → Domains → Add Custom Domain
- DNS: CNAME → `your-app.railway.app`

---

## 📚 Nächste Schritte

### 1. Deployment-Option wählen

**Empfehlung:** Railway.app für schnellsten Start

### 2. Repository vorbereiten

```bash
cd /home/ubuntu/pcbf_framework
git init
git add .
git commit -m "Initial commit"
```

### 3. Plattform-spezifische Anleitung folgen

- **Railway:** Siehe oben
- **Render:** Siehe `RENDER_DEPLOYMENT.md`
- **DigitalOcean:** Siehe `DIGITALOCEAN_DEPLOYMENT.md`
- **VPS:** Siehe `VPS_DEPLOYMENT.md`

### 4. Domain konfigurieren (optional)

**Eigene Domain:**
- Domain kaufen (z.B. Namecheap, GoDaddy)
- DNS konfigurieren
- HTTPS automatisch via Let's Encrypt

---

## ✅ Zusammenfassung

### Problem

❌ Temporäre URL nicht dauerhaft erreichbar

### Lösung

✅ **Permanentes Hosting** auf Cloud-Plattform

### Empfehlung

🚀 **Railway.app** - Einfachstes Setup, $5/Monat

### Alternative

💧 **Hetzner Cloud VPS** - Günstig, €4/Monat (für Fortgeschrittene)

---

**Nächster Schritt:** Deployment-Option wählen und Anleitung folgen!

