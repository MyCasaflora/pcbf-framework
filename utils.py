"""
PCBF 2.1 Framework - Utility-Funktionen
"""
import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import config


def setup_logging():
    """Logging-System konfigurieren"""
    import os
    os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


def calculate_bio_quality(bio: Optional[str]) -> Dict:
    """
    Bewertet die Qualität der Bio für NLP-Analyse.
    
    Args:
        bio: Profilbeschreibung/Bio
        
    Returns:
        Dictionary mit Bio-Qualitäts-Metriken
    """
    if not bio or bio == 'N/A' or len(bio.strip()) == 0:
        return {
            'score': 0.0,
            'word_count': 0,
            'has_job_title': False,
            'has_company': False,
            'has_structure': False,
            'emoji_count': 0,
            'category': 'very_low'
        }
    
    score = 0.0
    
    # 1. Wortanzahl (40 Punkte)
    words = bio.split()
    word_count = len(words)
    
    if word_count >= 500:
        score += 40
    elif word_count >= 200:
        score += 30
    elif word_count >= 100:
        score += 20
    elif word_count >= 50:
        score += 10
    
    # 2. Informationsdichte (30 Punkte)
    # Job-Titel vorhanden?
    job_keywords = [
        'CEO', 'CTO', 'CFO', 'Manager', 'Director', 'Consultant', 
        'Engineer', 'Developer', 'Designer', 'Analyst', 'Specialist',
        'Gründer', 'Founder', 'Geschäftsführer', 'Leiter', 'Head'
    ]
    has_job_title = any(kw.lower() in bio.lower() for kw in job_keywords)
    if has_job_title:
        score += 10
    
    # Unternehmen vorhanden?
    company_indicators = ['bei ', 'at ', 'GmbH', 'AG', 'Inc', 'Ltd', 'LLC', 'Corp']
    has_company = any(ind in bio for ind in company_indicators)
    if has_company:
        score += 10
    
    # Fachbegriffe vorhanden? (lange Wörter als Proxy)
    long_words = [w for w in words if len(w) > 10]
    if len(long_words) > 5:
        score += 10
    
    # 3. Struktur (20 Punkte)
    # Emojis (zeigt Engagement)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbole & Piktogramme
        "\U0001F680-\U0001F6FF"  # Transport & Karten
        "\U0001F1E0-\U0001F1FF"  # Flaggen
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", 
        flags=re.UNICODE
    )
    emoji_count = len(emoji_pattern.findall(bio))
    has_structure = False
    
    if emoji_count > 0:
        score += 10
        has_structure = True
    
    # Absätze/Struktur
    if '\n' in bio or '•' in bio or '-' in bio or '|' in bio:
        score += 10
        has_structure = True
    
    # 4. Sprache (10 Punkte)
    # Vollständige Sätze (kein Keyword-Spam)
    sentences = [s.strip() for s in bio.split('.') if s.strip()]
    if len(sentences) >= 3:
        score += 10
    
    # Kategorie bestimmen
    if score >= config.BIO_QUALITY_THRESHOLDS['high']:
        category = 'high'
    elif score >= config.BIO_QUALITY_THRESHOLDS['medium']:
        category = 'medium'
    elif score >= config.BIO_QUALITY_THRESHOLDS['low']:
        category = 'low'
    else:
        category = 'very_low'
    
    return {
        'score': min(100.0, score),
        'word_count': word_count,
        'has_job_title': has_job_title,
        'has_company': has_company,
        'has_structure': has_structure,
        'emoji_count': emoji_count,
        'category': category
    }


def calculate_keywords_match_score(bio: Optional[str], categories: Optional[str], 
                                   target_keywords: List[str]) -> float:
    """
    Berechnet Keywords-Match-Score basierend auf Ziel-Keywords.
    
    Args:
        bio: Profilbeschreibung
        categories: Kategorien
        target_keywords: Liste der Ziel-Keywords
        
    Returns:
        Keywords-Match-Score (0-100)
    """
    if not target_keywords or len(target_keywords) == 0:
        return 50.0  # Neutral wenn keine Keywords angegeben
    
    text = ""
    if bio and bio != 'N/A':
        text += bio.lower() + " "
    if categories and categories != 'None':
        text += categories.lower()
    
    if not text.strip():
        return 0.0
    
    matches = 0
    for keyword in target_keywords:
        if keyword.lower() in text:
            matches += 1
    
    # Score berechnen
    match_ratio = matches / len(target_keywords)
    score = match_ratio * 100
    
    return min(100.0, score)


def calculate_overall_confidence(bio_quality_score: float, 
                                 categories_available: bool,
                                 keywords_match_score: float) -> float:
    """
    Berechnet Gesamt-Confidence basierend auf verfügbaren Daten.
    
    Args:
        bio_quality_score: Bio-Qualitäts-Score (0-100)
        categories_available: Kategorien vorhanden
        keywords_match_score: Keywords-Match-Score (0-100)
        
    Returns:
        Gesamt-Confidence (0-100)
    """
    confidence = (
        0.60 * (bio_quality_score / 100) +
        0.20 * (1.0 if categories_available else 0.3) +
        0.10 * (keywords_match_score / 100) +
        0.10 * 0.5  # Baseline für Behavioral-Features (immer teilweise verfügbar)
    )
    
    return confidence * 100


def extract_bio_features(bio: Optional[str]) -> Dict:
    """
    Extrahiert NLP-Features aus Bio für DISC/NEO-Analyse.
    
    Args:
        bio: Profilbeschreibung
        
    Returns:
        Dictionary mit extrahierten Features
    """
    if not bio or bio == 'N/A' or len(bio.strip()) == 0:
        return {
            'avg_sentence_length': 0,
            'avg_word_length': 0,
            'emoji_count': 0,
            'exclamation_count': 0,
            'question_count': 0,
            'i_ratio': 0.0,
            'we_ratio': 0.0,
            'sentence_count': 0
        }
    
    # Sätze
    sentences = [s.strip() for s in re.split(r'[.!?]+', bio) if s.strip()]
    sentence_count = len(sentences)
    
    # Wörter
    words = bio.split()
    word_count = len(words)
    
    # Durchschnittliche Satzlänge
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    
    # Durchschnittliche Wortlänge
    avg_word_length = sum(len(w) for w in words) / word_count if word_count > 0 else 0
    
    # Emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", 
        flags=re.UNICODE
    )
    emoji_count = len(emoji_pattern.findall(bio))
    
    # Interpunktion
    exclamation_count = bio.count('!')
    question_count = bio.count('?')
    
    # Pronomen-Verhältnis
    bio_lower = bio.lower()
    i_count = len(re.findall(r'\bich\b|\bi\b', bio_lower))
    we_count = len(re.findall(r'\bwir\b|\bwe\b', bio_lower))
    
    i_ratio = i_count / word_count if word_count > 0 else 0.0
    we_ratio = we_count / word_count if word_count > 0 else 0.0
    
    return {
        'avg_sentence_length': avg_sentence_length,
        'avg_word_length': avg_word_length,
        'emoji_count': emoji_count,
        'exclamation_count': exclamation_count,
        'question_count': question_count,
        'i_ratio': i_ratio,
        'we_ratio': we_ratio,
        'sentence_count': sentence_count
    }


def calculate_follower_following_ratio(followers: Optional[int], 
                                       following: Optional[int]) -> float:
    """
    Berechnet Follower/Following-Ratio als Verhaltens-Proxy.
    
    Args:
        followers: Anzahl Follower
        following: Anzahl Following
        
    Returns:
        Follower/Following-Ratio (0 wenn keine Daten)
    """
    if not followers or not following or following == 0:
        return 1.0  # Neutral
    
    return followers / following


def normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """
    Normalisiert Scores auf Summe = 1.0.
    
    Args:
        scores: Dictionary mit Scores
        
    Returns:
        Normalisierte Scores
    """
    total = sum(scores.values())
    if total == 0:
        # Gleichverteilung wenn alle Scores 0
        n = len(scores)
        return {k: 1.0/n for k in scores.keys()}
    
    return {k: v/total for k, v in scores.items()}


def get_top_n_types(scores: Dict[str, float], n: int = 3, 
                    threshold: float = 0.15) -> List[Tuple[str, float]]:
    """
    Gibt die Top N Typen aus einem Score-Dictionary zurück.
    
    Args:
        scores: Dictionary mit Scores
        n: Anzahl Top-Typen
        threshold: Minimaler Score-Threshold
        
    Returns:
        Liste von (Typ, Score) Tupeln
    """
    sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(t, s) for t, s in sorted_types[:n] if s >= threshold]


def generate_warnings(bio_quality: Dict, overall_confidence: float, 
                     categories_available: bool) -> List[Dict]:
    """
    Generiert Warnmeldungen basierend auf Datenqualität.
    
    Args:
        bio_quality: Bio-Qualitäts-Metriken
        overall_confidence: Gesamt-Confidence
        categories_available: Kategorien vorhanden
        
    Returns:
        Liste von Warnmeldungen
    """
    warnings = []
    
    # Niedrige Gesamt-Confidence
    if overall_confidence < config.CONFIDENCE_THRESHOLDS['low']:
        warnings.append({
            'level': 'critical',
            'message': f'Sehr niedrige Gesamt-Confidence ({overall_confidence:.1f}%). Analyse nicht empfohlen.',
            'affected_modules': ['all']
        })
    elif overall_confidence < config.CONFIDENCE_THRESHOLDS['medium']:
        warnings.append({
            'level': 'warning',
            'message': f'Niedrige Gesamt-Confidence ({overall_confidence:.1f}%). Ergebnisse mit Vorsicht interpretieren.',
            'affected_modules': ['all']
        })
    
    # Kurze Bio
    if bio_quality['word_count'] < 50:
        warnings.append({
            'level': 'warning',
            'message': f'Sehr kurze Bio ({bio_quality["word_count"]} Wörter). DISC/NEO-Analyse eingeschränkt.',
            'affected_modules': ['DISC', 'NEO', 'Persuasion']
        })
    elif bio_quality['word_count'] < 200:
        warnings.append({
            'level': 'info',
            'message': f'Kurze Bio ({bio_quality["word_count"]} Wörter). Für höhere Genauigkeit werden >200 Wörter empfohlen.',
            'affected_modules': ['DISC', 'NEO']
        })
    
    # Fehlende Kategorien
    if not categories_available:
        warnings.append({
            'level': 'warning',
            'message': 'Keine Kategorien verfügbar. RIASEC-Analyse basiert nur auf Bio-Keywords.',
            'affected_modules': ['RIASEC']
        })
    
    # Niedrige Bio-Qualität
    if bio_quality['category'] == 'very_low':
        warnings.append({
            'level': 'critical',
            'message': 'Sehr niedrige Bio-Qualität. Analyse stark eingeschränkt.',
            'affected_modules': ['DISC', 'NEO', 'Persuasion', 'Communication']
        })
    elif bio_quality['category'] == 'low':
        warnings.append({
            'level': 'warning',
            'message': 'Niedrige Bio-Qualität. Confidence-Werte reduziert.',
            'affected_modules': ['DISC', 'NEO', 'Persuasion']
        })
    
    return warnings


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Formatiert Zeitstempel für Logging.
    
    Args:
        dt: Datetime-Objekt (default: jetzt)
        
    Returns:
        Formatierter Zeitstempel
    """
    if dt is None:
        dt = datetime.utcnow()
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def sanitize_for_logging(data: Dict) -> Dict:
    """
    Entfernt sensible Daten für Logging (E-Mail, Telefon).
    
    Args:
        data: Dictionary mit Daten
        
    Returns:
        Bereinigtes Dictionary
    """
    sanitized = data.copy()
    
    # Sensible Felder anonymisieren
    if 'email' in sanitized and sanitized['email']:
        sanitized['email'] = '***@***.***'
    if 'phone' in sanitized and sanitized['phone']:
        sanitized['phone'] = '***********'
    
    return sanitized

