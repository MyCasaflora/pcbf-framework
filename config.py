"""
PCBF 2.1 Framework - Konfigurationsdatei
"""
import os
from typing import Dict, List

# API-Konfiguration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "gpt-4.1-mini"

# Datenqualitäts-Schwellenwerte
BIO_QUALITY_THRESHOLDS = {
    "high": 80,
    "medium": 60,
    "low": 40
}

# Confidence-Schwellenwerte
CONFIDENCE_THRESHOLDS = {
    "high": 80,
    "medium": 60,
    "low": 40
}

# DISC-Keyword-Mappings
DISC_KEYWORDS = {
    'D': [
        'CEO', 'Gründer', 'Founder', 'Leader', 'Ergebnis', 'Results', 
        'ROI', 'Effizienz', 'Efficiency', 'Ziel', 'Goal', 'Durchsetzung',
        'Entscheidung', 'Decision', 'Macht', 'Power', 'Kontrolle', 'Control'
    ],
    'I': [
        'Community', 'Netzwerk', 'Network', 'Innovation', 'kreativ', 
        'creative', 'Inspiration', 'Begeisterung', 'Enthusiasm', 'Motivation',
        'Event', 'Speaker', 'Präsentation', 'Presentation', 'Social'
    ],
    'S': [
        'Team', 'Zusammenarbeit', 'Collaboration', 'Unterstützung', 
        'Support', 'helfen', 'help', 'Harmonie', 'Harmony', 'Stabilität',
        'Stability', 'Zuverlässig', 'Reliable', 'Geduld', 'Patience'
    ],
    'C': [
        'Daten', 'Data', 'Analyse', 'Analysis', 'Forschung', 'Research', 
        'Qualität', 'Quality', 'Präzision', 'Precision', 'Struktur', 
        'Structure', 'Prozess', 'Process', 'Standard', 'Systematisch'
    ]
}

# OCEAN-Keyword-Mappings
OCEAN_KEYWORDS = {
    'openness': [
        'Innovation', 'kreativ', 'creative', 'Zukunft', 'Future', 
        'Technologie', 'Technology', 'Forschung', 'Research', 'Kunst', 
        'Art', 'Imagination', 'Neugier', 'Curiosity', 'Experiment'
    ],
    'conscientiousness': [
        'Qualität', 'Quality', 'Prozess', 'Process', 'Struktur', 
        'Structure', 'Planung', 'Planning', 'Zertifizierung', 
        'Certification', 'Standard', 'Organisation', 'Disziplin', 'Discipline'
    ],
    'extraversion': [
        'Netzwerk', 'Network', 'Community', 'Event', 'Speaker', 
        'Präsentation', 'Presentation', 'Social', 'Kommunikation', 
        'Communication', 'Energie', 'Energy', 'Enthusiasmus'
    ],
    'agreeableness': [
        'Team', 'Zusammenarbeit', 'Collaboration', 'Unterstützung', 
        'Support', 'helfen', 'help', 'gemeinsam', 'together', 'Empathie', 
        'Empathy', 'Vertrauen', 'Trust', 'Kooperation'
    ],
    'neuroticism': [
        'Stress', 'Sorge', 'Worry', 'Angst', 'Anxiety', 'Unsicherheit', 
        'Uncertainty', 'Emotion', 'Sensibel', 'Sensitive'
    ]
}

# RIASEC-Category-Mappings
RIASEC_CATEGORY_MAPPING = {
    'Softwareentwicklung': {'I': 0.6, 'R': 0.3, 'C': 0.1},
    'Software Development': {'I': 0.6, 'R': 0.3, 'C': 0.1},
    'Künstliche Intelligenz (KI)': {'I': 0.7, 'R': 0.2, 'E': 0.1},
    'Artificial Intelligence': {'I': 0.7, 'R': 0.2, 'E': 0.1},
    'Business Development': {'E': 0.7, 'S': 0.2, 'I': 0.1},
    'Digitale Strategie': {'E': 0.5, 'I': 0.3, 'C': 0.2},
    'Digital Strategy': {'E': 0.5, 'I': 0.3, 'C': 0.2},
    'Projektmanagement': {'C': 0.5, 'E': 0.3, 'S': 0.2},
    'Project Management': {'C': 0.5, 'E': 0.3, 'S': 0.2},
    'Beratung': {'S': 0.5, 'E': 0.3, 'I': 0.2},
    'Consulting': {'S': 0.5, 'E': 0.3, 'I': 0.2},
    'Design': {'A': 0.7, 'I': 0.2, 'E': 0.1},
    'Marketing': {'E': 0.5, 'A': 0.3, 'S': 0.2},
    'Sales': {'E': 0.7, 'S': 0.2, 'C': 0.1},
    'Vertrieb': {'E': 0.7, 'S': 0.2, 'C': 0.1},
    'Engineering': {'I': 0.6, 'R': 0.3, 'C': 0.1},
    'Ingenieurwesen': {'I': 0.6, 'R': 0.3, 'C': 0.1},
    'HR': {'S': 0.6, 'E': 0.2, 'C': 0.2},
    'Finance': {'C': 0.6, 'I': 0.2, 'E': 0.2},
    'Finanzen': {'C': 0.6, 'I': 0.2, 'E': 0.2}
}

# RIASEC-Keyword-Mappings für Bio-Fallback
RIASEC_KEYWORDS = {
    'R': ['Produktion', 'Production', 'Fertigung', 'Manufacturing', 'Maschine', 
          'Machine', 'Technik', 'Technical', 'Handwerk', 'Craft', 'Bau', 'Construction'],
    'I': ['Forschung', 'Research', 'Analyse', 'Analysis', 'Daten', 'Data', 
          'Wissenschaft', 'Science', 'Labor', 'Laboratory', 'Studie', 'Study'],
    'A': ['Design', 'kreativ', 'creative', 'Kunst', 'Art', 'Content', 
          'Medien', 'Media', 'Grafik', 'Graphic', 'Musik', 'Music'],
    'S': ['Beratung', 'Consulting', 'Training', 'Coaching', 'HR', 'Team', 
          'Bildung', 'Education', 'Pflege', 'Care', 'Sozial', 'Social'],
    'E': ['Vertrieb', 'Sales', 'Business', 'Gründer', 'Founder', 'CEO', 
          'Manager', 'Führung', 'Leadership', 'Unternehmer', 'Entrepreneur'],
    'C': ['Verwaltung', 'Administration', 'Buchhaltung', 'Accounting', 
          'Controlling', 'Prozess', 'Process', 'Qualität', 'Quality', 'Finanzen', 'Finance']
}

# Persuasion-Keyword-Mappings
PERSUASION_KEYWORDS = {
    'authority': ['Professor', 'Dr.', 'PhD', 'Experte', 'Expert', 'Zertifiziert', 
                  'Certified', 'Spezialist', 'Specialist', 'Autorität', 'Authority'],
    'social_proof': ['Kunden', 'Customers', 'Unternehmen', 'Companies', 'Partner', 
                     'Referenzen', 'References', 'Erfolge', 'Success', 'Testimonial'],
    'scarcity': ['exklusiv', 'exclusive', 'limitiert', 'limited', 'begrenzt', 
                 'restricted', 'einzigartig', 'unique', 'selten', 'rare'],
    'reciprocity': ['kostenlos', 'free', 'Geschenk', 'Gift', 'Mehrwert', 'Value', 
                    'helfen', 'help', 'unterstützen', 'support', 'geben', 'give'],
    'consistency': ['Werte', 'Values', 'Prinzipien', 'Principles', 'Mission', 
                    'Vision', 'Ziel', 'Goal', 'Engagement', 'Commitment'],
    'liking': ['Leidenschaft', 'Passion', 'liebe', 'love', 'Begeisterung', 
               'Enthusiasm', 'Freude', 'Joy', 'Spaß', 'Fun'],
    'unity': ['Team', 'Gemeinschaft', 'Community', 'Zusammen', 'Together', 
              'gemeinsam', 'collective', 'Gruppe', 'Group', 'Familie', 'Family']
}

# DISC-Archetypen-Mapping
DISC_ARCHETYPE_MAPPING = {
    'D': 'Captain',
    'Di': 'Driver',
    'DI': 'Initiator',
    'Dc': 'Architect',
    'DC': 'Questioner',
    'Ds': 'Pioneer',
    'DS': 'Adventurer',
    'I': 'Motivator',
    'Id': 'Influencer',
    'ID': 'Persuader',
    'Is': 'Encourager',
    'IS': 'Harmonizer',
    'Ic': 'Appraiser',
    'IC': 'Promoter',
    'S': 'Supporter',
    'Si': 'Counselor',
    'SI': 'Specialist',
    'Sc': 'Planner',
    'SC': 'Stabilizer',
    'Sd': 'Agent',
    'SD': 'Investigator',
    'C': 'Analyst',
    'Cs': 'Editor',
    'CS': 'Objective Thinker',
    'Cd': 'Skeptic',
    'CD': 'Perfectionist',
    'Ci': 'Assessor',
    'CI': 'Creative'
}

# Purchase Intent Produkt-Kategorie-Mappings
PURCHASE_INTENT_PRODUCT_MAPPING = {
    'Software': {'I': 0.8, 'E': 0.6, 'C': 0.4, 'R': 0.3, 'A': 0.2, 'S': 0.1},
    'Beratung': {'S': 0.9, 'E': 0.7, 'I': 0.5, 'C': 0.3, 'A': 0.2, 'R': 0.1},
    'Hardware': {'R': 0.8, 'I': 0.6, 'C': 0.5, 'E': 0.3, 'S': 0.2, 'A': 0.1},
    'Kreativ': {'A': 0.9, 'I': 0.6, 'E': 0.4, 'S': 0.3, 'C': 0.2, 'R': 0.1},
    'Training': {'S': 0.8, 'I': 0.6, 'E': 0.5, 'C': 0.3, 'A': 0.2, 'R': 0.1},
    'Daten': {'I': 0.9, 'C': 0.7, 'R': 0.4, 'E': 0.3, 'S': 0.2, 'A': 0.1}
}

# Logging-Konfiguration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "/home/ubuntu/pcbf_framework/logs/pcbf.log"

# Datenbank-Konfiguration (optional für spätere Erweiterung)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pcbf.db")

# API-Konfiguration
API_HOST = "0.0.0.0"
API_PORT = 8000
API_TITLE = "PCBF 2.1 Framework API"
API_VERSION = "2.1.0"
API_DESCRIPTION = """
PCBF 2.1 Framework API für psychologische Profilanalyse aus Social-Media-Daten.

Hauptfunktionen:
- DISC-Persönlichkeitsanalyse
- NEO/OCEAN Big Five Dimensionen
- RIASEC-Interessensprofile (Holland-Codes)
- Cialdini Persuasion-Prinzipien
- Purchase Intent Scoring
- Personalisierte Kommunikationsstrategien
"""

