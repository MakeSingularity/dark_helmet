# dnsmasq Service Fix Guide

## Problem
You installed dnsmasq but getting "dnsmasq.service does not exist" error.

## Quick Fix
Run the troubleshooting script on your Raspberry Pi:

```bash
cd /home/rickmoranis/dark_helmet/scripts
chmod +x fix_dnsmasq.sh
sudo ./fix_dnsmasq.sh
```

## Manual Fix Steps

If the script doesn't work, follow these manual steps:

### 1. Check Installation
```bash
sudo apt update
sudo apt install -y dnsmasq
```

### 2. Create Service File
```bash
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
```

### 3. Create PID Directory
```bash
sudo mkdir -p /run/dnsmasq
sudo chown nobody:nogroup /run/dnsmasq
```

### 4. Disable Conflicting Services
```bash
sudo systemctl disable systemd-resolved
sudo systemctl stop systemd-resolved
```

### 5. Enable and Start dnsmasq
```bash
sudo systemctl daemon-reload
sudo systemctl enable dnsmasq
sudo systemctl start dnsmasq
```

### 6. Check Status
```bash
sudo systemctl status dnsmasq
```

## Full Network Setup

For complete Dark Helmet network configuration (AP mode):

```bash
cd /home/rickmoranis/dark_helmet/scripts
chmod +x setup_network.sh
sudo ./setup_network.sh
```

This will:
- Install and configure dnsmasq properly
- Set up hostapd for WiFi hotspot
- Create "Dark-Helmet-Voice-Changer" WiFi network
- Configure web interface at http://192.168.4.1

## Troubleshooting

If you still have issues:

```bash
# Check logs
sudo journalctl -u dnsmasq -f

# Test configuration
sudo dnsmasq --test

# Run in foreground for debugging
sudo dnsmasq --no-daemon
```

## Network Mode Switching

After setup, you can switch modes:

```bash
# Access Point mode (standalone)
sudo darkhelmet-ap-mode

# Station mode (connect to WiFi)
sudo darkhelmet-sta-mode
```
