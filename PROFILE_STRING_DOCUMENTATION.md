# PCBF 2.1 Framework - Profil-String-Dokumentation

## Kompakte Profil-Repräsentation für externe Tools

---

## 🎯 Überblick

Das PCBF 2.1 Framework generiert **kompakte Profil-Strings**, die alle Analyse-Ergebnisse in einer einzigen Zeile zusammenfassen. Diese Strings ermöglichen die einfache Integration mit CRM-Systemen, Datenbanken und anderen Tools.

---

## 📝 String-Formate

### 1. Kompakter String (Standard)

**Format:**
```
DISC:D | NEO:C=0.92,E=0.88,O=0.85 | RIASEC:IEC | PERS:authority | PI:82
```

**Komponenten:**
- `DISC:D` - DISC Primary Type (D/I/S/C)
- `NEO:C=0.92,E=0.88,O=0.85` - Top 3 NEO-Dimensionen mit Scores
- `RIASEC:IEC` - Holland-Code (3 Buchstaben)
- `PERS:authority` - Primäres Persuasion-Prinzip
- `PI:82` - Purchase Intent Score (0-100)

**Mit Confidence:**
```
DISC:Di(68%) | NEO:C=0.92,E=0.88,O=0.85(58%) | RIASEC:IEC(75%) | PERS:authority(72%) | PI:82
```

**Verwendung:**
- Datenbank-Speicherung (VARCHAR 200)
- API-Responses
- Logging und Audit-Trails

---

### 2. Detaillierter String

**Format:**
```
DISC:C=0.10,D=0.45,I=0.30,S=0.15 | NEO:O=0.85,C=0.92,E=0.88,A=0.65,N=0.42 | RIASEC:A=0.15,C=0.40,E=0.55,I=0.60,R=0.10,S=0.20 | PERS:AUTH=0.85,SPROOF=0.60,SCAR=0.30,RECIP=0.40,CONS=0.55,LIKE=0.50,UNITY=0.45 | PI:82.50 | CONF:78.50
```

**Komponenten:**
- Alle DISC-Scores (D, I, S, C)
- Alle NEO-Dimensionen (O, C, E, A, N)
- Alle RIASEC-Scores (R, I, A, S, E, C)
- Alle Persuasion-Scores (7 Prinzipien)
- Purchase Intent Score
- Overall Confidence

**Verwendung:**
- Machine Learning Features
- Detaillierte Analyse
- Debugging

---

### 3. Benutzerdefinierte Strings

**Template-Variablen:**

| Variable | Beschreibung | Beispiel |
|----------|--------------|----------|
| `{disc_primary}` | DISC Primary Type | D |
| `{disc_archetype}` | DISC Archetyp | Captain |
| `{neo_o}`, `{neo_c}`, `{neo_e}`, `{neo_a}`, `{neo_n}` | NEO-Dimensionen | 0.85 |
| `{riasec_code}` | Holland-Code | IEC |
| `{riasec_primary}` | Primärer RIASEC-Typ | I |
| `{persuasion_primary}` | Primäres Persuasion-Prinzip | authority |
| `{pi_score}` | Purchase Intent Score | 82 |
| `{pi_category}` | Purchase Intent Kategorie | very_high |
| `{confidence}` | Overall Confidence | 78 |

**Beispiel-Templates:**

```python
# Sehr kurz (für CRM-Tags)
"{disc_primary}-{riasec_code}-PI{pi_score}"
# Ergebnis: D-IEC-PI82

# Für Segmentierung
"{disc_primary}_{riasec_primary}_{persuasion_primary}_{pi_category}"
# Ergebnis: D_I_authority_very_high

# Für Dashboards
"DISC:{disc_primary}({disc_archetype}) | RIASEC:{riasec_code} | PI:{pi_score}"
# Ergebnis: DISC:D(Captain) | RIASEC:IEC | PI:82
```

---

## 📊 CSV-Export

### Struktur

Die CSV-Datei enthält **52 Spalten** mit allen Analyse-Daten:

#### Meta-Daten (5 Spalten)
- `profile_id`
- `timestamp`
- `processing_time_seconds`
- `warnings_count`
- `has_critical_warnings`

#### Datenqualität (5 Spalten)
- `bio_quality_score`
- `bio_word_count`
- `bio_category`
- `keywords_match_score`
- `overall_confidence`

#### DISC (10 Spalten)
- `disc_primary`, `disc_secondary`, `disc_subtype`, `disc_archetype`
- `disc_confidence`
- `disc_score_d`, `disc_score_i`, `disc_score_s`, `disc_score_c`

#### NEO (6 Spalten)
- `neo_openness`, `neo_conscientiousness`, `neo_extraversion`, `neo_agreeableness`, `neo_neuroticism`
- `neo_confidence`

#### RIASEC (10 Spalten)
- `riasec_holland_code`, `riasec_primary`, `riasec_source`
- `riasec_confidence`
- `riasec_score_r`, `riasec_score_i`, `riasec_score_a`, `riasec_score_s`, `riasec_score_e`, `riasec_score_c`

#### Persuasion (9 Spalten)
- `persuasion_primary`, `persuasion_confidence`
- `persuasion_authority`, `persuasion_social_proof`, `persuasion_scarcity`, `persuasion_reciprocity`, `persuasion_consistency`, `persuasion_liking`, `persuasion_unity`

#### Purchase Intent (2 Spalten)
- `purchase_intent_score`
- `purchase_intent_category`

#### Communication Strategy (4 Spalten)
- `comm_style`
- `comm_tone`
- `comm_content_focus`
- `comm_persuasion_approach`

#### Profil-Strings (2 Spalten)
- `profile_string_compact` - Kompakter String
- `profile_string_detailed` - Detaillierter String

---

## 🔌 API-Integration

### Endpoint 1: Standard-Analyse mit Profil-String

```bash
POST /analyze
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "profile_id": "test_001",
      "disc": {...},
      "neo": {...},
      "riasec": {...},
      "persuasion": {...},
      "purchase_intent": {...},
      "profile_string": "DISC:Di(68%) | NEO:C=0.92,E=0.88,O=0.85(58%) | RIASEC:IEC(75%) | PERS:authority(72%) | PI:82"
    }
  ]
}
```

---

### Endpoint 2: CSV-Export

```bash
POST /analyze/export-csv
```

**Request:**
```json
{
  "profiles": [
    {
      "id": "profile_001",
      "bio": "CEO bei TechCorp...",
      "categories": "KI • Software"
    }
  ],
  "target_keywords": ["KI", "Software"],
  "product_category": "Software"
}
```

**Response:**
- CSV-Datei als Download
- Dateiname: `pcbf_analysis_<timestamp>.csv`

---

### Endpoint 3: JSON-Lines-Export

```bash
POST /analyze/export-jsonl
```

**Response:**
- JSON-Lines-Datei (eine JSON-Zeile pro Profil)
- Dateiname: `pcbf_analysis_<timestamp>.jsonl`

**Beispiel-Zeile:**
```json
{"profile_id":"test_001","disc_primary":"D","neo_openness":0.85,...}
```

---

## 💡 Use Cases

### Use Case 1: CRM-Integration (Salesforce, HubSpot)

**Problem:** Profil-Daten in CRM speichern.

**Lösung:** Kompakter String in Custom-Field.

```python
# Salesforce Custom Field: "PCBF_Profile__c" (Text, 200 Zeichen)
profile_string = "DISC:D | NEO:C=0.92,E=0.88,O=0.85 | RIASEC:IEC | PI:82"

# API-Call
sf.Contact.update(contact_id, {'PCBF_Profile__c': profile_string})
```

**Vorteile:**
- Kompakt (< 200 Zeichen)
- Menschenlesbar
- Einfach zu filtern (z.B. alle "DISC:D")

---

### Use Case 2: Lead-Scoring in Marketing-Automation

**Problem:** Leads automatisch priorisieren.

**Lösung:** Purchase Intent Score extrahieren.

```python
# Aus Profil-String extrahieren
profile_string = "DISC:D | NEO:C=0.92 | RIASEC:IEC | PI:82"
pi_score = int(profile_string.split("PI:")[1])

# Lead-Scoring
if pi_score > 80:
    priority = "Hot"
elif pi_score > 60:
    priority = "Warm"
else:
    priority = "Cold"
```

---

### Use Case 3: Personalisierte E-Mail-Kampagnen

**Problem:** E-Mails basierend auf DISC-Typ personalisieren.

**Lösung:** DISC-Typ aus String extrahieren.

```python
# DISC-Typ extrahieren
profile_string = "DISC:Di(68%) | NEO:C=0.92 | RIASEC:IEC | PI:82"
disc_type = profile_string.split("DISC:")[1].split("(")[0]  # "Di"

# Template auswählen
if disc_type.startswith('D'):
    template = "direct_email_template"
elif disc_type.startswith('I'):
    template = "enthusiastic_email_template"
# ...
```

---

### Use Case 4: Datenanalyse in Excel/Tableau

**Problem:** Profil-Daten visualisieren.

**Lösung:** CSV-Export nutzen.

```bash
# CSV exportieren
curl -X POST http://localhost:8000/analyze/export-csv \
  -H "Content-Type: application/json" \
  -d @profiles.json \
  -o analysis.csv

# In Excel/Tableau öffnen
# Pivot-Tabellen erstellen:
# - DISC-Verteilung
# - Purchase Intent nach RIASEC
# - NEO-Dimensionen nach Industrie
```

---

### Use Case 5: Machine Learning Features

**Problem:** Profil-Daten für ML-Modell nutzen.

**Lösung:** Detaillierter String oder CSV.

```python
import pandas as pd

# CSV laden
df = pd.read_csv('analysis.csv')

# Features extrahieren
features = df[[
    'disc_score_d', 'disc_score_i', 'disc_score_s', 'disc_score_c',
    'neo_openness', 'neo_conscientiousness', 'neo_extraversion',
    'riasec_score_i', 'riasec_score_e', 'riasec_score_c',
    'persuasion_authority', 'persuasion_social_proof'
]]

# Target
target = df['purchase_intent_score']

# ML-Modell trainieren
from sklearn.ensemble import RandomForestRegressor
model = RandomForestRegressor()
model.fit(features, target)
```

---

## 🔧 Implementierung

### Python-Code

```python
from profile_string_generator import ProfileStringGenerator

# Generator erstellen
generator = ProfileStringGenerator()

# Kompakter String
compact = generator.generate_compact_string(result)
# "DISC:D | NEO:C=0.92,E=0.88,O=0.85 | RIASEC:IEC | PI:82"

# Detaillierter String
detailed = generator.generate_detailed_string(result)
# "DISC:C=0.10,D=0.45,I=0.30,S=0.15 | ..."

# Benutzerdefiniert
template = "{disc_primary}-{riasec_code}-PI{pi_score}"
custom = generator.generate_custom_string(result, template)
# "D-IEC-PI82"

# CSV-Export
from profile_string_generator import export_to_csv
export_to_csv(results, 'output.csv')
```

---

### API-Verwendung

```bash
# Standard-Analyse (inkl. profile_string)
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "profiles": [{"id": "test", "bio": "CEO..."}]
  }'

# CSV-Export
curl -X POST http://localhost:8000/analyze/export-csv \
  -H "Content-Type: application/json" \
  -d @profiles.json \
  -o analysis.csv

# JSON-Lines-Export
curl -X POST http://localhost:8000/analyze/export-jsonl \
  -H "Content-Type: application/json" \
  -d @profiles.json \
  -o analysis.jsonl
```

---

## 📋 Best Practices

### 1. Datenbank-Speicherung

**Empfehlung:** Kompakter String in separater Spalte.

```sql
CREATE TABLE profiles (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200),
    email VARCHAR(200),
    pcbf_profile VARCHAR(200),  -- Kompakter String
    pcbf_pi_score INT,          -- Purchase Intent (für Queries)
    pcbf_disc_type CHAR(2),     -- DISC-Typ (für Filtering)
    created_at TIMESTAMP
);

-- Index für schnelle Queries
CREATE INDEX idx_pi_score ON profiles(pcbf_pi_score);
CREATE INDEX idx_disc_type ON profiles(pcbf_disc_type);
```

---

### 2. CRM-Integration

**Empfehlung:** Custom Fields für wichtigste Werte.

```
Custom Fields:
- PCBF_Profile_String (Text, 200)
- PCBF_Purchase_Intent (Number, 0-100)
- PCBF_DISC_Type (Picklist: D, I, S, C)
- PCBF_RIASEC_Code (Text, 3)
- PCBF_Last_Updated (Date)
```

---

### 3. Datenanalyse

**Empfehlung:** CSV-Export für Batch-Analysen.

```python
# Monatlicher Report
profiles = get_all_profiles_from_crm()
results = analyze_batch(profiles)
export_to_csv(results, f'report_{month}.csv')

# Tableau/Power BI importieren
# Pivot-Tabellen erstellen
# Dashboards bauen
```

---

## 🔍 String-Parsing

### Python

```python
def parse_compact_string(profile_string):
    """Parst kompakten Profil-String"""
    parts = profile_string.split(' | ')
    
    parsed = {}
    for part in parts:
        if part.startswith('DISC:'):
            parsed['disc'] = part.split(':')[1].split('(')[0]
        elif part.startswith('NEO:'):
            neo_str = part.split(':')[1].split('(')[0]
            parsed['neo'] = dict(item.split('=') for item in neo_str.split(','))
        elif part.startswith('RIASEC:'):
            parsed['riasec'] = part.split(':')[1].split('(')[0]
        elif part.startswith('PERS:'):
            parsed['persuasion'] = part.split(':')[1].split('(')[0]
        elif part.startswith('PI:'):
            parsed['pi_score'] = int(part.split(':')[1])
    
    return parsed

# Beispiel
profile_string = "DISC:D | NEO:C=0.92,E=0.88,O=0.85 | RIASEC:IEC | PI:82"
parsed = parse_compact_string(profile_string)
# {'disc': 'D', 'neo': {'C': '0.92', 'E': '0.88', 'O': '0.85'}, 'riasec': 'IEC', 'pi_score': 82}
```

---

### JavaScript

```javascript
function parseCompactString(profileString) {
    const parts = profileString.split(' | ');
    const parsed = {};
    
    parts.forEach(part => {
        if (part.startsWith('DISC:')) {
            parsed.disc = part.split(':')[1].split('(')[0];
        } else if (part.startsWith('NEO:')) {
            const neoStr = part.split(':')[1].split('(')[0];
            parsed.neo = Object.fromEntries(
                neoStr.split(',').map(item => item.split('='))
            );
        } else if (part.startsWith('RIASEC:')) {
            parsed.riasec = part.split(':')[1].split('(')[0];
        } else if (part.startsWith('PI:')) {
            parsed.piScore = parseInt(part.split(':')[1]);
        }
    });
    
    return parsed;
}
```

---

## 📝 Zusammenfassung

### Verfügbare Formate:

| Format | Länge | Use Case |
|--------|-------|----------|
| **Kompakt** | ~90 Zeichen | Datenbank, CRM, Logging |
| **Kompakt (ohne Confidence)** | ~70 Zeichen | Platzsparend |
| **Detailliert** | ~230 Zeichen | ML-Features, Debugging |
| **Custom (Kurz)** | ~10 Zeichen | Tags, Segmentierung |
| **CSV** | 52 Spalten | Datenanalyse, Excel, Tableau |
| **JSON-Lines** | 1 Zeile/Profil | Streaming, Big Data |

### Empfohlene Formate:

- **CRM-Integration:** Kompakt (ohne Confidence)
- **Lead-Scoring:** Custom (Kurz) - `{disc_primary}-{riasec_code}-PI{pi_score}`
- **Datenanalyse:** CSV-Export
- **Machine Learning:** CSV oder Detailliert
- **Segmentierung:** Custom - `{disc_primary}_{riasec_primary}_{pi_category}`

---

**PCBF 2.1 Framework** - Profil-Strings für nahtlose Tool-Integration

