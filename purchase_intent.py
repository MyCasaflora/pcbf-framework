"""
PCBF 2.1 Framework - Purchase Intent Berechnung
"""
import logging
from typing import Dict, Optional
import config
from models import (
    DISCResult, NEOResult, RIASECResult, PersuasionResult,
    EnneagramResult, PurchaseIntentResult
)

logger = logging.getLogger(__name__)


class PurchaseIntentCalculator:
    """Berechnet Purchase Intent Score basierend auf psychologischem Profil"""
    
    def calculate(self, disc: DISCResult, neo: NEOResult, riasec: RIASECResult,
                  persuasion: PersuasionResult, bio_quality_score: float,
                  keywords_match_score: float, product_category: str,
                  enneagram: Optional[EnneagramResult] = None) -> PurchaseIntentResult:
        """
        Berechnet Purchase Intent Score (0-100).
        
        Args:
            disc: DISC-Ergebnis
            neo: NEO-Ergebnis
            riasec: RIASEC-Ergebnis
            persuasion: Persuasion-Ergebnis
            bio_quality_score: Bio-Qualitäts-Score
            keywords_match_score: Keywords-Match-Score
            product_category: Produkt-Kategorie
            enneagram: Enneagram-Ergebnis (optional)
            
        Returns:
            PurchaseIntentResult mit Score und Kategorisierung
        """
        logger.info(f"Purchase Intent Berechnung für Kategorie: {product_category}")
        
        score = 50.0  # Basis-Score
        contributing_factors = {}
        
        # 1. DISC (15%)
        disc_contribution = self._calculate_disc_contribution(disc)
        score += disc_contribution
        contributing_factors['DISC'] = disc_contribution
        
        # 2. NEO (15%)
        neo_contribution = self._calculate_neo_contribution(neo)
        score += neo_contribution
        contributing_factors['NEO'] = neo_contribution
        
        # 3. Persuasion (20%)
        persuasion_contribution = self._calculate_persuasion_contribution(persuasion)
        score += persuasion_contribution
        contributing_factors['Persuasion'] = persuasion_contribution
        
        # 4. Enneagram (5%) - Optional
        if enneagram:
            enneagram_contribution = self._calculate_enneagram_contribution(enneagram)
            score += enneagram_contribution
            contributing_factors['Enneagram'] = enneagram_contribution
        else:
            contributing_factors['Enneagram'] = 0.0
        
        # 5. RIASEC (25%)
        riasec_contribution = self._calculate_riasec_contribution(riasec, product_category)
        score += riasec_contribution
        contributing_factors['RIASEC'] = riasec_contribution
        
        # 6. Verhalten (10%)
        behavior_contribution = self._calculate_behavior_contribution(disc, neo)
        score += behavior_contribution
        contributing_factors['Behavior'] = behavior_contribution
        
        # 7. Datenqualität (10%)
        data_quality_contribution = self._calculate_data_quality_contribution(
            bio_quality_score, keywords_match_score
        )
        score += data_quality_contribution
        contributing_factors['Data_Quality'] = data_quality_contribution
        
        # Score auf 0-100 begrenzen
        score = max(0.0, min(100.0, score))
        
        # Kategorie bestimmen
        if score > 80:
            category = 'very_high'
        elif score > 60:
            category = 'high'
        elif score > 40:
            category = 'medium'
        else:
            category = 'low'
        
        # Reasoning generieren
        reasoning = self._generate_reasoning(score, category, contributing_factors, product_category)
        
        logger.info(f"Purchase Intent Score: {score:.1f} ({category})")
        
        return PurchaseIntentResult(
            score=score,
            category=category,
            contributing_factors=contributing_factors,
            reasoning=reasoning
        )
    
    def _calculate_disc_contribution(self, disc: DISCResult) -> float:
        """DISC-Beitrag zum Purchase Intent (15%)"""
        disc_adjustments = {
            'D': +12,  # Dominant: Entscheidungsfreudig
            'I': +8,   # Influencer: Innovationsbereit
            'S': -3,   # Supporter: Vorsichtig
            'C': -6    # Analyst: Skeptisch
        }
        
        adjustment = disc_adjustments.get(disc.primary_type, 0)
        
        # Confidence-Gewichtung
        confidence_factor = disc.confidence / 100.0
        
        return adjustment * 0.15 * confidence_factor
    
    def _calculate_neo_contribution(self, neo: NEOResult) -> float:
        """NEO-Beitrag zum Purchase Intent (15%)"""
        contribution = 0.0
        
        # Conscientiousness (Qualitätsfokus)
        c_score = neo.dimensions.get('conscientiousness', 0.5)
        contribution += (c_score - 0.5) * 20 * 0.15
        
        # Openness (Innovationsbereitschaft)
        o_score = neo.dimensions.get('openness', 0.5)
        contribution += (o_score - 0.5) * 15 * 0.15
        
        # Confidence-Gewichtung
        confidence_factor = neo.confidence / 100.0
        
        return contribution * confidence_factor
    
    def _calculate_persuasion_contribution(self, persuasion: PersuasionResult) -> float:
        """Persuasion-Beitrag zum Purchase Intent (20%)"""
        # Primary Prinzip
        primary_score = persuasion.scores.get(persuasion.primary, 0.5)
        
        # Authority und Social Proof erhöhen Intent
        if persuasion.primary in ['authority', 'social_proof']:
            contribution = (primary_score - 0.5) * 25 * 0.20
        # Reciprocity und Liking moderat
        elif persuasion.primary in ['reciprocity', 'liking']:
            contribution = (primary_score - 0.5) * 20 * 0.20
        # Consistency und Unity neutral
        elif persuasion.primary in ['consistency', 'unity']:
            contribution = (primary_score - 0.5) * 15 * 0.20
        # Scarcity kann negativ sein (Skepsis)
        else:
            contribution = (primary_score - 0.5) * 10 * 0.20
        
        # Confidence-Gewichtung
        confidence_factor = persuasion.confidence / 100.0
        
        return contribution * confidence_factor
    
    def _calculate_enneagram_contribution(self, enneagram: EnneagramResult) -> float:
        """Enneagram-Beitrag zum Purchase Intent (5%)"""
        # Typ 3 (Achiever) und 8 (Challenger) = höherer Intent
        enneagram_adjustments = {
            1: 0,   # Perfectionist
            2: +2,  # Helper
            3: +5,  # Achiever
            4: -2,  # Individualist
            5: -3,  # Investigator
            6: -1,  # Loyalist
            7: +3,  # Enthusiast
            8: +4,  # Challenger
            9: 0    # Peacemaker
        }
        
        adjustment = enneagram_adjustments.get(enneagram.type, 0)
        
        # Confidence-Gewichtung (Enneagram hat niedrige Confidence)
        confidence_factor = enneagram.confidence / 100.0
        
        return adjustment * 0.05 * confidence_factor
    
    def _calculate_riasec_contribution(self, riasec: RIASECResult, 
                                      product_category: str) -> float:
        """RIASEC-Beitrag zum Purchase Intent (25%)"""
        
        # Produkt-Kategorie-Match
        if product_category in config.PURCHASE_INTENT_PRODUCT_MAPPING:
            product_weights = config.PURCHASE_INTENT_PRODUCT_MAPPING[product_category]
        else:
            # Default: Software
            product_weights = config.PURCHASE_INTENT_PRODUCT_MAPPING['Software']
        
        # Match-Score berechnen
        match_score = 0.0
        for riasec_type, weight in product_weights.items():
            match_score += riasec.scores.get(riasec_type, 0.0) * weight
        
        # Normalisieren auf -15 bis +15
        contribution = (match_score - 0.5) * 30 * 0.25
        
        # Confidence-Gewichtung
        confidence_factor = riasec.confidence / 100.0
        
        return contribution * confidence_factor
    
    def _calculate_behavior_contribution(self, disc: DISCResult, neo: NEOResult) -> float:
        """Verhaltens-Beitrag zum Purchase Intent (10%)"""
        contribution = 0.0
        
        # Extraversion (aus NEO) = aktiver
        e_score = neo.dimensions.get('extraversion', 0.5)
        contribution += (e_score - 0.5) * 10 * 0.10
        
        # DISC-I oder DISC-D = kaufbereiter
        if disc.primary_type in ['I', 'D']:
            contribution += 5 * 0.10
        
        return contribution
    
    def _calculate_data_quality_contribution(self, bio_quality_score: float,
                                            keywords_match_score: float) -> float:
        """Datenqualitäts-Beitrag zum Purchase Intent (10%)"""
        
        # Bio-Qualität (60%)
        bio_contribution = (bio_quality_score / 100.0 - 0.5) * 20 * 0.10 * 0.6
        
        # Keywords-Match (40%)
        keywords_contribution = (keywords_match_score / 100.0 - 0.5) * 20 * 0.10 * 0.4
        
        return bio_contribution + keywords_contribution
    
    def _generate_reasoning(self, score: float, category: str,
                           contributing_factors: Dict[str, float],
                           product_category: str) -> str:
        """Generiert Reasoning für Purchase Intent"""
        
        # Top-Faktoren identifizieren
        sorted_factors = sorted(
            contributing_factors.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        top_positive = [f for f, v in sorted_factors if v > 0][:2]
        top_negative = [f for f, v in sorted_factors if v < 0][:2]
        
        reasoning = f"Purchase Intent Score: {score:.1f}/100 ({category.replace('_', ' ').title()}) für Produkt-Kategorie '{product_category}'.\n\n"
        
        if top_positive:
            reasoning += f"Positive Faktoren: {', '.join(top_positive)}. "
        
        if top_negative:
            reasoning += f"Negative Faktoren: {', '.join(top_negative)}. "
        
        # Kategorie-spezifische Empfehlung
        if category == 'very_high':
            reasoning += "\n\nEmpfehlung: Hochpriorisierter Lead. Direkter Kontakt empfohlen."
        elif category == 'high':
            reasoning += "\n\nEmpfehlung: Qualifizierter Lead. Personalisierte Ansprache empfohlen."
        elif category == 'medium':
            reasoning += "\n\nEmpfehlung: Potentieller Lead. Nurturing-Kampagne empfohlen."
        else:
            reasoning += "\n\nEmpfehlung: Niedriger Intent. Allgemeine Awareness-Kampagne."
        
        return reasoning

