#!/bin/bash
# Network setup script for Dark Helmet device
# Configures dnsmasq and hostapd for standalone web interface

set -e  # Exit on any error

echo "Setting up network configuration for Dark Helmet device..."

# Update package list
sudo apt update

# Install required packages
echo "Installing network packages..."
sudo apt install -y dnsmasq hostapd iptables-persistent

# Stop services while we configure them
echo "Stopping services for configuration..."
sudo systemctl stop dnsmasq 2>/dev/null || true
sudo systemctl stop hostapd 2>/dev/null || true

# Backup original dnsmasq configuration
if [ -f /etc/dnsmasq.conf ]; then
    sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup
fi

# Create dnsmasq configuration
echo "Configuring dnsmasq..."
sudo tee /etc/dnsmasq.conf > /dev/null << 'EOF'
# Dark Helmet DNS/DHCP Configuration
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
domain=darkhelmet.local
address=/darkhelmet.local/192.168.4.1
server=8.8.8.8
server=8.8.4.4
EOF

# Configure hostapd
echo "Configuring hostapd..."
sudo tee /etc/hostapd/hostapd.conf > /dev/null << 'EOF'
# Dark Helmet WiFi Hotspot Configuration
interface=wlan0
driver=nl80211
ssid=DarkHelmet
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=SpaceBalls2024
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

# Configure hostapd daemon
sudo tee /etc/default/hostapd > /dev/null << 'EOF'
DAEMON_CONF="/etc/hostapd/hostapd.conf"
EOF

# Configure dhcpcd to ignore wlan0 when in AP mode
echo "Configuring dhcpcd..."
if ! grep -q "denyinterfaces wlan0" /etc/dhcpcd.conf; then
    echo "denyinterfaces wlan0" | sudo tee -a /etc/dhcpcd.conf
fi

# Configure static IP for wlan0 in AP mode
echo "Configuring static IP..."
sudo tee /etc/systemd/network/08-wlan0.network > /dev/null << 'EOF'
[Match]
Name=wlan0

[Network]
Address=192.168.4.1/24
DHCPServer=no
IPForward=yes
EOF

# Enable IP forwarding
echo "Enabling IP forwarding..."
echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf

# Create iptables rules for NAT (if internet sharing is needed later)
echo "Setting up iptables rules..."
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE 2>/dev/null || true
sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null || true
sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT 2>/dev/null || true

# Save iptables rules
sudo sh -c "iptables-save > /etc/iptables/rules.v4"

# Enable and start services
echo "Enabling services..."
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq

# Create a service for the Dark Helmet application
echo "Creating Dark Helmet service..."
sudo tee /etc/systemd/system/dark-helmet.service > /dev/null << 'EOF'
[Unit]
Description=Dark Helmet Voice Changer
After=network.target

[Service]
Type=simple
User=rickmoranis
WorkingDirectory=/home/rickmoranis/dark_helmet
Environment=PATH=/home/rickmoranis/dark_helmet/SpaceBalls/bin
ExecStart=/home/rickmoranis/dark_helmet/SpaceBalls/bin/python /home/rickmoranis/dark_helmet/src/run_voice_changer.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create script to switch between AP and STA modes
echo "Creating mode switching scripts..."
sudo tee /usr/local/bin/darkhelmet-ap-mode > /dev/null << 'EOF'
#!/bin/bash
# Switch to Access Point mode
sudo systemctl stop wpa_supplicant
sudo systemctl start hostapd
sudo systemctl start dnsmasq
sudo systemctl start dark-helmet
echo "Dark Helmet is now in Access Point mode"
echo "Connect to WiFi: Dark-Helmet-Voice-Changer"
echo "Password: SpaceBalls2024"
echo "Open browser to: http://192.168.4.1"
EOF

sudo tee /usr/local/bin/darkhelmet-sta-mode > /dev/null << 'EOF'
#!/bin/bash
# Switch to Station mode (connect to existing WiFi)
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq
sudo systemctl start wpa_supplicant
echo "Dark Helmet is now in Station mode"
echo "Connect to your regular WiFi network"
EOF

sudo chmod +x /usr/local/bin/darkhelmet-ap-mode
sudo chmod +x /usr/local/bin/darkhelmet-sta-mode

# Reload systemd
sudo systemctl daemon-reload

echo ""
echo "Network setup complete!"
echo ""
echo "To start Access Point mode:"
echo "  sudo darkhelmet-ap-mode"
echo ""
echo "To return to normal WiFi mode:"
echo "  sudo darkhelmet-sta-mode"
echo ""
echo "WiFi Network: Dark-Helmet-Voice-Changer"
echo "Password: SpaceBalls2024"
echo "Web Interface: http://192.168.4.1"
echo ""
echo "Reboot recommended to apply all changes:"
echo "  sudo reboot"
