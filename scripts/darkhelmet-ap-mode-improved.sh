#!/bin/bash
# Improved Access Point mode script with diagnostics
# Switch to Access Point mode and verify it's working

echo "Starting Dark Helmet Access Point mode..."

# Stop conflicting services
echo "1. Stopping conflicting services..."
sudo systemctl stop wpa_supplicant 2>/dev/null || true
sudo pkill wpa_supplicant 2>/dev/null || true

# Unblock WiFi if blocked
echo "2. Unblocking WiFi..."
sudo rfkill unblock wifi

# Reset network interface
echo "3. Resetting network interface..."
sudo ip link set wlan0 down
sleep 1
sudo ip link set wlan0 up
sudo ip addr flush dev wlan0
sudo ip addr add 192.168.4.1/24 dev wlan0

# Start services in correct order
echo "4. Starting network services..."
sudo systemctl start dnsmasq
sleep 2

echo "5. Starting WiFi Access Point..."
sudo systemctl start hostapd
sleep 3

# Start the Dark Helmet application
echo "6. Starting Dark Helmet service..."
sudo systemctl start dark-helmet

# Check if everything is working
echo ""
echo "=== STATUS CHECK ==="

# Check services
for service in dnsmasq hostapd dark-helmet; do
    if systemctl is-active --quiet $service; then
        echo "✓ $service is running"
    else
        echo "✗ $service failed to start"
        echo "  Error: $(systemctl is-failed $service 2>/dev/null || echo 'unknown')"
    fi
done

# Check interface
echo ""
echo "Network interface:"
ip addr show wlan0 | grep -E "inet|state"

# Check for SSID broadcast
echo ""
echo "Scanning for SSID (this may take 10 seconds)..."
timeout 10 sudo iwlist scan 2>/dev/null | grep -E "ESSID.*DarkHelmet" && echo "✓ SSID is broadcasting!" || echo "✗ SSID not detected"

# Check listening services
echo ""
echo "Network services:"
sudo netstat -tulpn | grep -E ":53|:67|:80" | while read line; do
    echo "  $line"
done

echo ""
echo "=== Dark Helmet Access Point Setup Complete ==="
echo ""
echo "📡 WiFi Network: DarkHelmet"
echo "🔑 Password: SpaceBalls2024"
echo "🌐 Web Interface: http://192.168.4.1"
echo ""
echo "If the SSID is not visible:"
echo "  1. Wait 30 seconds and scan again"
echo "  2. Try different WiFi channel: sudo nano /etc/hostapd/hostapd.conf"
echo "  3. Run diagnostic: sudo ./scripts/fix_wifi_ap.sh"
echo ""
echo "To debug hostapd: sudo hostapd -d /etc/hostapd/hostapd.conf"
