**[Project documentation]**
# 🎭 Dark Helmet Voice Changer Project
A real-time voice processing system for Raspberry Pi Zero 2 W using the SpaceBalls virtual environment.

## 🎤 Features
- **Real-time voice effects** with Dark Helmet character transformation
- **Web-based control interface** accessible from any device
- **WM8960 audio HAT support** for Raspberry Pi
- **Professional audio processing** using numpy, scipy, and SoX
- **SpaceBalls virtual environment** for isolated dependencies

## 🚀 Quick Setup
1. **Clone the repository**
2. **Set up SpaceBalls virtual environment:**
   ```bash
   cd scripts
   python setup_venv.py              # Local development
   ./setup_pi.sh                     # Raspberry Pi setup
   ```
3. **Run the voice changer:**
   - **Windows:** `.\run_voice_changer.bat`
   - **Linux/macOS:** `./run_voice_changer.sh`
   - **Manual:** `source ./activate_spaceBalls.sh && cd src && python run_voice_changer.py`

## 🎛️ Voice Effects
- **Pitch Shift:** Lower pitch for Dark Helmet's deep voice
- **Distortion:** Adds robotic/gritty effect
- **Reverb:** Simulates helmet interior acoustics  
- **Volume:** Output level control
- **Real-time adjustment** via web interface at `http://localhost:8000`

## 🖥️ Deployment to Raspberry Pi
```bash
cd scripts
./deploy.sh        # Linux/macOS
deploy.bat         # Windows
```

## 📋 Requirements
- **Python 3.11.2**
- **Raspberry Pi OS Lite Debian Bookworm**
- **WM8960 Audio HAT** (optional, falls back to default audio)
- **SpaceBalls virtual environment** (auto-created)

## 🎯 Virtual Environment Benefits
- ✅ **Isolated dependencies** - No system conflicts
- ✅ **Reproducible environments** - Same setup everywhere  
- ✅ **Easy deployment** - One-command setup
- ✅ **Professional development** - Industry best practices

## 📁 Project Structure
```
dark_helmet/
├── SpaceBalls/                    # Virtual environment
├── src/
│   ├── voice_changer.py          # Main voice processing engine
│   ├── index.html                # Web control interface
│   ├── run_voice_changer.py      # Launcher with environment checks
│   ├── main.py                   # Basic project demo
│   └── requirements.txt          # Python dependencies
├── scripts/
│   ├── setup_venv.py            # Virtual environment setup
│   ├── setup_pi.sh              # Raspberry Pi configuration
│   └── deploy.sh/bat            # Deployment scripts
├── run_voice_changer.sh/bat      # Easy launchers
└── tests/                        # Unit tests
```

## 🔧 Audio Processing Details
- **Sample Rate:** 44.1kHz (WM8960 compatible)
- **Channels:** Stereo processing
- **Block Size:** 1024 samples for low latency
- **Effects Chain:** Notch filter → Pitch shift → Distortion → Reverb → Volume
- **Web Interface:** Real-time parameter control

## 🌐 Web Interface
Access the control panel at `http://<device-ip>:8000`:
- **Real-time sliders** for all voice parameters
- **Auto-save** settings as you adjust
- **Connection status** monitoring
- **SpaceBalls themed** design

## 🛠️ Troubleshooting
- **No audio:** Check device connections and permissions
- **Web interface not loading:** Verify port 8000 is available
- **Installation issues:** Ensure SpaceBalls environment is active
- **Performance issues:** Check CPU usage on Pi Zero 2 W

See `VIRTUAL_ENV_SETUP.md` for detailed environment setup instructions.

---
*"I am your father's brother's nephew's cousin's former roommate... with a really cool voice changer!"* 🎭