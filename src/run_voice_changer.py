#!/usr/bin/env python3
"""
Dark Helmet Voice Changer Launcher
Ensures proper environment and launches the voice changer with all checks
"""

import os
import sys
import subprocess
import platform

def check_spaceBalls_environment():
    """Check if SpaceBalls virtual environment is active"""
    venv_path = os.environ.get('VIRTUAL_ENV', '')
    if 'SpaceBalls' in venv_path:
        return True, venv_path
    else:
        return False, venv_path

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'numpy', 'scipy', 'sounddevice', 'sox'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_missing_packages(packages):
    """Install missing packages using pip"""
    if not packages:
        return True
    
    print(f"Installing missing packages: {', '.join(packages)}")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install'
        ] + packages)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🎭 Dark Helmet Voice Changer Launcher")
    print("=" * 50)
    
    # Check virtual environment
    is_spaceBalls, venv_path = check_spaceBalls_environment()
    if is_spaceBalls:
        print(f"✅ SpaceBalls environment active: {venv_path}")
    else:
        print("⚠️  SpaceBalls virtual environment not detected!")
        if venv_path:
            print(f"   Current environment: {venv_path}")
        else:
            print("   No virtual environment active")
        print("\n🚀 To activate SpaceBalls environment:")
        if platform.system() == "Windows":
            print("   .\\activate_spaceBalls.bat")
        else:
            print("   source ./activate_spaceBalls.sh")
        
        response = input("\nContinue anyway? (y/N): ").lower()
        if response != 'y':
            print("Exiting. Please activate SpaceBalls environment and try again.")
            sys.exit(1)
    
    # Check dependencies
    print("\n🔍 Checking dependencies...")
    missing = check_dependencies()
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        response = input("Install missing packages? (Y/n): ").lower()
        if response != 'n':
            if install_missing_packages(missing):
                print("✅ Packages installed successfully!")
            else:
                print("❌ Failed to install packages. Please install manually.")
                sys.exit(1)
        else:
            print("❌ Cannot run without required packages.")
            sys.exit(1)
    else:
        print("✅ All dependencies satisfied!")
    
    # Check if we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    voice_changer_path = os.path.join(script_dir, 'voice_changer.py')
    index_path = os.path.join(script_dir, 'index.html')
    
    if not os.path.exists(voice_changer_path):
        print(f"❌ voice_changer.py not found at {voice_changer_path}")
        sys.exit(1)
    
    if not os.path.exists(index_path):
        print(f"❌ index.html not found at {index_path}")
        sys.exit(1)
    
    print("✅ All files found!")
    
    # Change to the script directory (important for web server to find index.html)
    os.chdir(script_dir)
    
    print(f"\n🎤 Starting Dark Helmet Voice Changer...")
    print(f"📁 Working directory: {script_dir}")
    print("🌐 Web interface will be available at http://localhost:8000")
    print("🛑 Press Ctrl+C to stop\n")
    
    try:
        # Import and run the voice changer
        import voice_changer
        if hasattr(voice_changer, 'main'):
            if platform.system() == "Emscripten":
                import asyncio
                asyncio.ensure_future(voice_changer.main())
            else:
                import asyncio
                asyncio.run(voice_changer.main())
        else:
            print("❌ main() function not found in voice_changer.py")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Voice changer stopped by user. May the Schwartz be with you!")
    except Exception as e:
        print(f"\n❌ Error running voice changer: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("  • Make sure audio devices are connected")
        print("  • Check that no other app is using the microphone")
        print("  • Verify SpaceBalls environment is properly set up")
        print("  • Try running: python setup_venv.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
