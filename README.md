# PCBF 2.1 Framework

**Psychological & Cognitive Behavioral Framework** für die Analyse von Social-Media-Profilen und die Erstellung psychologischer Profile mit Purchase Intent Scoring.

## 📋 Übersicht

Das PCBF 2.1 Framework ist eine serverbasierte Python-Anwendung, die Social-Media-Profile analysiert und umfassende psychologische Profile erstellt. Die Analyse basiert auf etablierten psychologischen Modellen:

- **DISC**: Persönlichkeitstypen (Dominant, Influencer, Supporter, Analyst)
- **NEO/OCEAN**: Big Five Persönlichkeitsdimensionen
- **RIASEC**: Interessensprofile nach Holland-Codes
- **Cialdini**: 7 Persuasion-Prinzipien
- **Purchase Intent**: Kaufabsichtsbewertung (0-100)
- **Communication Strategy**: Personalisierte Kommunikationsempfehlungen

## 🎯 Hauptfunktionen

### 1. Bio-zentrierte Analyse
- Optimiert für minimale Datenverfügbarkeit
- Primäre Datenquelle: LinkedIn/Instagram Bio
- Sekundäre Quellen: Categories, Follower/Following-Ratio, Account-Status

### 2. Hybride Analyse-Methodik
- **Keyword-basiert**: Schnelle Basis-Klassifikation
- **LLM-basiert**: Semantisches Verständnis via GPT-4.1-mini (OpenRouter)
- **Kombiniert**: Gewichtete Fusion beider Ansätze

### 3. Confidence-basierte Bewertung
- Realistische Confidence-Levels (40-80%)
- Automatische Warnungen bei niedriger Datenqualität
- Transparente Begründung aller Klassifikationen

### 4. Parallele Verarbeitung
- Agenten laufen parallel (ThreadPoolExecutor)
- Batch-Verarbeitung für mehrere Profile
- Optimierte API-Aufrufe

## 🏗️ Architektur

```
pcbf_framework/
├── app.py                          # FastAPI Application
├── config.py                       # Konfiguration & Keywords
├── models.py                       # Pydantic-Datenmodelle
├── utils.py                        # Utility-Funktionen
├── llm_client.py                   # OpenRouter API-Client
├── analyzer.py                     # Main Analyzer (orchestriert Agenten)
├── purchase_intent.py              # Purchase Intent Calculator
├── communication_strategy.py       # Communication Strategy Generator
├── agents/
│   ├── __init__.py
│   ├── disc_agent.py              # DISC-Analyse
│   ├── neo_agent.py               # NEO/OCEAN-Analyse
│   ├── riasec_agent.py            # RIASEC-Analyse
│   └── persuasion_agent.py        # Persuasion-Analyse
├── logs/                           # Log-Dateien
├── requirements.txt                # Python-Dependencies
└── README.md                       # Diese Datei
```

## 🚀 Installation & Setup

### Voraussetzungen
- Python 3.11+
- OpenRouter API-Key

### 1. Dependencies installieren

```bash
cd /home/ubuntu/pcbf_framework
pip3 install -r requirements.txt
```

### 2. Umgebungsvariablen setzen

```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

Oder `.env`-Datei erstellen:

```
OPENROUTER_API_KEY=your-api-key-here
```

### 3. Server starten

```bash
python3 app.py
```

Server läuft auf: `http://0.0.0.0:8000`

## 📡 API-Verwendung

### Endpoint: `POST /analyze`

Analysiert ein oder mehrere Profile.

**Request-Body:**

```json
{
  "profiles": [
    {
      "id": "profile_001",
      "platform_name": "LinkedIn",
      "full_name": "Max Mustermann",
      "bio": "CEO bei TechCorp. Leidenschaft für Innovation und KI. 15+ Jahre Erfahrung in Software-Entwicklung.",
      "categories": "Künstliche Intelligenz (KI) • Softwareentwicklung • Business Development",
      "followers": 5000,
      "following": 1200,
      "verified": true,
      "business_account": true
    }
  ],
  "target_keywords": ["KI", "Software", "Innovation"],
  "product_category": "Software",
  "include_enneagram": false
}
```

**Response:**

```json
{
  "success": true,
  "results": [
    {
      "profile_id": "profile_001",
      "timestamp": "2025-10-21T04:30:00Z",
      "bio_quality": {
        "score": 85.0,
        "word_count": 120,
        "category": "high"
      },
      "keywords_match_score": 100.0,
      "overall_confidence": 78.5,
      "disc": {
        "primary_type": "D",
        "archetype": "Captain",
        "confidence": 68.0
      },
      "neo": {
        "dimensions": {
          "openness": 0.75,
          "conscientiousness": 0.68,
          "extraversion": 0.72,
          "agreeableness": 0.55,
          "neuroticism": 0.42
        },
        "confidence": 58.0
      },
      "riasec": {
        "holland_code": "IEC",
        "primary": "I",
        "confidence": 75.0
      },
      "persuasion": {
        "primary": "authority",
        "confidence": 72.0
      },
      "purchase_intent": {
        "score": 82.5,
        "category": "very_high"
      },
      "communication_strategy": {
        "style": "Direkt und ergebnisorientiert",
        "subject_line": "Software-Innovation: Konkrete ROI-Steigerung",
        "message_body": "...",
        "call_to_action": "..."
      },
      "warnings": [],
      "processing_time_seconds": 3.2
    }
  ],
  "total_profiles": 1,
  "total_processing_time_seconds": 3.2
}
```

### Weitere Endpoints

- `GET /` - API-Informationen
- `GET /health` - Health-Check
- `GET /logs` - Agent-Logs abrufen (Debugging)
- `DELETE /logs` - Logs löschen

## 🔧 Konfiguration

### config.py

Zentrale Konfigurationsdatei mit:
- API-Einstellungen
- Keyword-Mappings für alle Module
- Confidence-Schwellenwerte
- Produkt-Kategorie-Mappings

### Wichtige Parameter

```python
# API
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DEFAULT_MODEL = "gpt-4.1-mini"

# Confidence-Schwellenwerte
CONFIDENCE_THRESHOLDS = {
    "high": 80,
    "medium": 60,
    "low": 40
}

# Purchase Intent Gewichtung
# DISC: 15%, NEO: 15%, Persuasion: 20%, RIASEC: 25%, Behavior: 10%, Data Quality: 10%
```

## 📊 Datenqualität & Confidence

### Bio-Qualitäts-Score (0-100)

- **80-100**: Hoch (>500 Wörter, strukturiert, Job-Titel, Unternehmen)
- **60-79**: Mittel (200-500 Wörter, teilweise strukturiert)
- **40-59**: Niedrig (<200 Wörter, wenig Struktur)
- **<40**: Sehr niedrig (Analyse nicht empfohlen)

### Modul-spezifische Confidence

- **DISC**: 50-70% (Bio-basiert)
- **NEO**: 40-60% (nur 5 Dimensionen ohne Posts)
- **RIASEC**: 65-80% (Categories verfügbar) / 45-60% (nur Bio)
- **Persuasion**: 60-75% (Bio-Keywords)

### Gesamt-Confidence

Berechnung:
```
Overall Confidence = 
  60% * (Bio Quality / 100) +
  20% * (Categories vorhanden ? 1.0 : 0.3) +
  10% * (Keywords Match / 100) +
  10% * 0.5 (Behavioral Baseline)
```

## ⚠️ Warnungen & Fallbacks

### Automatische Warnungen bei:

- Gesamt-Confidence < 60%
- Bio < 200 Wörter
- Fehlende Categories
- Bio-Qualität < 40

### Fallback-Logik:

- **Fehlende Bio**: Analyse basiert auf Follower-Ratio und Account-Typ
- **Fehlende Categories**: RIASEC-Analyse nur aus Bio-Keywords
- **LLM-Fehler**: Keyword-basierte Analyse als Fallback
- **API-Fehler**: Retry mit exponentiellem Backoff (3 Versuche)

## 🧪 Testing

### Einzelnes Profil testen

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "profiles": [{
      "id": "test_001",
      "platform_name": "LinkedIn",
      "bio": "Software Engineer mit Fokus auf KI und Machine Learning.",
      "categories": "Softwareentwicklung • KI",
      "followers": 1000,
      "following": 500
    }],
    "target_keywords": ["KI", "Software"],
    "product_category": "Software"
  }'
```

### Health-Check

```bash
curl http://localhost:8000/health
```

## 📈 Performance

### Typische Verarbeitungszeiten

- **Einzelnes Profil**: 2-4 Sekunden
- **10 Profile (parallel)**: 5-8 Sekunden
- **100 Profile (batch)**: 40-60 Sekunden

### Optimierungen

- Parallele Agent-Ausführung (ThreadPoolExecutor)
- LLM-API-Caching (zukünftig)
- Batch-Verarbeitung mit max_workers=5

## 🔐 Sicherheit & Datenschutz

### Implementierte Maßnahmen

- Sensible Daten (E-Mail, Telefon) werden in Logs anonymisiert
- API-Key über Umgebungsvariablen
- Keine persistente Speicherung von Profildaten (nur Logs)
- CORS-Middleware für sichere API-Nutzung

### Empfehlungen

- API-Key niemals im Code speichern
- Logs regelmäßig bereinigen
- HTTPS für Produktion verwenden
- Rate-Limiting implementieren (zukünftig)

## 📚 Dokumentation

### Für Entwickler

Siehe Inline-Dokumentation in:
- `models.py`: Alle Datenmodelle mit Beschreibungen
- `agents/*.py`: Agent-spezifische Logik und Prompts
- `analyzer.py`: Orchestrierung und Logging

### Für Stakeholder

**Prozessbeschreibung:**

1. **Daten-Input**: Profile werden via API-Endpunkt übermittelt
2. **Qualitätsbewertung**: Bio-Qualität und Keywords-Match werden bewertet
3. **Parallele Analyse**: 4 Agenten analysieren gleichzeitig:
   - DISC-Agent: Persönlichkeitstyp
   - NEO-Agent: Big Five Dimensionen
   - RIASEC-Agent: Interessensprofil
   - Persuasion-Agent: Cialdini-Prinzipien
4. **Purchase Intent**: Gewichtete Berechnung aus allen Modulen
5. **Communication Strategy**: LLM generiert personalisierte Nachricht
6. **Output**: Vollständiges Profil mit Confidence-Werten und Warnungen

## 🛠️ Troubleshooting

### Problem: "OPENROUTER_API_KEY nicht gesetzt"

**Lösung:**
```bash
export OPENROUTER_API_KEY="your-key"
```

### Problem: LLM-API-Fehler

**Lösung:**
- API-Key überprüfen
- OpenRouter-Status prüfen: https://openrouter.ai/status
- Retry-Mechanismus greift automatisch (3 Versuche)

### Problem: Niedrige Confidence

**Lösung:**
- Bio-Länge erhöhen (>200 Wörter empfohlen)
- Categories hinzufügen
- Strukturierte Bio (Absätze, Emojis, Job-Titel)

## 📝 Changelog

### Version 2.1.0 (2025-10-21)

- ✅ Bio-zentrierte Analyse für minimale Datenverfügbarkeit
- ✅ Hybride Keyword + LLM Analyse
- ✅ Parallele Agent-Ausführung
- ✅ Realistische Confidence-Levels (40-80%)
- ✅ Automatische Warnungen und Fallbacks
- ✅ Purchase Intent mit angepasster Gewichtung
- ✅ Communication Strategy Generator
- ✅ Umfassendes Logging-System

## 📄 Lizenz

Proprietär - Alle Rechte vorbehalten.

## 👥 Kontakt

Bei Fragen oder Support-Anfragen wenden Sie sich bitte an das Entwicklungsteam.

---

**PCBF 2.1 Framework** - Powered by Manus AI

