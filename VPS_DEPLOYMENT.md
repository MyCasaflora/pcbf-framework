

# PCBF 2.1 - VPS Deployment Guide (Hetzner Cloud)

## 🚀 Volle Kontrolle mit einem eigenen Server

---

## 🎯 Überblick

Ein **Virtual Private Server (VPS)** gibt Ihnen die volle Kontrolle über Ihre Anwendung. Diese Anleitung verwendet **Hetzner Cloud** als Beispiel.

### Vorteile

- ✅ **Volle Kontrolle:** Installieren Sie was Sie wollen
- ✅ **Günstig:** Ab €4/Monat
- ✅ **Mehrere Apps:** Auf einem Server möglich
- ✅ **EU-Server:** DSGVO-konform

### Nachteile

- ❌ **Mehr Aufwand:** Server-Administration
- ❌ **Sicherheit:** Sie sind verantwortlich
- ❌ **Updates:** Manuell durchführen

---

## 🚀 Schritt-für-Schritt-Anleitung

### Schritt 1: Server erstellen

1. Gehe zu https://console.hetzner.cloud
2. **New Project**
3. **Add Server**
   - **Location:** Nürnberg (Deutschland)
   - **Image:** Ubuntu 22.04
   - **Type:** CX11 (2GB RAM, €4.51/Monat)
   - **SSH Key:** Hinzufügen (wichtig!)

---

### Schritt 2: Server konfigurieren

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
# Erstelle .env Datei
nano .env
```

**Inhalt von `.env`:**
```
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
PORT=8002
```

---

### Schritt 3: Systemd-Service einrichten

**Die `pcbf-csv-ui.service` Datei ist bereits im Projekt enthalten.**

```bash
# Service-Datei anpassen (API-Key aus .env laden)
sed -i 
  -e 
    "s|Environment=\"OPENROUTER_API_KEY=.*\"|EnvironmentFile=/opt/pcbf-framework/.env|" \
  pcbf-csv-ui.service

# Service installieren
cp pcbf-csv-ui.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable pcbf-csv-ui
systemctl start pcbf-csv-ui

# Status prüfen
systemctl status pcbf-csv-ui
```

---

### Schritt 4: Firewall konfigurieren

```bash
# UFW installieren
apt install -y ufw

# Firewall-Regeln
ufw allow 22/tcp   # SSH
ufw allow 8002/tcp # PCBF App
ufw enable
```

**Deine App ist jetzt unter `http://your-server-ip:8002` erreichbar!**

---

## 🔒 HTTPS mit Nginx & Let's Encrypt (optional)

### Schritt 1: Domain konfigurieren

**Bei deinem Domain-Anbieter:**
- Erstelle einen **A-Record**:
  - **Host/Name:** `pcbf` (oder `@`)
  - **Value/Points to:** `your-server-ip`

---

### Schritt 2: Nginx installieren

```bash
apt install -y nginx

# Firewall für Nginx öffnen
ufw allow "Nginx Full"
```

---

### Schritt 3: Nginx konfigurieren

```bash
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
```

---

### Schritt 4: HTTPS mit Let's Encrypt

```bash
# Certbot installieren
apt install -y certbot python3-certbot-nginx

# Zertifikat erstellen
certbot --nginx -d your-domain.com
```

**Certbot konfiguriert Nginx automatisch für HTTPS!**

---

## ✅ Fertig!

**Deine Website ist jetzt unter `https://your-domain.com` erreichbar!**

---

## 🚀 Zusammenfassung

### Workflow

1. **Code ändern**
2. **`git commit` & `git push`**
3. **Auf Server:** `git pull`
4. **Service neu starten:** `systemctl restart pcbf-csv-ui`

### Vorteile

- ✅ **Volle Kontrolle**
- ✅ **Günstig**
- ✅ **Flexibel**

### Nachteile

- ❌ **Mehr Aufwand**
- ❌ **Sicherheit selbst verwalten**

---

**Ein VPS ist die beste Wahl für erfahrene Benutzer, die volle Kontrolle benötigen!** 🎉

