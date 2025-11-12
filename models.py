"""
PCBF 2.1 Framework - Datenmodelle
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class ProfileInput(BaseModel):
    """Input-Modell für ein einzelnes Social-Media-Profil"""
    id: str = Field(..., description="Eindeutige Profil-ID")
    email: Optional[str] = Field(None, description="E-Mail-Adresse")
    phone: Optional[str] = Field(None, description="Telefonnummer")
    platform_name: str = Field(..., description="Plattform (LinkedIn, Instagram, etc.)")
    nickname: Optional[str] = Field(None, description="Benutzername/Nickname")
    full_name: Optional[str] = Field(None, description="Vollständiger Name")
    followers: Optional[int] = Field(None, description="Anzahl Follower")
    following: Optional[int] = Field(None, description="Anzahl Following")
    posts: Optional[int] = Field(None, description="Anzahl Posts")
    likes: Optional[int] = Field(None, description="Anzahl Likes")
    region: Optional[str] = Field(None, description="Region/Land")
    bio: Optional[str] = Field(None, description="Profilbeschreibung/Bio")
    verified: Optional[bool] = Field(False, description="Verifizierter Account")
    business_account: Optional[bool] = Field(False, description="Business Account")
    private_account: Optional[bool] = Field(False, description="Privater Account")
    avatar_url: Optional[str] = Field(None, description="Avatar-URL")
    bio_link: Optional[str] = Field(None, description="Link in Bio")
    categories: Optional[str] = Field(None, description="Kategorien/Interessen")
    signup_date: Optional[str] = Field(None, description="Registrierungsdatum")
    last_post: Optional[str] = Field(None, description="Letzter Post (oft N/A)")

    @validator('followers', 'following', 'posts', 'likes', pre=True)
    def parse_int_or_none(cls, v):
        """Konvertiert String-Werte zu Int oder None"""
        if v is None or v == 'N/A' or v == '' or v == 'NULL':
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None


class AnalysisRequest(BaseModel):
    """Request-Modell für Analyse-API"""
    profiles: List[ProfileInput] = Field(..., description="Liste der zu analysierenden Profile")
    target_keywords: Optional[List[str]] = Field(
        default=[], 
        description="Ziel-Keywords für Keywords-Match-Score"
    )
    product_category: Optional[str] = Field(
        default="Software", 
        description="Produkt-Kategorie für Purchase Intent"
    )
    include_enneagram: bool = Field(
        default=False, 
        description="Enneagram-Analyse einbeziehen (optional, niedrige Confidence)"
    )


class BioQualityResult(BaseModel):
    """Ergebnis der Bio-Qualitäts-Bewertung"""
    score: float = Field(..., ge=0, le=100, description="Bio-Qualitäts-Score (0-100)")
    word_count: int = Field(..., description="Anzahl Wörter in Bio")
    has_job_title: bool = Field(..., description="Job-Titel vorhanden")
    has_company: bool = Field(..., description="Unternehmensname vorhanden")
    has_structure: bool = Field(..., description="Strukturierte Bio (Absätze, Emojis)")
    emoji_count: int = Field(..., description="Anzahl Emojis")
    category: str = Field(..., description="Qualitätskategorie (high/medium/low)")


class DISCResult(BaseModel):
    """Ergebnis der DISC-Analyse"""
    primary_type: str = Field(..., description="Primärer DISC-Typ (D/I/S/C)")
    secondary_type: Optional[str] = Field(None, description="Sekundärer DISC-Typ")
    subtype: str = Field(..., description="DISC-Subtyp (z.B. Di, DC)")
    archetype: str = Field(..., description="DISC-Archetyp (z.B. Captain, Motivator)")
    scores: Dict[str, float] = Field(..., description="DISC-Scores für alle Typen")
    confidence: float = Field(..., ge=0, le=100, description="Confidence-Level (0-100)")
    reasoning: Optional[str] = Field(None, description="Begründung der Klassifikation")


class NEOResult(BaseModel):
    """Ergebnis der NEO/OCEAN-Analyse"""
    dimensions: Dict[str, float] = Field(
        ..., 
        description="OCEAN-Dimensionen (openness, conscientiousness, extraversion, agreeableness, neuroticism)"
    )
    confidence: float = Field(..., ge=0, le=100, description="Confidence-Level (0-100)")
    reasoning: Optional[str] = Field(None, description="Begründung der Bewertung")


class RIASECResult(BaseModel):
    """Ergebnis der RIASEC-Analyse"""
    holland_code: str = Field(..., description="Holland-Code (z.B. IEC, SAE)")
    scores: Dict[str, float] = Field(..., description="RIASEC-Scores für alle Typen")
    primary: str = Field(..., description="Primärer RIASEC-Typ")
    confidence: float = Field(..., ge=0, le=100, description="Confidence-Level (0-100)")
    source: str = Field(..., description="Datenquelle (categories/bio/mixed)")
    reasoning: Optional[str] = Field(None, description="Begründung der Klassifikation")


class PersuasionResult(BaseModel):
    """Ergebnis der Persuasion-Analyse"""
    scores: Dict[str, float] = Field(
        ..., 
        description="Cialdini-Prinzipien (authority, social_proof, scarcity, reciprocity, consistency, liking, unity)"
    )
    primary: str = Field(..., description="Primäres Persuasion-Prinzip")
    confidence: float = Field(..., ge=0, le=100, description="Confidence-Level (0-100)")
    reasoning: Optional[str] = Field(None, description="Begründung der Bewertung")


class EnneagramResult(BaseModel):
    """Ergebnis der Enneagram-Analyse (optional)"""
    type: int = Field(..., ge=1, le=9, description="Enneagram-Typ (1-9)")
    wing: Optional[int] = Field(None, description="Enneagram-Wing")
    confidence: float = Field(..., ge=0, le=100, description="Confidence-Level (0-100)")
    reasoning: Optional[str] = Field(None, description="Begründung der Klassifikation")


class PurchaseIntentResult(BaseModel):
    """Ergebnis der Purchase Intent-Berechnung"""
    score: float = Field(..., ge=0, le=100, description="Purchase Intent Score (0-100)")
    category: str = Field(..., description="Intent-Kategorie (very_high/high/medium/low)")
    contributing_factors: Dict[str, float] = Field(
        ..., 
        description="Beitragende Faktoren mit Gewichtung"
    )
    reasoning: Optional[str] = Field(None, description="Begründung des Scores")


class CommunicationStrategy(BaseModel):
    """Personalisierte Kommunikationsstrategie"""
    style: str = Field(..., description="Kommunikationsstil (basierend auf DISC)")
    tone: str = Field(..., description="Tonalität (basierend auf NEO)")
    content_focus: str = Field(..., description="Inhaltsfokus (basierend auf RIASEC)")
    persuasion_approach: str = Field(..., description="Persuasion-Ansatz (basierend auf Cialdini)")
    subject_line: str = Field(..., description="Personalisierte Betreffzeile")
    message_body: str = Field(..., description="Personalisierter Nachrichtentext")
    call_to_action: str = Field(..., description="Call-to-Action")


class WarningMessage(BaseModel):
    """Warnmeldung bei niedriger Datenqualität"""
    level: str = Field(..., description="Warning-Level (info/warning/critical)")
    message: str = Field(..., description="Warnmeldung")
    affected_modules: List[str] = Field(..., description="Betroffene Analyse-Module")


class ProfileAnalysisResult(BaseModel):
    """Vollständiges Analyse-Ergebnis für ein Profil"""
    profile_id: str = Field(..., description="Profil-ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analyse-Zeitstempel")
    
    # Datenqualität
    bio_quality: BioQualityResult
    keywords_match_score: float = Field(..., ge=0, le=100, description="Keywords-Match-Score")
    overall_confidence: float = Field(..., ge=0, le=100, description="Gesamt-Confidence")
    
    # Analyse-Ergebnisse
    disc: DISCResult
    neo: NEOResult
    riasec: RIASECResult
    persuasion: PersuasionResult
    enneagram: Optional[EnneagramResult] = None
    
    # Purchase Intent & Strategie
    purchase_intent: PurchaseIntentResult
    communication_strategy: CommunicationStrategy
    
    # Warnungen
    warnings: List[WarningMessage] = Field(default=[], description="Warnmeldungen")
    
    # Metadaten
    processing_time_seconds: Optional[float] = Field(None, description="Verarbeitungszeit in Sekunden")
    api_calls_made: Optional[int] = Field(None, description="Anzahl API-Aufrufe")
    
    # Kompakter Profil-String für externe Tools
    profile_string: Optional[str] = Field(None, description="Kompakter Profil-String (z.B. DISC:D | NEO:C=0.92,E=0.88 | RIASEC:IEC | PI:82)")


class AnalysisResponse(BaseModel):
    """Response-Modell für Analyse-API"""
    success: bool = Field(..., description="Erfolgreicher Request")
    results: List[ProfileAnalysisResult] = Field(..., description="Analyse-Ergebnisse")
    total_profiles: int = Field(..., description="Anzahl analysierter Profile")
    total_processing_time_seconds: float = Field(..., description="Gesamt-Verarbeitungszeit")
    errors: List[Dict[str, str]] = Field(default=[], description="Fehler bei der Verarbeitung")


class AgentLogEntry(BaseModel):
    """Log-Eintrag für Agent-Aktivität"""
    agent_name: str = Field(..., description="Name des Agenten")
    profile_id: str = Field(..., description="Profil-ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Zeitstempel")
    input_data: Dict[str, Any] = Field(..., description="Input-Daten für Agent")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Output-Daten vom Agent")
    api_call_latency_ms: Optional[float] = Field(None, description="API-Aufruf-Latenz in ms")
    success: bool = Field(..., description="Erfolgreicher Agent-Aufruf")
    error_message: Optional[str] = Field(None, description="Fehlermeldung bei Fehler")
    fallback_used: bool = Field(default=False, description="Fallback-Logik verwendet")

