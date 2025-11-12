# PCBF 2.1 Framework - Technische Dokumentation

## Für Entwickler

Diese Dokumentation richtet sich an Programmierer und beschreibt die technische Implementierung des PCBF 2.1 Frameworks.

---

## 📐 Architektur-Übersicht

### Schichtenmodell

```
┌─────────────────────────────────────────────┐
│         FastAPI Application Layer           │
│              (app.py)                       │
├─────────────────────────────────────────────┤
│         Orchestration Layer                 │
│         (analyzer.py)                       │
├─────────────────────────────────────────────┤
│         Agent Layer                         │
│  (disc, neo, riasec, persuasion)           │
├─────────────────────────────────────────────┤
│         Calculation Layer                   │
│  (purchase_intent, communication_strategy)  │
├─────────────────────────────────────────────┤
│         Infrastructure Layer                │
│  (llm_client, utils, config, models)       │
└─────────────────────────────────────────────┘
```

### Datenfluss

```
1. API Request (JSON)
   ↓
2. Pydantic Validation (models.py)
   ↓
3. ProfileAnalyzer.analyze_batch()
   ↓
4. Parallel Agent Execution (ThreadPoolExecutor)
   ├─→ DISC Agent
   ├─→ NEO Agent
   ├─→ RIASEC Agent
   └─→ Persuasion Agent
   ↓
5. Purchase Intent Calculation
   ↓
6. Communication Strategy Generation
   ↓
7. Result Assembly & Logging
   ↓
8. API Response (JSON)
```

---

## 🔧 Komponenten-Details

### 1. FastAPI Application (`app.py`)

**Verantwortlichkeiten:**
- HTTP-Endpunkte bereitstellen
- Request-Validierung
- Error-Handling
- CORS-Konfiguration
- Background-Tasks (Logging)

**Hauptendpunkte:**

```python
POST /analyze
- Input: AnalysisRequest (Pydantic)
- Output: AnalysisResponse (Pydantic)
- Validierung: Max 100 Profile pro Request
- Timeout: Keine (async)
```

**Implementierungsdetails:**

```python
# ThreadPoolExecutor für Batch-Verarbeitung
with ThreadPoolExecutor(max_workers=5) as executor:
    results = analyzer.analyze_batch(...)

# Background-Task für Logging
background_tasks.add_task(save_logs_to_file, logs)
```

---

### 2. Profile Analyzer (`analyzer.py`)

**Hauptklasse:** `ProfileAnalyzer`

**Methoden:**

```python
def analyze_profile(profile, target_keywords, product_category, include_enneagram) -> ProfileAnalysisResult
    """Analysiert ein einzelnes Profil vollständig"""
    
def analyze_batch(profiles, ..., max_workers=5) -> List[ProfileAnalysisResult]
    """Analysiert mehrere Profile parallel"""
```

**Parallele Ausführung:**

```python
with ThreadPoolExecutor(max_workers=4) as executor:
    disc_future = executor.submit(self._run_disc_analysis, profile)
    neo_future = executor.submit(self._run_neo_analysis, profile)
    riasec_future = executor.submit(self._run_riasec_analysis, profile)
    persuasion_future = executor.submit(self._run_persuasion_analysis, profile)
    
    # Ergebnisse sammeln
    disc_result = disc_future.result()
    neo_result = neo_future.result()
    # ...
```

**Logging:**

Jeder Agent-Aufruf wird geloggt:

```python
AgentLogEntry(
    agent_name="DISC",
    profile_id="profile_001",
    input_data={...},
    output_data={...},
    api_call_latency_ms=1234.5,
    success=True,
    error_message=None
)
```

---

### 3. Agenten-Architektur

Alle Agenten folgen dem gleichen Pattern:

```python
class XYZAgent:
    def __init__(self):
        self.llm_client = get_llm_client()
    
    def analyze(self, ...) -> XYZResult:
        # 1. Fallback-Check
        if not bio:
            return self._fallback_analysis()
        
        # 2. Keyword-basierte Analyse
        keyword_scores = self._calculate_keyword_scores(bio)
        
        # 3. LLM-basierte Analyse
        llm_result = self._llm_analysis(bio)
        
        # 4. Merge & Normalisierung
        if llm_result:
            scores = self._merge_scores(keyword_scores, llm_result)
        
        # 5. Confidence-Berechnung
        confidence = self._calculate_confidence(bio, llm_available)
        
        return XYZResult(...)
```

#### 3.1 DISC Agent (`agents/disc_agent.py`)

**Input:**
- `bio`: Profilbeschreibung
- `followers`, `following`: Für Follower-Ratio
- `full_name`, `nickname`: Für Kontext

**Keyword-Scoring:**

```python
# D (Dominant)
for kw in config.DISC_KEYWORDS['D']:
    if kw.lower() in bio_lower:
        scores['D'] += 0.1

# Kurze Sätze = direkter Stil
if features['avg_sentence_length'] < 15:
    scores['D'] += 0.2
```

**LLM-Prompt:**

```python
system_prompt = """Du bist ein Experte für DISC-Persönlichkeitsanalyse.
Analysiere die gegebene Bio und bestimme den DISC-Typ.

DISC-Typen:
- D (Dominant): Direkt, ergebnisorientiert, ...
- I (Influencer): Enthusiastisch, sozial, ...
- S (Supporter): Teamorientiert, geduldig, ...
- C (Analyst): Analytisch, präzise, ...

Gib deine Analyse als JSON zurück:
{
  "scores": {"D": 0.0-1.0, ...},
  "reasoning": "..."
}"""
```

**Merge-Strategie:**

```python
merged[key] = (
    0.4 * keyword_scores[key] +  # 40% Keywords
    0.6 * llm_scores[key]        # 60% LLM
)
```

**Confidence:**

```python
confidence = 50.0  # Basis
if word_count > 300: confidence += 20
if word_count > 200: confidence += 15
if llm_available: confidence += 10
return min(70.0, confidence)  # Max 70%
```

#### 3.2 NEO Agent (`agents/neo_agent.py`)

**Besonderheiten:**
- Nur 5 Dimensionen (keine 30 Facetten)
- Neuroticism schwer aus Bio zu inferieren (Default: 0.5)
- Niedrigere Confidence als DISC (40-60%)

**Keyword-Scoring Beispiel (Openness):**

```python
o_score = 0.0
for kw in config.OCEAN_KEYWORDS['openness']:
    if kw.lower() in bio_lower:
        o_score += 0.15

# Emojis = Kreativität
o_score += features['emoji_count'] * 0.05

# Lange Wörter = intellektuell
if features['avg_word_length'] > 6.5:
    o_score += 0.1

scores['openness'] = min(1.0, max(0.0, 0.5 + o_score - 0.3))
```

#### 3.3 RIASEC Agent (`agents/riasec_agent.py`)

**Besonderheiten:**
- Categories als primäre Quelle (höchste Confidence)
- Bio als Fallback
- Zuverlässigstes Modul (65-80% Confidence)

**Category-Mapping:**

```python
category_mapping = {
    'Softwareentwicklung': {'I': 0.6, 'R': 0.3, 'C': 0.1},
    'Business Development': {'E': 0.7, 'S': 0.2, 'I': 0.1},
    # ...
}
```

**Holland-Code-Generierung:**

```python
# Top 3 Typen mit Threshold 0.15
top_types = get_top_n_types(riasec_scores, n=3, threshold=0.15)
holland_code = ''.join([t[0] for t in top_types])  # z.B. "IEC"
```

#### 3.4 Persuasion Agent (`agents/persuasion_agent.py`)

**Cialdini's 7 Prinzipien:**

1. Authority
2. Social Proof
3. Scarcity
4. Reciprocity
5. Consistency
6. Liking
7. Unity

**Keyword-Scoring mit Bonuses:**

```python
# Authority
for kw in config.PERSUASION_KEYWORDS['authority']:
    if kw.lower() in bio_lower:
        scores['authority'] += 0.3

# Verifiziert = Autorität
if verified:
    scores['authority'] += 0.2

# Social Proof + Zahlen
if len(re.findall(r'\d+\+?', bio)) > 0:
    scores['social_proof'] += 0.2
```

---

### 4. LLM Client (`llm_client.py`)

**Klasse:** `LLMClient`

**Features:**
- OpenRouter API-Integration
- Retry-Mechanismus (3 Versuche, exponentielles Backoff)
- JSON-Response-Parsing
- Latenz-Tracking

**Implementierung:**

```python
class LLMClient:
    def __init__(self, api_key, model="gpt-4.1-mini"):
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
    
    def call(self, prompt, system_prompt, temperature=0.7, max_tokens=2000):
        # API-Aufruf mit Retry
        response = self.session.post(...)
        return {
            'success': True,
            'content': content,
            'latency_ms': latency,
            'usage': {...}
        }
```

**JSON-Parsing:**

```python
def parse_json_response(self, response):
    content = response['content'].strip()
    
    # JSON-Block extrahieren (Markdown-Code-Block)
    if '```json' in content:
        content = content.split('```json')[1].split('```')[0].strip()
    
    return json.loads(content)
```

---

### 5. Purchase Intent Calculator (`purchase_intent.py`)

**Formel:**

```
Score = 50 (Basis)
  + DISC * 15%
  + NEO * 15%
  + Persuasion * 20%
  + Enneagram * 5% (optional)
  + RIASEC * 25%
  + Behavior * 10%
  + Data Quality * 10%
```

**DISC-Beitrag:**

```python
disc_adjustments = {
    'D': +12,  # Entscheidungsfreudig
    'I': +8,   # Innovationsbereit
    'S': -3,   # Vorsichtig
    'C': -6    # Skeptisch
}
contribution = adjustment * 0.15 * confidence_factor
```

**RIASEC-Produkt-Match:**

```python
# Produkt-Kategorie-Mapping
product_weights = {
    'Software': {'I': 0.8, 'E': 0.6, 'C': 0.4, ...},
    'Beratung': {'S': 0.9, 'E': 0.7, 'I': 0.5, ...}
}

# Match-Score berechnen
match_score = sum(
    riasec.scores[type] * weight 
    for type, weight in product_weights.items()
)
```

**Kategorisierung:**

```python
if score > 80: category = 'very_high'
elif score > 60: category = 'high'
elif score > 40: category = 'medium'
else: category = 'low'
```

---

### 6. Communication Strategy Generator (`communication_strategy.py`)

**Ablauf:**

1. **Stil** ← DISC
2. **Ton** ← NEO (Extraversion, Agreeableness)
3. **Inhaltsfokus** ← RIASEC
4. **Persuasion-Ansatz** ← Cialdini

**LLM-Prompt:**

```python
prompt = f"""Erstelle eine personalisierte Outreach-Nachricht für {recipient}.

Psychologisches Profil:
- DISC-Typ: {disc.primary_type} ({disc.archetype})
- Kommunikationsstil: {style}
- Tonalität: {tone}
- Inhaltsfokus: {content_focus}
- Persuasion-Ansatz: {persuasion_approach}

Produkt-Kategorie: {product_category}

Erstelle eine Nachricht, die:
1. Den Kommunikationsstil respektiert
2. Die richtige Tonalität trifft
3. Auf berufliche Interessen eingeht
4. Das Persuasion-Prinzip nutzt

Gib Betreffzeile, Nachrichtentext und CTA als JSON zurück."""
```

**Fallback-Nachrichten:**

Für jeden DISC-Typ gibt es vordefinierte Fallback-Templates:

```python
if 'Direkt' in style:
    body = """ich habe gesehen, dass Sie im Bereich {product_category} tätig sind.
    Kurz und knapp: 30% Effizienzsteigerung in 3 Monaten.
    Interesse an einem 15-minütigen Call?"""
```

---

## 🔍 Utility-Funktionen (`utils.py`)

### Bio-Qualitäts-Berechnung

```python
def calculate_bio_quality(bio: str) -> Dict:
    score = 0.0
    
    # 1. Wortanzahl (40 Punkte)
    word_count = len(bio.split())
    if word_count >= 500: score += 40
    elif word_count >= 200: score += 30
    # ...
    
    # 2. Informationsdichte (30 Punkte)
    has_job_title = any(kw in bio for kw in job_keywords)
    if has_job_title: score += 10
    # ...
    
    # 3. Struktur (20 Punkte)
    emoji_count = len(emoji_pattern.findall(bio))
    if emoji_count > 0: score += 10
    # ...
    
    # 4. Sprache (10 Punkte)
    sentences = bio.split('.')
    if len(sentences) >= 3: score += 10
    
    return {'score': min(100, score), ...}
```

### Feature-Extraktion

```python
def extract_bio_features(bio: str) -> Dict:
    return {
        'avg_sentence_length': word_count / sentence_count,
        'avg_word_length': sum(len(w) for w in words) / word_count,
        'emoji_count': len(emoji_pattern.findall(bio)),
        'exclamation_count': bio.count('!'),
        'question_count': bio.count('?'),
        'i_ratio': i_count / word_count,
        'we_ratio': we_count / word_count,
        'sentence_count': sentence_count
    }
```

### Gesamt-Confidence

```python
def calculate_overall_confidence(bio_quality_score, categories_available, keywords_match_score):
    confidence = (
        0.60 * (bio_quality_score / 100) +
        0.20 * (1.0 if categories_available else 0.3) +
        0.10 * (keywords_match_score / 100) +
        0.10 * 0.5  # Behavioral Baseline
    )
    return confidence * 100
```

---

## 🗂️ Datenmodelle (`models.py`)

Alle Modelle basieren auf **Pydantic** für automatische Validierung.

### Wichtigste Modelle:

```python
class ProfileInput(BaseModel):
    """Input für ein Profil"""
    id: str
    bio: Optional[str]
    categories: Optional[str]
    followers: Optional[int]
    # ...

class DISCResult(BaseModel):
    """DISC-Analyse-Ergebnis"""
    primary_type: str
    archetype: str
    scores: Dict[str, float]
    confidence: float
    reasoning: Optional[str]

class ProfileAnalysisResult(BaseModel):
    """Vollständiges Analyse-Ergebnis"""
    profile_id: str
    bio_quality: BioQualityResult
    disc: DISCResult
    neo: NEOResult
    riasec: RIASECResult
    persuasion: PersuasionResult
    purchase_intent: PurchaseIntentResult
    communication_strategy: CommunicationStrategy
    warnings: List[WarningMessage]
```

---

## ⚙️ Konfiguration (`config.py`)

Zentrale Konfigurationsdatei mit:

### API-Einstellungen

```python
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "gpt-4.1-mini"
```

### Keyword-Mappings

```python
DISC_KEYWORDS = {
    'D': ['CEO', 'Gründer', 'Leader', ...],
    'I': ['Community', 'Netzwerk', ...],
    # ...
}

RIASEC_CATEGORY_MAPPING = {
    'Softwareentwicklung': {'I': 0.6, 'R': 0.3, 'C': 0.1},
    # ...
}
```

### Schwellenwerte

```python
BIO_QUALITY_THRESHOLDS = {"high": 80, "medium": 60, "low": 40}
CONFIDENCE_THRESHOLDS = {"high": 80, "medium": 60, "low": 40}
```

---

## 🚀 Deployment

### Lokale Entwicklung

```bash
# 1. Dependencies installieren
pip3 install -r requirements.txt

# 2. Umgebungsvariablen setzen
export OPENROUTER_API_KEY="your-key"

# 3. Server starten
python3 app.py
```

### Produktion (Empfehlungen)

```bash
# Mit Gunicorn (Production WSGI Server)
pip3 install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000

# Mit Docker
# Dockerfile erstellen:
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

# Build & Run
docker build -t pcbf-framework .
docker run -p 8000:8000 -e OPENROUTER_API_KEY=xxx pcbf-framework
```

---

## 🧪 Testing

### Unit-Tests (TODO)

```python
# tests/test_disc_agent.py
import pytest
from agents.disc_agent import DISCAgent

def test_disc_analysis():
    agent = DISCAgent()
    result = agent.analyze(
        bio="CEO und Gründer. Ergebnisorientiert.",
        followers=1000,
        following=500
    )
    assert result.primary_type == 'D'
    assert result.confidence > 50
```

### Integration-Tests

```bash
# API-Tests ausführen
python3 test_api.py
```

---

## 📊 Performance-Optimierung

### Aktuelle Optimierungen:

1. **Parallele Agent-Ausführung**: ThreadPoolExecutor (4 Agenten gleichzeitig)
2. **Batch-Verarbeitung**: Mehrere Profile parallel (max_workers=5)
3. **LLM-Retry-Mechanismus**: Exponentielles Backoff

### Zukünftige Optimierungen:

1. **LLM-Response-Caching**: Redis für häufige Anfragen
2. **Async/Await**: Vollständig asynchrone Verarbeitung
3. **Database-Caching**: PostgreSQL für Profil-Ergebnisse
4. **Rate-Limiting**: Token-Bucket-Algorithmus

---

## 🔐 Sicherheit

### Implementierte Maßnahmen:

1. **API-Key-Management**: Nur via Umgebungsvariablen
2. **Daten-Anonymisierung**: E-Mail/Telefon in Logs
3. **Input-Validierung**: Pydantic-Schemas
4. **Error-Handling**: Keine Stack-Traces in Responses

### Best Practices:

```python
# ✅ Gut
api_key = os.getenv("OPENROUTER_API_KEY")

# ❌ Schlecht
api_key = "sk-1234..."  # Niemals hardcoden!
```

---

## 📝 Logging

### Log-Levels:

- **DEBUG**: Agent-Details, API-Calls
- **INFO**: Analyse-Start/Ende, Erfolge
- **WARNING**: Fallbacks, niedrige Confidence
- **ERROR**: API-Fehler, Exceptions

### Log-Dateien:

```
logs/
├── pcbf.log                      # Haupt-Log
└── agent_logs_20251021_043000.json  # Agent-Aktivitäts-Logs
```

### Beispiel-Log:

```
2025-10-21 04:30:15 - analyzer - INFO - Starte Analyse für Profil: profile_001
2025-10-21 04:30:15 - disc_agent - INFO - DISC-Analyse gestartet
2025-10-21 04:30:16 - llm_client - DEBUG - LLM API-Erfolg: Latenz=1234ms
2025-10-21 04:30:18 - analyzer - INFO - ✓ Profil profile_001 erfolgreich analysiert
```

---

## 🐛 Debugging

### Häufige Probleme:

**1. "OPENROUTER_API_KEY nicht gesetzt"**

```bash
# Lösung:
export OPENROUTER_API_KEY="your-key"
```

**2. JSON-Parse-Fehler**

```python
# LLM gibt manchmal Markdown zurück
# Lösung: parse_json_response() extrahiert JSON-Block
if '```json' in content:
    content = content.split('```json')[1].split('```')[0]
```

**3. Niedrige Confidence**

```python
# Ursachen:
# - Bio zu kurz (<200 Wörter)
# - Keine Categories
# - LLM-API-Fehler

# Lösung: Warnungen prüfen
if profile_result['warnings']:
    for warning in profile_result['warnings']:
        print(warning['message'])
```

---

## 📚 Weiterführende Ressourcen

- **DISC-Modell**: https://www.discprofile.com/
- **Big Five**: https://en.wikipedia.org/wiki/Big_Five_personality_traits
- **RIASEC**: https://en.wikipedia.org/wiki/Holland_Codes
- **Cialdini**: https://www.influenceatwork.com/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Pydantic**: https://docs.pydantic.dev/

---

**Ende der technischen Dokumentation**

