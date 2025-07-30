#!/bin/bash
# WiFi Access Point troubleshooting script for Dark Helmet
# Diagnoses and fixes SSID not showing up issues

echo "Dark Helmet WiFi AP Troubleshooting"
echo "===================================="

# Function to check service status
check_service() {
    local service=$1
    echo "Checking $service..."
    if systemctl is-active --quiet $service; then
        echo "   ✓ $service is running"
        return 0
    else
        echo "   ✗ $service is not running"
        echo "   Status: $(systemctl is-active $service)"
        return 1
    fi
}

# Function to show service logs
show_logs() {
    local service=$1
    echo "Recent $service logs:"
    sudo journalctl -u $service --no-pager -n 5
    echo ""
}

echo "1. Checking WiFi hardware..."
if iwconfig 2>/dev/null | grep -q wlan0; then
    echo "   ✓ wlan0 interface detected"
    iwconfig wlan0 | grep -E "IEEE|ESSID|Mode"
else
    echo "   ✗ wlan0 interface not found"
    echo "   Available interfaces:"
    ip link show | grep -E "wlan|wlp"
    exit 1
fi

echo ""

echo "2. Checking interface configuration..."
ip addr show wlan0 | grep -E "inet|state"
echo ""

echo "3. Checking conflicting processes..."
# Check for wpa_supplicant
if pgrep wpa_supplicant > /dev/null; then
    echo "   ⚠ wpa_supplicant is running - this conflicts with AP mode"
    echo "   Stopping wpa_supplicant..."
    sudo systemctl stop wpa_supplicant
    sudo pkill wpa_supplicant 2>/dev/null || true
else
    echo "   ✓ No wpa_supplicant conflicts"
fi

# Check for NetworkManager
if systemctl is-active --quiet NetworkManager 2>/dev/null; then
    echo "   ⚠ NetworkManager is running - this may conflict"
    echo "   You may need to configure NetworkManager to ignore wlan0"
else
    echo "   ✓ NetworkManager not interfering"
fi

echo ""

echo "4. Checking hostapd configuration..."
if [ -f /etc/hostapd/hostapd.conf ]; then
    echo "   ✓ hostapd.conf exists"
    if sudo hostapd -t /etc/hostapd/hostapd.conf; then
        echo "   ✓ hostapd configuration is valid"
    else
        echo "   ✗ hostapd configuration has errors"
        exit 1
    fi
else
    echo "   ✗ hostapd.conf not found"
    exit 1
fi

echo ""

echo "5. Checking dnsmasq configuration..."
if [ -f /etc/dnsmasq.conf ]; then
    echo "   ✓ dnsmasq.conf exists"
    if sudo dnsmasq --test > /dev/null 2>&1; then
        echo "   ✓ dnsmasq configuration is valid"
    else
        echo "   ✗ dnsmasq configuration has errors"
        sudo dnsmasq --test
    fi
else
    echo "   ✗ dnsmasq.conf not found"
fi

echo ""

echo "6. Checking service status..."
HOSTAPD_OK=false
DNSMASQ_OK=false

if check_service hostapd; then
    HOSTAPD_OK=true
else
    show_logs hostapd
fi

if check_service dnsmasq; then
    DNSMASQ_OK=true
else
    show_logs dnsmasq
fi

echo ""

echo "7. Checking RF kill status..."
if rfkill list wifi | grep -q "Soft blocked: yes"; then
    echo "   ⚠ WiFi is soft-blocked, unblocking..."
    sudo rfkill unblock wifi
else
    echo "   ✓ WiFi is not blocked"
fi

echo ""

# If services aren't running, try to fix them
if [ "$HOSTAPD_OK" = false ] || [ "$DNSMASQ_OK" = false ]; then
    echo "8. Attempting to fix and restart services..."
    
    # Stop everything first
    sudo systemctl stop hostapd dnsmasq 2>/dev/null || true
    sudo pkill hostapd 2>/dev/null || true
    sudo pkill dnsmasq 2>/dev/null || true
    sleep 2
    
    # Bring down the interface
    sudo ip link set wlan0 down 2>/dev/null || true
    sleep 1
    
    # Configure interface manually
    echo "   Setting up wlan0 interface..."
    sudo ip link set wlan0 up
    sudo ip addr flush dev wlan0
    sudo ip addr add 192.168.4.1/24 dev wlan0
    
    # Start services in order
    echo "   Starting dnsmasq..."
    sudo systemctl start dnsmasq
    sleep 2
    
    echo "   Starting hostapd..."
    sudo systemctl start hostapd
    sleep 3
    
    # Check results
    echo "   Checking services after restart..."
    check_service dnsmasq
    check_service hostapd
fi

echo ""

echo "9. Final status check..."
echo "Interface status:"
ip addr show wlan0 | grep -E "inet|state"

echo ""
echo "Scanning for our SSID..."
timeout 10 sudo iwlist scan 2>/dev/null | grep -E "ESSID|Cell" | grep -A1 -B1 "DarkHelmet" || echo "SSID not found in scan"

echo ""
echo "Active hostapd process:"
ps aux | grep hostapd | grep -v grep || echo "No hostapd process found"

echo ""
echo "Listening ports:"
sudo netstat -tulpn | grep -E ":53|:67|:80" || echo "No services listening on expected ports"

echo ""
echo "=== TROUBLESHOOTING COMPLETE ==="
echo ""
echo "If SSID still not visible, try:"
echo "1. sudo systemctl restart hostapd"
echo "2. sudo hostapd -d /etc/hostapd/hostapd.conf  # Debug mode"
echo "3. Check different WiFi channel in hostapd.conf"
echo "4. Verify wlan0 supports AP mode: iw list | grep -A 10 'Supported interface modes'"
