"""
PCBF 2.1 Framework - Communication Strategy Generator
"""
import logging
from typing import Optional
from models import (
    DISCResult, NEOResult, RIASECResult, PersuasionResult,
    CommunicationStrategy
)
from llm_client import get_llm_client

logger = logging.getLogger(__name__)


class CommunicationStrategyGenerator:
    """Generiert personalisierte Kommunikationsstrategien"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
    
    def generate(self, disc: DISCResult, neo: NEOResult, riasec: RIASECResult,
                 persuasion: PersuasionResult, product_category: str,
                 full_name: Optional[str] = None,
                 company_name: Optional[str] = None) -> CommunicationStrategy:
        """
        Generiert personalisierte Kommunikationsstrategie.
        
        Args:
            disc: DISC-Ergebnis
            neo: NEO-Ergebnis
            riasec: RIASEC-Ergebnis
            persuasion: Persuasion-Ergebnis
            product_category: Produkt-Kategorie
            full_name: Name des Empfängers (optional)
            company_name: Unternehmensname (optional)
            
        Returns:
            CommunicationStrategy mit personalisierten Nachrichten
        """
        logger.info("Communication Strategy Generierung gestartet")
        
        # Stil basierend auf DISC
        style = self._determine_style(disc)
        
        # Ton basierend auf NEO
        tone = self._determine_tone(neo)
        
        # Inhaltsfokus basierend auf RIASEC
        content_focus = self._determine_content_focus(riasec)
        
        # Persuasion-Ansatz basierend auf Cialdini
        persuasion_approach = self._determine_persuasion_approach(persuasion)
        
        # LLM-basierte Nachrichtengenerierung
        message_result = self._generate_message(
            style, tone, content_focus, persuasion_approach,
            product_category, full_name, company_name,
            disc, neo, riasec, persuasion
        )
        
        if message_result:
            subject_line = message_result.get('subject_line', '')
            message_body = message_result.get('message_body', '')
            call_to_action = message_result.get('call_to_action', '')
        else:
            # Fallback
            logger.warning("LLM-Nachrichtengenerierung fehlgeschlagen - verwende Fallback")
            subject_line = self._fallback_subject(style, product_category)
            message_body = self._fallback_message(style, tone, content_focus, product_category, full_name)
            call_to_action = self._fallback_cta(style)
        
        return CommunicationStrategy(
            style=style,
            tone=tone,
            content_focus=content_focus,
            persuasion_approach=persuasion_approach,
            subject_line=subject_line,
            message_body=message_body,
            call_to_action=call_to_action
        )
    
    def _determine_style(self, disc: DISCResult) -> str:
        """Bestimmt Kommunikationsstil basierend auf DISC"""
        style_map = {
            'D': 'Direkt und ergebnisorientiert',
            'I': 'Enthusiastisch und inspirierend',
            'S': 'Unterstützend und harmonisch',
            'C': 'Analytisch und detailliert'
        }
        return style_map.get(disc.primary_type, 'Ausgewogen')
    
    def _determine_tone(self, neo: NEOResult) -> str:
        """Bestimmt Tonalität basierend auf NEO"""
        # Extraversion und Agreeableness sind key
        e_score = neo.dimensions.get('extraversion', 0.5)
        a_score = neo.dimensions.get('agreeableness', 0.5)
        
        if e_score > 0.6 and a_score > 0.6:
            return 'Freundlich und energetisch'
        elif e_score > 0.6:
            return 'Energetisch und dynamisch'
        elif a_score > 0.6:
            return 'Freundlich und empathisch'
        elif e_score < 0.4:
            return 'Professionell und zurückhaltend'
        else:
            return 'Professionell und ausgewogen'
    
    def _determine_content_focus(self, riasec: RIASECResult) -> str:
        """Bestimmt Inhaltsfokus basierend auf RIASEC"""
        focus_map = {
            'R': 'Praktische Anwendungen und konkrete Ergebnisse',
            'I': 'Innovation, Daten und technische Details',
            'A': 'Kreativität, Design und einzigartige Lösungen',
            'S': 'Teamnutzen, Zusammenarbeit und Support',
            'E': 'ROI, Wachstum und Business-Impact',
            'C': 'Prozesse, Qualität und Zuverlässigkeit'
        }
        return focus_map.get(riasec.primary, 'Allgemeine Vorteile')
    
    def _determine_persuasion_approach(self, persuasion: PersuasionResult) -> str:
        """Bestimmt Persuasion-Ansatz basierend auf Cialdini"""
        approach_map = {
            'authority': 'Expertise und Credentials betonen',
            'social_proof': 'Erfolgsgeschichten und Referenzen nutzen',
            'scarcity': 'Exklusivität und Einzigartigkeit hervorheben',
            'reciprocity': 'Mehrwert und kostenlose Ressourcen anbieten',
            'consistency': 'Werte und langfristige Vision betonen',
            'liking': 'Persönliche Verbindung und Sympathie aufbauen',
            'unity': 'Gemeinschaft und Zugehörigkeit betonen'
        }
        return approach_map.get(persuasion.primary, 'Ausgewogener Ansatz')
    
    def _generate_message(self, style: str, tone: str, content_focus: str,
                         persuasion_approach: str, product_category: str,
                         full_name: Optional[str], company_name: Optional[str],
                         disc: DISCResult, neo: NEOResult, riasec: RIASECResult,
                         persuasion: PersuasionResult) -> Optional[dict]:
        """LLM-basierte Nachrichtengenerierung"""
        
        system_prompt = """Du bist ein Experte für personalisierte B2B-Kommunikation.
Erstelle eine personalisierte Outreach-Nachricht basierend auf dem psychologischen Profil des Empfängers.

Die Nachricht sollte:
- Kurz und prägnant sein (max. 150 Wörter)
- Professionell und authentisch wirken
- Auf die Persönlichkeit des Empfängers zugeschnitten sein
- Einen klaren Call-to-Action enthalten

Gib deine Nachricht als JSON zurück:
{
  "subject_line": "Betreffzeile (max. 60 Zeichen)",
  "message_body": "Nachrichtentext",
  "call_to_action": "Call-to-Action"
}"""
        
        recipient = full_name if full_name else "dem Empfänger"
        company = f" bei {company_name}" if company_name else ""
        
        prompt = f"""Erstelle eine personalisierte Outreach-Nachricht für {recipient}{company}.

Psychologisches Profil:
- DISC-Typ: {disc.primary_type} ({disc.archetype})
- Kommunikationsstil: {style}
- Tonalität: {tone}
- Inhaltsfokus: {content_focus}
- Persuasion-Ansatz: {persuasion_approach}
- RIASEC: {riasec.holland_code}
- Primäres Persuasion-Prinzip: {persuasion.primary}

Produkt-Kategorie: {product_category}

Erstelle eine Nachricht, die:
1. Den Kommunikationsstil des Empfängers respektiert
2. Die richtige Tonalität trifft
3. Auf die beruflichen Interessen eingeht
4. Das primäre Persuasion-Prinzip nutzt

Gib Betreffzeile, Nachrichtentext und CTA als JSON zurück."""
        
        response = self.llm_client.call(prompt, system_prompt, temperature=0.7, max_tokens=1000)
        
        if response['success']:
            return self.llm_client.parse_json_response(response)
        
        return None
    
    def _fallback_subject(self, style: str, product_category: str) -> str:
        """Fallback-Betreffzeile"""
        if 'Direkt' in style:
            return f"{product_category}: Konkrete Ergebnisse für Ihr Team"
        elif 'Enthusiastisch' in style:
            return f"Spannende {product_category}-Innovation für Sie!"
        elif 'Unterstützend' in style:
            return f"Wie wir Ihr Team mit {product_category} unterstützen können"
        else:
            return f"{product_category}-Lösung: Qualität und Zuverlässigkeit"
    
    def _fallback_message(self, style: str, tone: str, content_focus: str,
                         product_category: str, full_name: Optional[str]) -> str:
        """Fallback-Nachricht"""
        greeting = f"Hallo {full_name}," if full_name else "Hallo,"
        
        if 'Direkt' in style:
            body = f"""

ich habe gesehen, dass Sie im Bereich {product_category} tätig sind. Wir haben eine Lösung entwickelt, die konkrete Ergebnisse liefert: {content_focus}.

Kurz und knapp: Unsere Kunden sehen durchschnittlich 30% Effizienzsteigerung in den ersten 3 Monaten.

Interesse an einem 15-minütigen Call?"""
        
        elif 'Enthusiastisch' in style:
            body = f"""

ich bin begeistert von Ihrem Profil! Wir arbeiten an innovativen {product_category}-Lösungen, die perfekt zu Ihren Interessen passen.

Was uns auszeichnet: {content_focus}. Unsere Community liebt die Ergebnisse!

Lust auf einen Austausch?"""
        
        elif 'Unterstützend' in style:
            body = f"""

ich würde gerne mit Ihnen über {product_category} sprechen. Wir unterstützen Teams dabei, ihre Ziele zu erreichen.

Unser Fokus: {content_focus}. Wir arbeiten partnerschaftlich und langfristig.

Hätten Sie Zeit für ein unverbindliches Gespräch?"""
        
        else:
            body = f"""

ich möchte Sie auf unsere {product_category}-Lösung aufmerksam machen. Wir legen Wert auf Qualität und Zuverlässigkeit.

Details: {content_focus}. Alle Prozesse sind zertifiziert und dokumentiert.

Interesse an weiteren Informationen?"""
        
        return greeting + body
    
    def _fallback_cta(self, style: str) -> str:
        """Fallback-Call-to-Action"""
        if 'Direkt' in style:
            return "Buchen Sie jetzt einen 15-Minuten-Call: [Link]"
        elif 'Enthusiastisch' in style:
            return "Lassen Sie uns connecten! [Link zum Kalender]"
        elif 'Unterstützend' in style:
            return "Ich freue mich auf Ihre Rückmeldung: [E-Mail]"
        else:
            return "Fordern Sie detaillierte Informationen an: [Link]"

