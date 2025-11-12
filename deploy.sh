#!/bin/bash
# PCBF 2.1 CSV Validation UI - Deployment Script

set -e  # Exit bei Fehler

echo "🚀 PCBF 2.1 CSV Validation UI - Deployment"
echo "=========================================="
echo ""

# Farben für Output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Funktionen
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. Verzeichnis prüfen
echo "1. Prüfe Arbeitsverzeichnis..."
if [ ! -f "validation_ui_csv.py" ]; then
    print_error "validation_ui_csv.py nicht gefunden!"
    echo "Bitte führe das Script aus /home/ubuntu/pcbf_framework/ aus"
    exit 1
fi
print_success "Arbeitsverzeichnis OK"
echo ""

# 2. Dependencies prüfen
echo "2. Prüfe Python-Dependencies..."
if ! python3 -c "import fastapi, uvicorn, pydantic" 2>/dev/null; then
    print_warning "Dependencies fehlen, installiere..."
    pip3 install -r requirements.txt
fi
print_success "Dependencies OK"
echo ""

# 3. Logs-Verzeichnis erstellen
echo "3. Erstelle Logs-Verzeichnis..."
mkdir -p logs
print_success "Logs-Verzeichnis erstellt"
echo ""

# 4. Alte Prozesse stoppen
echo "4. Stoppe alte Prozesse..."
pkill -f "validation_ui_csv.py" 2>/dev/null || true
sleep 2
print_success "Alte Prozesse gestoppt"
echo ""

# 5. Service-Datei installieren
echo "5. Installiere Systemd-Service..."
if [ -f "pcbf-csv-ui.service" ]; then
    sudo cp pcbf-csv-ui.service /etc/systemd/system/
    sudo systemctl daemon-reload
    print_success "Service-Datei installiert"
else
    print_warning "Service-Datei nicht gefunden, überspringe..."
fi
echo ""

# 6. Service aktivieren und starten
echo "6. Aktiviere und starte Service..."
if [ -f "/etc/systemd/system/pcbf-csv-ui.service" ]; then
    sudo systemctl enable pcbf-csv-ui
    sudo systemctl restart pcbf-csv-ui
    sleep 3
    
    # Status prüfen
    if sudo systemctl is-active --quiet pcbf-csv-ui; then
        print_success "Service läuft"
    else
        print_error "Service konnte nicht gestartet werden"
        echo "Prüfe Logs mit: sudo journalctl -u pcbf-csv-ui -n 50"
        exit 1
    fi
else
    print_warning "Systemd-Service nicht installiert, starte manuell..."
    nohup python3 validation_ui_csv.py > logs/service.log 2>&1 &
    sleep 3
    print_success "Manuell gestartet"
fi
echo ""

# 7. Health-Check
echo "7. Führe Health-Check durch..."
sleep 2
if curl -s http://localhost:8002/ > /dev/null; then
    print_success "Server antwortet auf Port 8002"
else
    print_error "Server antwortet nicht!"
    exit 1
fi
echo ""

# 8. Zusammenfassung
echo "=========================================="
echo -e "${GREEN}✅ Deployment erfolgreich!${NC}"
echo ""
echo "📊 Service-Informationen:"
echo "  - Name: pcbf-csv-ui"
echo "  - Port: 8002"
echo "  - Logs: /home/ubuntu/pcbf_framework/logs/"
echo ""
echo "🔧 Nützliche Befehle:"
echo "  - Status: sudo systemctl status pcbf-csv-ui"
echo "  - Logs: sudo journalctl -u pcbf-csv-ui -f"
echo "  - Neustart: sudo systemctl restart pcbf-csv-ui"
echo "  - Stoppen: sudo systemctl stop pcbf-csv-ui"
echo ""
echo "🌐 Zugriff:"
echo "  - Lokal: http://localhost:8002"
echo "  - Öffentlich: https://8002-i10gec5oawwi59ab9yrf5-2da1d099.manusvm.computer"
echo ""

