"""
PCBF 2.1 Framework - Main Analyzer
Orchestriert alle Analyse-Agenten und erstellt vollständige Profile
"""
import logging
import time
import json
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from models import (
    ProfileInput, ProfileAnalysisResult, BioQualityResult,
    WarningMessage, AgentLogEntry
)
from utils import (
    calculate_bio_quality, calculate_keywords_match_score,
    calculate_overall_confidence, generate_warnings
)
from agents.disc_agent import DISCAgent
from agents.neo_agent import NEOAgent
from agents.riasec_agent import RIASECAgent
from agents.persuasion_agent import PersuasionAgent
from purchase_intent import PurchaseIntentCalculator
from communication_strategy import CommunicationStrategyGenerator

logger = logging.getLogger(__name__)


class ProfileAnalyzer:
    """Hauptklasse für vollständige Profilanalyse"""
    
    def __init__(self):
        """Initialisiert alle Agenten"""
        self.disc_agent = DISCAgent()
        self.neo_agent = NEOAgent()
        self.riasec_agent = RIASECAgent()
        self.persuasion_agent = PersuasionAgent()
        self.purchase_intent_calculator = PurchaseIntentCalculator()
        self.communication_strategy_generator = CommunicationStrategyGenerator()
        
        self.agent_logs: List[AgentLogEntry] = []
    
    def analyze_profile(self, profile: ProfileInput, target_keywords: List[str],
                       product_category: str, include_enneagram: bool = False) -> ProfileAnalysisResult:
        """
        Analysiert ein einzelnes Profil vollständig.
        
        Args:
            profile: Profil-Input-Daten
            target_keywords: Ziel-Keywords für Match-Score
            product_category: Produkt-Kategorie für Purchase Intent
            include_enneagram: Enneagram-Analyse einbeziehen
            
        Returns:
            ProfileAnalysisResult mit vollständiger Analyse
        """
        start_time = time.time()
        logger.info(f"Starte Analyse für Profil: {profile.id}")
        
        # 1. Datenqualität bewerten
        bio_quality_dict = calculate_bio_quality(profile.bio)
        bio_quality = BioQualityResult(**bio_quality_dict)
        
        keywords_match_score = calculate_keywords_match_score(
            profile.bio, profile.categories, target_keywords
        )
        
        categories_available = bool(profile.categories and profile.categories != 'None')
        
        overall_confidence = calculate_overall_confidence(
            bio_quality.score, categories_available, keywords_match_score
        )
        
        logger.info(f"Datenqualität - Bio: {bio_quality.score:.1f}, Keywords: {keywords_match_score:.1f}, Overall: {overall_confidence:.1f}")
        
        # 2. Warnungen generieren
        warnings_list = generate_warnings(bio_quality_dict, overall_confidence, categories_available)
        warnings = [WarningMessage(**w) for w in warnings_list]
        
        # 3. Parallel Analyse-Agenten ausführen
        api_calls_made = 0
        
        try:
            with ThreadPoolExecutor(max_workers=4) as executor:
                # DISC-Analyse
                disc_future = executor.submit(
                    self._run_disc_analysis,
                    profile
                )
                
                # NEO-Analyse
                neo_future = executor.submit(
                    self._run_neo_analysis,
                    profile
                )
                
                # RIASEC-Analyse
                riasec_future = executor.submit(
                    self._run_riasec_analysis,
                    profile
                )
                
                # Persuasion-Analyse
                persuasion_future = executor.submit(
                    self._run_persuasion_analysis,
                    profile
                )
                
                # Ergebnisse sammeln
                disc_result = disc_future.result()
                neo_result = neo_future.result()
                riasec_result = riasec_future.result()
                persuasion_result = persuasion_future.result()
                
                api_calls_made = 4  # Mindestens 4 Agenten
                
        except Exception as e:
            logger.error(f"Fehler bei paralleler Agent-Ausführung: {str(e)}")
            raise
        
        # 4. Enneagram (optional)
        enneagram_result = None
        if include_enneagram and bio_quality.score > 50:
            logger.info("Enneagram-Analyse übersprungen (niedrige Confidence)")
            # TODO: Enneagram-Agent implementieren
        
        # 5. Purchase Intent berechnen
        purchase_intent = self.purchase_intent_calculator.calculate(
            disc_result, neo_result, riasec_result, persuasion_result,
            bio_quality.score, keywords_match_score, product_category,
            enneagram_result
        )
        
        # 6. Communication Strategy generieren
        communication_strategy = self.communication_strategy_generator.generate(
            disc_result, neo_result, riasec_result, persuasion_result,
            product_category, profile.full_name, None  # company_name aus Bio extrahieren
        )
        
        api_calls_made += 1  # Communication Strategy LLM-Call
        
        # 7. Verarbeitungszeit
        processing_time = time.time() - start_time
        
        logger.info(f"Analyse abgeschlossen für {profile.id} in {processing_time:.2f}s")
        
        # 8. Ergebnis zusammenstellen
        result = ProfileAnalysisResult(
            profile_id=profile.id,
            bio_quality=bio_quality,
            keywords_match_score=keywords_match_score,
            overall_confidence=overall_confidence,
            disc=disc_result,
            neo=neo_result,
            riasec=riasec_result,
            persuasion=persuasion_result,
            enneagram=enneagram_result,
            purchase_intent=purchase_intent,
            communication_strategy=communication_strategy,
            warnings=warnings,
            processing_time_seconds=processing_time,
            api_calls_made=api_calls_made
        )
        
        # 9. Kompakten Profil-String generieren
        from profile_string_generator import ProfileStringGenerator
        generator = ProfileStringGenerator()
        result.profile_string = generator.generate_compact_string(result)
        
        return result
    
    def analyze_batch(self, profiles: List[ProfileInput], target_keywords: List[str],
                     product_category: str, include_enneagram: bool = False,
                     max_workers: int = 5) -> List[ProfileAnalysisResult]:
        """
        Analysiert mehrere Profile parallel.
        
        Args:
            profiles: Liste von Profilen
            target_keywords: Ziel-Keywords
            product_category: Produkt-Kategorie
            include_enneagram: Enneagram einbeziehen
            max_workers: Maximale parallele Worker
            
        Returns:
            Liste von ProfileAnalysisResult
        """
        logger.info(f"Starte Batch-Analyse für {len(profiles)} Profile")
        
        results = []
        errors = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_profile = {
                executor.submit(
                    self.analyze_profile,
                    profile,
                    target_keywords,
                    product_category,
                    include_enneagram
                ): profile for profile in profiles
            }
            
            for future in as_completed(future_to_profile):
                profile = future_to_profile[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"✓ Profil {profile.id} erfolgreich analysiert")
                except Exception as e:
                    error_msg = f"Fehler bei Profil {profile.id}: {str(e)}"
                    logger.error(error_msg)
                    errors.append({
                        'profile_id': profile.id,
                        'error': str(e)
                    })
        
        logger.info(f"Batch-Analyse abgeschlossen: {len(results)} erfolgreich, {len(errors)} Fehler")
        
        return results
    
    def _run_disc_analysis(self, profile: ProfileInput):
        """Führt DISC-Analyse aus und loggt"""
        start_time = time.time()
        try:
            result = self.disc_agent.analyze(
                profile.bio,
                profile.followers,
                profile.following,
                profile.full_name,
                profile.nickname
            )
            
            self._log_agent_activity(
                'DISC',
                profile.id,
                {'bio_length': len(profile.bio) if profile.bio else 0},
                result.dict(),
                time.time() - start_time,
                True
            )
            
            return result
        except Exception as e:
            self._log_agent_activity(
                'DISC',
                profile.id,
                {},
                None,
                time.time() - start_time,
                False,
                str(e)
            )
            raise
    
    def _run_neo_analysis(self, profile: ProfileInput):
        """Führt NEO-Analyse aus und loggt"""
        start_time = time.time()
        try:
            result = self.neo_agent.analyze(
                profile.bio,
                profile.verified or False,
                profile.business_account or False
            )
            
            self._log_agent_activity(
                'NEO',
                profile.id,
                {'bio_length': len(profile.bio) if profile.bio else 0},
                result.dict(),
                time.time() - start_time,
                True
            )
            
            return result
        except Exception as e:
            self._log_agent_activity(
                'NEO',
                profile.id,
                {},
                None,
                time.time() - start_time,
                False,
                str(e)
            )
            raise
    
    def _run_riasec_analysis(self, profile: ProfileInput):
        """Führt RIASEC-Analyse aus und loggt"""
        start_time = time.time()
        try:
            result = self.riasec_agent.analyze(
                profile.categories,
                profile.bio,
                profile.full_name
            )
            
            self._log_agent_activity(
                'RIASEC',
                profile.id,
                {
                    'categories': profile.categories,
                    'bio_length': len(profile.bio) if profile.bio else 0
                },
                result.dict(),
                time.time() - start_time,
                True
            )
            
            return result
        except Exception as e:
            self._log_agent_activity(
                'RIASEC',
                profile.id,
                {},
                None,
                time.time() - start_time,
                False,
                str(e)
            )
            raise
    
    def _run_persuasion_analysis(self, profile: ProfileInput):
        """Führt Persuasion-Analyse aus und loggt"""
        start_time = time.time()
        try:
            result = self.persuasion_agent.analyze(
                profile.bio,
                profile.verified or False,
                profile.business_account or False
            )
            
            self._log_agent_activity(
                'Persuasion',
                profile.id,
                {'bio_length': len(profile.bio) if profile.bio else 0},
                result.dict(),
                time.time() - start_time,
                True
            )
            
            return result
        except Exception as e:
            self._log_agent_activity(
                'Persuasion',
                profile.id,
                {},
                None,
                time.time() - start_time,
                False,
                str(e)
            )
            raise
    
    def _log_agent_activity(self, agent_name: str, profile_id: str,
                           input_data: Dict[str, Any], output_data: Optional[Dict[str, Any]],
                           duration: float, success: bool, error_message: Optional[str] = None):
        """Loggt Agent-Aktivität für Audit-Trail"""
        log_entry = AgentLogEntry(
            agent_name=agent_name,
            profile_id=profile_id,
            input_data=input_data,
            output_data=output_data,
            api_call_latency_ms=duration * 1000,
            success=success,
            error_message=error_message
        )
        
        self.agent_logs.append(log_entry)
        
        # Auch in File-Log schreiben
        logger.debug(f"Agent {agent_name} für {profile_id}: {'✓' if success else '✗'} ({duration*1000:.0f}ms)")
    
    def get_agent_logs(self) -> List[Dict[str, Any]]:
        """Gibt alle Agent-Logs zurück"""
        return [log.dict() for log in self.agent_logs]
    
    def clear_logs(self):
        """Löscht Agent-Logs"""
        self.agent_logs = []

