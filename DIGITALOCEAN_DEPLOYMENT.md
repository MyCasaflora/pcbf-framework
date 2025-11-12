

# PCBF 2.1 - DigitalOcean App Platform Deployment Guide

## 🚀 Professionelles Deployment für skalierbare Anwendungen

---

## 🎯 Überblick

**DigitalOcean App Platform** ist eine professionelle Lösung, die sich gut für wachsende Projekte eignet.

### Vorteile

- ✅ **Einfaches Deployment:** Git Push genügt
- ✅ **Skalierbar:** Horizontale und vertikale Skalierung
- ✅ **Gute Dokumentation:** Sehr detailliert
- ✅ **Integriertes Monitoring:** CPU, RAM, etc.
- ✅ **Datenbanken:** Einfach PostgreSQL oder Redis hinzufügen

### Kosten

- **Basic:** $5/Monat (512MB RAM)
- **Professional:** $12/Monat (1GB RAM, empfohlen)

---

## 🚀 Schritt-für-Schritt-Anleitung

### Schritt 1: GitHub Repository vorbereiten

**Siehe `RAILWAY_DEPLOYMENT.md` für Details.**

---

### Schritt 2: DigitalOcean App erstellen

1. Gehe zu https://cloud.digitalocean.com/apps
2. Klicke **"Create App"**.
3. Verbinde dein GitHub Repository.
4. Wähle das `pcbf-framework` Repository und den `main` Branch.

---

### Schritt 3: App konfigurieren

DigitalOcean erkennt die meisten Einstellungen automatisch:

- **Type:** Web Service
- **Build Command:** `pip install -r requirements.txt`
- **Run Command:** `python3 validation_ui_csv.py`

**Passe den Port an:**
- Klicke auf **"Edit"** neben dem Run Command.
- Setze den **HTTP Port** auf `8002`.

---

### Schritt 4: Umgebungsvariablen setzen

1. Im Konfigurations-Schritt, gehe zu **"Environment Variables"**.
2. Klicke **"Edit"**.
3. Füge folgende Variable hinzu:

   - **`OPENROUTER_API_KEY`**: `sk-or-v1-your-api-key-here`

---

### Schritt 5: Ressourcen wählen

1. Wähle den Plan:
   - **Basic:** $5/Monat (für kleine Tests)
   - **Professional:** $12/Monat (empfohlen)
2. Wähle die Region (z.B. Frankfurt).

---

### Schritt 6: App erstellen

1. Klicke **"Create Resources"**.
2. DigitalOcean baut und deployed die App.

---

### Schritt 7: Fertig!

**Deine Website ist jetzt unter `https://your-app.ondigitalocean.app` erreichbar!**

---

## 🌐 Custom Domain (optional)

1. Im DigitalOcean Dashboard, gehe zu **"Settings"** → **"Domains"**.
2. Klicke **"Add Domain"**.
3. Folge den Anweisungen zur DNS-Konfiguration (A-Record und CNAME).

---

## 🐛 Troubleshooting

### Problem 1: Build schlägt fehl

**Logs prüfen:**
- Im DigitalOcean Dashboard, gehe zu **"Deployments"** → **"Build Logs"**.

**Lösung:**
- `requirements.txt` prüfen.

---

### Problem 2: App startet nicht

**Logs prüfen:**
- Im DigitalOcean Dashboard, gehe zu **"Runtime Logs"**.

**Lösung:**
- Umgebungsvariablen prüfen.
- Port-Konfiguration prüfen.

---

## 🚀 Zusammenfassung

### Workflow

1. **Code ändern**
2. **`git commit`**
3. **`git push`**
4. **DigitalOcean deployed automatisch!**

### Vorteile

- ✅ **Professionell:** Stabil und zuverlässig
- ✅ **Skalierbar:** Bereit für Wachstum
- ✅ **Gute Integration:** Datenbanken, etc.

### Nachteile

- ❌ **Etwas teurer** als andere Optionen
- ❌ **Komplexere UI** als Railway

---

**DigitalOcean ist eine gute Wahl für professionelle Projekte, die wachsen sollen!** 🎉

