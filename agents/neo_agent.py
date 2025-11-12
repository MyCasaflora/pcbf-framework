"""
PCBF 2.1 Framework - NEO/OCEAN-Analyse-Agent
"""
import logging
from typing import Dict, Optional
import sys
sys.path.append('/home/ubuntu/pcbf_framework')

import config
from utils import extract_bio_features
from llm_client import get_llm_client
from models import NEOResult

logger = logging.getLogger(__name__)


class NEOAgent:
    """Agent für NEO/OCEAN Big Five Persönlichkeitsanalyse"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
    
    def analyze(self, bio: Optional[str], verified: bool = False,
                business_account: bool = False) -> NEOResult:
        """
        Analysiert OCEAN-Dimensionen aus Bio.
        
        Args:
            bio: Profilbeschreibung
            verified: Verifizierter Account
            business_account: Business Account
            
        Returns:
            NEOResult mit OCEAN-Dimensionen
        """
        logger.info("NEO/OCEAN-Analyse gestartet")
        
        # Fallback bei fehlender Bio
        if not bio or bio == 'N/A' or len(bio.strip()) < 20:
            logger.warning("Bio fehlt oder zu kurz - verwende Fallback-Logik")
            return self._fallback_analysis(verified, business_account)
        
        # Features extrahieren
        features = extract_bio_features(bio)
        
        # Keyword-basierte Basis-Scores
        ocean_scores = self._calculate_keyword_scores(bio, features, verified, business_account)
        
        # LLM-basierte Analyse
        llm_result = self._llm_analysis(bio, features)
        
        if llm_result:
            # LLM-Ergebnis mit Keyword-Scores kombinieren
            ocean_scores = self._merge_scores(ocean_scores, llm_result.get('dimensions', {}))
            reasoning = llm_result.get('reasoning', '')
        else:
            logger.warning("LLM-Analyse fehlgeschlagen - verwende nur Keyword-Scores")
            reasoning = "Analyse basiert auf Keyword-Matching (LLM nicht verfügbar)"
        
        # Confidence berechnen
        confidence = self._calculate_confidence(bio, features, llm_result is not None)
        
        return NEOResult(
            dimensions=ocean_scores,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _calculate_keyword_scores(self, bio: str, features: Dict,
                                  verified: bool, business_account: bool) -> Dict[str, float]:
        """Berechnet OCEAN-Scores basierend auf Keywords und Features"""
        scores = {
            'openness': 0.5,
            'conscientiousness': 0.5,
            'extraversion': 0.5,
            'agreeableness': 0.5,
            'neuroticism': 0.5
        }
        bio_lower = bio.lower()
        
        # O (Openness) - Offenheit für Erfahrungen
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
        
        # C (Conscientiousness) - Gewissenhaftigkeit
        c_score = 0.0
        for kw in config.OCEAN_KEYWORDS['conscientiousness']:
            if kw.lower() in bio_lower:
                c_score += 0.15
        
        # Lange Sätze = detailliert
        if features['avg_sentence_length'] > 20:
            c_score += 0.2
        
        # Business Account = professionell
        if business_account:
            c_score += 0.1
        
        # Strukturierte Bio
        if features['emoji_count'] == 0 and len(bio.split()) > 100:
            c_score += 0.1  # Sachlich
        
        scores['conscientiousness'] = min(1.0, max(0.0, 0.5 + c_score - 0.3))
        
        # E (Extraversion) - Extraversion
        e_score = 0.0
        for kw in config.OCEAN_KEYWORDS['extraversion']:
            if kw.lower() in bio_lower:
                e_score += 0.15
        
        # Ausrufezeichen = Enthusiasmus
        e_score += features['exclamation_count'] * 0.05
        
        # Emojis = expressiv
        if features['emoji_count'] > 3:
            e_score += 0.2
        
        # Verifiziert = öffentliche Person
        if verified:
            e_score += 0.1
        
        scores['extraversion'] = min(1.0, max(0.0, 0.5 + e_score - 0.3))
        
        # A (Agreeableness) - Verträglichkeit
        a_score = 0.0
        for kw in config.OCEAN_KEYWORDS['agreeableness']:
            if kw.lower() in bio_lower:
                a_score += 0.15
        
        # "Wir"-Orientierung
        if features['we_ratio'] > 0.02:
            a_score += 0.2
        
        # Wenig Ich-Fokus
        if features['i_ratio'] < 0.01:
            a_score += 0.1
        
        scores['agreeableness'] = min(1.0, max(0.0, 0.5 + a_score - 0.3))
        
        # N (Neuroticism) - Neurotizismus
        # Schwer aus Bio zu inferieren - bleibe bei Mittelwert
        n_score = 0.0
        for kw in config.OCEAN_KEYWORDS['neuroticism']:
            if kw.lower() in bio_lower:
                n_score += 0.1
        
        # Viele Fragezeichen = Unsicherheit
        if features['question_count'] > 3:
            n_score += 0.1
        
        scores['neuroticism'] = min(1.0, max(0.0, 0.5 + n_score - 0.2))
        
        return scores
    
    def _llm_analysis(self, bio: str, features: Dict) -> Optional[Dict]:
        """LLM-basierte OCEAN-Analyse"""
        
        system_prompt = """Du bist ein Experte für Big Five (OCEAN) Persönlichkeitsanalyse.
Analysiere die gegebene Bio und bewerte die fünf Dimensionen.

OCEAN-Dimensionen (jeweils 0.0-1.0):
- Openness (Offenheit): Kreativität, Neugier, Intellekt
- Conscientiousness (Gewissenhaftigkeit): Organisation, Disziplin, Zuverlässigkeit
- Extraversion: Geselligkeit, Energie, Assertivität
- Agreeableness (Verträglichkeit): Empathie, Kooperation, Vertrauen
- Neuroticism (Neurotizismus): Emotionale Stabilität (niedrig) vs. Labilität (hoch)

Gib deine Analyse als JSON zurück:
{
  "dimensions": {
    "openness": 0.0-1.0,
    "conscientiousness": 0.0-1.0,
    "extraversion": 0.0-1.0,
    "agreeableness": 0.0-1.0,
    "neuroticism": 0.0-1.0
  },
  "reasoning": "Begründung der Bewertung"
}"""
        
        prompt = f"""Analysiere folgende Bio für OCEAN-Dimensionen:

Bio: {bio}

Zusätzliche Metriken:
- Durchschnittliche Satzlänge: {features['avg_sentence_length']:.1f} Wörter
- Durchschnittliche Wortlänge: {features['avg_word_length']:.1f} Zeichen
- Emoji-Anzahl: {features['emoji_count']}
- Ausrufezeichen: {features['exclamation_count']}
- Fragezeichen: {features['question_count']}
- Ich/Wir-Verhältnis: {features['i_ratio']:.3f} / {features['we_ratio']:.3f}

Gib OCEAN-Scores (0.0-1.0) und Begründung als JSON zurück."""
        
        response = self.llm_client.call(prompt, system_prompt, temperature=0.3)
        
        if response['success']:
            return self.llm_client.parse_json_response(response)
        
        return None
    
    def _merge_scores(self, keyword_scores: Dict[str, float],
                     llm_scores: Dict[str, float],
                     keyword_weight: float = 0.3) -> Dict[str, float]:
        """Kombiniert Keyword- und LLM-Scores"""
        merged = {}
        for key in keyword_scores.keys():
            merged[key] = (
                keyword_weight * keyword_scores.get(key, 0.5) +
                (1 - keyword_weight) * llm_scores.get(key, 0.5)
            )
        return merged
    
    def _calculate_confidence(self, bio: str, features: Dict,
                             llm_available: bool) -> float:
        """Berechnet Confidence-Level"""
        confidence = 40.0  # Basis (niedriger als DISC)
        
        # Bio-Länge
        word_count = len(bio.split())
        if word_count > 400:
            confidence += 20
        elif word_count > 300:
            confidence += 15
        elif word_count > 200:
            confidence += 10
        elif word_count > 100:
            confidence += 5
        
        # LLM verfügbar
        if llm_available:
            confidence += 10
        
        return min(60.0, confidence)  # Max 60% für Bio-only
    
    def _fallback_analysis(self, verified: bool, business_account: bool) -> NEOResult:
        """Fallback bei fehlender Bio"""
        logger.info("Verwende NEO-Fallback-Analyse")
        
        # Default: Mittelwerte
        dimensions = {
            'openness': 0.5,
            'conscientiousness': 0.5,
            'extraversion': 0.5,
            'agreeableness': 0.5,
            'neuroticism': 0.5
        }
        
        # Kleine Anpassungen basierend auf Account-Typ
        if business_account:
            dimensions['conscientiousness'] = 0.6
            dimensions['extraversion'] = 0.55
        
        if verified:
            dimensions['extraversion'] = 0.6
            dimensions['openness'] = 0.55
        
        return NEOResult(
            dimensions=dimensions,
            confidence=30.0,  # Sehr niedrig
            reasoning="Fallback-Analyse aufgrund fehlender Bio. Mittelwerte mit leichten Anpassungen."
        )

