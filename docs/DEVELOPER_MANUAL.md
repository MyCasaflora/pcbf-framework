# PCBF 2.1 - Entwickler-Handbuch für das Prüfprotokoll

## 📋 Inhaltsverzeichnis

1. [Einführung](#einführung)
2. [Systemanforderungen](#systemanforderungen)
3. [Installation](#installation)
4. [Projektstruktur](#projektstruktur)
5. [Kernkomponenten](#kernkomponenten)
6. [Workflow](#workflow)
7. [API-Dokumentation](#api-dokumentation)
8. [Anpassung & Erweiterung](#anpassung--erweiterung)
9. [Testing](#testing)
10. [Deployment](#deployment)

---

## 1. Einführung

Dieses Handbuch beschreibt die technische Implementierung des **PCBF 2.1 Prüfprotokolls** und wie es in Betrieb genommen, angepasst und erweitert werden kann.

### Zielgruppe

- Software-Entwickler
- DevOps-Ingenieure
- Technische Projektmanager

### Was ist das Prüfprotokoll?

Das Prüfprotokoll ist ein Python-Modul (`validation_protocol.py`), das die Qualität und Plausibilität der PCBF 2.1 Analyse-Ergebnisse sicherstellt.

**Siehe:** `docs/VALIDATION_CONCEPT_OVERVIEW.md` für eine detaillierte Konzept-Beschreibung.

---

## 2. Systemanforderungen

- **Python:** 3.10+
- **Betriebssystem:** Linux, macOS, Windows (WSL2 empfohlen)
- **Abhängigkeiten:** Siehe `requirements.txt`

---

## 3. Installation

### 1. Repository klonen

```bash
git clone https://github.com/MyCasaflora/pcbf-framework.git
cd pcbf-framework
```

### 2. Virtuelle Umgebung erstellen

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 4. Umgebungsvariablen setzen

Erstellen Sie eine `.env`-Datei im Hauptverzeichnis:

```bash
cp .env.example .env
```

Öffnen Sie die `.env`-Datei und fügen Sie Ihren API-Key hinzu:

```
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
```

---

## 4. Projektstruktur

```
pcbf_framework/
├── docs/                          # Dokumentation
│   ├── DEVELOPER_MANUAL.md        # Dieses Handbuch
│   ├── VALIDATION_CONCEPT_OVERVIEW.md # Konzept-Übersicht
│   ├── QA_GUIDE.md                # Qualitätssicherungs-Leitfaden
│   └── ...
├── agents/                        # Analyse-Agenten (DISC, NEO, etc.)
├── logs/                          # Log-Dateien
├── tests/                         # Test-Dateien
├── venv/                          # Virtuelle Umgebung
├── .env                           # Umgebungsvariablen
├── .gitignore
├── app.py                         # Haupt-API (FastAPI)
├── analyzer.py                    # Orchestriert die Analyse-Agenten
├── csv_processor.py               # Verarbeitet CSV-Uploads
├── llm_client.py                  # LLM-Integration (OpenRouter)
├── models.py                      # Pydantic-Datenmodelle
├── requirements.txt               # Python-Abhängigkeiten
├── validation_protocol.py         # ⭐ Das Prüfprotokoll
├── validation_ui_csv.py           # Web-UI für Validierung
└── ...
```

---

## 5. Kernkomponenten

### `validation_protocol.py`

**Zweck:** Führt alle Validierungs-Checks durch.

**Klasse:** `ValidationProtocol`

**Hauptmethode:** `validate(profile_input, analysis_result)`

**Rückgabewert:** `ValidationReport` (Pydantic-Modell)

**Beispiel-Verwendung:**

```python
from validation_protocol import ValidationProtocol
from models import ProfileInput, AnalysisResult, ValidationReport

# 1. Eingangsdaten und Analyse-Ergebnis
profile_input = ProfileInput(...)
analysis_result = AnalysisResult(...)

# 2. Validator instanziieren
validator = ValidationProtocol()

# 3. Validierung durchführen
report: ValidationReport = validator.validate(profile_input, analysis_result)

# 4. Ergebnisse prüfen
print(f"Status: {report.overall_status}")  # PASS/REVIEW/WARNING/FAIL
print(f"Score: {report.score}/100")

if report.overall_status == "FAIL":
    print("Fehler:", report.errors)
```

### `models.py`

**Zweck:** Definiert alle Datenstrukturen mit Pydantic.

**Wichtige Modelle:**

- `ProfileInput`: Eingangsdaten aus der CSV-Datei
- `AnalysisResult`: Ergebnisse der Analyse-Agenten
- `ValidationReport`: Ergebnis des Prüfprotokolls
- `CheckResult`: Ergebnis eines einzelnen Checks

### `validation_ui_csv.py`

**Zweck:** Stellt eine Web-UI für den CSV-Upload und die Validierung bereit.

**Framework:** FastAPI

**Starten:**

```bash
python3 validation_ui_csv.py
```

**URL:** http://localhost:8002

---

## 6. Workflow

### 1. CSV-Upload (via UI oder API)

- Benutzer lädt `raw-data-pcbf.csv` hoch
- `validation_ui_csv.py` empfängt die Datei

### 2. CSV-Verarbeitung (`csv_processor.py`)

- `CSVProcessor` parst die CSV-Datei
- Erstellt eine Liste von `ProfileInput`-Objekten

### 3. Analyse (`analyzer.py`)

- `ProfileAnalyzer` führt die Analyse für jedes Profil durch:
  - DISC, NEO, RIASEC, Persuasion, Purchase Intent
- Gibt eine Liste von `AnalysisResult`-Objekten zurück

### 4. Validierung (`validation_protocol.py`)

- `ValidationProtocol` validiert jedes `AnalysisResult` gegen das `ProfileInput`
- Führt 27+ Checks durch
- Gibt eine Liste von `ValidationReport`-Objekten zurück

### 5. Ergebnis-Anzeige (UI)

- Die Web-UI zeigt die Ergebnisse in gruppierten Tabellen an
- Status (PASS/FAIL) wird farblich hervorgehoben
- Detaillierte Reports sind per Klick einsehbar

---

## 7. API-Dokumentation

Die API wird mit FastAPI erstellt und bietet eine automatische Swagger-Dokumentation.

### API starten

```bash
python3 validation_ui_csv.py
```

### API-Dokumentation öffnen

**URL:** http://localhost:8002/docs

### Haupt-Endpoint

**Endpoint:** `/analyze-csv/`

**Methode:** `POST`

**Body:** `multipart/form-data`

- **`file`**: Die CSV-Datei (`raw-data-pcbf.csv`)

**Response:** `JSON`

- Eine Liste von `ValidationReport`-Objekten

**Beispiel-Aufruf mit `curl`:**

```bash
curl -X POST -F "file=@/path/to/raw-data-pcbf.csv" http://localhost:8002/analyze-csv/
```

---

## 8. Anpassung & Erweiterung

### Neue Validierungs-Checks hinzufügen

1. **Öffnen Sie `validation_protocol.py`**

2. **Erstellen Sie eine neue Check-Methode:**

   ```python
   def _check_custom_rule(self, profile_input: ProfileInput, analysis_result: AnalysisResult) -> CheckResult:
       """Prüft eine benutzerdefinierte Regel."""
       if profile_input.followers > 10000 and analysis_result.purchase_intent < 50:
           return CheckResult(
               name="Custom Rule: High Followers, Low PI",
               passed=False,
               message="Warnung: Hohe Follower-Zahl aber niedrige Kaufabsicht",
               severity="WARNING"
           )
       return CheckResult(name="Custom Rule: High Followers, Low PI", passed=True)
   ```

3. **Fügen Sie den Check zur `validate`-Methode hinzu:**

   ```python
   def validate(self, profile_input: ProfileInput, analysis_result: AnalysisResult) -> ValidationReport:
       # ...
       all_checks.append(self._check_custom_rule(profile_input, analysis_result))
       # ...
   ```

### Schwellenwerte anpassen

Die Schwellenwerte für die Checks sind am Anfang von `validation_protocol.py` definiert:

```python
# Schwellenwerte für Eingangsdaten-Validierung
MIN_BIO_LENGTH = 20
MIN_POSTS = 10
MIN_SOCIAL_ENGAGEMENT = 100

# ...
```

Ändern Sie diese Werte, um die Sensitivität der Validierung anzupassen.

---

## 9. Testing

### Unit-Tests

Ein umfassendes Test-Script für das Prüfprotokoll ist in `test_validation.py` enthalten.

**Starten:**

```bash
python3 test_validation.py
```

**Was wird getestet?**

- 3 Test-Profile (Gut, Mittel, Schlecht)
- Alle 27+ Validierungs-Checks
- Status-Berechnung (PASS/FAIL)
- Score-Berechnung

### API-Tests

Ein Test-Script für den CSV-Upload ist in `test_csv_upload.py` enthalten.

**Starten:**

```bash
python3 test_csv_upload.py
```

---

## 10. Deployment

Die Anwendung ist für das Deployment auf verschiedenen Plattformen vorbereitet.

### Docker

**Dockerfile** und **docker-compose.yml** sind im Hauptverzeichnis enthalten.

**Bauen:**
```bash
docker-compose build
```

**Starten:**
```bash
docker-compose up
```

### Systemd-Service (Linux)

Ein Systemd-Service für den dauerhaften Betrieb ist in `pcbf-csv-ui.service` definiert.

**Deployment-Script:**
```bash
./deploy.sh
```

**Management-Script:**
```bash
./manage.sh status|start|stop|restart|logs
```

### Platform-as-a-Service (PaaS)

**Empfehlung:** Railway.app oder Render.com

**Anleitungen:**
- `docs/guides/RAILWAY_DEPLOYMENT.md`
- `docs/guides/RENDER_DEPLOYMENT.md`

---

## Zusammenfassung

### In Betrieb nehmen

1. **Klonen:** `git clone ...`
2. **Installieren:** `pip install -r requirements.txt`
3. **Konfigurieren:** `.env`-Datei erstellen
4. **Starten:** `python3 validation_ui_csv.py`
5. **Öffnen:** http://localhost:8002

### Verstehen

- **Konzept:** `docs/VALIDATION_CONCEPT_OVERVIEW.md`
- **Code:** `validation_protocol.py`
- **Daten:** `models.py`

### Anpassen

- **Neue Checks:** `validation_protocol.py` → `_check_...` Methode hinzufügen
- **Schwellenwerte:** `validation_protocol.py` → Konstanten am Anfang ändern

### Testen

- **Unit-Tests:** `python3 test_validation.py`
- **API-Tests:** `python3g test_csv_upload.py`

---

**Bei Fragen:** Siehe die entsprechenden Dokumentations-Dateien im `docs`-Verzeichnis.

