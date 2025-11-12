"""
PCBF 2.1 Framework - Validation Protocol
Automatisierte Validierung von Analyse-Ergebnissen
"""
import re
import logging
from typing import Dict, List, Tuple
from datetime import datetime

from models import ProfileInput, ProfileAnalysisResult
import config

logger = logging.getLogger(__name__)


class ValidationCheck:
    """Einzelner Validierungs-Check"""
    def __init__(self, name: str, status: str, message: str, severity: str = "info"):
        self.name = name
        self.status = status  # PASS, WARNING, FAIL
        self.message = message
        self.severity = severity  # info, warning, error, critical
        self.timestamp = datetime.now()


class ValidationReport:
    """Validierungs-Bericht"""
    def __init__(self, profile_id: str):
        self.profile_id = profile_id
        self.checks: List[ValidationCheck] = []
        self.overall_status = "PASS"
        self.score = 100.0  # Qualitäts-Score (0-100)
        self.timestamp = datetime.now()
    
    def add_check(self, check: ValidationCheck):
        """Fügt Check hinzu"""
        self.checks.append(check)
        
        # Score reduzieren bei Problemen
        if check.status == "WARNING":
            self.score -= 2
        elif check.status == "FAIL":
            self.score -= 10
    
    def finalize(self):
        """Finalisiert Bericht und berechnet Gesamtstatus"""
        errors = sum(1 for c in self.checks if c.status == "FAIL")
        warnings = sum(1 for c in self.checks if c.status == "WARNING")
        
        if errors > 0:
            self.overall_status = "FAIL"
        elif warnings > 6:
            self.overall_status = "WARNING"
        elif warnings > 3:
            self.overall_status = "REVIEW"
        else:
            self.overall_status = "PASS"
        
        self.score = max(0, self.score)
    
    def to_dict(self) -> Dict:
        """Konvertiert zu Dictionary"""
        return {
            'profile_id': self.profile_id,
            'overall_status': self.overall_status,
            'score': self.score,
            'timestamp': self.timestamp.isoformat(),
            'checks': [
                {
                    'name': c.name,
                    'status': c.status,
                    'message': c.message,
                    'severity': c.severity
                }
                for c in self.checks
            ],
            'summary': {
                'total_checks': len(self.checks),
                'passed': sum(1 for c in self.checks if c.status == "PASS"),
                'warnings': sum(1 for c in self.checks if c.status == "WARNING"),
                'failed': sum(1 for c in self.checks if c.status == "FAIL")
            }
        }


class ValidationProtocol:
    """Hauptklasse für Validierung"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate(self, profile_input: ProfileInput, 
                 analysis_result: ProfileAnalysisResult) -> ValidationReport:
        """
        Führt vollständige Validierung durch.
        
        Args:
            profile_input: Eingangsdaten
            analysis_result: Analyse-Ergebnis
            
        Returns:
            ValidationReport
        """
        report = ValidationReport(analysis_result.profile_id)
        
        self.logger.info(f"Starte Validierung für Profil {analysis_result.profile_id}")
        
        # Ebene 1: Eingangsdaten
        self._validate_input_data(profile_input, report)
        
        # Ebene 2: Modul-spezifisch
        self._validate_disc(profile_input, analysis_result, report)
        self._validate_neo(profile_input, analysis_result, report)
        self._validate_riasec(profile_input, analysis_result, report)
        self._validate_persuasion(profile_input, analysis_result, report)
        
        # Ebene 3: Cross-Modul-Konsistenz
        self._validate_cross_module(analysis_result, report)
        
        # Ebene 4: Confidence
        self._validate_confidence(profile_input, analysis_result, report)
        
        # Ebene 5: String-Format
        if analysis_result.profile_string:
            self._validate_string_format(analysis_result.profile_string, report)
        
        # Finalisieren
        report.finalize()
        
        self.logger.info(f"Validierung abgeschlossen: {report.overall_status} (Score: {report.score:.1f})")
        
        return report
    
    # ===== EBENE 1: EINGANGSDATEN =====
    
    def _validate_input_data(self, profile: ProfileInput, report: ValidationReport):
        """Validiert Eingangsdaten"""
        
        # Bio vorhanden
        if profile.bio:
            word_count = len(profile.bio.split())
            report.add_check(ValidationCheck(
                "input_bio_present",
                "PASS",
                f"Bio vorhanden ({word_count} Wörter)"
            ))
            
            # Bio-Länge
            if word_count < 50:
                report.add_check(ValidationCheck(
                    "input_bio_length",
                    "WARNING",
                    f"Bio sehr kurz ({word_count} Wörter, empfohlen: >200)",
                    "warning"
                ))
            elif word_count < 200:
                report.add_check(ValidationCheck(
                    "input_bio_length",
                    "WARNING",
                    f"Bio kurz ({word_count} Wörter, empfohlen: >200)",
                    "info"
                ))
            else:
                report.add_check(ValidationCheck(
                    "input_bio_length",
                    "PASS",
                    f"Bio-Länge ausreichend ({word_count} Wörter)"
                ))
        else:
            report.add_check(ValidationCheck(
                "input_bio_present",
                "FAIL",
                "Keine Bio vorhanden",
                "critical"
            ))
        
        # Categories
        if profile.categories:
            report.add_check(ValidationCheck(
                "input_categories_present",
                "PASS",
                f"Categories vorhanden: {profile.categories[:50]}..."
            ))
        else:
            report.add_check(ValidationCheck(
                "input_categories_present",
                "WARNING",
                "Keine Categories vorhanden (RIASEC-Confidence reduziert)",
                "info"
            ))
        
        # Follower/Following
        if profile.followers is not None and profile.following is not None:
            ratio = profile.followers / max(profile.following, 1)
            report.add_check(ValidationCheck(
                "input_social_metrics",
                "PASS",
                f"Social Metrics: {profile.followers} Follower, {profile.following} Following (Ratio: {ratio:.2f})"
            ))
        else:
            report.add_check(ValidationCheck(
                "input_social_metrics",
                "WARNING",
                "Follower/Following-Daten fehlen",
                "info"
            ))
    
    # ===== EBENE 2: MODUL-SPEZIFISCH =====
    
    def _validate_disc(self, profile: ProfileInput, result: ProfileAnalysisResult, 
                       report: ValidationReport):
        """Validiert DISC-Modul"""
        disc = result.disc
        
        # Score-Summe
        score_sum = sum(disc.scores.values())
        if abs(score_sum - 1.0) > 0.15:
            report.add_check(ValidationCheck(
                "disc_score_sum",
                "WARNING",
                f"DISC-Score-Summe {score_sum:.2f} weicht von 1.0 ab (Toleranz: ±0.15)",
                "warning"
            ))
        else:
            report.add_check(ValidationCheck(
                "disc_score_sum",
                "PASS",
                f"DISC-Score-Summe korrekt ({score_sum:.2f})"
            ))
        
        # Primary > Secondary
        primary_score = disc.scores.get(disc.primary_type, 0)
        other_scores = [v for k, v in disc.scores.items() if k != disc.primary_type]
        if other_scores and primary_score <= max(other_scores):
            report.add_check(ValidationCheck(
                "disc_primary_highest",
                "FAIL",
                f"Primary Type {disc.primary_type} hat nicht den höchsten Score",
                "error"
            ))
        else:
            report.add_check(ValidationCheck(
                "disc_primary_highest",
                "PASS",
                f"Primary Type {disc.primary_type} hat höchsten Score ({primary_score:.2f})"
            ))
        
        # Plausibilität mit Bio
        if profile.bio:
            plausible = self._check_disc_plausibility(profile.bio, disc.primary_type)
            if plausible:
                report.add_check(ValidationCheck(
                    "disc_bio_plausibility",
                    "PASS",
                    f"DISC-Typ {disc.primary_type} plausibel mit Bio-Keywords"
                ))
            else:
                report.add_check(ValidationCheck(
                    "disc_bio_plausibility",
                    "WARNING",
                    f"DISC-Typ {disc.primary_type} nicht offensichtlich aus Bio erkennbar",
                    "info"
                ))
        
        # Confidence-Range
        if 50 <= disc.confidence <= 70:
            report.add_check(ValidationCheck(
                "disc_confidence_range",
                "PASS",
                f"DISC-Confidence im erwarteten Bereich ({disc.confidence:.1f}%)"
            ))
        else:
            report.add_check(ValidationCheck(
                "disc_confidence_range",
                "WARNING",
                f"DISC-Confidence außerhalb erwartetem Bereich ({disc.confidence:.1f}%, erwartet: 50-70%)",
                "warning"
            ))
    
    def _check_disc_plausibility(self, bio: str, disc_type: str) -> bool:
        """Prüft DISC-Plausibilität mit Bio"""
        bio_lower = bio.lower()
        keywords = config.DISC_KEYWORDS.get(disc_type, [])
        
        # Mindestens 1 Keyword gefunden?
        for kw in keywords[:10]:  # Top 10 Keywords
            if kw.lower() in bio_lower:
                return True
        return False
    
    def _validate_neo(self, profile: ProfileInput, result: ProfileAnalysisResult,
                      report: ValidationReport):
        """Validiert NEO-Modul"""
        neo = result.neo
        
        # Alle Dimensionen im Range 0-1
        for dim, value in neo.dimensions.items():
            if not (0.0 <= value <= 1.0):
                report.add_check(ValidationCheck(
                    f"neo_{dim}_range",
                    "FAIL",
                    f"NEO-Dimension {dim} außerhalb Range 0-1: {value}",
                    "error"
                ))
            else:
                report.add_check(ValidationCheck(
                    f"neo_{dim}_range",
                    "PASS",
                    f"NEO-Dimension {dim} im Range ({value:.2f})"
                ))
        
        # Extreme Werte warnen
        for dim, value in neo.dimensions.items():
            if value < 0.2 or value > 0.95:
                report.add_check(ValidationCheck(
                    f"neo_{dim}_extreme",
                    "WARNING",
                    f"NEO-Dimension {dim} hat extremen Wert ({value:.2f})",
                    "info"
                ))
        
        # Confidence-Range
        if 40 <= neo.confidence <= 60:
            report.add_check(ValidationCheck(
                "neo_confidence_range",
                "PASS",
                f"NEO-Confidence im erwarteten Bereich ({neo.confidence:.1f}%)"
            ))
        else:
            report.add_check(ValidationCheck(
                "neo_confidence_range",
                "WARNING",
                f"NEO-Confidence außerhalb erwartetem Bereich ({neo.confidence:.1f}%, erwartet: 40-60%)",
                "warning"
            ))
    
    def _validate_riasec(self, profile: ProfileInput, result: ProfileAnalysisResult,
                        report: ValidationReport):
        """Validiert RIASEC-Modul"""
        riasec = result.riasec
        
        # Holland-Code Format
        if not re.match(r'^[RIASEC]{1,3}$', riasec.holland_code):
            report.add_check(ValidationCheck(
                "riasec_code_format",
                "FAIL",
                f"Holland-Code ungültiges Format: {riasec.holland_code}",
                "error"
            ))
        else:
            report.add_check(ValidationCheck(
                "riasec_code_format",
                "PASS",
                f"Holland-Code Format korrekt ({riasec.holland_code})"
            ))
        
        # Primary = erster Buchstabe
        if riasec.holland_code and riasec.holland_code[0] != riasec.primary:
            report.add_check(ValidationCheck(
                "riasec_primary_match",
                "FAIL",
                f"Primary Type {riasec.primary} stimmt nicht mit erstem Buchstaben in {riasec.holland_code} überein",
                "error"
            ))
        else:
            report.add_check(ValidationCheck(
                "riasec_primary_match",
                "PASS",
                f"Primary Type {riasec.primary} stimmt mit Holland-Code überein"
            ))
        
        # Score-Summe (lockerer als DISC)
        score_sum = sum(riasec.scores.values())
        if score_sum < 0.5 or score_sum > 2.5:
            report.add_check(ValidationCheck(
                "riasec_score_sum",
                "WARNING",
                f"RIASEC-Score-Summe ungewöhnlich ({score_sum:.2f}, erwartet: 0.8-2.0)",
                "warning"
            ))
        else:
            report.add_check(ValidationCheck(
                "riasec_score_sum",
                "PASS",
                f"RIASEC-Score-Summe plausibel ({score_sum:.2f})"
            ))
        
        # Confidence abhängig von Source
        if riasec.source == "categories":
            if 65 <= riasec.confidence <= 80:
                report.add_check(ValidationCheck(
                    "riasec_confidence_categories",
                    "PASS",
                    f"RIASEC-Confidence mit Categories im erwarteten Bereich ({riasec.confidence:.1f}%)"
                ))
            else:
                report.add_check(ValidationCheck(
                    "riasec_confidence_categories",
                    "WARNING",
                    f"RIASEC-Confidence mit Categories außerhalb erwartetem Bereich ({riasec.confidence:.1f}%, erwartet: 65-80%)",
                    "warning"
                ))
        else:  # bio
            if 45 <= riasec.confidence <= 60:
                report.add_check(ValidationCheck(
                    "riasec_confidence_bio",
                    "PASS",
                    f"RIASEC-Confidence nur Bio im erwarteten Bereich ({riasec.confidence:.1f}%)"
                ))
            else:
                report.add_check(ValidationCheck(
                    "riasec_confidence_bio",
                    "WARNING",
                    f"RIASEC-Confidence nur Bio außerhalb erwartetem Bereich ({riasec.confidence:.1f}%, erwartet: 45-60%)",
                    "warning"
                ))
    
    def _validate_persuasion(self, profile: ProfileInput, result: ProfileAnalysisResult,
                            report: ValidationReport):
        """Validiert Persuasion-Modul"""
        pers = result.persuasion
        
        # Score-Summe (7 Prinzipien, Durchschnitt 0.5)
        score_sum = sum(pers.scores.values())
        if score_sum < 2.5 or score_sum > 4.5:
            report.add_check(ValidationCheck(
                "persuasion_score_sum",
                "WARNING",
                f"Persuasion-Score-Summe ungewöhnlich ({score_sum:.2f}, erwartet: ~3.5)",
                "warning"
            ))
        else:
            report.add_check(ValidationCheck(
                "persuasion_score_sum",
                "PASS",
                f"Persuasion-Score-Summe plausibel ({score_sum:.2f})"
            ))
        
        # Primary Score > 0.6
        primary_score = pers.scores.get(pers.primary, 0)
        if primary_score < 0.6:
            report.add_check(ValidationCheck(
                "persuasion_primary_score",
                "WARNING",
                f"Primary Persuasion-Score niedrig ({primary_score:.2f}, erwartet: >0.6)",
                "warning"
            ))
        else:
            report.add_check(ValidationCheck(
                "persuasion_primary_score",
                "PASS",
                f"Primary Persuasion-Score ausreichend ({primary_score:.2f})"
            ))
        
        # Confidence-Range
        if 60 <= pers.confidence <= 75:
            report.add_check(ValidationCheck(
                "persuasion_confidence_range",
                "PASS",
                f"Persuasion-Confidence im erwarteten Bereich ({pers.confidence:.1f}%)"
            ))
        else:
            report.add_check(ValidationCheck(
                "persuasion_confidence_range",
                "WARNING",
                f"Persuasion-Confidence außerhalb erwartetem Bereich ({pers.confidence:.1f}%, erwartet: 60-75%)",
                "warning"
            ))
    
    # ===== EBENE 3: CROSS-MODUL-KONSISTENZ =====
    
    def _validate_cross_module(self, result: ProfileAnalysisResult, report: ValidationReport):
        """Validiert Cross-Modul-Konsistenz"""
        
        # DISC ↔ NEO
        disc_type = result.disc.primary_type
        neo = result.neo.dimensions
        
        # D-Typ → hohe Extraversion
        if disc_type == 'D':
            if neo.get('extraversion', 0) > 0.7:
                report.add_check(ValidationCheck(
                    "cross_disc_neo_d_extraversion",
                    "PASS",
                    f"D-Typ + hohe Extraversion ({neo['extraversion']:.2f}) konsistent"
                ))
            else:
                report.add_check(ValidationCheck(
                    "cross_disc_neo_d_extraversion",
                    "WARNING",
                    f"D-Typ mit niedriger Extraversion ({neo.get('extraversion', 0):.2f}) ungewöhnlich",
                    "info"
                ))
        
        # I-Typ → hohe Extraversion + Openness
        if disc_type == 'I':
            if neo.get('extraversion', 0) > 0.7 and neo.get('openness', 0) > 0.7:
                report.add_check(ValidationCheck(
                    "cross_disc_neo_i_traits",
                    "PASS",
                    f"I-Typ + hohe Extraversion/Openness konsistent"
                ))
        
        # S-Typ → hohe Agreeableness
        if disc_type == 'S':
            if neo.get('agreeableness', 0) > 0.7:
                report.add_check(ValidationCheck(
                    "cross_disc_neo_s_agreeableness",
                    "PASS",
                    f"S-Typ + hohe Agreeableness ({neo['agreeableness']:.2f}) konsistent"
                ))
        
        # C-Typ → hohe Conscientiousness
        if disc_type == 'C':
            if neo.get('conscientiousness', 0) > 0.8:
                report.add_check(ValidationCheck(
                    "cross_disc_neo_c_conscientiousness",
                    "PASS",
                    f"C-Typ + hohe Conscientiousness ({neo['conscientiousness']:.2f}) konsistent"
                ))
        
        # DISC ↔ Communication Strategy
        comm_style = result.communication_strategy.style.lower()
        if disc_type == 'D' and 'direkt' in comm_style:
            report.add_check(ValidationCheck(
                "cross_disc_comm_style",
                "PASS",
                f"D-Typ + direkter Kommunikationsstil konsistent"
            ))
        elif disc_type == 'I' and ('enthusiastisch' in comm_style or 'kreativ' in comm_style):
            report.add_check(ValidationCheck(
                "cross_disc_comm_style",
                "PASS",
                f"I-Typ + enthusiastischer Kommunikationsstil konsistent"
            ))
    
    # ===== EBENE 4: CONFIDENCE =====
    
    def _validate_confidence(self, profile: ProfileInput, result: ProfileAnalysisResult,
                            report: ValidationReport):
        """Validiert Confidence-Werte"""
        
        # Overall Confidence
        if result.overall_confidence < 40:
            report.add_check(ValidationCheck(
                "confidence_overall_low",
                "WARNING",
                f"Overall Confidence sehr niedrig ({result.overall_confidence:.1f}%), Ergebnisse mit Vorsicht interpretieren",
                "warning"
            ))
        elif result.overall_confidence < 60:
            report.add_check(ValidationCheck(
                "confidence_overall_medium",
                "WARNING",
                f"Overall Confidence mittel ({result.overall_confidence:.1f}%), einige Unsicherheiten",
                "info"
            ))
        else:
            report.add_check(ValidationCheck(
                "confidence_overall_good",
                "PASS",
                f"Overall Confidence gut ({result.overall_confidence:.1f}%)"
            ))
        
        # Confidence-Reihenfolge: RIASEC > Persuasion > DISC > NEO
        if result.riasec.confidence < result.neo.confidence:
            report.add_check(ValidationCheck(
                "confidence_order",
                "WARNING",
                f"RIASEC-Confidence ({result.riasec.confidence:.1f}%) niedriger als NEO ({result.neo.confidence:.1f}%), ungewöhnlich",
                "info"
            ))
        
        # Warnungen-Konsistenz
        expected_warnings = 0
        if result.overall_confidence < 60:
            expected_warnings += 1
        if profile.bio and len(profile.bio.split()) < 200:
            expected_warnings += 1
        if not profile.categories:
            expected_warnings += 1
        
        actual_warnings = len(result.warnings)
        if actual_warnings < expected_warnings:
            report.add_check(ValidationCheck(
                "warnings_consistency",
                "WARNING",
                f"Weniger Warnungen als erwartet ({actual_warnings} vs. {expected_warnings})",
                "info"
            ))
        else:
            report.add_check(ValidationCheck(
                "warnings_consistency",
                "PASS",
                f"Warnungen konsistent ({actual_warnings} Warnungen)"
            ))
    
    # ===== EBENE 5: STRING-FORMAT =====
    
    def _validate_string_format(self, profile_string: str, report: ValidationReport):
        """Validiert Profil-String-Format"""
        
        # Kompakter String Pattern
        pattern = r'DISC:[DISC][isc]?(\(\d+%\))? \| NEO:[OCEAN]=\d\.\d{2}(,[OCEAN]=\d\.\d{2})*(\(\d+%\))? \| RIASEC:[RIASEC]{1,3}(\(\d+%\))? \| PERS:\w+(\(\d+%\))? \| PI:\d{1,3}'
        
        if re.match(pattern, profile_string):
            report.add_check(ValidationCheck(
                "string_format_valid",
                "PASS",
                "Profil-String Format korrekt"
            ))
        else:
            report.add_check(ValidationCheck(
                "string_format_valid",
                "FAIL",
                f"Profil-String Format ungültig: {profile_string[:100]}",
                "error"
            ))
        
        # Länge prüfen
        if len(profile_string) > 200:
            report.add_check(ValidationCheck(
                "string_length",
                "WARNING",
                f"Profil-String sehr lang ({len(profile_string)} Zeichen, empfohlen: <200)",
                "info"
            ))
        else:
            report.add_check(ValidationCheck(
                "string_length",
                "PASS",
                f"Profil-String Länge OK ({len(profile_string)} Zeichen)"
            ))


def validate_batch(profiles: List[Tuple[ProfileInput, ProfileAnalysisResult]]) -> List[ValidationReport]:
    """
    Validiert mehrere Profile.
    
    Args:
        profiles: Liste von (ProfileInput, ProfileAnalysisResult) Tupeln
        
    Returns:
        Liste von ValidationReport
    """
    validator = ValidationProtocol()
    reports = []
    
    for profile_input, analysis_result in profiles:
        report = validator.validate(profile_input, analysis_result)
        reports.append(report)
    
    return reports

