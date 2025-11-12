# PCBF 2.1 - Schnellstart

## Was macht das System?

Analysiert Social-Media-Profile und prüft automatisch, ob die Ergebnisse gut genug sind.

---

## Installation (5 Minuten)

```bash
# 1. Klonen
git clone https://github.com/MyCasaflora/pcbf-framework.git
cd pcbf-framework

# 2. Installieren
pip install -r requirements.txt

# 3. API-Key setzen
echo "OPENROUTER_API_KEY=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" > .env

# 4. Starten
python3 validation_ui_csv.py
```

**Fertig!** Öffne: http://localhost:8002

---

## Verwendung

1. **CSV hochladen** (mit Spalten: lead_id, bio, posts, likes, followers, categories)
2. **Warten** (3 Sekunden pro Profil)
3. **Ergebnisse ansehen** (gruppiert nach DISC, NEO, RIASEC, Persuasion)

---

## Ergebnisse prüfen

### Status verstehen

- **PASS** (grün) = Gut, verwenden ✅
- **REVIEW** (gelb) = Manuell prüfen ⚠️
- **FAIL** (rot) = Nicht verwenden ❌

### Ist das Ergebnis richtig?

**4 einfache Checks:**

1. **Keywords:** Passen die Wörter in der Bio zum Ergebnis?
   - Bio: "CEO, Investor" → DISC: D ✅
   
2. **Konsistenz:** Widersprechen sich die Module?
   - DISC: I (extrovertiert) + NEO: Extraversion hoch ✅
   - DISC: I (extrovertiert) + NEO: Extraversion niedrig ❌

3. **Confidence:** Passt zur Datenmenge?
   - 74 Posts → Confidence 68% ✅
   - 2 Posts → Confidence 95% ❌

4. **Intuition:** Macht es Sinn?
   - Bio: "Loves quiet evenings" → Extraversion niedrig ✅

---

## Anpassen

**Schwellenwerte ändern:**

Öffne `validation_protocol.py` (Zeile 10-15):

```python
MIN_BIO_LENGTH = 20      # Mindest-Bio-Länge
MIN_POSTS = 10           # Mindest-Posts
MIN_SOCIAL_ENGAGEMENT = 100  # Mindest-Likes+Followers
```

---

## Probleme?

**App startet nicht:**
```bash
# API-Key prüfen
cat .env
```

**Keine Ergebnisse:**
- CSV-Format prüfen (siehe `raw-data-pcbf.csv` als Beispiel)

---

Das war's! 🎉

