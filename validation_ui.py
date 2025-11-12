"""
PCBF 2.1 Framework - Validation Web UI
Web-Interface für manuelle Validierung von Analyse-Ergebnissen
"""
import logging
import json
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from models import ProfileInput, AnalysisRequest
from analyzer import ProfileAnalyzer
from validation_protocol import ValidationProtocol
from utils import setup_logging

# Logging konfigurieren
setup_logging()
logger = logging.getLogger(__name__)

# FastAPI App
app = FastAPI(
    title="PCBF 2.1 Validation UI",
    version="2.1.1",
    description="Web-Interface für Profil-Validierung"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globale Instanzen
analyzer = ProfileAnalyzer()
validator = ValidationProtocol()

# Speicher für Validierungs-Historie
validation_history = []


@app.get("/", response_class=HTMLResponse)
async def root():
    """Hauptseite mit Validierungs-Interface"""
    return HTML_TEMPLATE


@app.post("/api/validate")
async def validate_profile(request: Request):
    """
    Validiert ein Profil.
    
    Request Body:
    {
        "profile": {...},
        "target_keywords": [...],
        "product_category": "..."
    }
    """
    try:
        data = await request.json()
        
        # Profil erstellen
        profile_data = data.get('profile', {})
        profile = ProfileInput(**profile_data)
        
        # Analyse durchführen
        logger.info(f"Starte Analyse für Profil {profile.id}")
        result = analyzer.analyze_profile(
            profile=profile,
            target_keywords=data.get('target_keywords', []),
            product_category=data.get('product_category', 'Software'),
            include_enneagram=False
        )
        
        # Validierung durchführen
        logger.info(f"Starte Validierung für Profil {profile.id}")
        validation_report = validator.validate(profile, result)
        
        # In Historie speichern
        validation_history.append({
            'timestamp': datetime.now().isoformat(),
            'profile_id': profile.id,
            'status': validation_report.overall_status,
            'score': validation_report.score
        })
        
        # Response
        return {
            'success': True,
            'profile_id': profile.id,
            'analysis': {
                'profile_string': result.profile_string,
                'disc': {
                    'primary': result.disc.primary_type,
                    'archetype': result.disc.archetype,
                    'scores': result.disc.scores,
                    'confidence': result.disc.confidence
                },
                'neo': {
                    'dimensions': result.neo.dimensions,
                    'confidence': result.neo.confidence
                },
                'riasec': {
                    'holland_code': result.riasec.holland_code,
                    'scores': result.riasec.scores,
                    'confidence': result.riasec.confidence
                },
                'persuasion': {
                    'primary': result.persuasion.primary,
                    'scores': result.persuasion.scores,
                    'confidence': result.persuasion.confidence
                },
                'purchase_intent': {
                    'score': result.purchase_intent.score,
                    'category': result.purchase_intent.category
                },
                'overall_confidence': result.overall_confidence,
                'processing_time': result.processing_time_seconds
            },
            'validation': validation_report.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Fehler bei Validierung: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
async def get_history():
    """Gibt Validierungs-Historie zurück"""
    return {
        'success': True,
        'history': validation_history[-50:]  # Letzte 50
    }


@app.get("/api/stats")
async def get_stats():
    """Gibt Statistiken zurück"""
    if not validation_history:
        return {
            'success': True,
            'stats': {
                'total': 0,
                'pass': 0,
                'review': 0,
                'warning': 0,
                'fail': 0,
                'avg_score': 0
            }
        }
    
    stats = {
        'total': len(validation_history),
        'pass': sum(1 for h in validation_history if h['status'] == 'PASS'),
        'review': sum(1 for h in validation_history if h['status'] == 'REVIEW'),
        'warning': sum(1 for h in validation_history if h['status'] == 'WARNING'),
        'fail': sum(1 for h in validation_history if h['status'] == 'FAIL'),
        'avg_score': sum(h['score'] for h in validation_history) / len(validation_history)
    }
    
    return {
        'success': True,
        'stats': stats
    }


# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PCBF 2.1 Validation UI</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #667eea;
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 16px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-value {
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .stat-label {
            color: #666;
            font-size: 14px;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        .panel {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .panel h2 {
            color: #333;
            font-size: 24px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #667eea;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .form-group input,
        .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .form-group textarea {
            min-height: 120px;
            resize: vertical;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .result-section {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            display: none;
        }
        
        .result-section.show {
            display: block;
        }
        
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 15px;
        }
        
        .status-pass {
            background: #d4edda;
            color: #155724;
        }
        
        .status-review {
            background: #fff3cd;
            color: #856404;
        }
        
        .status-warning {
            background: #fff3cd;
            color: #856404;
        }
        
        .status-fail {
            background: #f8d7da;
            color: #721c24;
        }
        
        .score-display {
            font-size: 48px;
            font-weight: bold;
            color: #667eea;
            text-align: center;
            margin: 20px 0;
        }
        
        .checks-list {
            margin-top: 20px;
        }
        
        .check-item {
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 6px;
            background: white;
            border-left: 4px solid #ccc;
        }
        
        .check-item.pass {
            border-left-color: #28a745;
        }
        
        .check-item.warning {
            border-left-color: #ffc107;
        }
        
        .check-item.fail {
            border-left-color: #dc3545;
        }
        
        .check-name {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        
        .check-message {
            color: #666;
            font-size: 14px;
        }
        
        .profile-string {
            background: #2d3748;
            color: #68d391;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            overflow-x: auto;
            margin: 15px 0;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #667eea;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .analysis-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin: 20px 0;
        }
        
        .analysis-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
        }
        
        .analysis-card h4 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 16px;
        }
        
        .analysis-value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        
        .analysis-detail {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        
        @media (max-width: 1024px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .analysis-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🔍 PCBF 2.1 Validation UI</h1>
            <p>Validierung von Profil-Analysen mit automatischen Plausibilitätsprüfungen</p>
        </div>
        
        <!-- Statistiken -->
        <div class="stats" id="stats">
            <div class="stat-card">
                <div class="stat-value" id="stat-total">0</div>
                <div class="stat-label">Gesamt</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-pass">0</div>
                <div class="stat-label">✅ Pass</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-review">0</div>
                <div class="stat-label">⚠️ Review</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-fail">0</div>
                <div class="stat-label">❌ Fail</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-avg">0</div>
                <div class="stat-label">Ø Score</div>
            </div>
        </div>
        
        <!-- Hauptinhalt -->
        <div class="main-content">
            <!-- Eingabe-Panel -->
            <div class="panel">
                <h2>📝 Profil-Eingabe</h2>
                
                <form id="validationForm">
                    <div class="form-group">
                        <label for="profileId">Profil-ID *</label>
                        <input type="text" id="profileId" required placeholder="z.B. test_001">
                    </div>
                    
                    <div class="form-group">
                        <label for="fullName">Name</label>
                        <input type="text" id="fullName" placeholder="z.B. Max Mustermann">
                    </div>
                    
                    <div class="form-group">
                        <label for="bio">Bio *</label>
                        <textarea id="bio" required placeholder="CEO bei TechCorp. Leidenschaft für KI..."></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="categories">Categories</label>
                        <input type="text" id="categories" placeholder="KI • Software • Business Development">
                    </div>
                    
                    <div class="form-group">
                        <label for="targetKeywords">Target Keywords (kommagetrennt)</label>
                        <input type="text" id="targetKeywords" placeholder="KI, Software, Innovation">
                    </div>
                    
                    <div class="form-group">
                        <label for="productCategory">Produkt-Kategorie</label>
                        <input type="text" id="productCategory" value="Software">
                    </div>
                    
                    <button type="submit" class="btn" id="validateBtn">
                        🔍 Analysieren & Validieren
                    </button>
                </form>
            </div>
            
            <!-- Ergebnis-Panel -->
            <div class="panel">
                <h2>📊 Validierungs-Ergebnis</h2>
                
                <div id="loadingState" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    <p>Analyse läuft...</p>
                </div>
                
                <div id="resultSection" class="result-section">
                    <div id="statusBadge"></div>
                    <div id="scoreDisplay" class="score-display"></div>
                    
                    <div class="profile-string" id="profileString"></div>
                    
                    <div class="analysis-grid" id="analysisGrid"></div>
                    
                    <div class="checks-list" id="checksList"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Statistiken laden
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('stat-total').textContent = data.stats.total;
                    document.getElementById('stat-pass').textContent = data.stats.pass;
                    document.getElementById('stat-review').textContent = data.stats.review;
                    document.getElementById('stat-fail').textContent = data.stats.fail;
                    document.getElementById('stat-avg').textContent = data.stats.avg_score.toFixed(1);
                }
            } catch (error) {
                console.error('Fehler beim Laden der Statistiken:', error);
            }
        }
        
        // Formular-Submit
        document.getElementById('validationForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // UI-Zustand
            document.getElementById('validateBtn').disabled = true;
            document.getElementById('loadingState').style.display = 'block';
            document.getElementById('resultSection').classList.remove('show');
            
            // Daten sammeln
            const profileData = {
                profile: {
                    id: document.getElementById('profileId').value,
                    platform_name: 'Manual Input',
                    full_name: document.getElementById('fullName').value || 'Unknown',
                    bio: document.getElementById('bio').value,
                    categories: document.getElementById('categories').value || null
                },
                target_keywords: document.getElementById('targetKeywords').value
                    .split(',')
                    .map(k => k.trim())
                    .filter(k => k),
                product_category: document.getElementById('productCategory').value || 'Software'
            };
            
            try {
                const response = await fetch('/api/validate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(profileData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayResults(data);
                    loadStats();
                } else {
                    alert('Fehler: ' + (data.detail || 'Unbekannter Fehler'));
                }
            } catch (error) {
                alert('Fehler bei der Validierung: ' + error.message);
            } finally {
                document.getElementById('validateBtn').disabled = false;
                document.getElementById('loadingState').style.display = 'none';
            }
        });
        
        // Ergebnisse anzeigen
        function displayResults(data) {
            const resultSection = document.getElementById('resultSection');
            const validation = data.validation;
            const analysis = data.analysis;
            
            // Status Badge
            const statusBadge = document.getElementById('statusBadge');
            statusBadge.className = `status-badge status-${validation.overall_status.toLowerCase()}`;
            statusBadge.textContent = validation.overall_status;
            
            // Score
            document.getElementById('scoreDisplay').textContent = 
                `${validation.score.toFixed(1)}/100`;
            
            // Profil-String
            document.getElementById('profileString').textContent = analysis.profile_string;
            
            // Analyse-Grid
            const analysisGrid = document.getElementById('analysisGrid');
            analysisGrid.innerHTML = `
                <div class="analysis-card">
                    <h4>DISC</h4>
                    <div class="analysis-value">${analysis.disc.primary}</div>
                    <div class="analysis-detail">${analysis.disc.archetype} (${analysis.disc.confidence.toFixed(1)}%)</div>
                </div>
                <div class="analysis-card">
                    <h4>RIASEC</h4>
                    <div class="analysis-value">${analysis.riasec.holland_code}</div>
                    <div class="analysis-detail">Confidence: ${analysis.riasec.confidence.toFixed(1)}%</div>
                </div>
                <div class="analysis-card">
                    <h4>Persuasion</h4>
                    <div class="analysis-value">${analysis.persuasion.primary}</div>
                    <div class="analysis-detail">Confidence: ${analysis.persuasion.confidence.toFixed(1)}%</div>
                </div>
                <div class="analysis-card">
                    <h4>Purchase Intent</h4>
                    <div class="analysis-value">${analysis.purchase_intent.score.toFixed(1)}</div>
                    <div class="analysis-detail">${analysis.purchase_intent.category}</div>
                </div>
            `;
            
            // Checks-Liste
            const checksList = document.getElementById('checksList');
            checksList.innerHTML = '<h3 style="margin-bottom: 15px;">Validierungs-Checks:</h3>';
            
            validation.checks.forEach(check => {
                const checkItem = document.createElement('div');
                checkItem.className = `check-item ${check.status.toLowerCase()}`;
                checkItem.innerHTML = `
                    <div class="check-name">${check.status} - ${check.name}</div>
                    <div class="check-message">${check.message}</div>
                `;
                checksList.appendChild(checkItem);
            });
            
            // Anzeigen
            resultSection.classList.add('show');
        }
        
        // Initial Stats laden
        loadStats();
        
        // Auto-Refresh alle 30 Sekunden
        setInterval(loadStats, 30000);
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starte PCBF 2.1 Validation UI")
    logger.info("Server läuft auf http://localhost:8001")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )

