#!/usr/bin/env python3
"""
Virtual Environment Setup Script for Dark Helmet Project
Creates a virtual environment named 'SpaceBalls' for both local development and Pi deployment
"""
import os
import sys
import subprocess
import platform

VENV_NAME = "SpaceBalls"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_PATH = os.path.join(PROJECT_ROOT, VENV_NAME)
REQUIREMENTS_PATH = os.path.join(PROJECT_ROOT, "src", "requirements.txt")

def run_command(command, shell=False):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=shell, check=True, capture_output=True, text=True)
        print(f"✓ {' '.join(command) if isinstance(command, list) else command}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running command: {' '.join(command) if isinstance(command, list) else command}")
        print(f"  Error: {e.stderr}")
        return None

def check_python_version():
    """Check if Python 3.11.2 is available"""
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"Using Python: {version}")
        
        # Check if it's close to 3.11.2
        if "3.11" in version:
            return True
        else:
            print("Warning: Python 3.11.2 recommended, but continuing with current version")
            return True
    except Exception as e:
        print(f"Error checking Python version: {e}")
        return False

def create_venv():
    """Create the virtual environment"""
    if os.path.exists(VENV_PATH):
        print(f"Virtual environment '{VENV_NAME}' already exists at {VENV_PATH}")
        return True
    
    print(f"Creating virtual environment '{VENV_NAME}'...")
    result = run_command([sys.executable, "-m", "venv", VENV_PATH])
    return result is not None

def get_activation_script():
    """Get the path to the activation script based on platform"""
    if platform.system() == "Windows":
        return os.path.join(VENV_PATH, "Scripts", "activate.bat")
    else:
        return os.path.join(VENV_PATH, "bin", "activate")

def get_python_executable():
    """Get the path to the Python executable in the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join(VENV_PATH, "Scripts", "python.exe")
    else:
        return os.path.join(VENV_PATH, "bin", "python")

def install_requirements():
    """Install requirements in the virtual environment"""
    python_exe = get_python_executable()
    
    if not os.path.exists(python_exe):
        print("Error: Virtual environment Python executable not found")
        return False
    
    print("Installing requirements...")
    result = run_command([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
    if result is None:
        return False
    
    if os.path.exists(REQUIREMENTS_PATH):
        result = run_command([python_exe, "-m", "pip", "install", "-r", REQUIREMENTS_PATH])
        return result is not None
    else:
        print(f"No requirements.txt found at {REQUIREMENTS_PATH}")
        return True

def create_activation_scripts():
    """Create convenient activation scripts"""
    # Windows activation script
    windows_script = os.path.join(PROJECT_ROOT, "activate_spaceBalls.bat")
    with open(windows_script, 'w') as f:
        f.write(f"""@echo off
echo Activating SpaceBalls virtual environment...
call "{os.path.join(VENV_PATH, 'Scripts', 'activate.bat')}"
echo SpaceBalls environment activated!
echo Use 'deactivate' to exit the virtual environment.
cmd /k
""")
    
    # Unix activation script
    unix_script = os.path.join(PROJECT_ROOT, "activate_spaceBalls.sh")
    with open(unix_script, 'w') as f:
        f.write(f"""#!/bin/bash
echo "Activating SpaceBalls virtual environment..."
source "{os.path.join(VENV_PATH, 'bin', 'activate')}"
echo "SpaceBalls environment activated!"
echo "Use 'deactivate' to exit the virtual environment."
exec "$SHELL"
""")
    
    # Make Unix script executable
    if platform.system() != "Windows":
        os.chmod(unix_script, 0o755)
    
    print(f"Created activation scripts:")
    print(f"  Windows: {windows_script}")
    print(f"  Unix/Linux: {unix_script}")

def main():
    """Main setup function"""
    print("=" * 60)
    print("Dark Helmet Project - SpaceBalls Virtual Environment Setup")
    print("=" * 60)
    
    if not check_python_version():
        print("Error: Python check failed")
        sys.exit(1)
    
    if not create_venv():
        print("Error: Failed to create virtual environment")
        sys.exit(1)
    
    if not install_requirements():
        print("Error: Failed to install requirements")
        sys.exit(1)
    
    create_activation_scripts()
    
    print("\n" + "=" * 60)
    print("✓ SpaceBalls virtual environment setup complete!")
    print("=" * 60)
    print(f"Virtual environment location: {VENV_PATH}")
    print(f"Python executable: {get_python_executable()}")
    print(f"Activation script: {get_activation_script()}")
    print("\nTo activate the environment:")
    if platform.system() == "Windows":
        print(f"  .\\activate_spaceBalls.bat")
    else:
        print(f"  source ./activate_spaceBalls.sh")
    print("\nTo deactivate: deactivate")

if __name__ == "__main__":
    main()
