# PCBF 2.1 - Railway.app Deployment Guide

## 🚀 Website in 5 Minuten dauerhaft bereitstellen

---

## 🎯 Überblick

**Railway.app** ist die **empfohlene Methode** für ein schnelles, einfaches und stabiles Deployment.

### Vorteile

- ✅ **Einfachstes Deployment:** Git Push genügt
- ✅ **Automatische HTTPS:** Kostenlose SSL-Zertifikate
- ✅ **Custom Domain:** Eigene Domain möglich
- ✅ **Automatische Skalierung:** Bei Bedarf
- ✅ **Umgebungsvariablen:** Einfache Konfiguration
- ✅ **Logs & Monitoring:** Integriert

### Kosten

- **Starter:** $5/Monat (500 Stunden)
- **Pro:** $20/Monat (unbegrenzt)

---

## 🚀 Schritt-für-Schritt-Anleitung

### Schritt 1: GitHub Repository erstellen

#### A) Code vorbereiten

```bash
cd /home/ubuntu/pcbf_framework

# Git initialisieren
git init
git add .
git commit -m "Initial commit"
```

#### B) GitHub Repository erstellen

1. Gehe zu https://github.com/new
2. **Repository name:** `pcbf-framework`
3. **Description:** PCBF 2.1 CSV Validation UI
4. **Public** oder **Private** wählen
5. **Create repository**

#### C) Code pushen

```bash
# Remote hinzufügen
git remote add origin https://github.com/YOUR-USERNAME/pcbf-framework.git

# Code pushen
git push -u origin main
```

---

### Schritt 2: Railway-Projekt erstellen

1. Gehe zu https://railway.app und melde dich mit GitHub an.
2. Klicke **"Start a New Project"**.
3. Wähle **"Deploy from GitHub repo"**.
4. Wähle dein `pcbf-framework` Repository.
5. Railway erkennt automatisch Python und startet den Build.

---

### Schritt 3: Umgebungsvariablen setzen

1. Im Railway Dashboard, gehe zu **"Variables"**.
2. Klicke **"New Variable"**.
3. Füge folgende Variablen hinzu:

   - **`OPENROUTER_API_KEY`**: `sk-or-v1-your-api-key-here`
   - **`PORT`**: `8002`

**Wichtig:** Railway erkennt den Port automatisch, aber es ist gut, ihn explizit zu setzen.

---

### Schritt 4: Deploy-Konfiguration (optional)

Railway erkennt die meisten Einstellungen automatisch. Für mehr Kontrolle, erstelle eine `railway.json` Datei:

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

```bash
git add railway.json
git commit -m "Add Railway config"
git push
```

Railway deployed automatisch bei jedem Git Push!

---

### Schritt 5: Fertig!

**Deine Website ist jetzt unter `https://your-app.railway.app` erreichbar!**

---

## 🌐 Custom Domain (optional)

### Schritt 1: Domain hinzufügen

1. Im Railway Dashboard, gehe zu **"Settings"** → **"Domains"**.
2. Klicke **"Add Custom Domain"**.
3. Gib deine Domain ein (z.B. `pcbf.your-domain.com`).

### Schritt 2: DNS konfigurieren

**Bei deinem Domain-Anbieter (z.B. Namecheap, GoDaddy):**

1. Gehe zu den DNS-Einstellungen.
2. Erstelle einen **CNAME-Record**:
   - **Host/Name:** `pcbf` (oder `@` für Root-Domain)
   - **Value/Points to:** `your-app.railway.app`
   - **TTL:** Auto oder 1 Stunde

**Warte einige Minuten, bis die DNS-Änderungen aktiv sind.**

### Schritt 3: HTTPS

Railway stellt automatisch ein **kostenloses SSL-Zertifikat** für deine Domain aus.

---

## 🐛 Troubleshooting

### Problem 1: Build schlägt fehl

**Logs prüfen:**
- Im Railway Dashboard, gehe zu **"Deployments"** → **"Build Logs"**.

**Häufige Ursachen:**
- `requirements.txt` fehlt oder ist fehlerhaft.
- Python-Version nicht kompatibel (Railway verwendet neueste).

**Lösung:**
- `requirements.txt` prüfen.
- Sicherstellen, dass alle Dependencies aufgeführt sind.

---

### Problem 2: App startet nicht

**Logs prüfen:**
- Im Railway Dashboard, gehe zu **"Deployments"** → **"Deploy Logs"**.

**Häufige Ursachen:**
- `OPENROUTER_API_KEY` fehlt.
- `PORT` nicht korrekt gesetzt.
- Fehler im Python-Code.

**Lösung:**
- Umgebungsvariablen prüfen.
- Logs auf `ValueError` oder andere Fehler prüfen.

---

### Problem 3: 502 Bad Gateway

**Ursache:**
- App ist abgestürzt oder startet nicht.

**Lösung:**
- Logs prüfen (siehe oben).
- Neustart via Railway Dashboard: **"Redeploy"**

---

## 📈 Monitoring & Logs

### Logs

- **Live Logs:** Im Railway Dashboard unter **"Deployments"** → **"Deploy Logs"**.
- **Build Logs:** Im Railway Dashboard unter **"Deployments"** → **"Build Logs"**.

### Metriken

- **CPU-Auslastung:** Im Railway Dashboard unter **"Metrics"**.
- **Speicherverbrauch:** Im Railway Dashboard unter **"Metrics"**.
- **Netzwerk-Traffic:** Im Railway Dashboard unter **"Metrics"**.

---

## 🚀 Zusammenfassung

### Workflow

1. **Code ändern**
2. **`git commit`**
3. **`git push`**
4. **Railway deployed automatisch!**

### Vorteile

- ✅ **Schnell:** < 5 Minuten zum Deployment
- ✅ **Einfach:** Kein Server-Management
- ✅ **Stabil:** Automatischer Neustart
- ✅ **Sicher:** Automatische HTTPS
- ✅ **Skalierbar:** Bei Bedarf mehr Ressourcen

---

**Railway.app ist die ideale Lösung für dieses Projekt!** 🎉

