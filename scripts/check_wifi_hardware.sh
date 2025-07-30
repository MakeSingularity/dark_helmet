#!/bin/bash
# Check WiFi hardware capabilities for Access Point mode
# Some WiFi adapters don't support AP mode

echo "Dark Helmet WiFi Hardware Check"
echo "==============================="

echo "1. Detecting WiFi hardware..."
lsusb | grep -i wireless || echo "No USB wireless devices detected"
lsusb | grep -i wifi || echo "No USB WiFi devices detected"

echo ""
echo "2. Available wireless interfaces:"
iw dev | grep -E "Interface|type"

echo ""
echo "3. WiFi driver information:"
lshw -C network 2>/dev/null | grep -A 10 -B 2 wireless || echo "No wireless hardware info available"

echo ""
echo "4. Checking AP mode support..."
if command -v iw > /dev/null; then
    echo "Supported interface modes:"
    iw list 2>/dev/null | grep -A 10 "Supported interface modes" | head -15
    
    echo ""
    if iw list 2>/dev/null | grep -q "AP"; then
        echo "✓ Your WiFi adapter SUPPORTS Access Point mode"
    else
        echo "✗ Your WiFi adapter does NOT support Access Point mode"
        echo ""
        echo "SOLUTION: You need a WiFi adapter that supports AP mode"
        echo "Recommended USB WiFi adapters for Raspberry Pi:"
        echo "  - TP-Link AC600T2U Nano"
        echo "  - Panda PAU09"
        echo "  - Edimax EW-7811Un"
        echo "  - Any adapter with Realtek RTL8188EUS chipset"
    fi
else
    echo "iw command not available - installing..."
    sudo apt update && sudo apt install -y iw
fi

echo ""
echo "5. Current wlan0 capabilities:"
if [ -d /sys/class/net/wlan0 ]; then
    echo "wlan0 exists"
    iw dev wlan0 info 2>/dev/null || echo "Cannot get wlan0 info"
else
    echo "wlan0 interface not found"
    echo "Available interfaces:"
    ls /sys/class/net/ | grep -E "wl|eth"
fi

echo ""
echo "6. RF Kill status:"
rfkill list all

echo ""
echo "7. Kernel modules:"
lsmod | grep -E "cfg80211|mac80211|brcm|8021" | head -10

echo ""
echo "8. hostapd test (if configured):"
if [ -f /etc/hostapd/hostapd.conf ]; then
    echo "Testing hostapd configuration..."
    sudo hostapd -t /etc/hostapd/hostapd.conf 2>&1 | head -5
else
    echo "hostapd not configured yet"
fi

echo ""
echo "=== HARDWARE CHECK COMPLETE ==="
echo ""
echo "If AP mode is NOT supported:"
echo "1. Get a compatible USB WiFi adapter"
echo "2. Or use ethernet connection instead"
echo "3. Or connect to existing WiFi and use port forwarding"
