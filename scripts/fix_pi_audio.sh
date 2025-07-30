#!/bin/bash
# ALSA Audio Setup Script for Raspberry Pi
# Fixes common audio issues for the Dark Helmet Voice Changer

echo "🔧 Dark Helmet Audio Setup for Raspberry Pi"
echo "============================================"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Please don't run this script as root"
    echo "Run as: ./fix_pi_audio.sh"
    exit 1
fi

echo "🔍 Checking current audio setup..."

# Check if ALSA is installed
if ! command -v aplay &> /dev/null; then
    echo "📦 Installing ALSA utilities..."
    sudo apt update
    sudo apt install -y alsa-utils
fi

# Check current audio devices
echo "📱 Current audio devices:"
aplay -l 2>/dev/null || echo "No playback devices found"
echo ""
echo "🎤 Current capture devices:"
arecord -l 2>/dev/null || echo "No capture devices found"

# Check if user is in audio group
if groups $USER | grep -q "audio"; then
    echo "✅ User $USER is in audio group"
else
    echo "👤 Adding $USER to audio group..."
    sudo usermod -a -G audio $USER
    echo "⚠️  You need to logout and login again for this to take effect"
fi

# Create/update ALSA configuration
echo "⚙️  Setting up ALSA configuration..."

# Create asoundrc for better default settings
cat > ~/.asoundrc << 'EOF'
# ALSA configuration for Dark Helmet Voice Changer
# This sets up better defaults for audio processing

pcm.!default {
    type asym
    playback.pcm "playback"
    capture.pcm "capture"
}

pcm.playback {
    type plug
    slave.pcm "hw:0,0"
    slave.channels 2
    slave.rate 44100
    slave.format S16_LE
}

pcm.capture {
    type plug
    slave.pcm "hw:0,0"
    slave.channels 2
    slave.rate 44100
    slave.format S16_LE
}

ctl.!default {
    type hw
    card 0
}
EOF

echo "✅ Created ~/.asoundrc with optimized settings"

# Set reasonable volume levels
echo "🔊 Setting audio levels..."
amixer sset 'Master' 80% 2>/dev/null || echo "Could not set Master volume"
amixer sset 'PCM' 80% 2>/dev/null || echo "Could not set PCM volume"
amixer sset 'Capture' 70% 2>/dev/null || echo "Could not set Capture volume"

# Enable audio service
echo "🎵 Enabling audio services..."
sudo systemctl enable alsa-state
sudo systemctl start alsa-state

# Check for WM8960 HAT
echo "🔍 Checking for WM8960 audio HAT..."
if lsmod | grep -q snd_soc_wm8960; then
    echo "✅ WM8960 driver detected"
    
    # WM8960 specific configuration
    cat > ~/.asoundrc_wm8960 << 'EOF'
# WM8960 Audio HAT Configuration
pcm.!default {
    type asym
    playback.pcm "wm8960_playback"
    capture.pcm "wm8960_capture"
}

pcm.wm8960_playback {
    type plug
    slave.pcm "hw:wm8960soundcard,0"
    slave.channels 2
    slave.rate 44100
    slave.format S16_LE
}

pcm.wm8960_capture {
    type plug
    slave.pcm "hw:wm8960soundcard,0"
    slave.channels 2
    slave.rate 44100
    slave.format S16_LE
}

ctl.!default {
    type hw
    card wm8960soundcard
}
EOF
    
    echo "🎧 WM8960 configuration created as ~/.asoundrc_wm8960"
    echo "   To use WM8960, run: cp ~/.asoundrc_wm8960 ~/.asoundrc"
    
else
    echo "ℹ️  WM8960 not detected, using standard audio"
fi

# Test audio
echo ""
echo "🧪 Testing audio setup..."
echo "📢 Testing playback (you should hear a tone)..."
timeout 3s speaker-test -t sine -f 1000 -l 1 2>/dev/null || echo "Playback test failed"

echo ""
echo "🎤 Testing capture (recording 2 seconds)..."
timeout 2s arecord -f cd -t wav test_recording.wav 2>/dev/null && rm -f test_recording.wav && echo "✅ Capture test passed" || echo "❌ Capture test failed"

echo ""
echo "🎭 Audio setup complete!"
echo "==============================="
echo "✅ ALSA utilities installed"
echo "✅ User added to audio group"
echo "✅ Audio configuration created"
echo "✅ Volume levels set"
echo ""
echo "🚀 Next steps:"
echo "1. Logout and login again (if user was added to audio group)"
echo "2. Test with: cd src && python audio_diagnostic.py"
echo "3. Run voice changer: cd src && python run_voice_changer.py"
echo ""
echo "🔧 If still having issues:"
echo "• Check 'sudo raspi-config' -> Advanced Options -> Audio"
echo "• Try: sudo reboot"
echo "• Check connections and hardware"
