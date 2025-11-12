"""
PCBF 2.1 Framework - Validation UI mit CSV-Upload
Erweiterte Web-UI für CSV-Upload und Batch-Analyse
"""
import logging
import json
import time
from datetime import datetime
from typing import List, Dict
from io import BytesIO

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from csv_processor import CSVProcessor, extract_model_data, export_model_to_csv
from utils import setup_logging

# Logging konfigurieren
setup_logging()
logger = logging.getLogger(__name__)

# FastAPI App
app = FastAPI(
    title="PCBF 2.1 CSV Validation UI",
    version="2.1.2",
    description="CSV-Upload und Batch-Analyse mit Modell-Gruppierung"
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
csv_processor = CSVProcessor()

# Speicher für Analyse-Ergebnisse
analysis_results = {}


@app.get("/", response_class=HTMLResponse)
async def root():
    """Hauptseite mit CSV-Upload-Interface"""
    return HTML_TEMPLATE


@app.post("/api/upload-csv")
async def upload_csv(
    file: UploadFile = File(...)
):
    """
    Lädt CSV hoch und führt Batch-Analyse durch.
    
    Args:
        file: CSV-Datei
        target_keywords: Kommagetrennte Keywords
        product_category: Produkt-Kategorie
        
    Returns:
        Analyse-Ergebnisse gruppiert nach Modellen
    """
    try:
        # CSV lesen
        contents = await file.read()
        csv_content = contents.decode('utf-8')
        
        logger.info(f"CSV hochgeladen: {file.filename}")
        
        # Profile extrahieren
        profiles = csv_processor.parse_csv(csv_content)
        
        if not profiles:
            raise HTTPException(status_code=400, detail="Keine Profile in CSV gefunden")
        
        logger.info(f"{len(profiles)} Profile extrahiert")
        
        # Batch-Analyse (ohne Keywords und Kategorie)
        results = csv_processor.analyze_batch(
            profiles=profiles,
            target_keywords=[],
            product_category='Software'
        )
        
        # Ergebnisse speichern
        analysis_id = str(int(time.time()))
        analysis_results[analysis_id] = results
        
        # Nach Modellen gruppieren
        disc_data = extract_model_data(results, 'disc')
        neo_data = extract_model_data(results, 'neo')
        persuasion_data = extract_model_data(results, 'persuasion')
        riasec_data = extract_model_data(results, 'riasec')
        
        logger.info(f"Analyse abgeschlossen: {len(results)} Profile")
        
        return {
            'success': True,
            'analysis_id': analysis_id,
            'total_profiles': len(results),
            'models': {
                'disc': disc_data[:10],  # Erste 10 für Vorschau
                'neo': neo_data[:10],
                'persuasion': persuasion_data[:10],
                'riasec': riasec_data[:10]
            },
            'summary': {
                'disc_count': len(disc_data),
                'neo_count': len(neo_data),
                'persuasion_count': len(persuasion_data),
                'riasec_count': len(riasec_data)
            }
        }
        
    except Exception as e:
        logger.error(f"Fehler bei CSV-Upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export/{analysis_id}/{model}")
async def export_model(analysis_id: str, model: str):
    """
    Exportiert Modell-Daten als CSV.
    
    Args:
        analysis_id: Analyse-ID
        model: Modell-Name (disc/neo/persuasion/riasec)
        
    Returns:
        CSV-Datei
    """
    try:
        if analysis_id not in analysis_results:
            raise HTTPException(status_code=404, detail="Analyse nicht gefunden")
        
        results = analysis_results[analysis_id]
        model_data = extract_model_data(results, model)
        
        if not model_data:
            raise HTTPException(status_code=404, detail="Keine Daten für Modell")
        
        # CSV erstellen
        output = BytesIO()
        
        import csv
        fieldnames = model_data[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(model_data)
        
        output.seek(0)
        
        filename = f"pcbf_{model}_{analysis_id}.csv"
        
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler bei Export: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/results/{analysis_id}")
async def get_results(analysis_id: str):
    """Gibt vollständige Ergebnisse zurück"""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analyse nicht gefunden")
    
    results = analysis_results[analysis_id]
    
    return {
        'success': True,
        'analysis_id': analysis_id,
        'total_profiles': len(results),
        'models': {
            'disc': extract_model_data(results, 'disc'),
            'neo': extract_model_data(results, 'neo'),
            'persuasion': extract_model_data(results, 'persuasion'),
            'riasec': extract_model_data(results, 'riasec')
        }
    }


# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PCBF 2.1 CSV Validation UI</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1600px;
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
        
        .upload-section {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 10px;
            padding: 60px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            background: #f8f9fa;
        }
        
        .upload-area:hover {
            border-color: #764ba2;
            background: #f0f0ff;
        }
        
        .upload-area.dragover {
            border-color: #764ba2;
            background: #e8e8ff;
        }
        
        .upload-icon {
            font-size: 64px;
            margin-bottom: 20px;
        }
        
        .upload-text {
            font-size: 18px;
            color: #333;
            margin-bottom: 10px;
        }
        
        .upload-hint {
            font-size: 14px;
            color: #666;
        }
        
        .form-group {
            margin: 20px 0;
        }
        
        .form-group label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
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
            margin-top: 20px;
            transition: transform 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }
        
        .loading.show {
            display: block;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .results-section {
            display: none;
        }
        
        .results-section.show {
            display: block;
        }
        
        .model-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .tab {
            background: white;
            padding: 15px 30px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .tab:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        
        .tab.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .tab-title {
            font-weight: 600;
            font-size: 16px;
            margin-bottom: 5px;
        }
        
        .tab-count {
            font-size: 24px;
            font-weight: bold;
        }
        
        .model-content {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            display: none;
        }
        
        .model-content.active {
            display: block;
        }
        
        .export-btn {
            background: #28a745;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            margin-bottom: 20px;
        }
        
        .export-btn:hover {
            background: #218838;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        
        td {
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .reasoning-cell {
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            cursor: help;
        }
        
        .reasoning-cell:hover {
            white-space: normal;
            overflow: visible;
        }
        
        .summary-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .summary-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .summary-value {
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
        }
        
        .summary-label {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 PCBF 2.1 CSV Validation UI</h1>
            <p>CSV-Upload für Batch-Analyse mit automatischer Modell-Gruppierung</p>
        </div>
        
        <!-- Upload Section -->
        <div class="upload-section" id="uploadSection">
            <h2 style="margin-bottom: 20px;">CSV-Datei hochladen</h2>
            
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-area" id="uploadArea">
                    <div class="upload-icon">📁</div>
                    <div class="upload-text">CSV-Datei hier ablegen oder klicken zum Auswählen</div>
                    <div class="upload-hint">Unterstützt: raw-data-pcbf.csv Format</div>
                    <input type="file" id="fileInput" accept=".csv" style="display: none;">
                </div>
                
                <div id="fileName" style="margin-top: 15px; color: #667eea; font-weight: 600;"></div>
                
                <button type="submit" class="btn" id="analyzeBtn" style="margin-top: 20px;">
                    🚀 Analysieren
                </button>
            </form>
        </div>
        
        <!-- Loading -->
        <div class="loading" id="loadingSection">
            <div class="spinner"></div>
            <p style="color: white; font-size: 18px;">Analyse läuft...</p>
            <p style="color: white; font-size: 14px; margin-top: 10px;">Dies kann einige Minuten dauern</p>
        </div>
        
        <!-- Results Section -->
        <div class="results-section" id="resultsSection">
            <!-- Summary -->
            <div class="summary-card">
                <h3>📈 Analyse-Zusammenfassung</h3>
                <div class="summary-grid">
                    <div class="summary-item">
                        <div class="summary-value" id="totalProfiles">0</div>
                        <div class="summary-label">Profile analysiert</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value" id="discCount">0</div>
                        <div class="summary-label">DISC-Profile</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value" id="neoCount">0</div>
                        <div class="summary-label">NEO-Profile</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value" id="persuasionCount">0</div>
                        <div class="summary-label">Persuasion-Profile</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value" id="riasecCount">0</div>
                        <div class="summary-label">RIASEC-Profile</div>
                    </div>
                </div>
            </div>
            
            <!-- Model Tabs -->
            <div class="model-tabs">
                <div class="tab active" data-model="disc">
                    <div class="tab-title">DISC-Modell</div>
                    <div class="tab-count" id="discTabCount">0</div>
                </div>
                <div class="tab" data-model="neo">
                    <div class="tab-title">NEO-Modell (Big Five)</div>
                    <div class="tab-count" id="neoTabCount">0</div>
                </div>
                <div class="tab" data-model="persuasion">
                    <div class="tab-title">Cialdini-Modell</div>
                    <div class="tab-count" id="persuasionTabCount">0</div>
                </div>
                <div class="tab" data-model="riasec">
                    <div class="tab-title">RIASEC-Modell</div>
                    <div class="tab-count" id="riasecTabCount">0</div>
                </div>
            </div>
            
            <!-- Model Contents -->
            <div class="model-content active" id="discContent">
                <button class="export-btn" onclick="exportModel('disc')">📥 DISC als CSV exportieren</button>
                <div id="discTable"></div>
            </div>
            
            <div class="model-content" id="neoContent">
                <button class="export-btn" onclick="exportModel('neo')">📥 NEO als CSV exportieren</button>
                <div id="neoTable"></div>
            </div>
            
            <div class="model-content" id="persuasionContent">
                <button class="export-btn" onclick="exportModel('persuasion')">📥 Persuasion als CSV exportieren</button>
                <div id="persuasionTable"></div>
            </div>
            
            <div class="model-content" id="riasecContent">
                <button class="export-btn" onclick="exportModel('riasec')">📥 RIASEC als CSV exportieren</button>
                <div id="riasecTable"></div>
            </div>
        </div>
    </div>
    
    <script>
        let currentAnalysisId = null;
        let selectedFile = null;
        
        // Upload Area
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const fileName = document.getElementById('fileName');
        
        uploadArea.addEventListener('click', () => fileInput.click());
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });
        
        function handleFile(file) {
            if (!file.name.endsWith('.csv')) {
                alert('Bitte nur CSV-Dateien hochladen');
                return;
            }
            selectedFile = file;
            fileName.textContent = `✅ Datei ausgewählt: ${file.name}`;
        }
        
        // Form Submit
        document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (!selectedFile) {
                alert('Bitte erst eine CSV-Datei auswählen');
                return;
            }
            
            // UI-Zustand
            document.getElementById('uploadSection').style.display = 'none';
            document.getElementById('loadingSection').classList.add('show');
            
            // FormData erstellen
            const formData = new FormData();
            formData.append('file', selectedFile);
            
            try {
                const response = await fetch('/api/upload-csv', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentAnalysisId = data.analysis_id;
                    displayResults(data);
                } else {
                    alert('Fehler: ' + (data.detail || 'Unbekannter Fehler'));
                    resetUI();
                }
            } catch (error) {
                alert('Fehler bei der Analyse: ' + error.message);
                resetUI();
            }
        });
        
        function resetUI() {
            document.getElementById('loadingSection').classList.remove('show');
            document.getElementById('uploadSection').style.display = 'block';
        }
        
        function displayResults(data) {
            document.getElementById('loadingSection').classList.remove('show');
            document.getElementById('resultsSection').classList.add('show');
            
            // Summary
            document.getElementById('totalProfiles').textContent = data.total_profiles;
            document.getElementById('discCount').textContent = data.summary.disc_count;
            document.getElementById('neoCount').textContent = data.summary.neo_count;
            document.getElementById('persuasionCount').textContent = data.summary.persuasion_count;
            document.getElementById('riasecCount').textContent = data.summary.riasec_count;
            
            // Tab Counts
            document.getElementById('discTabCount').textContent = data.summary.disc_count;
            document.getElementById('neoTabCount').textContent = data.summary.neo_count;
            document.getElementById('persuasionTabCount').textContent = data.summary.persuasion_count;
            document.getElementById('riasecTabCount').textContent = data.summary.riasec_count;
            
            // Tables
            renderTable('disc', data.models.disc);
            renderTable('neo', data.models.neo);
            renderTable('persuasion', data.models.persuasion);
            renderTable('riasec', data.models.riasec);
        }
        
        function renderTable(model, data) {
            const container = document.getElementById(`${model}Table`);
            
            if (!data || data.length === 0) {
                container.innerHTML = '<p>Keine Daten verfügbar</p>';
                return;
            }
            
            const keys = Object.keys(data[0]);
            
            let html = '<table><thead><tr>';
            keys.forEach(key => {
                html += `<th>${key.replace(/_/g, ' ').toUpperCase()}</th>`;
            });
            html += '</tr></thead><tbody>';
            
            data.forEach(row => {
                html += '<tr>';
                keys.forEach(key => {
                    let value = row[key];
                    if (typeof value === 'number') {
                        value = value.toFixed(2);
                    }
                    const cellClass = key === 'reasoning' ? 'reasoning-cell' : '';
                    html += `<td class="${cellClass}" title="${value}">${value}</td>`;
                });
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            container.innerHTML = html;
        }
        
        // Tab Switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const model = tab.dataset.model;
                
                // Tabs
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Contents
                document.querySelectorAll('.model-content').forEach(c => c.classList.remove('active'));
                document.getElementById(`${model}Content`).classList.add('active');
            });
        });
        
        // Export
        async function exportModel(model) {
            if (!currentAnalysisId) {
                alert('Keine Analyse verfügbar');
                return;
            }
            
            window.location.href = `/api/export/${currentAnalysisId}/${model}`;
        }
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starte PCBF 2.1 CSV Validation UI")
    logger.info("Server läuft auf http://localhost:8002")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )

