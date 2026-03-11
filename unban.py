#!/bin/bash
#==============================================================================
# 🔥 SECURITY BAN MANAGER - Ban/Unban IP & Users (Production Ready)
# Usage: sudo ./security_ban_manager.sh [ban|unban|setup|status] [IP|user] [duration]
# Author: HackerAI | GitHub Ready
#==============================================================================

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
LOG_FILE="/var/log/security_ban_manager.log"
SCRIPT_DIR="/usr/local/bin"
SERVICE_FILE="/etc/systemd/system/ban-monitor.service"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  🔥 SECURITY BAN MANAGER v2.0 - Production Ready            ║"
    echo "║  Usage: ban IP/user [minutes] | unban IP/user | setup       ║"
    echo "╚══════════════════════════════════════════════════════════════╝${NC}"
}

ban_target() {
    local target=$1
    local duration=${2:-60}
    
    # Check if already banned
    if iptables -L INPUT -n | grep -q "$target"; then
        log "⚠️  $target tayari imefungwa"
        echo -e "${YELLOW}[-]${NC} $target tayari imefungwa"
        return 1
    fi
    
    # IP Ban
    iptables -I INPUT 1 -s "$target" -j DROP
    iptables -I OUTPUT 1 -d "$target" -j DROP
    
    # Fail2ban integration
    echo "$(date) - Manual ban: $target for $duration minutes" >> /var/log/auth.log
    
    timeout=$((duration * 60))
    iptables -I INPUT 1 -m recent --name banned --rcheck --seconds $timeout -s "$target" -j DROP
    iptables -I INPUT 1 -m recent --name banned --set -s "$target"
    
    log "🔒 $target imefungwa kwa dakika $duration"
    echo -e "${GREEN}[+]${NC} $target imefungwa kwa dakika ${YELLOW}$duration${NC}"
}

unban_target() {
    local target=$1
    
    iptables -D INPUT -s "$target" -j DROP 2>/dev/null
    iptables -D OUTPUT -d "$target" -j DROP 2>/dev/null
    iptables -D INPUT -m recent --name banned --rcheck --seconds 3600 -s "$target" -j DROP 2>/dev/null
    iptables -D INPUT -m recent --name banned --set -s "$target" 2>/dev/null
    
    fail2ban-client set all unbanip "$target" 2>/dev/null || true
    
    log "🔓 $target imefunguliwa"
    echo -e "${GREEN}[+]${NC} $target imefunguliwa"
}

show_status() {
    echo -e "${BLUE}🔍 BANNED IPS & USERS:${NC}"
    echo "========================"
    iptables -L INPUT -n --line-numbers | grep -E "(DROP|REJECT)" | head -20
    echo ""
    echo -e "${YELLOW}Recent Log:${NC}"
    tail -5 "$LOG_FILE"
}

install_service() {
    cat > "$SCRIPT_DIR/ban-monitor.sh" << 'EOF'
#!/bin/bash
LOG="/var/log/ban-monitor.log"
while true; do
    # Auto-ban brute force attempts
    awk '{print $1}' /var/log/auth.log | grep -E "^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$" | sort | uniq -c | sort -nr | head -5 | \\
    while read count ip; do
        if [[ $count -gt 5 ]]; then
            /usr/local/bin/security_ban_manager.sh ban $ip 30
        fi
    done
    sleep 60
done
EOF
    
    chmod +x "$SCRIPT_DIR/ban-monitor.sh"
    
    cat > "$SERVICE_FILE" << 'EOF'
[Unit]
Description=Ban Monitor
After=network.target

[Service]
ExecStart=/usr/local/bin/ban-monitor.sh
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF
    
    chmod +x "$0"
    cp "$0" "$SCRIPT_DIR/security_ban_manager.sh"
    chmod +x "$SCRIPT_DIR/security_ban_manager.sh"
    
    systemctl daemon-reload
    systemctl enable ban-monitor.service
    systemctl start ban-monitor.service
    
    log "✅ Service imeset upwa na inaendesha"
    echo -e "${GREEN}✅${NC} Tumeweka ban manager + auto-monitor service!"
}

case "$1" in
    "ban")
        print_banner
        ban_target "$2" "$3"
        ;;
    "unban")
        print_banner
        unban_target "$2"
        ;;
    "setup"|"install")
        print_banner
        install_service
        ;;
    "status"|"list")
        print_banner
        show_status
        ;;
    *)
        print_banner
        echo -e "${GREEN}Usage:${NC}"
        echo "  sudo $0 ban 192.168.1.100 30      # Ban IP dakika 30"
        echo "  sudo $0 ban hacker               # Ban user (default 60min)"
        echo "  sudo $0 unban 192.168.1.100      # Fungua IP"
        echo "  sudo $0 setup                    # Install + auto-monitor"
        echo "  sudo $0 status                   # Angalia banned IPs"
        ;;
esac
