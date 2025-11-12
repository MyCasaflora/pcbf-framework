"""
PCBF 2.1 Framework - FastAPI Application
RESTful API für psychologische Profilanalyse
"""
import time
import logging
from typing import List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import config
from models import AnalysisRequest, AnalysisResponse, ProfileAnalysisResult
from analyzer import ProfileAnalyzer
from utils import setup_logging

# Logging konfigurieren
setup_logging()
logger = logging.getLogger(__name__)

# FastAPI App initialisieren
app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description=config.API_DESCRIPTION
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globaler Analyzer
analyzer = ProfileAnalyzer()


@app.get("/")
async def root():
    """Root-Endpoint mit API-Informationen"""
    return {
        "name": config.API_TITLE,
        "version": config.API_VERSION,
        "status": "running",
        "endpoints": {
            "analyze": "/analyze",
            "health": "/health",
            "logs": "/logs"
        }
    }


@app.get("/health")
async def health_check():
    """Health-Check-Endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_profiles(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Hauptendpoint für Profilanalyse.
    
    Analysiert ein oder mehrere Social-Media-Profile und gibt
    vollständige psychologische Profile mit Purchase Intent zurück.
    
    Args:
        request: AnalysisRequest mit Profilen und Parametern
        
    Returns:
        AnalysisResponse mit Analyse-Ergebnissen
    """
    start_time = time.time()
    
    logger.info(f"Neue Analyse-Anfrage: {len(request.profiles)} Profile")
    
    try:
        # Validierung
        if not request.profiles or len(request.profiles) == 0:
            raise HTTPException(status_code=400, detail="Keine Profile angegeben")
        
        if len(request.profiles) > 100:
            raise HTTPException(status_code=400, detail="Maximal 100 Profile pro Request")
        
        # Batch-Analyse
        results = analyzer.analyze_batch(
            profiles=request.profiles,
            target_keywords=request.target_keywords or [],
            product_category=request.product_category or "Software",
            include_enneagram=request.include_enneagram,
            max_workers=5
        )
        
        # Fehler sammeln
        errors = []
        successful_results = []
        
        for result in results:
            if result:
                successful_results.append(result)
        
        # Gesamt-Verarbeitungszeit
        total_time = time.time() - start_time
        
        logger.info(f"Analyse abgeschlossen: {len(successful_results)} erfolgreich in {total_time:.2f}s")
        
        # Logs im Hintergrund speichern
        background_tasks.add_task(save_logs_to_file, analyzer.get_agent_logs())
        
        return AnalysisResponse(
            success=True,
            results=successful_results,
            total_profiles=len(request.profiles),
            total_processing_time_seconds=total_time,
            errors=errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler bei Analyse: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Interner Fehler: {str(e)}")


@app.get("/logs")
async def get_logs():
    """
    Gibt Agent-Logs zurück (für Debugging).
    
    Returns:
        Liste von Agent-Log-Einträgen
    """
    logs = analyzer.get_agent_logs()
    return {
        "total_logs": len(logs),
        "logs": logs[-100:]  # Letzte 100 Logs
    }


@app.delete("/logs")
async def clear_logs():
    """
    Löscht Agent-Logs.
    
    Returns:
        Bestätigung
    """
    analyzer.clear_logs()
    return {"message": "Logs gelöscht"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Globaler Exception-Handler"""
    logger.error(f"Unbehandelter Fehler: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "detail": "Ein unerwarteter Fehler ist aufgetreten"
        }
    )


def save_logs_to_file(logs: List[dict]):
    """Speichert Logs in Datei (Background-Task)"""
    try:
        import json
        from datetime import datetime
        
        log_file = f"/home/ubuntu/pcbf_framework/logs/agent_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Agent-Logs gespeichert: {log_file}")
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Logs: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starte {config.API_TITLE} v{config.API_VERSION}")
    logger.info(f"Server läuft auf http://{config.API_HOST}:{config.API_PORT}")
    
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        log_level="info"
    )

