# Main application code
# Dark Helmet project main script
import sys
import os

def check_virtual_environment():
    """Check if we're running in the SpaceBalls virtual environment"""
    venv_path = os.environ.get('VIRTUAL_ENV', '')
    if 'SpaceBalls' in venv_path:
        print(f"✓ Running in SpaceBalls virtual environment: {venv_path}")
        return True
    elif venv_path:
        print(f"⚠ Running in different virtual environment: {venv_path}")
        return True
    else:
        print("⚠ WARNING: Not running in a virtual environment!")
        print("  Consider activating the SpaceBalls environment:")
        print("  - Windows: .\\activate_spaceBalls.bat")
        print("  - Linux/macOS: source ./activate_spaceBalls.sh")
        return False

def main():
    print("Dark Helmet Project - SpaceBalls Edition")
    print("=" * 50)
    
    # Check virtual environment
    check_virtual_environment()
    
    # Display Python information
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    print("\nHello from Dark Helmet on Raspberry Pi!")
    print("Ready for audio processing with SpaceBalls environment!")

if __name__ == "__main__":
    main()