"""
PCBF 2.1 Framework - Profile String Generator
Erstellt kompakte String-Repräsentationen von Profilen für externe Tools
"""
import logging
from typing import Dict, List, Optional
from models import ProfileAnalysisResult, DISCResult, NEOResult, RIASECResult, PersuasionResult

logger = logging.getLogger(__name__)


class ProfileStringGenerator:
    """Generiert kompakte String-Repräsentationen von Analyse-Ergebnissen"""
    
    @staticmethod
    def generate_compact_string(result: ProfileAnalysisResult, 
                               include_confidence: bool = True,
                               top_n_scores: int = 3) -> str:
        """
        Generiert einen kompakten String für ein Profil.
        
        Format: DISC:D | NEO:C=0.92,E=0.88,O=0.85 | RIASEC:IEC | PERS:authority | PI:82
        
        Args:
            result: ProfileAnalysisResult
            include_confidence: Confidence-Werte einbeziehen
            top_n_scores: Anzahl Top-Scores für NEO
            
        Returns:
            Kompakter Profil-String
        """
        parts = []
        
        # DISC
        disc_str = f"DISC:{result.disc.primary_type}"
        if result.disc.secondary_type:
            disc_str += result.disc.secondary_type.lower()
        if include_confidence:
            disc_str += f"({result.disc.confidence:.0f}%)"
        parts.append(disc_str)
        
        # NEO/OCEAN - Top N Dimensionen
        neo_dims = sorted(
            result.neo.dimensions.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_n_scores]
        
        neo_str = "NEO:" + ",".join([
            f"{dim[0][0].upper()}={dim[1]:.2f}" 
            for dim in neo_dims
        ])
        if include_confidence:
            neo_str += f"({result.neo.confidence:.0f}%)"
        parts.append(neo_str)
        
        # RIASEC
        riasec_str = f"RIASEC:{result.riasec.holland_code}"
        if include_confidence:
            riasec_str += f"({result.riasec.confidence:.0f}%)"
        parts.append(riasec_str)
        
        # Persuasion
        pers_str = f"PERS:{result.persuasion.primary}"
        if include_confidence:
            pers_str += f"({result.persuasion.confidence:.0f}%)"
        parts.append(pers_str)
        
        # Purchase Intent
        pi_str = f"PI:{result.purchase_intent.score:.0f}"
        parts.append(pi_str)
        
        return " | ".join(parts)
    
    @staticmethod
    def generate_detailed_string(result: ProfileAnalysisResult) -> str:
        """
        Generiert einen detaillierten String mit allen Scores.
        
        Format: DISC:D=0.45,I=0.30,S=0.15,C=0.10 | NEO:O=0.85,C=0.92,E=0.88,A=0.65,N=0.42 | ...
        
        Args:
            result: ProfileAnalysisResult
            
        Returns:
            Detaillierter Profil-String
        """
        parts = []
        
        # DISC - Alle Scores
        disc_scores = ",".join([
            f"{k}={v:.2f}" 
            for k, v in sorted(result.disc.scores.items())
        ])
        parts.append(f"DISC:{disc_scores}")
        
        # NEO - Alle Dimensionen
        neo_mapping = {
            'openness': 'O',
            'conscientiousness': 'C',
            'extraversion': 'E',
            'agreeableness': 'A',
            'neuroticism': 'N'
        }
        neo_scores = ",".join([
            f"{neo_mapping[k]}={v:.2f}" 
            for k, v in result.neo.dimensions.items()
        ])
        parts.append(f"NEO:{neo_scores}")
        
        # RIASEC - Alle Scores
        riasec_scores = ",".join([
            f"{k}={v:.2f}" 
            for k, v in sorted(result.riasec.scores.items())
        ])
        parts.append(f"RIASEC:{riasec_scores}")
        
        # Persuasion - Alle Scores
        pers_mapping = {
            'authority': 'AUTH',
            'social_proof': 'SPROOF',
            'scarcity': 'SCAR',
            'reciprocity': 'RECIP',
            'consistency': 'CONS',
            'liking': 'LIKE',
            'unity': 'UNITY'
        }
        pers_scores = ",".join([
            f"{pers_mapping[k]}={v:.2f}" 
            for k, v in result.persuasion.scores.items()
        ])
        parts.append(f"PERS:{pers_scores}")
        
        # Purchase Intent
        parts.append(f"PI:{result.purchase_intent.score:.2f}")
        
        # Overall Confidence
        parts.append(f"CONF:{result.overall_confidence:.2f}")
        
        return " | ".join(parts)
    
    @staticmethod
    def generate_custom_string(result: ProfileAnalysisResult, 
                               format_template: str) -> str:
        """
        Generiert einen String basierend auf einem benutzerdefinierten Template.
        
        Template-Variablen:
        - {disc_primary} - DISC Primary Type (D/I/S/C)
        - {disc_archetype} - DISC Archetyp
        - {neo_o}, {neo_c}, {neo_e}, {neo_a}, {neo_n} - NEO Dimensionen
        - {riasec_code} - Holland-Code (z.B. IEC)
        - {riasec_primary} - Primärer RIASEC-Typ
        - {persuasion_primary} - Primäres Persuasion-Prinzip
        - {pi_score} - Purchase Intent Score
        - {pi_category} - Purchase Intent Kategorie
        - {confidence} - Overall Confidence
        
        Args:
            result: ProfileAnalysisResult
            format_template: Format-String mit Platzhaltern
            
        Returns:
            Formatierter Profil-String
        """
        replacements = {
            'disc_primary': result.disc.primary_type,
            'disc_archetype': result.disc.archetype,
            'neo_o': f"{result.neo.dimensions.get('openness', 0):.2f}",
            'neo_c': f"{result.neo.dimensions.get('conscientiousness', 0):.2f}",
            'neo_e': f"{result.neo.dimensions.get('extraversion', 0):.2f}",
            'neo_a': f"{result.neo.dimensions.get('agreeableness', 0):.2f}",
            'neo_n': f"{result.neo.dimensions.get('neuroticism', 0):.2f}",
            'riasec_code': result.riasec.holland_code,
            'riasec_primary': result.riasec.primary,
            'persuasion_primary': result.persuasion.primary,
            'pi_score': f"{result.purchase_intent.score:.0f}",
            'pi_category': result.purchase_intent.category,
            'confidence': f"{result.overall_confidence:.0f}"
        }
        
        formatted = format_template
        for key, value in replacements.items():
            formatted = formatted.replace(f"{{{key}}}", value)
        
        return formatted
    
    @staticmethod
    def to_flat_dict(result: ProfileAnalysisResult) -> Dict:
        """
        Konvertiert ProfileAnalysisResult in ein flaches Dictionary für CSV-Export.
        
        Args:
            result: ProfileAnalysisResult
            
        Returns:
            Flaches Dictionary mit allen Werten
        """
        flat = {
            # Meta
            'profile_id': result.profile_id,
            'timestamp': result.timestamp.isoformat(),
            'processing_time_seconds': result.processing_time_seconds,
            
            # Data Quality
            'bio_quality_score': result.bio_quality.score,
            'bio_word_count': result.bio_quality.word_count,
            'bio_category': result.bio_quality.category,
            'keywords_match_score': result.keywords_match_score,
            'overall_confidence': result.overall_confidence,
            
            # DISC
            'disc_primary': result.disc.primary_type,
            'disc_secondary': result.disc.secondary_type or '',
            'disc_subtype': result.disc.subtype,
            'disc_archetype': result.disc.archetype,
            'disc_confidence': result.disc.confidence,
            'disc_score_d': result.disc.scores.get('D', 0),
            'disc_score_i': result.disc.scores.get('I', 0),
            'disc_score_s': result.disc.scores.get('S', 0),
            'disc_score_c': result.disc.scores.get('C', 0),
            
            # NEO
            'neo_openness': result.neo.dimensions.get('openness', 0),
            'neo_conscientiousness': result.neo.dimensions.get('conscientiousness', 0),
            'neo_extraversion': result.neo.dimensions.get('extraversion', 0),
            'neo_agreeableness': result.neo.dimensions.get('agreeableness', 0),
            'neo_neuroticism': result.neo.dimensions.get('neuroticism', 0),
            'neo_confidence': result.neo.confidence,
            
            # RIASEC
            'riasec_holland_code': result.riasec.holland_code,
            'riasec_primary': result.riasec.primary,
            'riasec_confidence': result.riasec.confidence,
            'riasec_source': result.riasec.source,
            'riasec_score_r': result.riasec.scores.get('R', 0),
            'riasec_score_i': result.riasec.scores.get('I', 0),
            'riasec_score_a': result.riasec.scores.get('A', 0),
            'riasec_score_s': result.riasec.scores.get('S', 0),
            'riasec_score_e': result.riasec.scores.get('E', 0),
            'riasec_score_c': result.riasec.scores.get('C', 0),
            
            # Persuasion
            'persuasion_primary': result.persuasion.primary,
            'persuasion_confidence': result.persuasion.confidence,
            'persuasion_authority': result.persuasion.scores.get('authority', 0),
            'persuasion_social_proof': result.persuasion.scores.get('social_proof', 0),
            'persuasion_scarcity': result.persuasion.scores.get('scarcity', 0),
            'persuasion_reciprocity': result.persuasion.scores.get('reciprocity', 0),
            'persuasion_consistency': result.persuasion.scores.get('consistency', 0),
            'persuasion_liking': result.persuasion.scores.get('liking', 0),
            'persuasion_unity': result.persuasion.scores.get('unity', 0),
            
            # Purchase Intent
            'purchase_intent_score': result.purchase_intent.score,
            'purchase_intent_category': result.purchase_intent.category,
            
            # Communication Strategy
            'comm_style': result.communication_strategy.style,
            'comm_tone': result.communication_strategy.tone,
            'comm_content_focus': result.communication_strategy.content_focus,
            'comm_persuasion_approach': result.communication_strategy.persuasion_approach,
            
            # Warnings
            'warnings_count': len(result.warnings),
            'has_critical_warnings': any(w.level == 'critical' for w in result.warnings)
        }
        
        # Compact String hinzufügen
        generator = ProfileStringGenerator()
        flat['profile_string_compact'] = generator.generate_compact_string(result)
        flat['profile_string_detailed'] = generator.generate_detailed_string(result)
        
        return flat
    
    @staticmethod
    def to_csv_row(result: ProfileAnalysisResult) -> List:
        """
        Konvertiert ProfileAnalysisResult in eine CSV-Zeile.
        
        Args:
            result: ProfileAnalysisResult
            
        Returns:
            Liste von Werten für CSV-Zeile
        """
        flat = ProfileStringGenerator.to_flat_dict(result)
        
        # Sortierte Liste der Keys (alphabetisch)
        keys = sorted(flat.keys())
        
        return [flat[key] for key in keys]
    
    @staticmethod
    def get_csv_headers() -> List[str]:
        """
        Gibt CSV-Header zurück.
        
        Returns:
            Liste von Header-Namen
        """
        # Dummy-Result erstellen um Keys zu extrahieren
        from models import (
            BioQualityResult, DISCResult, NEOResult, RIASECResult,
            PersuasionResult, PurchaseIntentResult, CommunicationStrategy
        )
        from datetime import datetime
        
        dummy_result = ProfileAnalysisResult(
            profile_id='dummy',
            timestamp=datetime.now(),
            bio_quality=BioQualityResult(
                score=0, word_count=0, has_job_title=False,
                has_company=False, has_structure=False,
                emoji_count=0, category='low'
            ),
            keywords_match_score=0,
            overall_confidence=0,
            disc=DISCResult(
                primary_type='D', secondary_type=None, subtype='D',
                archetype='Captain', scores={'D': 0, 'I': 0, 'S': 0, 'C': 0},
                confidence=0
            ),
            neo=NEOResult(
                dimensions={
                    'openness': 0, 'conscientiousness': 0,
                    'extraversion': 0, 'agreeableness': 0, 'neuroticism': 0
                },
                confidence=0
            ),
            riasec=RIASECResult(
                holland_code='IEC', scores={'R': 0, 'I': 0, 'A': 0, 'S': 0, 'E': 0, 'C': 0},
                primary='I', confidence=0, source='bio'
            ),
            persuasion=PersuasionResult(
                scores={
                    'authority': 0, 'social_proof': 0, 'scarcity': 0,
                    'reciprocity': 0, 'consistency': 0, 'liking': 0, 'unity': 0
                },
                primary='authority', confidence=0
            ),
            purchase_intent=PurchaseIntentResult(
                score=0, category='low', contributing_factors={}
            ),
            communication_strategy=CommunicationStrategy(
                style='', tone='', content_focus='',
                persuasion_approach='', subject_line='',
                message_body='', call_to_action=''
            ),
            warnings=[]
        )
        
        flat = ProfileStringGenerator.to_flat_dict(dummy_result)
        return sorted(flat.keys())


def export_to_csv(results: List[ProfileAnalysisResult], 
                  output_file: str) -> str:
    """
    Exportiert Analyse-Ergebnisse in CSV-Datei.
    
    Args:
        results: Liste von ProfileAnalysisResult
        output_file: Pfad zur Output-CSV-Datei
        
    Returns:
        Pfad zur erstellten CSV-Datei
    """
    import csv
    
    generator = ProfileStringGenerator()
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header schreiben
        headers = generator.get_csv_headers()
        writer.writerow(headers)
        
        # Daten schreiben
        for result in results:
            flat = generator.to_flat_dict(result)
            row = [flat[key] for key in headers]
            writer.writerow(row)
    
    logger.info(f"CSV-Export abgeschlossen: {output_file} ({len(results)} Profile)")
    
    return output_file


def export_to_json_lines(results: List[ProfileAnalysisResult],
                         output_file: str) -> str:
    """
    Exportiert Analyse-Ergebnisse in JSON-Lines-Format.
    
    Args:
        results: Liste von ProfileAnalysisResult
        output_file: Pfad zur Output-Datei
        
    Returns:
        Pfad zur erstellten Datei
    """
    import json
    
    generator = ProfileStringGenerator()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            flat = generator.to_flat_dict(result)
            f.write(json.dumps(flat, ensure_ascii=False) + '\n')
    
    logger.info(f"JSON-Lines-Export abgeschlossen: {output_file} ({len(results)} Profile)")
    
    return output_file

