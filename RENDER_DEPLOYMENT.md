

# PCBF 2.1 - Render.com Deployment Guide

## 🚀 Website dauerhaft bereitstellen (mit kostenlosem Plan)

---

## 🎯 Überblick

**Render.com** ist eine gute Alternative zu Railway, die einen **kostenlosen Plan** anbietet.

### Vorteile

- ✅ **Kostenloser Plan:** Ideal zum Testen und für kleine Projekte
- ✅ **Automatische HTTPS:** Kostenlose SSL-Zertifikate
- ✅ **Custom Domain:** Eigene Domain möglich
- ✅ **Auto-Deploy:** Bei Git Push

### Nachteile (kostenloser Plan)

- ❌ **Schläft nach 15 Min Inaktivität:** Erster Ladevorgang dauert länger
- ❌ **Limitierte Ressourcen:** Weniger RAM und CPU

### Kosten

- **Free:** $0/Monat (schläft nach 15 Min)
- **Starter:** $7/Monat (immer aktiv)
- **Standard:** $25/Monat (mehr Ressourcen)

---

## 🚀 Schritt-für-Schritt-Anleitung

### Schritt 1: GitHub Repository vorbereiten

**Siehe `RAILWAY_DEPLOYMENT.md` für Details zum Erstellen eines GitHub Repositories.**

---

### Schritt 2: Render-Konfiguration erstellen

**Erstelle eine `render.yaml` Datei im Projektverzeichnis:**

```yaml
services:
  - type: web
    name: pcbf-csv-ui
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python3 validation_ui_csv.py
    healthCheckPath: /
    envVars:
      - key: OPENROUTER_API_KEY
        sync: false  # API-Key wird im Dashboard gesetzt
      - key: PORT
        value: 8002
      - key: PYTHONUNBUFFERED
        value: 1
    plan: free  # Wähle "free" oder "starter"
```

**Code pushen:**

```bash
git add render.yaml
git commit -m "Add Render config"
git push
```

---

### Schritt 3: Render-Service erstellen

1. Gehe zu https://dashboard.render.com
2. Klicke **"New"** → **"Blueprint"**.
3. Verbinde dein GitHub Repository.
4. Render erkennt automatisch die `render.yaml` Datei.
5. Klicke **"Apply"**.

---

### Schritt 4: Umgebungsvariablen setzen

1. Im Render Dashboard, gehe zu **"Environment"**.
2. Klicke **"Add Environment Variable"**.
3. Füge folgende Variable hinzu:

   - **`OPENROUTER_API_KEY`**: `sk-or-v1-your-api-key-here`

**Wichtig:** Setze den Wert für `sync` auf `false`, damit der Key nicht im Code sichtbar ist.

---

### Schritt 5: Fertig!

**Deine Website ist jetzt unter `https://your-app.onrender.com` erreichbar!**

---

## 🌐 Custom Domain (optional)

1. Im Render Dashboard, gehe zu **"Settings"** → **"Custom Domains"**.
2. Klicke **"Add Custom Domain"**.
3. Gib deine Domain ein.
4. Folge den Anweisungen zur DNS-Konfiguration (CNAME-Record).

---

## 🐛 Troubleshooting

### Problem 1: Build schlägt fehl

**Logs prüfen:**
- Im Render Dashboard, gehe zu **"Events"**.

**Lösung:**
- `requirements.txt` prüfen.

---

### Problem 2: App startet nicht

**Logs prüfen:**
- Im Render Dashboard, gehe zu **"Logs"**.

**Lösung:**
- Umgebungsvariablen prüfen.
- Logs auf Fehler prüfen.

---

## 🚀 Zusammenfassung

### Workflow

1. **Code ändern**
2. **`git commit`**
3. **`git push`**
4. **Render deployed automatisch!**

### Vorteile

- ✅ **Kostenloser Start:** Ideal zum Testen
- ✅ **Einfaches Setup:** Fast so einfach wie Railway
- ✅ **Gute Dokumentation:** Viele Beispiele

### Nachteile

- ❌ **Schläft im kostenlosen Plan:** Langsamer erster Ladevorgang
- ❌ **Etwas komplexer** als Railway

---

**Render.com ist eine gute Alternative, wenn Sie kostenlos starten möchten!** 🎉

