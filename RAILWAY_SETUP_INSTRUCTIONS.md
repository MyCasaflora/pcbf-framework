# PCBF 2.1 - Railway.app Setup-Anleitung

## ✅ GitHub Repository ist bereit!

**Repository:** https://github.com/MyCasaflora/pcbf-framework

---

## 🚀 Railway.app Deployment - Letzte Schritte

### Schritt 1: Railway.app öffnen

1. Gehe zu https://railway.app
2. Klicke **"Login"** oder **"Start a New Project"**
3. Melde dich mit deinem **GitHub-Account** an (MyCasaflora)

---

### Schritt 2: Neues Projekt erstellen

1. Klicke **"Start a New Project"**
2. Wähle **"Deploy from GitHub repo"**
3. Suche nach **"pcbf-framework"**
4. Wähle **"MyCasaflora/pcbf-framework"**
5. Klicke **"Deploy Now"**

**Railway startet automatisch den Build-Prozess!**

---

### Schritt 3: Umgebungsvariablen setzen

1. Im Railway Dashboard, klicke auf dein Projekt
2. Gehe zu **"Variables"**
3. Klicke **"New Variable"**
4. Füge folgende Variablen hinzu:

#### Variable 1: OPENROUTER_API_KEY

- **Name:** `OPENROUTER_API_KEY`
- **Value:** `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`

#### Variable 2: PORT (optional, wird automatisch erkannt)

- **Name:** `PORT`
- **Value:** `8002`

5. Klicke **"Add"** für jede Variable

---

### Schritt 4: Deployment abwarten

Railway baut und deployed die App automatisch. Das dauert ca. 2-3 Minuten.

**Status prüfen:**
- Gehe zu **"Deployments"**
- Warte bis der Status **"Success"** anzeigt

---

### Schritt 5: URL abrufen

1. Im Railway Dashboard, gehe zu **"Settings"**
2. Scrolle zu **"Domains"**
3. Klicke **"Generate Domain"**
4. Railway erstellt eine URL wie: `https://pcbf-framework-production.up.railway.app`

**Deine Website ist jetzt dauerhaft online!** 🎉

---

## 🌐 Custom Domain (optional)

### Eigene Domain hinzufügen

1. Im Railway Dashboard, gehe zu **"Settings"** → **"Domains"**
2. Klicke **"Custom Domain"**
3. Gib deine Domain ein (z.B. `pcbf.your-domain.com`)
4. Railway zeigt dir die DNS-Einstellungen

### DNS konfigurieren

Bei deinem Domain-Anbieter (z.B. Namecheap, GoDaddy):

1. Erstelle einen **CNAME-Record**:
   - **Host/Name:** `pcbf` (oder `@` für Root-Domain)
   - **Value/Points to:** `pcbf-framework-production.up.railway.app`
   - **TTL:** Auto oder 1 Stunde

2. Warte 5-10 Minuten bis DNS aktiv ist

**Railway stellt automatisch ein SSL-Zertifikat aus!**

---

## 🔄 Workflow nach dem Deployment

### Code-Änderungen deployen

```bash
cd /home/ubuntu/pcbf_framework

# Code ändern...

# Änderungen committen
git add .
git commit -m "Beschreibung der Änderung"
git push

# Railway deployed automatisch!
```

**Kein weiterer Aufwand nötig!**

---

## 📊 Monitoring & Logs

### Logs anzeigen

1. Im Railway Dashboard, gehe zu **"Deployments"**
2. Klicke auf das aktuelle Deployment
3. Gehe zu **"View Logs"**

### Metriken

1. Im Railway Dashboard, gehe zu **"Metrics"**
2. Sieh CPU, RAM, Netzwerk-Traffic

---

## 🐛 Troubleshooting

### Problem 1: Build schlägt fehl

**Lösung:**
1. Gehe zu **"Deployments"** → **"Build Logs"**
2. Prüfe Fehlermeldungen
3. Meist: `requirements.txt` fehlt oder ist fehlerhaft

### Problem 2: App startet nicht

**Lösung:**
1. Gehe zu **"Deployments"** → **"Deploy Logs"**
2. Prüfe auf Fehler wie `ValueError: OPENROUTER_API_KEY nicht gesetzt!`
3. Umgebungsvariablen prüfen

### Problem 3: 502 Bad Gateway

**Lösung:**
1. App ist abgestürzt
2. Gehe zu **"Deployments"** → **"Redeploy"**
3. Oder: Logs prüfen und Fehler beheben

---

## ✅ Checkliste

- [ ] Railway.app Account erstellt
- [ ] Mit GitHub verbunden
- [ ] Repository "pcbf-framework" deployed
- [ ] Umgebungsvariable `OPENROUTER_API_KEY` gesetzt
- [ ] Deployment erfolgreich (Status: Success)
- [ ] Domain generiert
- [ ] Website erreichbar

---

## 🎉 Fertig!

**Deine Website ist jetzt dauerhaft online unter:**

`https://pcbf-framework-production.up.railway.app`

(oder deine Custom Domain)

---

## 💰 Kosten

**Railway Starter Plan:** $5/Monat

**Inkludiert:**
- 500 Stunden Laufzeit/Monat
- Automatische HTTPS
- Custom Domain
- Unbegrenzte Deployments

---

## 📚 Weitere Hilfe

- **Railway Dokumentation:** https://docs.railway.app
- **Support:** https://railway.app/help
- **Community:** https://discord.gg/railway

---

**Bei Fragen:** Siehe `RAILWAY_DEPLOYMENT.md` für Details

