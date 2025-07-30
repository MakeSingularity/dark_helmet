#!/bin/bash
# Troubleshoot and fix dnsmasq service issues on Raspberry Pi

echo "Dark Helmet - dnsmasq Troubleshooting Script"
echo "============================================="

# Check if dnsmasq is installed
echo "1. Checking if dnsmasq is installed..."
if dpkg -l | grep -q dnsmasq; then
    echo "   ✓ dnsmasq is installed"
    DNSMASQ_VERSION=$(dpkg -l | grep dnsmasq | awk '{print $3}')
    echo "   Version: $DNSMASQ_VERSION"
else
    echo "   ✗ dnsmasq is not installed"
    echo "   Installing dnsmasq..."
    sudo apt update
    sudo apt install -y dnsmasq
fi

echo ""

# Check systemd service file
echo "2. Checking systemd service file..."
if [ -f /etc/systemd/system/dnsmasq.service ]; then
    echo "   ✓ Custom service file exists at /etc/systemd/system/dnsmasq.service"
elif [ -f /lib/systemd/system/dnsmasq.service ]; then
    echo "   ✓ Default service file exists at /lib/systemd/system/dnsmasq.service"
else
    echo "   ✗ No service file found - creating one..."
    sudo tee /etc/systemd/system/dnsmasq.service > /dev/null << 'EOF'
[Unit]
Description=dnsmasq - A lightweight DHCP and caching DNS server
Requires=network.target
After=network.target
Conflicts=systemd-resolved.service

[Service]
Type=forking
PIDFile=/run/dnsmasq/dnsmasq.pid
ExecStartPre=/usr/sbin/dnsmasq --test
ExecStart=/usr/sbin/dnsmasq -x /run/dnsmasq/dnsmasq.pid
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    echo "   ✓ Service file created"
fi

echo ""

# Check for conflicts with systemd-resolved
echo "3. Checking for conflicts with systemd-resolved..."
if systemctl is-active --quiet systemd-resolved; then
    echo "   ⚠ systemd-resolved is running - this may conflict with dnsmasq"
    echo "   Disabling systemd-resolved..."
    sudo systemctl disable systemd-resolved
    sudo systemctl stop systemd-resolved
    echo "   ✓ systemd-resolved disabled"
else
    echo "   ✓ No conflict with systemd-resolved"
fi

echo ""

# Create PID directory if it doesn't exist
echo "4. Checking PID directory..."
if [ ! -d /run/dnsmasq ]; then
    echo "   Creating PID directory..."
    sudo mkdir -p /run/dnsmasq
    sudo chown dnsmasq:dnsmasq /run/dnsmasq 2>/dev/null || sudo chown nobody:nogroup /run/dnsmasq
    echo "   ✓ PID directory created"
else
    echo "   ✓ PID directory exists"
fi

echo ""

# Check configuration file
echo "5. Checking configuration file..."
if [ -f /etc/dnsmasq.conf ]; then
    echo "   ✓ Configuration file exists"
    # Test configuration
    if sudo dnsmasq --test > /dev/null 2>&1; then
        echo "   ✓ Configuration is valid"
    else
        echo "   ✗ Configuration has errors:"
        sudo dnsmasq --test
    fi
else
    echo "   ⚠ No configuration file found - creating basic config..."
    sudo tee /etc/dnsmasq.conf > /dev/null << 'EOF'
# Basic dnsmasq configuration for Dark Helmet
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
domain=darkhelmet.local
address=/darkhelmet.local/192.168.4.1
EOF
    echo "   ✓ Basic configuration created"
fi

echo ""

# Reload systemd and check service status
echo "6. Reloading systemd and checking service..."
sudo systemctl daemon-reload
sleep 2

if systemctl is-enabled dnsmasq > /dev/null 2>&1; then
    echo "   ✓ dnsmasq service is enabled"
else
    echo "   Enabling dnsmasq service..."
    sudo systemctl enable dnsmasq
    echo "   ✓ dnsmasq service enabled"
fi

echo ""

# Try to start the service
echo "7. Testing service startup..."
sudo systemctl stop dnsmasq 2>/dev/null || true
sleep 2

if sudo systemctl start dnsmasq; then
    echo "   ✓ dnsmasq started successfully"
    if systemctl is-active --quiet dnsmasq; then
        echo "   ✓ dnsmasq is running"
    else
        echo "   ✗ dnsmasq failed to start properly"
    fi
else
    echo "   ✗ Failed to start dnsmasq"
    echo "   Error details:"
    sudo journalctl -u dnsmasq --no-pager -n 10
fi

echo ""

# Show final status
echo "8. Final Status Check:"
echo "   Service status: $(systemctl is-active dnsmasq)"
echo "   Service enabled: $(systemctl is-enabled dnsmasq)"

if systemctl is-active --quiet dnsmasq; then
    echo "   PID: $(cat /run/dnsmasq/dnsmasq.pid 2>/dev/null || echo 'No PID file')"
fi

echo ""
echo "Troubleshooting complete!"
echo ""
echo "If dnsmasq is still not working, check logs with:"
echo "  sudo journalctl -u dnsmasq -f"
echo ""
echo "To manually test dnsmasq:"
echo "  sudo dnsmasq --test"
echo "  sudo dnsmasq --no-daemon"
