#!/bin/bash
# PCBF 2.1 CSV Validation UI - Management Script

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVICE_NAME="pcbf-csv-ui"
PORT=8002

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  PCBF 2.1 CSV Validation UI Manager${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

show_status() {
    echo -e "${BLUE}📊 Service Status${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Systemd-Service prüfen
    if systemctl is-active --quiet $SERVICE_NAME 2>/dev/null; then
        echo -e "Service: ${GREEN}✅ Läuft${NC}"
        UPTIME=$(systemctl show $SERVICE_NAME --property=ActiveEnterTimestamp --value)
        echo "Gestartet: $UPTIME"
    else
        # Manueller Prozess prüfen
        if pgrep -f "validation_ui_csv.py" > /dev/null; then
            echo -e "Service: ${YELLOW}⚠️  Läuft (manuell)${NC}"
            PID=$(pgrep -f "validation_ui_csv.py")
            echo "PID: $PID"
        else
            echo -e "Service: ${RED}❌ Gestoppt${NC}"
        fi
    fi
    
    # Port prüfen
    if curl -s http://localhost:$PORT/ > /dev/null 2>&1; then
        echo -e "Port $PORT: ${GREEN}✅ Erreichbar${NC}"
    else
        echo -e "Port $PORT: ${RED}❌ Nicht erreichbar${NC}"
    fi
    
    # Logs prüfen
    if [ -f "logs/service.log" ]; then
        LOG_SIZE=$(du -h logs/service.log | cut -f1)
        LOG_LINES=$(wc -l < logs/service.log)
        echo "Logs: $LOG_SIZE ($LOG_LINES Zeilen)"
    fi
    
    echo ""
}

start_service() {
    echo -e "${GREEN}🚀 Starte Service...${NC}"
    
    if systemctl is-active --quiet $SERVICE_NAME 2>/dev/null; then
        echo "Service läuft bereits"
        return
    fi
    
    # Versuche Systemd-Service
    if [ -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
        sudo systemctl start $SERVICE_NAME
        sleep 2
        if systemctl is-active --quiet $SERVICE_NAME; then
            echo -e "${GREEN}✅ Service gestartet${NC}"
        else
            echo -e "${RED}❌ Fehler beim Starten${NC}"
            sudo journalctl -u $SERVICE_NAME -n 20
        fi
    else
        # Manuell starten
        cd /home/ubuntu/pcbf_framework
        nohup python3 validation_ui_csv.py > logs/service.log 2>&1 &
        sleep 2
        echo -e "${GREEN}✅ Service manuell gestartet${NC}"
    fi
}

stop_service() {
    echo -e "${YELLOW}🛑 Stoppe Service...${NC}"
    
    # Systemd-Service stoppen
    if systemctl is-active --quiet $SERVICE_NAME 2>/dev/null; then
        sudo systemctl stop $SERVICE_NAME
        echo -e "${GREEN}✅ Service gestoppt${NC}"
    else
        # Manuellen Prozess stoppen
        pkill -f "validation_ui_csv.py" 2>/dev/null && echo -e "${GREEN}✅ Prozess gestoppt${NC}" || echo "Kein Prozess gefunden"
    fi
}

restart_service() {
    echo -e "${YELLOW}🔄 Starte Service neu...${NC}"
    stop_service
    sleep 2
    start_service
}

show_logs() {
    echo -e "${BLUE}📋 Letzte 50 Log-Zeilen${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [ -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
        sudo journalctl -u $SERVICE_NAME -n 50 --no-pager
    elif [ -f "logs/service.log" ]; then
        tail -50 logs/service.log
    else
        echo "Keine Logs gefunden"
    fi
}

follow_logs() {
    echo -e "${BLUE}📋 Folge Logs (Ctrl+C zum Beenden)${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [ -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
        sudo journalctl -u $SERVICE_NAME -f
    elif [ -f "logs/service.log" ]; then
        tail -f logs/service.log
    else
        echo "Keine Logs gefunden"
    fi
}

show_help() {
    echo "Verwendung: ./manage.sh [BEFEHL]"
    echo ""
    echo "Befehle:"
    echo "  status    - Zeige Service-Status"
    echo "  start     - Starte Service"
    echo "  stop      - Stoppe Service"
    echo "  restart   - Starte Service neu"
    echo "  logs      - Zeige letzte 50 Log-Zeilen"
    echo "  follow    - Folge Logs in Echtzeit"
    echo "  help      - Zeige diese Hilfe"
    echo ""
}

# Hauptlogik
print_header

case "${1:-status}" in
    status)
        show_status
        ;;
    start)
        start_service
        echo ""
        show_status
        ;;
    stop)
        stop_service
        echo ""
        show_status
        ;;
    restart)
        restart_service
        echo ""
        show_status
        ;;
    logs)
        show_logs
        ;;
    follow)
        follow_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unbekannter Befehl: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

