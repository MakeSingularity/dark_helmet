# Dark Helmet Project - Virtual Environment Setup

This document explains how to set up and use the SpaceBalls virtual environment for the Dark Helmet project.

## Why Virtual Environments?

Installing Python packages system-wide can lead to:
- Version conflicts between projects
- Difficulty managing dependencies
- Potential system instability
- Hard to reproduce environments

The SpaceBalls virtual environment isolates your project dependencies.

## Setup Instructions

### For Local Development (Windows/Linux/macOS)

1. **Run the setup script:**
   ```bash
   cd scripts
   python setup_venv.py
   ```

2. **Activate the environment:**
   - **Windows:** `.\activate_spaceBalls.bat`
   - **Linux/macOS:** `source ./activate_spaceBalls.sh`

3. **Verify installation:**
   ```bash
   python --version
   pip list
   ```

### For Raspberry Pi Zero 2 W

#### Option 1: Remote Setup (from your development machine)
```bash
cd scripts
./setup_pi.sh
```

#### Option 2: Direct Setup (on the Pi)
1. Copy `setup_pi_local.sh` to your Pi
2. Run: `chmod +x setup_pi_local.sh && ./setup_pi_local.sh`

## Usage

### Local Development
```bash
# Activate environment
source ./activate_spaceBalls.sh  # Linux/macOS
# or
.\activate_spaceBalls.bat        # Windows

# Install new packages
pip install package_name

# Update requirements.txt
pip freeze > src/requirements.txt

# Deactivate when done
deactivate
```

### Raspberry Pi Deployment
```bash
# Deploy with virtual environment
cd scripts
./deploy.sh          # Linux/macOS
# or
deploy.bat           # Windows
```

### On the Raspberry Pi
```bash
# Activate environment
cd /home/rickmoranis/dark_helmet
source SpaceBalls/bin/activate

# Run your application
python main.py

# Deactivate when done
deactivate
```

## File Structure
```
dark_helmet/
├── SpaceBalls/              # Virtual environment (created)
├── src/
│   ├── main.py
│   └── requirements.txt     # Updated with dependencies
├── scripts/
│   ├── setup_venv.py        # Local venv setup
│   ├── setup_pi.sh          # Remote Pi setup
│   ├── setup_pi_local.sh    # Direct Pi setup
│   ├── deploy.sh            # Linux/macOS deployment
│   └── deploy.bat           # Windows deployment
├── activate_spaceBalls.sh   # Unix activation script
└── activate_spaceBalls.bat  # Windows activation script
```

## Troubleshooting

### Common Issues
1. **Permission denied:** Make scripts executable with `chmod +x script_name.sh`
2. **Python not found:** Ensure Python 3.11.2 is installed
3. **SSH connection fails:** Check Pi IP address and SSH configuration
4. **Package installation fails:** Ensure internet connection and try updating pip

### Verification Commands
```bash
# Check Python version
python --version

# Check virtual environment
which python
pip list

# Check if packages are installed in venv
pip show numpy
```

## Best Practices

1. **Always activate the virtual environment** before working on the project
2. **Keep requirements.txt updated** when adding new packages
3. **Use the same Python version** on all development machines
4. **Test deployments** in the virtual environment before production
5. **Document any system dependencies** that can't be installed via pip

## Python 3.11.2 Specific Notes

- Optimized performance for Raspberry Pi Zero 2 W
- Better memory management for constrained environments
- Improved error messages for debugging
- Enhanced security features

Remember: The SpaceBalls environment keeps your project isolated and reproducible across all platforms!
