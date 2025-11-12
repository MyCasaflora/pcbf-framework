"""
PCBF 2.1 Framework - DISC-Analyse-Agent
"""
import logging
from typing import Dict, Optional
import sys
sys.path.append('/home/ubuntu/pcbf_framework')

import config
from utils import extract_bio_features, calculate_follower_following_ratio, normalize_scores
from llm_client import get_llm_client
from models import DISCResult

logger = logging.getLogger(__name__)


class DISCAgent:
    """Agent für DISC-Persönlichkeitsanalyse"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
    
    def analyze(self, bio: Optional[str], followers: Optional[int], 
                following: Optional[int], full_name: Optional[str] = None,
                nickname: Optional[str] = None) -> DISCResult:
        """
        Analysiert DISC-Persönlichkeitstyp aus Bio und Behavioral-Daten.
        
        Args:
            bio: Profilbeschreibung
            followers: Anzahl Follower
            following: Anzahl Following
            full_name: Vollständiger Name (optional)
            nickname: Nickname (optional)
            
        Returns:
            DISCResult mit Klassifikation
        """
        logger.info("DISC-Analyse gestartet")
        
        # Fallback bei fehlender Bio
        if not bio or bio == 'N/A' or len(bio.strip()) < 20:
            logger.warning("Bio fehlt oder zu kurz - verwende Fallback-Logik")
            return self._fallback_analysis(bio, followers, following, full_name, nickname)
        
        # Features extrahieren
        features = extract_bio_features(bio)
        follower_ratio = calculate_follower_following_ratio(followers, following)
        
        # Keyword-basierte Basis-Scores
        disc_scores = self._calculate_keyword_scores(bio, features, follower_ratio)
        
        # LLM-basierte Analyse
        llm_result = self._llm_analysis(bio, features, follower_ratio)
        
        if llm_result:
            # LLM-Ergebnis mit Keyword-Scores kombinieren
            disc_scores = self._merge_scores(disc_scores, llm_result.get('scores', {}))
            reasoning = llm_result.get('reasoning', '')
        else:
            logger.warning("LLM-Analyse fehlgeschlagen - verwende nur Keyword-Scores")
            reasoning = "Analyse basiert auf Keyword-Matching (LLM nicht verfügbar)"
        
        # Normalisieren
        disc_scores = normalize_scores(disc_scores)
        
        # Primary/Secondary Typ bestimmen
        sorted_types = sorted(disc_scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_types[0][0]
        secondary = sorted_types[1][0] if sorted_types[1][1] > 0.25 else None
        
        # Subtyp bestimmen
        if secondary and sorted_types[1][1] > 0.35:
            subtype = primary + secondary  # Starker Secondary (z.B. "DI")
        elif secondary:
            subtype = primary + secondary.lower()  # Schwacher Secondary (z.B. "Di")
        else:
            subtype = primary  # Nur Primary
        
        # Archetyp-Mapping
        archetype = config.DISC_ARCHETYPE_MAPPING.get(subtype, 'Unknown')
        
        # Confidence berechnen
        confidence = self._calculate_confidence(bio, features, llm_result is not None)
        
        return DISCResult(
            primary_type=primary,
            secondary_type=secondary,
            subtype=subtype,
            archetype=archetype,
            scores=disc_scores,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _calculate_keyword_scores(self, bio: str, features: Dict, 
                                  follower_ratio: float) -> Dict[str, float]:
        """Berechnet DISC-Scores basierend auf Keywords und Features"""
        scores = {'D': 0.0, 'I': 0.0, 'S': 0.0, 'C': 0.0}
        bio_lower = bio.lower()
        
        # D (Dominant) - Indikatoren
        for kw in config.DISC_KEYWORDS['D']:
            if kw.lower() in bio_lower:
                scores['D'] += 0.1
        
        # Kurze Sätze = direkter Stil
        if features['avg_sentence_length'] < 15:
            scores['D'] += 0.2
        
        # Viele Ausrufezeichen = assertiv
        if features['exclamation_count'] > 2:
            scores['D'] += 0.15
        
        # I (Influencer) - Indikatoren
        for kw in config.DISC_KEYWORDS['I']:
            if kw.lower() in bio_lower:
                scores['I'] += 0.1
        
        # Emojis = enthusiastisch
        if features['emoji_count'] > 3:
            scores['I'] += 0.2
        elif features['emoji_count'] > 0:
            scores['I'] += 0.1
        
        # Hohe Follower-Ratio = Influencer
        if follower_ratio > 2.0:
            scores['I'] += 0.2
        elif follower_ratio > 1.5:
            scores['I'] += 0.1
        
        # S (Supporter) - Indikatoren
        for kw in config.DISC_KEYWORDS['S']:
            if kw.lower() in bio_lower:
                scores['S'] += 0.1
        
        # "Wir" statt "Ich"
        if features['we_ratio'] > features['i_ratio']:
            scores['S'] += 0.2
        
        # Lange Sätze = bedachtsam
        if features['avg_sentence_length'] > 20:
            scores['S'] += 0.1
        
        # C (Analyst) - Indikatoren
        for kw in config.DISC_KEYWORDS['C']:
            if kw.lower() in bio_lower:
                scores['C'] += 0.1
        
        # Lange Wörter = präzise
        if features['avg_word_length'] > 7:
            scores['C'] += 0.2
        
        # Wenig Emojis = sachlich
        if features['emoji_count'] == 0 and len(bio.split()) > 50:
            scores['C'] += 0.1
        
        return scores
    
    def _llm_analysis(self, bio: str, features: Dict, 
                     follower_ratio: float) -> Optional[Dict]:
        """LLM-basierte DISC-Analyse"""
        
        system_prompt = """Du bist ein Experte für DISC-Persönlichkeitsanalyse. 
Analysiere die gegebene Bio und bestimme den DISC-Typ.

DISC-Typen:
- D (Dominant): Direkt, ergebnisorientiert, entscheidungsfreudig, assertiv
- I (Influencer): Enthusiastisch, sozial, kreativ, optimistisch
- S (Supporter): Teamorientiert, geduldig, zuverlässig, harmonisch
- C (Analyst): Analytisch, präzise, qualitätsorientiert, systematisch

Gib deine Analyse als JSON zurück:
{
  "scores": {"D": 0.0-1.0, "I": 0.0-1.0, "S": 0.0-1.0, "C": 0.0-1.0},
  "reasoning": "Begründung der Klassifikation"
}"""
        
        prompt = f"""Analysiere folgende Bio für DISC-Klassifikation:

Bio: {bio}

Zusätzliche Metriken:
- Durchschnittliche Satzlänge: {features['avg_sentence_length']:.1f} Wörter
- Emoji-Anzahl: {features['emoji_count']}
- Ausrufezeichen: {features['exclamation_count']}
- Ich/Wir-Verhältnis: {features['i_ratio']:.3f} / {features['we_ratio']:.3f}
- Follower/Following-Ratio: {follower_ratio:.2f}

Gib DISC-Scores (0.0-1.0) und Begründung als JSON zurück."""
        
        response = self.llm_client.call(prompt, system_prompt, temperature=0.3)
        
        if response['success']:
            return self.llm_client.parse_json_response(response)
        
        return None
    
    def _merge_scores(self, keyword_scores: Dict[str, float], 
                     llm_scores: Dict[str, float], 
                     keyword_weight: float = 0.4) -> Dict[str, float]:
        """Kombiniert Keyword- und LLM-Scores"""
        merged = {}
        for key in keyword_scores.keys():
            merged[key] = (
                keyword_weight * keyword_scores.get(key, 0.0) +
                (1 - keyword_weight) * llm_scores.get(key, 0.0)
            )
        return merged
    
    def _calculate_confidence(self, bio: str, features: Dict, 
                             llm_available: bool) -> float:
        """Berechnet Confidence-Level"""
        confidence = 50.0  # Basis
        
        # Bio-Länge
        word_count = len(bio.split())
        if word_count > 300:
            confidence += 20
        elif word_count > 200:
            confidence += 15
        elif word_count > 100:
            confidence += 10
        elif word_count > 50:
            confidence += 5
        
        # LLM verfügbar
        if llm_available:
            confidence += 10
        
        # Strukturierte Bio
        if features['has_structure'] if 'has_structure' in features else features['emoji_count'] > 0:
            confidence += 5
        
        return min(70.0, confidence)  # Max 70% für Bio-only
    
    def _fallback_analysis(self, bio: Optional[str], followers: Optional[int],
                          following: Optional[int], full_name: Optional[str],
                          nickname: Optional[str]) -> DISCResult:
        """Fallback bei fehlender Bio"""
        logger.info("Verwende DISC-Fallback-Analyse")
        
        # Default: Balanced (alle gleich)
        scores = {'D': 0.25, 'I': 0.25, 'S': 0.25, 'C': 0.25}
        
        # Follower-Ratio als Hinweis
        follower_ratio = calculate_follower_following_ratio(followers, following)
        if follower_ratio > 2.0:
            scores['I'] = 0.4  # Influencer
            scores['D'] = 0.3
            scores['S'] = 0.2
            scores['C'] = 0.1
        elif follower_ratio < 0.5:
            scores['S'] = 0.4  # Networker
            scores['I'] = 0.3
            scores['C'] = 0.2
            scores['D'] = 0.1
        
        # Normalisieren
        scores = normalize_scores(scores)
        
        sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_types[0][0]
        
        return DISCResult(
            primary_type=primary,
            secondary_type=None,
            subtype=primary,
            archetype=config.DISC_ARCHETYPE_MAPPING.get(primary, 'Unknown'),
            scores=scores,
            confidence=30.0,  # Sehr niedrig
            reasoning="Fallback-Analyse aufgrund fehlender Bio. Basiert auf Follower-Ratio."
        )

