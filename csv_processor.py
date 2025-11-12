"""
PCBF 2.1 Framework - CSV Processor
Verarbeitet CSV-Rohdaten und führt Batch-Analyse durch
"""
import csv
import logging
from typing import List, Dict
from io import StringIO

from models import ProfileInput
from analyzer import ProfileAnalyzer

logger = logging.getLogger(__name__)


class CSVProcessor:
    """Verarbeitet CSV-Dateien mit Profil-Rohdaten"""
    
    def __init__(self):
        self.analyzer = ProfileAnalyzer()
    
    def parse_csv(self, csv_content: str) -> List[ProfileInput]:
        """
        Parst CSV-Inhalt und erstellt ProfileInput-Objekte.
        
        Args:
            csv_content: CSV-Datei als String
            
        Returns:
            Liste von ProfileInput-Objekten
        """
        profiles = []
        
        reader = csv.DictReader(StringIO(csv_content))
        
        for row in reader:
            try:
                # Profile Input erstellen
                profile = ProfileInput(
                    id=row.get('lead_uuid') or row.get('lead_id', 'unknown'),
                    platform_name=row.get('platform_name') or 'Unknown',
                    full_name=row.get('full_name', ''),
                    bio=row.get('bio', ''),
                    categories=row.get('categories', None),
                    followers=self._parse_int(row.get('followers')),
                    following=self._parse_int(row.get('following')),
                    posts=self._parse_int(row.get('posts')),
                    verified=self._parse_bool(row.get('verified')),
                    business_account=self._parse_bool(row.get('business_account'))
                )
                
                profiles.append(profile)
                
            except Exception as e:
                logger.error(f"Fehler beim Parsen von Zeile: {str(e)}")
                continue
        
        logger.info(f"{len(profiles)} Profile aus CSV extrahiert")
        return profiles
    
    def _parse_int(self, value) -> int:
        """Parst Integer-Wert"""
        if value is None or value == '' or value == 'NULL':
            return None
        try:
            return int(value)
        except:
            return None
    
    def _parse_bool(self, value) -> bool:
        """Parst Boolean-Wert"""
        if value is None or value == '' or value == 'NULL':
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes']
        return bool(value)
    
    def analyze_batch(self, profiles: List[ProfileInput], 
                     target_keywords: List[str] = None,
                     product_category: str = "Software") -> List[Dict]:
        """
        Führt Batch-Analyse durch.
        
        Args:
            profiles: Liste von ProfileInput
            target_keywords: Target Keywords
            product_category: Produkt-Kategorie
            
        Returns:
            Liste von Analyse-Ergebnissen als Dictionaries
        """
        logger.info(f"Starte Batch-Analyse für {len(profiles)} Profile")
        
        results = self.analyzer.analyze_batch(
            profiles=profiles,
            target_keywords=target_keywords or [],
            product_category=product_category,
            include_enneagram=False,
            max_workers=5
        )
        
        # Zu Dictionaries konvertieren
        results_dicts = []
        for result in results:
            if result:
                results_dicts.append(self._result_to_dict(result))
        
        logger.info(f"Batch-Analyse abgeschlossen: {len(results_dicts)} Ergebnisse")
        return results_dicts
    
    def _result_to_dict(self, result) -> Dict:
        """Konvertiert ProfileAnalysisResult zu Dictionary"""
        return {
            'lead_id': result.profile_id,
            'profile_string': result.profile_string,
            'processing_time': result.processing_time_seconds,
            'api_calls': result.api_calls_made,
            
            # DISC
            'disc_primary': result.disc.primary_type,
            'disc_secondary': result.disc.secondary_type,
            'disc_subtype': result.disc.subtype,
            'disc_archetype': result.disc.archetype,
            'disc_score_d': result.disc.scores.get('D', 0),
            'disc_score_i': result.disc.scores.get('I', 0),
            'disc_score_s': result.disc.scores.get('S', 0),
            'disc_score_c': result.disc.scores.get('C', 0),
            'disc_confidence': result.disc.confidence,
            'disc_reasoning': result.disc.reasoning,
            
            # NEO
            'neo_openness': result.neo.dimensions.get('openness', 0),
            'neo_conscientiousness': result.neo.dimensions.get('conscientiousness', 0),
            'neo_extraversion': result.neo.dimensions.get('extraversion', 0),
            'neo_agreeableness': result.neo.dimensions.get('agreeableness', 0),
            'neo_neuroticism': result.neo.dimensions.get('neuroticism', 0),
            'neo_confidence': result.neo.confidence,
            'neo_reasoning': result.neo.reasoning,
            
            # Persuasion
            'pers_authority': result.persuasion.scores.get('authority', 0),
            'pers_social_proof': result.persuasion.scores.get('social_proof', 0),
            'pers_scarcity': result.persuasion.scores.get('scarcity', 0),
            'pers_reciprocity': result.persuasion.scores.get('reciprocity', 0),
            'pers_consistency': result.persuasion.scores.get('consistency', 0),
            'pers_liking': result.persuasion.scores.get('liking', 0),
            'pers_unity': result.persuasion.scores.get('unity', 0),
            'pers_primary': result.persuasion.primary,
            'pers_confidence': result.persuasion.confidence,
            'pers_reasoning': result.persuasion.reasoning,
            
            # RIASEC
            'riasec_holland_code': result.riasec.holland_code,
            'riasec_score_r': result.riasec.scores.get('R', 0),
            'riasec_score_i': result.riasec.scores.get('I', 0),
            'riasec_score_a': result.riasec.scores.get('A', 0),
            'riasec_score_s': result.riasec.scores.get('S', 0),
            'riasec_score_e': result.riasec.scores.get('E', 0),
            'riasec_score_c': result.riasec.scores.get('C', 0),
            'riasec_primary': result.riasec.primary,
            'riasec_confidence': result.riasec.confidence,
            'riasec_source': result.riasec.source,
            'riasec_reasoning': result.riasec.reasoning,
            
            # Purchase Intent
            'pi_score': result.purchase_intent.score,
            'pi_category': result.purchase_intent.category,
            
            # Overall
            'overall_confidence': result.overall_confidence,
            'warnings': len(result.warnings)
        }


def extract_model_data(results: List[Dict], model: str) -> List[Dict]:
    """
    Extrahiert Daten für spezifisches Psychologisierungs-Modell.
    
    Args:
        results: Liste von Analyse-Ergebnissen
        model: Modell-Name (disc/neo/persuasion/riasec)
        
    Returns:
        Liste von Dictionaries mit Modell-spezifischen Daten
    """
    extracted = []
    
    for result in results:
        if model == 'disc':
            extracted.append({
                'lead_id': result['lead_id'],
                'primary_type': result['disc_primary'],
                'secondary_type': result['disc_secondary'],
                'subtype': result['disc_subtype'],
                'archetype': result['disc_archetype'],
                'score_d': result['disc_score_d'],
                'score_i': result['disc_score_i'],
                'score_s': result['disc_score_s'],
                'score_c': result['disc_score_c'],
                'confidence': result['disc_confidence'],
                'reasoning': result['disc_reasoning']
            })
        
        elif model == 'neo':
            extracted.append({
                'lead_id': result['lead_id'],
                'openness': result['neo_openness'],
                'conscientiousness': result['neo_conscientiousness'],
                'extraversion': result['neo_extraversion'],
                'agreeableness': result['neo_agreeableness'],
                'neuroticism': result['neo_neuroticism'],
                'confidence': result['neo_confidence'],
                'reasoning': result['neo_reasoning']
            })
        
        elif model == 'persuasion':
            extracted.append({
                'lead_id': result['lead_id'],
                'score_authority': result['pers_authority'],
                'score_social_proof': result['pers_social_proof'],
                'score_scarcity': result['pers_scarcity'],
                'score_reciprocity': result['pers_reciprocity'],
                'score_consistency': result['pers_consistency'],
                'score_liking': result['pers_liking'],
                'score_unity': result['pers_unity'],
                'primary_principle': result['pers_primary'],
                'confidence': result['pers_confidence'],
                'reasoning': result['pers_reasoning']
            })
        
        elif model == 'riasec':
            extracted.append({
                'lead_id': result['lead_id'],
                'holland_code': result['riasec_holland_code'],
                'score_r': result['riasec_score_r'],
                'score_i': result['riasec_score_i'],
                'score_a': result['riasec_score_a'],
                'score_s': result['riasec_score_s'],
                'score_e': result['riasec_score_e'],
                'score_c': result['riasec_score_c'],
                'primary_dim': result['riasec_primary'],
                'confidence': result['riasec_confidence'],
                'source': result['riasec_source'],
                'reasoning': result['riasec_reasoning']
            })
    
    return extracted


def export_model_to_csv(data: List[Dict], output_file: str):
    """
    Exportiert Modell-Daten als CSV.
    
    Args:
        data: Liste von Dictionaries
        output_file: Ausgabe-Datei
    """
    if not data:
        return
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    logger.info(f"Modell-Daten exportiert: {output_file}")

