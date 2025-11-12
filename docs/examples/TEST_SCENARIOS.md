# PCBF 2.1 - Test-Szenarien und Validierungs-Beispiele

## 📋 Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Test-Profil 1: Exzellent (PASS)](#test-profil-1-exzellent-pass)
3. [Test-Profil 2: Gut (REVIEW)](#test-profil-2-gut-review)
4. [Test-Profil 3: Schlecht (FAIL)](#test-profil-3-schlecht-fail)
5. [Spezifische Test-Fälle](#spezifische-test-fälle)
6. [Wie man Ergebnisse interpretiert](#wie-man-ergebnisse-interpretiert)

---

## Übersicht

Dieses Dokument enthält konkrete Test-Szenarien, mit denen Sie das Prüfprotokoll testen und verstehen können, wie es funktioniert.

### Verwendung

1. **Kopieren** Sie die Beispiel-Daten
2. **Erstellen** Sie eine CSV-Datei oder verwenden Sie die API direkt
3. **Führen** Sie die Analyse und Validierung durch
4. **Vergleichen** Sie die Ergebnisse mit den erwarteten Werten

---

## Test-Profil 1: Exzellent (PASS)

### Eingangsdaten

**CSV-Zeile:**
```csv
lead_id,bio,posts,likes,followers,categories
test_good_001,"Entrepreneur | Tech Enthusiast | AI & Machine Learning | Building the future of SaaS | Speaker | Investor",74,1250,3500,"Business,Technology,Innovation"
```

**ProfileInput (JSON):**
```json
{
  "lead_id": "test_good_001",
  "bio": "Entrepreneur | Tech Enthusiast | AI & Machine Learning | Building the future of SaaS | Speaker | Investor",
  "posts": 74,
  "likes": 1250,
  "followers": 3500,
  "categories": ["Business", "Technology", "Innovation"]
}
```

### Erwartete Analyse-Ergebnisse

**DISC:**
```json
{
  "primary_type": "D",
  "secondary_type": "I",
  "subtype": "Di",
  "archetype": "Captain",
  "scores": {
    "D": 0.45,
    "I": 0.30,
    "S": 0.15,
    "C": 0.10
  },
  "confidence": 0.68,
  "reasoning": "Bio enthält starke D-Keywords: 'Entrepreneur', 'Building', 'Investor'"
}
```

**NEO:**
```json
{
  "openness": 0.85,
  "conscientiousness": 0.92,
  "extraversion": 0.88,
  "agreeableness": 0.65,
  "neuroticism": 0.42,
  "confidence": 0.58,
  "reasoning": "Hohe Openness durch 'Innovation', 'AI'; Hohe Conscientiousness durch 'Building', 'Speaker'"
}
```

**RIASEC:**
```json
{
  "holland_code": "IEC",
  "scores": {
    "I": 0.60,
    "E": 0.55,
    "C": 0.40,
    "A": 0.15,
    "R": 0.10,
    "S": 0.20
  },
  "primary_dim": "I",
  "confidence": 0.75,
  "reasoning": "Investigative (AI, Tech), Enterprising (Entrepreneur, Investor)"
}
```

**Persuasion:**
```json
{
  "primary_principle": "authority",
  "scores": {
    "authority": 0.85,
    "social_proof": 0.60,
    "scarcity": 0.30,
    "reciprocity": 0.40,
    "consistency": 0.55,
    "liking": 0.50,
    "unity": 0.45
  },
  "confidence": 0.72,
  "reasoning": "Authority durch 'Speaker', 'Investor'; Social Proof durch Follower-Zahl"
}
```

**Purchase Intent:**
```json
{
  "score": 82,
  "category": "very_high",
  "confidence": 0.78
}
```

### Erwarteter Validierungs-Report

**Status:** `PASS`

**Score:** `96/100`

**Checks:**
- ✅ Passed: 26
- ❌ Failed: 1

**Warnings:**
- "Bio könnte noch detaillierter sein (aktuell 107 Zeichen)"

**Errors:**
- Keine

**Recommendation:**
- "Profil verwenden - Exzellente Datenqualität und konsistente Analyse-Ergebnisse"

### Warum PASS?

1. **Eingangsdaten:** ✅ Bio ist lang und aussagekräftig, viele Posts, gutes Social Engagement
2. **Module:** ✅ Alle Module liefern plausible Ergebnisse
3. **Konsistenz:** ✅ DISC "D" passt zu NEO Extraversion (0.88), RIASEC "E" passt zu Persuasion "authority"
4. **Confidence:** ✅ Confidence-Werte sind realistisch (0.58-0.78)
5. **Format:** ✅ Profile-String ist korrekt formatiert

---

## Test-Profil 2: Gut (REVIEW)

### Eingangsdaten

**CSV-Zeile:**
```csv
lead_id,bio,posts,likes,followers,categories
test_medium_002,"Marketing professional | Digital strategy",35,420,850,"Marketing"
```

**ProfileInput (JSON):**
```json
{
  "lead_id": "test_medium_002",
  "bio": "Marketing professional | Digital strategy",
  "posts": 35,
  "likes": 420,
  "followers": 850,
  "categories": ["Marketing"]
}
```

### Erwartete Analyse-Ergebnisse

**DISC:**
```json
{
  "primary_type": "I",
  "secondary_type": "S",
  "subtype": "Is",
  "archetype": "Counselor",
  "scores": {
    "D": 0.20,
    "I": 0.40,
    "S": 0.30,
    "C": 0.10
  },
  "confidence": 0.52,
  "reasoning": "Bio enthält I-Keywords: 'Marketing', 'professional'"
}
```

**NEO:**
```json
{
  "openness": 0.65,
  "conscientiousness": 0.70,
  "extraversion": 0.75,
  "agreeableness": 0.60,
  "neuroticism": 0.50,
  "confidence": 0.45,
  "reasoning": "Moderate Werte aufgrund begrenzter Daten"
}
```

**RIASEC:**
```json
{
  "holland_code": "ESC",
  "scores": {
    "E": 0.50,
    "S": 0.45,
    "C": 0.35,
    "I": 0.25,
    "A": 0.20,
    "R": 0.10
  },
  "primary_dim": "E",
  "confidence": 0.58,
  "reasoning": "Enterprising (Marketing), Social (professional)"
}
```

**Persuasion:**
```json
{
  "primary_principle": "social_proof",
  "scores": {
    "authority": 0.45,
    "social_proof": 0.65,
    "scarcity": 0.25,
    "reciprocity": 0.35,
    "consistency": 0.50,
    "liking": 0.60,
    "unity": 0.40
  },
  "confidence": 0.55,
  "reasoning": "Social Proof durch 'Marketing', 'Digital strategy'"
}
```

**Purchase Intent:**
```json
{
  "score": 68,
  "category": "high",
  "confidence": 0.62
}
```

### Erwarteter Validierungs-Report

**Status:** `REVIEW`

**Score:** `85/100`

**Checks:**
- ✅ Passed: 23
- ❌ Failed: 4

**Warnings:**
- "Bio ist kurz (43 Zeichen) - mehr Details empfohlen"
- "Nur 35 Posts - mehr Daten für höhere Confidence empfohlen"
- "Nur 1 Kategorie - mehr Kategorien für bessere Analyse empfohlen"
- "Confidence-Werte sind niedrig (0.45-0.62) - Ergebnisse mit Vorsicht interpretieren"

**Errors:**
- Keine

**Recommendation:**
- "Profil manuell prüfen - Gute Grundlage, aber begrenzte Daten"

### Warum REVIEW?

1. **Eingangsdaten:** ⚠️ Bio ist kurz, weniger Posts, moderates Social Engagement
2. **Module:** ✅ Alle Module liefern plausible Ergebnisse
3. **Konsistenz:** ✅ DISC "I" passt zu NEO Extraversion (0.75)
4. **Confidence:** ⚠️ Confidence-Werte sind niedrig (0.45-0.62)
5. **Format:** ✅ Profile-String ist korrekt formatiert

---

## Test-Profil 3: Schlecht (FAIL)

### Eingangsdaten

**CSV-Zeile:**
```csv
lead_id,bio,posts,likes,followers,categories
test_poor_003,"Hi there",2,5,10,""
```

**ProfileInput (JSON):**
```json
{
  "lead_id": "test_poor_003",
  "bio": "Hi there",
  "posts": 2,
  "likes": 5,
  "followers": 10,
  "categories": []
}
```

### Erwartete Analyse-Ergebnisse

**DISC:**
```json
{
  "primary_type": "S",
  "secondary_type": "C",
  "subtype": "Sc",
  "archetype": "Supporter",
  "scores": {
    "D": 0.10,
    "I": 0.15,
    "S": 0.40,
    "C": 0.35
  },
  "confidence": 0.25,
  "reasoning": "Sehr wenig Daten - Fallback auf Standard-Profil"
}
```

**NEO:**
```json
{
  "openness": 0.50,
  "conscientiousness": 0.50,
  "extraversion": 0.50,
  "agreeableness": 0.50,
  "neuroticism": 0.50,
  "confidence": 0.20,
  "reasoning": "Unzureichende Daten - Neutrale Werte"
}
```

**RIASEC:**
```json
{
  "holland_code": "SCA",
  "scores": {
    "S": 0.35,
    "C": 0.30,
    "A": 0.25,
    "I": 0.20,
    "E": 0.15,
    "R": 0.10
  },
  "primary_dim": "S",
  "confidence": 0.22,
  "reasoning": "Sehr wenig Daten - Fallback auf Standard-Profil"
}
```

**Persuasion:**
```json
{
  "primary_principle": "liking",
  "scores": {
    "authority": 0.30,
    "social_proof": 0.25,
    "scarcity": 0.20,
    "reciprocity": 0.30,
    "consistency": 0.35,
    "liking": 0.40,
    "unity": 0.35
  },
  "confidence": 0.18,
  "reasoning": "Unzureichende Daten - Neutrale Werte"
}
```

**Purchase Intent:**
```json
{
  "score": 35,
  "category": "low",
  "confidence": 0.25
}
```

### Erwarteter Validierungs-Report

**Status:** `FAIL`

**Score:** `55/100`

**Checks:**
- ✅ Passed: 15
- ❌ Failed: 12

**Warnings:**
- "Bio ist sehr kurz (8 Zeichen) - nicht aussagekräftig"
- "Nur 2 Posts - viel zu wenig für zuverlässige Analyse"
- "Social Engagement sehr niedrig (15 gesamt)"
- "Keine Kategorien - wichtige Informationen fehlen"

**Errors:**
- ❌ "Bio-Länge unter Minimum (< 20 Zeichen)"
- ❌ "Posts unter Minimum (< 10)"
- ❌ "Social Engagement unter Minimum (< 100)"
- ❌ "Keine Kategorien vorhanden"
- ❌ "Confidence-Werte zu niedrig (< 0.3)"
- ❌ "Datenqualität unzureichend für zuverlässige Analyse"

**Recommendation:**
- "Profil nicht verwenden - Unzureichende Datenqualität"

### Warum FAIL?

1. **Eingangsdaten:** ❌ Bio ist zu kurz, zu wenig Posts, kaum Social Engagement, keine Kategorien
2. **Module:** ⚠️ Module liefern nur Fallback-Werte
3. **Konsistenz:** ⚠️ Keine aussagekräftigen Daten für Konsistenz-Checks
4. **Confidence:** ❌ Confidence-Werte sind viel zu niedrig (0.18-0.25)
5. **Format:** ✅ Profile-String ist korrekt formatiert (aber Inhalt ist nicht aussagekräftig)

---

## Spezifische Test-Fälle

### Test-Fall 1: Inkonsistenz DISC vs. NEO

**Szenario:** DISC sagt "I" (Influencer, extrovertiert), aber NEO Extraversion ist niedrig.

**Eingangsdaten:**
```json
{
  "bio": "Quiet thinker | Analyst | Data scientist",
  "posts": 50,
  "likes": 300,
  "followers": 500,
  "categories": ["Data Science"]
}
```

**Analyse-Ergebnis:**
```json
{
  "disc": {"primary": "I", "confidence": 0.60},
  "neo": {"extraversion": 0.25, "confidence": 0.55}
}
```

**Erwartetes Validierungs-Ergebnis:**
- ⚠️ **Warning:** "Inkonsistenz: DISC=I (extrovertiert) aber NEO Extraversion niedrig (0.25)"
- **Status:** `REVIEW`
- **Empfehlung:** "Manuell prüfen - Widersprüchliche Persönlichkeits-Indikatoren"

### Test-Fall 2: Unrealistisch hohe Confidence bei wenig Daten

**Szenario:** Nur 5 Posts, aber Confidence = 0.95

**Eingangsdaten:**
```json
{
  "bio": "Tech enthusiast",
  "posts": 5,
  "likes": 20,
  "followers": 50,
  "categories": ["Technology"]
}
```

**Analyse-Ergebnis:**
```json
{
  "disc": {"primary": "D", "confidence": 0.95},
  "neo": {"openness": 0.80, "confidence": 0.92}
}
```

**Erwartetes Validierungs-Ergebnis:**
- ❌ **Error:** "Confidence zu hoch (0.95) für geringe Datenmenge (5 Posts)"
- **Status:** `FAIL`
- **Empfehlung:** "Profil nicht verwenden - Unrealistische Confidence-Werte"

### Test-Fall 3: Fehlende RIASEC-Dimensionen

**Szenario:** RIASEC-Scores haben nicht alle 6 Dimensionen.

**Analyse-Ergebnis:**
```json
{
  "riasec": {
    "code": "IEC",
    "scores": {
      "I": 0.60,
      "E": 0.55,
      "C": 0.40
      // A, R, S fehlen
    }
  }
}
```

**Erwartetes Validierungs-Ergebnis:**
- ❌ **Error:** "RIASEC-Scores unvollständig - Dimensionen A, R, S fehlen"
- **Status:** `FAIL`
- **Empfehlung:** "Profil nicht verwenden - Unvollständige Analyse-Ergebnisse"

---

## Wie man Ergebnisse interpretiert

### Status-Kategorien

| Status | Bedeutung | Aktion |
|--------|-----------|--------|
| **PASS** | Exzellente Qualität | ✅ Profil verwenden |
| **REVIEW** | Gute Qualität, aber prüfen | ⚠️ Manuell prüfen |
| **WARNING** | Akzeptabel mit Einschränkungen | ⚠️ Mit Vorsicht verwenden |
| **FAIL** | Unzureichende Qualität | ❌ Profil nicht verwenden |

### Score-Interpretation

| Score | Qualität | Empfehlung |
|-------|----------|------------|
| 90-100 | Exzellent | Profil ohne Bedenken verwenden |
| 75-89 | Gut | Profil verwenden, aber Warnings beachten |
| 60-74 | Akzeptabel | Profil mit Vorsicht verwenden |
| 0-59 | Unzureichend | Profil nicht verwenden |

### Checks-Interpretation

**Checks Passed / Total Checks:**

- **26/27 (96%):** Exzellent - nur 1 Check fehlgeschlagen
- **23/27 (85%):** Gut - 4 Checks fehlgeschlagen
- **15/27 (55%):** Schlecht - 12 Checks fehlgeschlagen

### Warnings vs. Errors

**Warnings:**
- Hinweise auf potenzielle Probleme
- Profil kann trotzdem verwendet werden
- Beispiel: "Bio könnte detaillierter sein"

**Errors:**
- Schwerwiegende Probleme
- Profil sollte nicht verwendet werden
- Beispiel: "Bio-Länge unter Minimum"

---

## Zusammenfassung

### Test-Profile

1. **Exzellent (PASS):** Vollständige Daten, konsistente Ergebnisse, realistische Confidence
2. **Gut (REVIEW):** Begrenzte Daten, plausible Ergebnisse, niedrige Confidence
3. **Schlecht (FAIL):** Unzureichende Daten, Fallback-Werte, zu niedrige Confidence

### Verwendung

1. **Kopieren** Sie die Test-Daten
2. **Führen** Sie die Analyse durch
3. **Vergleichen** Sie die Ergebnisse
4. **Verstehen** Sie, warum ein Profil PASS/FAIL erhält

### Nächste Schritte

- **Testen** Sie mit eigenen Daten
- **Passen** Sie Schwellenwerte an (siehe Entwickler-Handbuch)
- **Erweitern** Sie die Checks (siehe Entwickler-Handbuch)

---

**Bei Fragen:** Siehe `docs/DEVELOPER_MANUAL.md` oder `docs/QA_GUIDE.md`

