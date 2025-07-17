**[Project documentation]**
# Dark Helmet Project
A Python project for Raspberry Pi Zero 2 W using the SpaceBalls virtual environment.

## Quick Setup
1. **Clone the repository**
2. **Set up SpaceBalls virtual environment:**
   ```bash
   cd scripts
   python setup_venv.py              # Local development
   ./setup_pi.sh                     # Raspberry Pi setup
   ```
3. **Activate environment:**
   - Windows: `.\activate_spaceBalls.bat`
   - Linux/macOS: `source ./activate_spaceBalls.sh`
4. **Deploy to Pi:**
   ```bash
   cd scripts
   ./deploy.sh        # Linux/macOS
   deploy.bat         # Windows
   ```

## Requirements
- Python 3.11.2
- Raspberry Pi OS Lite Debian Bookworm
- SpaceBalls virtual environment (auto-created)

## Virtual Environment Benefits
- ✅ Isolated dependencies
- ✅ No system-wide package conflicts  
- ✅ Reproducible environments
- ✅ Easy deployment

See `VIRTUAL_ENV_SETUP.md` for detailed instructions.