"""
PCBF 2.1 Framework - RIASEC-Analyse-Agent
"""
import logging
from typing import Dict, Optional, List
import sys
sys.path.append('/home/ubuntu/pcbf_framework')

import config
from utils import normalize_scores, get_top_n_types
from llm_client import get_llm_client
from models import RIASECResult

logger = logging.getLogger(__name__)


class RIASECAgent:
    """Agent für RIASEC (Holland-Codes) Interessensanalyse"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
    
    def analyze(self, categories: Optional[str], bio: Optional[str],
                full_name: Optional[str] = None) -> RIASECResult:
        """
        Analysiert RIASEC-Interessensprofil aus Categories und Bio.
        
        Args:
            categories: Kategorien/Interessen (primäre Quelle)
            bio: Profilbeschreibung (Fallback)
            full_name: Vollständiger Name (optional für Kontext)
            
        Returns:
            RIASECResult mit Holland-Code
        """
        logger.info("RIASEC-Analyse gestartet")
        
        # Categories als primäre Quelle
        if categories and categories != 'None' and categories.strip():
            logger.info("Verwende Categories als primäre Quelle")
            return self._analyze_from_categories(categories, bio)
        
        # Bio als Fallback
        elif bio and bio != 'N/A' and len(bio.strip()) > 20:
            logger.info("Categories fehlen - verwende Bio als Fallback")
            return self._analyze_from_bio(bio, full_name)
        
        # Keine Daten verfügbar
        else:
            logger.warning("Weder Categories noch Bio verfügbar - verwende Fallback")
            return self._fallback_analysis()
    
    def _analyze_from_categories(self, categories: str, bio: Optional[str]) -> RIASECResult:
        """Analysiert RIASEC aus Categories"""
        
        riasec_scores = {
            'R': 0.0,  # Realistic
            'I': 0.0,  # Investigative
            'A': 0.0,  # Artistic
            'S': 0.0,  # Social
            'E': 0.0,  # Enterprising
            'C': 0.0   # Conventional
        }
        
        # Categories parsen (durch • oder , getrennt)
        category_list = []
        for sep in ['•', ',', ';', '\n']:
            if sep in categories:
                category_list = [c.strip() for c in categories.split(sep) if c.strip()]
                break
        
        if not category_list:
            category_list = [categories.strip()]
        
        logger.info(f"Gefundene Categories: {category_list}")
        
        # Mapping anwenden
        for category in category_list:
            if category in config.RIASEC_CATEGORY_MAPPING:
                mapping = config.RIASEC_CATEGORY_MAPPING[category]
                for riasec_type, weight in mapping.items():
                    riasec_scores[riasec_type] += weight
                logger.debug(f"Category '{category}' gemappt: {mapping}")
        
        # Wenn keine Mappings gefunden, versuche Keyword-Matching
        if sum(riasec_scores.values()) == 0:
            logger.info("Keine direkten Category-Mappings - verwende Keyword-Matching")
            categories_lower = categories.lower()
            for riasec_type, keywords in config.RIASEC_KEYWORDS.items():
                for kw in keywords:
                    if kw.lower() in categories_lower:
                        riasec_scores[riasec_type] += 0.2
        
        # Bio als zusätzliche Quelle (20% Gewicht)
        if bio and bio != 'N/A' and len(bio.strip()) > 20:
            bio_scores = self._extract_from_bio(bio)
            for key in riasec_scores.keys():
                riasec_scores[key] = 0.8 * riasec_scores[key] + 0.2 * bio_scores.get(key, 0.0)
        
        # Normalisieren
        riasec_scores = normalize_scores(riasec_scores)
        
        # Holland-Code bestimmen (Top 3)
        top_types = get_top_n_types(riasec_scores, n=3, threshold=0.15)
        holland_code = ''.join([t[0] for t in top_types])
        
        primary = top_types[0][0] if top_types else 'I'
        
        confidence = 75.0 if len(category_list) > 1 else 65.0
        
        return RIASECResult(
            holland_code=holland_code,
            scores=riasec_scores,
            primary=primary,
            confidence=confidence,
            source='categories',
            reasoning=f"Analyse basiert auf {len(category_list)} Kategorie(n): {', '.join(category_list[:3])}"
        )
    
    def _analyze_from_bio(self, bio: str, full_name: Optional[str]) -> RIASECResult:
        """Analysiert RIASEC aus Bio (Fallback)"""
        
        # Keyword-basierte Extraktion
        riasec_scores = self._extract_from_bio(bio)
        
        # LLM-basierte Analyse
        llm_result = self._llm_analysis(bio, full_name)
        
        if llm_result:
            # LLM-Ergebnis mit Keyword-Scores kombinieren
            riasec_scores = self._merge_scores(riasec_scores, llm_result.get('scores', {}))
            reasoning = llm_result.get('reasoning', '')
        else:
            logger.warning("LLM-Analyse fehlgeschlagen - verwende nur Keyword-Scores")
            reasoning = "Analyse basiert auf Bio-Keywords (LLM nicht verfügbar)"
        
        # Normalisieren
        riasec_scores = normalize_scores(riasec_scores)
        
        # Holland-Code bestimmen
        top_types = get_top_n_types(riasec_scores, n=3, threshold=0.15)
        holland_code = ''.join([t[0] for t in top_types])
        
        primary = top_types[0][0] if top_types else 'I'
        
        confidence = 55.0 if llm_result else 45.0
        
        return RIASECResult(
            holland_code=holland_code,
            scores=riasec_scores,
            primary=primary,
            confidence=confidence,
            source='bio',
            reasoning=reasoning
        )
    
    def _extract_from_bio(self, bio: str) -> Dict[str, float]:
        """Extrahiert RIASEC-Scores aus Bio via Keywords"""
        scores = {'R': 0.0, 'I': 0.0, 'A': 0.0, 'S': 0.0, 'E': 0.0, 'C': 0.0}
        bio_lower = bio.lower()
        
        for riasec_type, keywords in config.RIASEC_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in bio_lower:
                    scores[riasec_type] += 0.2
        
        return scores
    
    def _llm_analysis(self, bio: str, full_name: Optional[str]) -> Optional[Dict]:
        """LLM-basierte RIASEC-Analyse"""
        
        system_prompt = """Du bist ein Experte für RIASEC (Holland-Codes) Interessensanalyse.
Analysiere die gegebene Bio und bestimme die RIASEC-Typen.

RIASEC-Typen:
- R (Realistic): Handwerklich, technisch, praktisch orientiert
- I (Investigative): Forschend, analytisch, wissenschaftlich
- A (Artistic): Kreativ, künstlerisch, expressiv
- S (Social): Sozial, helfend, lehrend
- E (Enterprising): Unternehmerisch, führend, verkaufend
- C (Conventional): Organisierend, verwaltend, strukturiert

Gib deine Analyse als JSON zurück:
{
  "scores": {"R": 0.0-1.0, "I": 0.0-1.0, "A": 0.0-1.0, "S": 0.0-1.0, "E": 0.0-1.0, "C": 0.0-1.0},
  "reasoning": "Begründung der Klassifikation"
}"""
        
        context = f"Name: {full_name}\n" if full_name else ""
        prompt = f"""Analysiere folgende Bio für RIASEC-Klassifikation:

{context}Bio: {bio}

Gib RIASEC-Scores (0.0-1.0) und Begründung als JSON zurück."""
        
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
    
    def _fallback_analysis(self) -> RIASECResult:
        """Fallback bei fehlenden Daten"""
        logger.info("Verwende RIASEC-Fallback-Analyse")
        
        # Default: Investigative (häufigster Typ bei Tech-Profilen)
        scores = {
            'R': 0.1,
            'I': 0.3,
            'A': 0.1,
            'S': 0.2,
            'E': 0.2,
            'C': 0.1
        }
        
        return RIASECResult(
            holland_code='IES',
            scores=scores,
            primary='I',
            confidence=25.0,  # Sehr niedrig
            source='fallback',
            reasoning="Fallback-Analyse aufgrund fehlender Daten. Default: Investigative."
        )

