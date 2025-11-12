#!/bin/bash
# PCBF 2.1 CSV Validation UI - Health Check Script
# Kann als Cronjob verwendet werden

PORT=8002
LOG_FILE="/home/ubuntu/pcbf_framework/logs/healthcheck.log"
MAX_RESTARTS=3
RESTART_COUNT_FILE="/tmp/pcbf_restart_count"

# Logging-Funktion
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Restart-Counter initialisieren
if [ ! -f "$RESTART_COUNT_FILE" ]; then
    echo "0" > "$RESTART_COUNT_FILE"
fi

RESTART_COUNT=$(cat "$RESTART_COUNT_FILE")

# Health-Check
if curl -s --max-time 5 http://localhost:$PORT/ > /dev/null 2>&1; then
    log "✅ Health check OK"
    # Reset counter bei Erfolg
    echo "0" > "$RESTART_COUNT_FILE"
    exit 0
else
    log "❌ Health check FAILED - Server antwortet nicht"
    
    # Prüfe Restart-Limit
    if [ "$RESTART_COUNT" -ge "$MAX_RESTARTS" ]; then
        log "⚠️  Max. Restarts ($MAX_RESTARTS) erreicht - keine automatische Wiederherstellung"
        exit 1
    fi
    
    # Inkrementiere Counter
    RESTART_COUNT=$((RESTART_COUNT + 1))
    echo "$RESTART_COUNT" > "$RESTART_COUNT_FILE"
    
    log "🔄 Versuche Neustart ($RESTART_COUNT/$MAX_RESTARTS)..."
    
    # Versuche Neustart
    if systemctl is-active --quiet pcbf-csv-ui 2>/dev/null; then
        sudo systemctl restart pcbf-csv-ui
        log "Systemd-Service neu gestartet"
    else
        pkill -f "validation_ui_csv.py" 2>/dev/null
        sleep 2
        cd /home/ubuntu/pcbf_framework
        nohup python3 validation_ui_csv.py > logs/service.log 2>&1 &
        log "Manuell neu gestartet"
    fi
    
    # Warte und prüfe erneut
    sleep 5
    if curl -s --max-time 5 http://localhost:$PORT/ > /dev/null 2>&1; then
        log "✅ Neustart erfolgreich"
        exit 0
    else
        log "❌ Neustart fehlgeschlagen"
        exit 1
    fi
fi

