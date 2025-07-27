#!/usr/bin/env python3
"""
Audio System Diagnostic Tool for Dark Helmet Voice Changer
Helps diagnose and fix audio configuration issues
"""

import sys
import os
import platform

def check_imports():
    """Check if all required audio libraries are available"""
    print("🔍 Checking audio library imports...")
    
    missing = []
    try:
        import numpy
        print("✅ numpy imported successfully")
    except ImportError:
        missing.append("numpy")
        
    try:
        import scipy
        print("✅ scipy imported successfully")
    except ImportError:
        missing.append("scipy")
        
    try:
        import sounddevice as sd
        print("✅ sounddevice imported successfully")
    except ImportError:
        missing.append("sounddevice")
        
    try:
        import sox
        print("✅ sox imported successfully")
    except ImportError:
        missing.append("sox")
    
    if missing:
        print(f"❌ Missing libraries: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    return True

def test_sounddevice():
    """Test sounddevice functionality"""
    try:
        import sounddevice as sd
        print("\n🎵 Testing sounddevice...")
        
        # Query devices
        devices = sd.query_devices()
        print(f"✅ Found {len(devices)} audio devices")
        
        # Show default devices
        try:
            default_input = sd.default.device[0]
            default_output = sd.default.device[1]
            print(f"📱 Default input: {default_input}")
            print(f"📢 Default output: {default_output}")
        except Exception as e:
            print(f"⚠️  Could not determine default devices: {e}")
        
        # List all devices
        print("\n📋 Available audio devices:")
        for i, device in enumerate(devices):
            device_type = []
            if device['max_input_channels'] > 0:
                device_type.append(f"IN:{device['max_input_channels']}")
            if device['max_output_channels'] > 0:
                device_type.append(f"OUT:{device['max_output_channels']}")
            
            status = " ".join(device_type) if device_type else "No I/O"
            print(f"  {i:2d}: {device['name']:<30} [{status}] @ {device['default_samplerate']}Hz")
        
        return True
        
    except Exception as e:
        print(f"❌ sounddevice test failed: {e}")
        return False

def test_basic_audio():
    """Test basic audio stream creation"""
    try:
        import sounddevice as sd
        import numpy as np
        
        print("\n🧪 Testing basic audio stream...")
        
        # Test configurations from simple to complex
        configs = [
            (22050, 1, 512),   # Simple mono
            (44100, 1, 1024),  # Standard mono
            (44100, 2, 1024),  # Standard stereo
        ]
        
        for sample_rate, channels, blocksize in configs:
            print(f"   Testing: {sample_rate}Hz, {channels}ch, {blocksize} samples...", end=" ")
            try:
                def dummy_callback(indata, outdata, frames, time, status):
                    outdata.fill(0)  # Silence
                
                with sd.Stream(samplerate=sample_rate,
                             blocksize=blocksize,
                             channels=channels,
                             callback=dummy_callback,
                             dtype="float32"):
                    pass  # Just test opening
                print("✅ OK")
                return sample_rate, channels, blocksize
            except Exception as e:
                print(f"❌ {e}")
        
        print("❌ No working audio configuration found")
        return None
        
    except Exception as e:
        print(f"❌ Audio stream test failed: {e}")
        return None

def check_alsa_configuration():
    """Check ALSA configuration on Linux"""
    if platform.system() != "Linux":
        return
    
    print("\n🐧 Checking ALSA configuration (Linux)...")
    
    import subprocess
    
    # Check if ALSA tools are available
    try:
        result = subprocess.run(["aplay", "--version"], 
                              capture_output=True, text=True, timeout=5)
        print(f"✅ ALSA version: {result.stdout.strip()}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ ALSA tools not found. Install with: sudo apt install alsa-utils")
        return
    
    # List playback devices
    try:
        result = subprocess.run(["aplay", "-l"], 
                              capture_output=True, text=True, timeout=5)
        print("\n📢 ALSA playback devices:")
        print(result.stdout)
    except subprocess.TimeoutExpired:
        print("⚠️  aplay -l timed out")
    
    # List capture devices
    try:
        result = subprocess.run(["arecord", "-l"], 
                              capture_output=True, text=True, timeout=5)
        print("📱 ALSA capture devices:")
        print(result.stdout)
    except subprocess.TimeoutExpired:
        print("⚠️  arecord -l timed out")

def suggest_fixes():
    """Suggest common fixes for audio issues"""
    print("\n🔧 Common fixes for audio issues:")
    print("\n🐧 On Linux/Raspberry Pi:")
    print("  sudo apt update")
    print("  sudo apt install alsa-utils pulseaudio portaudio19-dev")
    print("  sudo usermod -a -G audio $USER")
    print("  # Then logout and login again")
    
    print("\n🍓 On Raspberry Pi specifically:")
    print("  # Enable audio in raspi-config")
    print("  sudo raspi-config")
    print("  # Go to Advanced Options -> Audio -> Force 3.5mm jack")
    print("  ")
    print("  # Or for HDMI audio:")
    print("  # Go to Advanced Options -> Audio -> Force HDMI")
    
    print("\n🎧 For USB/external audio devices:")
    print("  # Check if device is detected:")
    print("  lsusb")
    print("  # Check audio devices:")
    print("  cat /proc/asound/cards")
    
    print("\n💻 On Windows:")
    print("  # Install appropriate audio drivers")
    print("  # Check Windows audio settings")
    print("  # Try running as administrator")
    
    print("\n🐍 Python environment:")
    print("  # Reinstall sounddevice:")
    print("  pip uninstall sounddevice")
    print("  pip install sounddevice")

def main():
    print("🎭 Dark Helmet Audio Diagnostic Tool")
    print("=" * 50)
    
    # Check virtual environment
    venv_path = os.environ.get('VIRTUAL_ENV', '')
    if 'SpaceBalls' in venv_path:
        print(f"✅ Running in SpaceBalls environment")
    else:
        print("⚠️  Not in SpaceBalls virtual environment")
        if input("Continue anyway? (y/N): ").lower() != 'y':
            return
    
    print(f"\n💻 System: {platform.system()} {platform.machine()}")
    print(f"🐍 Python: {sys.version}")
    
    # Run diagnostics
    if not check_imports():
        print("\n❌ Cannot proceed without required libraries")
        return
    
    if not test_sounddevice():
        print("\n❌ sounddevice is not working properly")
        suggest_fixes()
        return
    
    result = test_basic_audio()
    if result:
        sample_rate, channels, blocksize = result
        print(f"\n✅ Found working audio config: {sample_rate}Hz, {channels}ch, {blocksize} samples")
        print("🎤 You should be able to run the voice changer now!")
    else:
        print("\n❌ No working audio configuration found")
        check_alsa_configuration()
        suggest_fixes()

if __name__ == "__main__":
    main()
