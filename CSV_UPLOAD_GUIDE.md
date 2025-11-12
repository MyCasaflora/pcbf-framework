# PCBF 2.1 - CSV-Upload & Batch-Analyse Leitfaden

## Vollständige Anleitung zur CSV-basierten Profil-Analyse

---

## 🎯 Überblick

Die **PCBF 2.1 CSV Validation UI** ermöglicht den Upload von CSV-Dateien mit Rohdaten und führt automatisch eine Batch-Analyse durch. Die Ergebnisse werden nach den vier Psychologisierungs-Modellen gruppiert und können einzeln exportiert werden.

---

## 📦 Features

### 1. CSV-Upload
- ✅ **Drag & Drop** oder Datei-Auswahl
- ✅ **Automatische Validierung** der CSV-Struktur
- ✅ **Batch-Verarbeitung** mehrerer Profile
- ✅ **Fortschritts-Anzeige**

### 2. Automatische Analyse
- ✅ **Parallele Verarbeitung** (5 Worker)
- ✅ **Alle 4 Psychologisierungs-Modelle**:
  - DISC-Modell
  - NEO-Modell (Big Five)
  - Cialdini-Modell (Persuasion)
  - RIASEC-Modell (Holland Codes)

### 3. Gruppierte Ergebnisse
- ✅ **Tab-basierte Navigation** zwischen Modellen
- ✅ **Übersichtliche Tabellen** mit allen Daten
- ✅ **Tooltips** für lange Texte (Reasoning)
- ✅ **Echtzeit-Statistiken**

### 4. Export-Funktionen
- ✅ **CSV-Export** pro Modell
- ✅ **Automatische Dateinamen** mit Analyse-ID
- ✅ **Alle Spalten** inklusive Reasoning

---

## 🚀 Schnellstart

### Schritt 1: Server starten

```bash
cd /home/ubuntu/pcbf_framework
python3 validation_ui_csv.py
```

Server läuft auf: **http://localhost:8002**

Öffentlich: **https://8002-i10gec5oawwi59ab9yrf5-2da1d099.manusvm.computer**

### Schritt 2: CSV-Datei vorbereiten

**Erforderliche Spalten:**
```csv
lead_uuid,email,phone,est_age,lead_id,full_name,nickname,verified,bio,bioLink,likes,posts,categories,business_account,followers,following,posts,platform_id,platform_name
```

**Beispiel:**
```csv
lead_uuid,lead_id,full_name,bio,categories,followers,following,posts,platform_name
ebb89000-bc09-40d6-8550-72cc5306adad,317210,Taxfintra,"💼 Virtual CFO | M&A | Valuation...",NULL,3343,74,10,Instagram
```

### Schritt 3: CSV hochladen

1. Öffne Web-UI
2. Drag & Drop oder Datei auswählen
3. Optional: Target Keywords eingeben
4. Optional: Produkt-Kategorie anpassen
5. **"Analysieren"** klicken

### Schritt 4: Ergebnisse ansehen

- **Dashboard:** Gesamt-Statistiken
- **Tabs:** Zwischen Modellen wechseln
- **Tabellen:** Alle Daten pro Modell
- **Export:** CSV pro Modell herunterladen

---

## 📋 CSV-Format

### Erforderliche Spalten

| Spalte | Typ | Erforderlich | Beschreibung |
|--------|-----|--------------|--------------|
| `lead_uuid` | String | Ja | Eindeutige ID |
| `lead_id` | Integer | Optional | Numerische ID |
| `full_name` | String | Optional | Vollständiger Name |
| `bio` | String | **Ja** | Profil-Bio (Hauptdatenquelle) |
| `categories` | String | Optional | Kategorien/Themen |
| `followers` | Integer | Optional | Follower-Anzahl |
| `following` | Integer | Optional | Following-Anzahl |
| `posts` | Integer | Optional | Post-Anzahl |
| `platform_name` | String | Optional | Plattform-Name |

### Optionale Spalten

- `email`, `phone`, `est_age`, `nickname`, `verified`, `bioLink`, `likes`, `business_account`, `platform_id`

### Hinweise

- **Bio ist Pflicht:** Ohne Bio keine Analyse möglich
- **NULL-Werte:** Werden als `None` interpretiert
- **Encoding:** UTF-8 empfohlen
- **Trennzeichen:** Komma (`,`)

---

## 🔍 Analyse-Prozess

### 1. CSV-Parsing

```python
# Automatisch
profiles = csv_processor.parse_csv(csv_content)
```

**Validierung:**
- ✅ Spalten vorhanden
- ✅ Bio nicht leer
- ✅ Datentypen korrekt

### 2. Batch-Analyse

```python
results = csv_processor.analyze_batch(
    profiles=profiles,
    target_keywords=['KI', 'Software'],
    product_category='Software'
)
```

**Parallel-Verarbeitung:**
- 5 Worker gleichzeitig
- Timeout: 60 Sekunden pro Profil
- Retry bei Fehlern

### 3. Modell-Gruppierung

```python
disc_data = extract_model_data(results, 'disc')
neo_data = extract_model_data(results, 'neo')
persuasion_data = extract_model_data(results, 'persuasion')
riasec_data = extract_model_data(results, 'riasec')
```

### 4. Ergebnis-Anzeige

- **Vorschau:** Erste 10 Profile pro Modell
- **Vollständig:** Alle Profile über API abrufbar
- **Export:** CSV-Download pro Modell

---

## 📊 Ergebnis-Struktur

### DISC-Modell

**Spalten:**
```
lead_id, primary_type, secondary_type, subtype, archetype, 
score_d, score_i, score_s, score_c, confidence, reasoning
```

**Beispiel:**
```json
{
  "lead_id": "317210",
  "primary_type": "C",
  "secondary_type": "D",
  "subtype": "Cd",
  "archetype": "Skeptic",
  "score_d": 0.17,
  "score_i": 0.13,
  "score_s": 0.33,
  "score_c": 0.38,
  "confidence": 65,
  "reasoning": "Die Bio zeigt eine stark sachlich-analytische Ausrichtung..."
}
```

---

### NEO-Modell (Big Five)

**Spalten:**
```
lead_id, openness, conscientiousness, extraversion, 
agreeableness, neuroticism, confidence, reasoning
```

**Beispiel:**
```json
{
  "lead_id": "317210",
  "openness": 0.66,
  "conscientiousness": 0.75,
  "extraversion": 0.40,
  "agreeableness": 0.44,
  "neuroticism": 0.30,
  "confidence": 50,
  "reasoning": "Die Bio zeigt hohe Fachkompetenz in anspruchsvollen..."
}
```

---

### Cialdini-Modell (Persuasion)

**Spalten:**
```
lead_id, score_authority, score_social_proof, score_scarcity, 
score_reciprocity, score_consistency, score_liking, score_unity, 
primary_principle, confidence, reasoning
```

**Beispiel:**
```json
{
  "lead_id": "317210",
  "score_authority": 0.54,
  "score_social_proof": 0.18,
  "score_scarcity": 0.06,
  "score_reciprocity": 0.00,
  "score_consistency": 0.18,
  "score_liking": 0.12,
  "score_unity": 0.00,
  "primary_principle": "authority",
  "confidence": 70,
  "reasoning": "Die Bio vermittelt stark Authority durch die klare Nennung..."
}
```

---

### RIASEC-Modell (Holland Codes)

**Spalten:**
```
lead_id, holland_code, score_r, score_i, score_a, score_s, 
score_e, score_c, primary_dim, confidence, source, reasoning
```

**Beispiel:**
```json
{
  "lead_id": "317210",
  "holland_code": "CIE",
  "score_r": 0.03,
  "score_i": 0.22,
  "score_a": 0.07,
  "score_s": 0.11,
  "score_e": 0.22,
  "score_c": 0.34,
  "primary_dim": "C",
  "confidence": 55,
  "source": "bio",
  "reasoning": "Die Bio beschreibt Tätigkeiten in den Bereichen Finanzmanagement..."
}
```

---

## 🌐 Web-UI Bedienung

### Dashboard

```
┌────────────────────────────────────────────────┐
│ 📊 PCBF 2.1 CSV Validation UI                 │
│ CSV-Upload für Batch-Analyse                  │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ CSV-Datei hochladen                            │
│                                                │
│ ┌──────────────────────────────────────────┐  │
│ │         📁                               │  │
│ │  CSV-Datei hier ablegen                  │  │
│ │  oder klicken zum Auswählen              │  │
│ └──────────────────────────────────────────┘  │
│                                                │
│ ✅ Datei ausgewählt: raw-data-pcbf.csv        │
│                                                │
│ Target Keywords: [KI, Software, Innovation]   │
│ Produkt-Kategorie: [Software            ]     │
│                                                │
│ [🚀 Analysieren]                              │
└────────────────────────────────────────────────┘
```

### Ergebnisse

```
┌────────────────────────────────────────────────┐
│ 📈 Analyse-Zusammenfassung                     │
├────────────────────────────────────────────────┤
│  Profile    DISC    NEO    Persuasion  RIASEC │
│    10        10     10        10         10    │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ [DISC-Modell: 10] [NEO-Modell: 10]            │
│ [Cialdini-Modell: 10] [RIASEC-Modell: 10]     │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ DISC-Modell                                    │
│ [📥 DISC als CSV exportieren]                 │
│                                                │
│ ┌──────────────────────────────────────────┐  │
│ │ LEAD_ID | PRIMARY | SECONDARY | ...     │  │
│ ├──────────────────────────────────────────┤  │
│ │ 317210  │    C    │     D     │ ...     │  │
│ │ 317211  │    D    │     I     │ ...     │  │
│ └──────────────────────────────────────────┘  │
└────────────────────────────────────────────────┘
```

---

## 🔧 API-Endpunkte

### 1. CSV hochladen

**POST** `/api/upload-csv`

**Request:**
```bash
curl -X POST http://localhost:8002/api/upload-csv \
  -F "file=@raw-data-pcbf.csv" \
  -F "target_keywords=KI,Software" \
  -F "product_category=Software"
```

**Response:**
```json
{
  "success": true,
  "analysis_id": "1731417600",
  "total_profiles": 10,
  "models": {
    "disc": [...],
    "neo": [...],
    "persuasion": [...],
    "riasec": [...]
  },
  "summary": {
    "disc_count": 10,
    "neo_count": 10,
    "persuasion_count": 10,
    "riasec_count": 10
  }
}
```

---

### 2. Ergebnisse abrufen

**GET** `/api/results/{analysis_id}`

**Request:**
```bash
curl http://localhost:8002/api/results/1731417600
```

**Response:**
```json
{
  "success": true,
  "analysis_id": "1731417600",
  "total_profiles": 10,
  "models": {
    "disc": [...],
    "neo": [...],
    "persuasion": [...],
    "riasec": [...]
  }
}
```

---

### 3. Modell exportieren

**GET** `/api/export/{analysis_id}/{model}`

**Request:**
```bash
curl -O http://localhost:8002/api/export/1731417600/disc
```

**Response:**
CSV-Datei: `pcbf_disc_1731417600.csv`

**Modelle:**
- `disc`
- `neo`
- `persuasion`
- `riasec`

---

## 💡 Use Cases

### Use Case 1: Lead-Analyse für Marketing

**Szenario:** 1000 Instagram-Profile analysieren

**Workflow:**
1. CSV mit Instagram-Daten exportieren
2. In PCBF CSV-UI hochladen
3. Target Keywords: "Fitness, Gesundheit, Ernährung"
4. Produkt-Kategorie: "Fitness-App"
5. Analysieren
6. DISC-Daten exportieren
7. In CRM importieren
8. Personalisierte Kampagnen erstellen

**Ergebnis:**
- Segmentierung nach DISC-Typen
- Personalisierte Ansprache
- Höhere Conversion-Rate

---

### Use Case 2: Talent-Acquisition

**Szenario:** 500 LinkedIn-Profile für Recruiting

**Workflow:**
1. CSV mit LinkedIn-Daten exportieren
2. In PCBF CSV-UI hochladen
3. Target Keywords: "Software, Development, Engineering"
4. Produkt-Kategorie: "Tech Job"
5. Analysieren
6. RIASEC-Daten exportieren
7. Nach Holland-Codes filtern (z.B. IEC für Developer)
8. Top-Kandidaten kontaktieren

**Ergebnis:**
- Bessere Job-Fit-Analyse
- Reduzierte Fehlbesetzungen
- Schnellere Hiring-Prozesse

---

### Use Case 3: Influencer-Matching

**Szenario:** 200 Influencer für Kampagne finden

**Workflow:**
1. CSV mit Influencer-Daten exportieren
2. In PCBF CSV-UI hochladen
3. Target Keywords: "Fashion, Lifestyle, Luxury"
4. Produkt-Kategorie: "Fashion Brand"
5. Analysieren
6. Persuasion-Daten exportieren
7. Nach Authority + Social Proof filtern
8. Top-Influencer auswählen

**Ergebnis:**
- Authentische Partnerschaften
- Höhere Engagement-Raten
- Besserer ROI

---

## 📈 Performance

### Geschwindigkeit

| Profile | Zeit (5 Worker) | Zeit pro Profil |
|---------|-----------------|-----------------|
| 10 | 20-30s | 2-3s |
| 50 | 2-3min | 2.4-3.6s |
| 100 | 4-6min | 2.4-3.6s |
| 500 | 20-30min | 2.4-3.6s |
| 1000 | 40-60min | 2.4-3.6s |

### Optimierung

**Mehr Worker:**
```python
# In csv_processor.py
results = self.analyzer.analyze_batch(
    profiles=profiles,
    max_workers=10  # Standard: 5
)
```

**Timeout anpassen:**
```python
# In validation_ui_csv.py
response = requests.post(url, files=files, data=data, timeout=600)  # 10 Min
```

---

## 🐛 Troubleshooting

### Problem 1: "Keine Profile in CSV gefunden"

**Ursache:** CSV-Format falsch oder Bio fehlt

**Lösung:**
1. CSV-Header prüfen
2. Bio-Spalte vorhanden?
3. Encoding UTF-8?

---

### Problem 2: Timeout bei großen CSV-Dateien

**Ursache:** Zu viele Profile, Server-Timeout

**Lösung:**
1. CSV in kleinere Batches aufteilen (z.B. 100 Profile)
2. Timeout erhöhen
3. Mehr Worker verwenden

---

### Problem 3: Leere Reasoning-Felder

**Ursache:** LLM-API-Fehler oder Rate-Limit

**Lösung:**
1. API-Key prüfen
2. Rate-Limits beachten
3. Retry-Logik nutzt automatisch Fallback

---

## ✅ Best Practices

### 1. CSV-Vorbereitung
- ✅ Bio-Qualität prüfen (>50 Wörter empfohlen)
- ✅ Duplikate entfernen
- ✅ NULL-Werte minimieren
- ✅ Encoding UTF-8

### 2. Batch-Größe
- ✅ **10-100 Profile** optimal
- ✅ Bei >100: In Batches aufteilen
- ✅ Bei >1000: Overnight-Job

### 3. Target Keywords
- ✅ 3-5 Keywords optimal
- ✅ Spezifisch, nicht generisch
- ✅ Produkt-relevant

### 4. Ergebnis-Validierung
- ✅ Stichproben manuell prüfen
- ✅ Confidence-Werte beachten
- ✅ Reasoning lesen

---

## 🚀 Deployment

### Lokal

```bash
python3 validation_ui_csv.py
```

### Docker

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "validation_ui_csv.py"]
```

```bash
docker build -t pcbf-csv-ui .
docker run -p 8002:8002 pcbf-csv-ui
```

### Systemd-Service

```ini
[Unit]
Description=PCBF CSV Validation UI
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/pcbf_framework
ExecStart=/usr/bin/python3 validation_ui_csv.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable pcbf-csv-ui
sudo systemctl start pcbf-csv-ui
```

---

## 📦 Zusammenfassung

### Implementiert

✅ **CSV-Upload** mit Drag & Drop  
✅ **Batch-Analyse** mit 5 Workern  
✅ **4 Psychologisierungs-Modelle**  
✅ **Gruppierte Ergebnisse** in Tabs  
✅ **CSV-Export** pro Modell  
✅ **Web-UI** mit Echtzeit-Statistiken  
✅ **API-Endpunkte** für Automatisierung

### Vorteile

- ⚡ **Schnell:** 2-3 Sekunden pro Profil
- 🎯 **Präzise:** 4 Modelle parallel
- 📊 **Übersichtlich:** Gruppierte Darstellung
- 📥 **Exportierbar:** CSV pro Modell
- 🔧 **Flexibel:** API + Web-UI

---

**PCBF 2.1 CSV Validation UI** - Professionelle Batch-Analyse für Psychologisierungs-Modelle! 🎉

