# PCBF 2.1 - Qualitätssicherungs-Leitfaden

## 📋 Inhaltsverzeichnis

1. [Einführung](#einführung)
2. [Rollen und Verantwortlichkeiten](#rollen-und-verantwortlichkeiten)
3. [Qualitäts-Metriken](#qualitäts-metriken)
4. [Test-Strategie](#test-strategie)
5. [Validierungs-Prozess](#validierungs-prozess)
6. [Fehler-Management](#fehler-management)
7. [Reporting](#reporting)
8. [Checkliste für Releases](#checkliste-für-releases)

---

## 1. Einführung

Dieser Leitfaden beschreibt den Qualitätssicherungs-Prozess (QA) für das **PCBF 2.1 Framework**, mit besonderem Fokus auf das **Prüfprotokoll**.

### Ziel

**Sicherstellen, dass das Framework zuverlässige, konsistente und genaue Analyse-Ergebnisse liefert.**

### Geltungsbereich

- **Code-Qualität:** Lesbarkeit, Wartbarkeit, Performance
- **Funktionale Korrektheit:** Alle Features funktionieren wie erwartet
- **Daten-Validität:** Analyse-Ergebnisse sind plausibel und konsistent
- **Sicherheit:** Keine offensichtlichen Sicherheitslücken

---

## 2. Rollen und Verantwortlichkeiten

### Entwickler

- **Verantwortlich für:**
  - Schreiben von Unit-Tests für neuen Code
  - Durchführung von lokalen Tests vor dem Commit
  - Behebung von Bugs, die vom QA-Team gemeldet werden

### QA-Team / Tester

- **Verantwortlich für:**
  - Durchführung von manuellen und automatisierten Tests
  - Erstellung und Pflege von Test-Szenarien
  - Meldung von Bugs im Bug-Tracking-System
  - Validierung von Bug-Fixes
  - Freigabe von Releases

### DevOps

- **Verantwortlich für:**
  - Bereitstellung der Test-Umgebung
  - Automatisierung des Test-Prozesses (CI/CD)
  - Monitoring der Anwendung in Produktion

---

## 3. Qualitäts-Metriken

### Code-Qualität

- **Code-Coverage:** ≥ 80% (gemessen mit `pytest-cov`)
- **Code-Style:** Konform mit PEP 8 (gemessen mit `flake8` oder `black`)
- **Komplexität:** Cyclomatic Complexity < 10 (gemessen mit `radon`)

### Funktionale Qualität

- **Bug-Rate:** < 5 kritische Bugs pro Release
- **Test-Pass-Rate:** ≥ 95% aller automatisierten Tests

### Daten-Validität (Prüfprotokoll)

- **PASS-Rate:** ≥ 80% der Test-Profile sollten `PASS` oder `REVIEW` erhalten
- **FAIL-Rate:** ≥ 90% der "schlechten" Test-Profile sollten `FAIL` erhalten
- **Score-Genauigkeit:** Validierungs-Score sollte die Datenqualität widerspiegeln

---

## 4. Test-Strategie

### Test-Ebenen

#### 1. Unit-Tests

- **Fokus:** Einzelne Funktionen und Methoden
- **Tools:** `pytest`
- **Beispiele:**
  - `test_validation_protocol.py`: Testet einzelne Checks im Prüfprotokoll
  - `test_llm_client.py`: Testet die LLM-Integration

#### 2. Integrations-Tests

- **Fokus:** Zusammenspiel mehrerer Komponenten
- **Tools:** `pytest`, `requests`
- **Beispiele:**
  - `test_csv_upload.py`: Testet den gesamten Workflow (CSV-Upload → Analyse → Validierung)
  - Testet die API-Endpunkte

#### 3. End-to-End (E2E) Tests

- **Fokus:** Gesamte Anwendung aus Sicht des Benutzers
- **Tools:** Manuelle Tests, Selenium (optional)
- **Beispiele:**
  - CSV-Datei in der Web-UI hochladen
  - Ergebnisse in der UI prüfen
  - CSV-Export herunterladen und prüfen

### Test-Umgebungen

#### 1. Lokal

- **Zweck:** Entwicklung und schnelle Tests
- **Setup:** Lokale Python-Umgebung

#### 2. Staging

- **Zweck:** Vollständige Tests vor dem Release
- **Setup:** Docker-Container oder PaaS (z.B. Railway Staging-Umgebung)
- **Daten:** Anonymisierte Test-Daten

#### 3. Produktion

- **Zweck:** Live-Betrieb
- **Setup:** PaaS (z.B. Railway) oder eigener Server
- **Daten:** Echte Benutzer-Daten

---

## 5. Validierungs-Prozess

### Schritt 1: Vorbereitung

1. **Test-Daten erstellen:**
   - Erstellen Sie eine CSV-Datei mit verschiedenen Test-Profilen (gut, mittel, schlecht)
   - Siehe `docs/examples/TEST_SCENARIOS.md` für Beispiele

2. **Test-Umgebung starten:**
   - Starten Sie die Anwendung lokal oder auf Staging
   - `python3 validation_ui_csv.py`

### Schritt 2: Durchführung

1. **CSV-Datei hochladen:**
   - Öffnen Sie die Web-UI (http://localhost:8002)
   - Laden Sie Ihre Test-CSV-Datei hoch

2. **Ergebnisse prüfen:**
   - Warten Sie, bis die Analyse abgeschlossen ist
   - Prüfen Sie die Ergebnisse in der UI

### Schritt 3: Bewertung

**Für jedes Test-Profil:**

1. **Status prüfen:**
   - Entspricht der Status (`PASS`/`REVIEW`/`FAIL`) Ihren Erwartungen?
   - **Beispiel:** Ein Profil mit sehr wenigen Daten sollte `FAIL` sein.

2. **Score prüfen:**
   - Ist der Score (0-100) angemessen für die Datenqualität?

3. **Checks prüfen:**
   - Gehen Sie die Liste der fehlgeschlagenen Checks durch
   - Sind die Fehlermeldungen verständlich und korrekt?

4. **Analyse-Ergebnisse prüfen:**
   - Sind die psychologischen Profile (DISC, NEO, etc.) plausibel?
   - **Beispiel:** Passt die Beschreibung in der Bio zum ermittelten Persönlichkeitsprofil?

### Wie man weiß, ob das Ergebnis richtig ist

**Es gibt keine 100%ige "Wahrheit" bei psychologischen Profilen, aber Sie können die Plausibilität prüfen:**

#### 1. Keyword-Matching

- **Frage:** Passen die Keywords in der Bio zum Ergebnis?
- **Beispiel:**
  - **Bio:** "Entrepreneur, CEO, Investor"
  - **Ergebnis:** DISC = "D" (Dominant)
  - **Bewertung:** ✅ Richtig

#### 2. Cross-Modul-Konsistenz

- **Frage:** Widersprechen sich die verschiedenen Module?
- **Beispiel:**
  - **DISC:** "I" (Influencer, extrovertiert)
  - **NEO:** Extraversion = 0.25 (niedrig)
  - **Bewertung:** ❌ Falsch (inkonsistent)

#### 3. Confidence-Werte

- **Frage:** Sind die Confidence-Werte realistisch?
- **Beispiel:**
  - **Daten:** 2 Posts, 5 Follower
  - **Confidence:** 0.95 (95%)
  - **Bewertung:** ❌ Falsch (unrealistisch hoch)

#### 4. Menschliche Intuition

- **Frage:** Würden Sie als Mensch eine ähnliche Einschätzung treffen?
- **Beispiel:**
  - **Bio:** "Loves hiking, nature, and quiet evenings"
  - **Ergebnis:** NEO Extraversion = 0.15 (sehr niedrig)
  - **Bewertung:** ✅ Richtig (plausibel)

---

## 6. Fehler-Management

### Bug-Meldung

Wenn Sie einen Fehler finden, erstellen Sie ein Bug-Ticket mit folgenden Informationen:

- **Titel:** Kurze, prägnante Beschreibung des Fehlers
- **Beschreibung:** Detaillierte Beschreibung des Problems
- **Schritte zur Reproduktion:**
  1. ...
  2. ...
  3. ...
- **Erwartetes Ergebnis:** Was hätte passieren sollen?
- **Tatsächliches Ergebnis:** Was ist passiert?
- **Screenshots/Logs:** Fügen Sie relevante Screenshots oder Log-Auszüge hinzu
- **Test-Daten:** Fügen Sie die verwendeten Test-Daten hinzu

### Bug-Priorisierung

| Priorität | Beschreibung | Beispiel |
|-----------|--------------|----------|
| **Kritisch** | Anwendung stürzt ab, Datenverlust | CSV-Upload führt zum Absturz |
| **Hoch** | Kernfunktion fehlerhaft | Validierungs-Status ist immer `PASS` |
| **Mittel** | Kleinere Funktion fehlerhaft | CSV-Export funktioniert nicht |
| **Niedrig** | UI-Fehler, Tippfehler | Button ist falsch beschriftet |

---

## 7. Reporting

### Test-Report

Nach jedem Test-Zyklus wird ein Test-Report erstellt, der folgende Informationen enthält:

- **Zusammenfassung:** Kurze Übersicht der Ergebnisse
- **Test-Umfang:** Was wurde getestet?
- **Ergebnisse:**
  - Anzahl der durchgeführten Tests
  - Anzahl der bestandenen/fehlgeschlagenen Tests
  - Pass-Rate (%)
- **Gefundene Bugs:** Liste der neuen Bugs (mit Link zum Ticket)
- **Offene Bugs:** Liste der noch offenen Bugs
- **Empfehlung:** Release freigeben (Go/No-Go)

---

## 8. Checkliste für Releases

Vor jedem Release muss diese Checkliste abgearbeitet werden:

- [ ] **Code-Qualität**
  - [ ] Code-Coverage ≥ 80%
  - [ ] Code-Style-Checks bestanden
- [ ] **Tests**
  - [ ] Alle Unit-Tests bestanden
  - [ ] Alle Integrations-Tests bestanden
  - [ ] E2E-Tests auf Staging durchgeführt und bestanden
- [ ] **Bugs**
  - [ ] Keine offenen kritischen Bugs
  - [ ] Alle neuen Bugs wurden dokumentiert
- [ ] **Dokumentation**
  - [ ] Entwickler-Handbuch aktualisiert
  - [ ] Release-Notes erstellt
- [ ] **Freigabe**
  - [ ] QA-Team hat Freigabe erteilt

---

## Zusammenfassung

### QA-Workflow

1. **Entwickler:** Schreibt Code + Unit-Tests
2. **CI/CD:** Führt automatisierte Tests durch
3. **QA-Team:** Führt manuelle Tests auf Staging durch
4. **QA-Team:** Meldet Bugs
5. **Entwickler:** Behebt Bugs
6. **QA-Team:** Validiert Bug-Fixes
7. **QA-Team:** Gibt Release frei
8. **DevOps:** Deployed auf Produktion

### Wie man Ergebnisse prüft

1. **Plausibilität:** Passen die Ergebnisse zu den Daten?
2. **Konsistenz:** Widersprechen sich die Module?
3. **Confidence:** Sind die Confidence-Werte realistisch?
4. **Intuition:** Entspricht das Ergebnis Ihrer menschlichen Einschätzung?

---

**Bei Fragen:** Kontaktieren Sie das Entwickler-Team oder den QA-Verantwortlichen.

