# WiFi Access Point Troubleshooting

## Problem: SSID "DarkHelmet" not showing up

### Quick Fixes

1. **Run the WiFi diagnostic script:**
   ```bash
   cd /home/rickmoranis/dark_helmet/scripts
   chmod +x fix_wifi_ap.sh
   sudo ./fix_wifi_ap.sh
   ```

2. **Check WiFi hardware compatibility:**
   ```bash
   chmod +x check_wifi_hardware.sh
   sudo ./check_wifi_hardware.sh
   ```

3. **Restart AP mode with diagnostics:**
   ```bash
   chmod +x darkhelmet-ap-mode-improved.sh
   sudo ./darkhelmet-ap-mode-improved.sh
   ```

### Common Issues

#### 1. WiFi Adapter Doesn't Support AP Mode
Many cheap WiFi adapters don't support Access Point mode.

**Check:** Run `sudo iw list | grep -A 10 "Supported interface modes"`
**Solution:** Get a compatible USB WiFi adapter:
- TP-Link AC600T2U Nano
- Panda PAU09
- Edimax EW-7811Un

#### 2. wpa_supplicant Conflict
If wpa_supplicant is running, it conflicts with hostapd.

**Fix:**
```bash
sudo systemctl stop wpa_supplicant
sudo pkill wpa_supplicant
sudo systemctl start hostapd
```

#### 3. Wrong WiFi Channel
Some regions/devices have restricted channels.

**Fix:** Edit `/etc/hostapd/hostapd.conf` and try different channels:
```bash
sudo nano /etc/hostapd/hostapd.conf
# Change: channel=7
# Try: channel=1, channel=6, or channel=11
sudo systemctl restart hostapd
```

#### 4. RF Kill Block
WiFi might be blocked by software.

**Fix:**
```bash
sudo rfkill unblock wifi
sudo systemctl restart hostapd
```

#### 5. Interface Configuration
wlan0 might not have correct IP.

**Fix:**
```bash
sudo ip link set wlan0 down
sudo ip link set wlan0 up
sudo ip addr add 192.168.4.1/24 dev wlan0
sudo systemctl restart hostapd
```

### Manual Debugging

#### Debug hostapd in foreground:
```bash
sudo systemctl stop hostapd
sudo hostapd -d /etc/hostapd/hostapd.conf
```

#### Check service logs:
```bash
sudo journalctl -u hostapd -f
sudo journalctl -u dnsmasq -f
```

#### Scan for SSID:
```bash
sudo iwlist scan | grep -i darkhelmet
```

### Alternative Solutions

#### Option 1: Use Ethernet + Port Forwarding
If WiFi AP doesn't work, connect via Ethernet and use SSH port forwarding:
```bash
ssh -L 8000:localhost:8000 rickmoranis@192.168.1.103
```
Then access via http://localhost:8000

#### Option 2: Connect to Existing WiFi
Configure to connect to your home WiFi instead of creating hotspot:
```bash
sudo ./scripts/darkhelmet-sta-mode
```

#### Option 3: Use Different WiFi Adapter
Get a USB WiFi adapter specifically for AP mode and keep built-in WiFi for internet.

### Network Configuration Files

- **hostapd config:** `/etc/hostapd/hostapd.conf`
- **dnsmasq config:** `/etc/dnsmasq.conf`  
- **dhcpcd config:** `/etc/dhcpcd.conf`
- **Network config:** `/etc/systemd/network/08-wlan0.network`
