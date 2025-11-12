"""
PCBF 2.1 Framework - Persuasion-Analyse-Agent (Cialdini-Prinzipien)
"""
import logging
from typing import Dict, Optional
import sys
sys.path.append('/home/ubuntu/pcbf_framework')

import config
from llm_client import get_llm_client
from models import PersuasionResult

logger = logging.getLogger(__name__)


class PersuasionAgent:
    """Agent für Cialdini Persuasion-Prinzipien-Analyse"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
    
    def analyze(self, bio: Optional[str], verified: bool = False,
                business_account: bool = False) -> PersuasionResult:
        """
        Analysiert Cialdini-Prinzipien aus Bio.
        
        Args:
            bio: Profilbeschreibung
            verified: Verifizierter Account
            business_account: Business Account
            
        Returns:
            PersuasionResult mit Cialdini-Scores
        """
        logger.info("Persuasion-Analyse gestartet")
        
        # Fallback bei fehlender Bio
        if not bio or bio == 'N/A' or len(bio.strip()) < 20:
            logger.warning("Bio fehlt oder zu kurz - verwende Fallback-Logik")
            return self._fallback_analysis(verified, business_account)
        
        # Keyword-basierte Basis-Scores
        persuasion_scores = self._calculate_keyword_scores(bio, verified, business_account)
        
        # LLM-basierte Analyse
        llm_result = self._llm_analysis(bio)
        
        if llm_result:
            # LLM-Ergebnis mit Keyword-Scores kombinieren
            persuasion_scores = self._merge_scores(persuasion_scores, llm_result.get('scores', {}))
            reasoning = llm_result.get('reasoning', '')
        else:
            logger.warning("LLM-Analyse fehlgeschlagen - verwende nur Keyword-Scores")
            reasoning = "Analyse basiert auf Keyword-Matching (LLM nicht verfügbar)"
        
        # Primary Prinzip
        primary = max(persuasion_scores, key=persuasion_scores.get)
        
        # Confidence berechnen
        confidence = self._calculate_confidence(bio, llm_result is not None)
        
        return PersuasionResult(
            scores=persuasion_scores,
            primary=primary,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _calculate_keyword_scores(self, bio: str, verified: bool,
                                  business_account: bool) -> Dict[str, float]:
        """Berechnet Persuasion-Scores basierend auf Keywords"""
        scores = {
            'authority': 0.0,
            'social_proof': 0.0,
            'scarcity': 0.0,
            'reciprocity': 0.0,
            'consistency': 0.0,
            'liking': 0.0,
            'unity': 0.0
        }
        bio_lower = bio.lower()
        
        # Authority
        for kw in config.PERSUASION_KEYWORDS['authority']:
            if kw.lower() in bio_lower:
                scores['authority'] += 0.3
        
        # Verifiziert = Autorität
        if verified:
            scores['authority'] += 0.2
        
        # Social Proof
        for kw in config.PERSUASION_KEYWORDS['social_proof']:
            if kw.lower() in bio_lower:
                scores['social_proof'] += 0.2
        
        # Zahlen in Bio (z.B. "500+ Kunden")
        import re
        numbers = re.findall(r'\d+\+?', bio)
        if len(numbers) > 0:
            scores['social_proof'] += 0.2
        
        # Scarcity
        for kw in config.PERSUASION_KEYWORDS['scarcity']:
            if kw.lower() in bio_lower:
                scores['scarcity'] += 0.3
        
        # Reciprocity
        for kw in config.PERSUASION_KEYWORDS['reciprocity']:
            if kw.lower() in bio_lower:
                scores['reciprocity'] += 0.2
        
        # Consistency
        for kw in config.PERSUASION_KEYWORDS['consistency']:
            if kw.lower() in bio_lower:
                scores['consistency'] += 0.2
        
        # Liking
        for kw in config.PERSUASION_KEYWORDS['liking']:
            if kw.lower() in bio_lower:
                scores['liking'] += 0.2
        
        # Unity
        for kw in config.PERSUASION_KEYWORDS['unity']:
            if kw.lower() in bio_lower:
                scores['unity'] += 0.2
        
        # Normalisieren auf 0-1
        for key in scores:
            scores[key] = min(1.0, scores[key])
        
        return scores
    
    def _llm_analysis(self, bio: str) -> Optional[Dict]:
        """LLM-basierte Persuasion-Analyse"""
        
        system_prompt = """Du bist ein Experte für Cialdini's Persuasion-Prinzipien.
Analysiere die gegebene Bio und bewerte, welche Prinzipien am stärksten ausgeprägt sind.

Cialdini's 7 Prinzipien:
1. Authority (Autorität): Expertise, Titel, Zertifikate, Status
2. Social Proof (Soziale Bewährtheit): Referenzen, Kundenzahlen, Erfolge
3. Scarcity (Knappheit): Exklusivität, Limitierung, Einzigartigkeit
4. Reciprocity (Reziprozität): Geben, Helfen, Mehrwert bieten
5. Consistency (Konsistenz): Werte, Prinzipien, Mission, Commitment
6. Liking (Sympathie): Leidenschaft, Begeisterung, Persönlichkeit
7. Unity (Einheit): Gemeinschaft, Zugehörigkeit, Wir-Gefühl

Gib deine Analyse als JSON zurück:
{
  "scores": {
    "authority": 0.0-1.0,
    "social_proof": 0.0-1.0,
    "scarcity": 0.0-1.0,
    "reciprocity": 0.0-1.0,
    "consistency": 0.0-1.0,
    "liking": 0.0-1.0,
    "unity": 0.0-1.0
  },
  "reasoning": "Begründung der Bewertung"
}"""
        
        prompt = f"""Analysiere folgende Bio für Cialdini's Persuasion-Prinzipien:

Bio: {bio}

Gib Persuasion-Scores (0.0-1.0) und Begründung als JSON zurück."""
        
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
    
    def _calculate_confidence(self, bio: str, llm_available: bool) -> float:
        """Berechnet Confidence-Level"""
        confidence = 60.0  # Basis
        
        # Bio-Länge
        word_count = len(bio.split())
        if word_count > 300:
            confidence += 15
        elif word_count > 200:
            confidence += 10
        elif word_count > 100:
            confidence += 5
        
        # LLM verfügbar
        if llm_available:
            confidence += 10
        
        return min(75.0, confidence)  # Max 75%
    
    def _fallback_analysis(self, verified: bool, business_account: bool) -> PersuasionResult:
        """Fallback bei fehlender Bio"""
        logger.info("Verwende Persuasion-Fallback-Analyse")
        
        # Default: Balanced
        scores = {
            'authority': 0.3 if verified else 0.2,
            'social_proof': 0.25,
            'scarcity': 0.1,
            'reciprocity': 0.15,
            'consistency': 0.2,
            'liking': 0.15,
            'unity': 0.15
        }
        
        # Business Account = mehr Authority
        if business_account:
            scores['authority'] += 0.1
            scores['social_proof'] += 0.05
        
        # Normalisieren
        total = sum(scores.values())
        scores = {k: v/total for k, v in scores.items()}
        
        primary = max(scores, key=scores.get)
        
        return PersuasionResult(
            scores=scores,
            primary=primary,
            confidence=35.0,  # Niedrig
            reasoning="Fallback-Analyse aufgrund fehlender Bio. Basiert auf Account-Typ."
        )

