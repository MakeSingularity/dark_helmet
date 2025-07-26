#!/bin/bash
# Dark Helmet Voice Changer Launcher for Linux/macOS
# Activates SpaceBalls environment and runs the voice changer

echo ""
echo "=========================================="
echo " 🎭 Dark Helmet Voice Changer Launcher"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -d "SpaceBalls" ]; then
    echo "❌ SpaceBalls virtual environment not found!"
    echo "Please run this script from the project root directory."
    echo ""
    echo "To set up the environment:"
    echo "  cd scripts"
    echo "  python setup_venv.py"
    echo ""
    exit 1
fi

# Activate SpaceBalls environment
echo "🚀 Activating SpaceBalls virtual environment..."
source SpaceBalls/bin/activate

# Change to src directory
cd src

# Check if required files exist
if [ ! -f "voice_changer.py" ]; then
    echo "❌ voice_changer.py not found in src directory!"
    exit 1
fi

if [ ! -f "index.html" ]; then
    echo "❌ index.html not found in src directory!"
    exit 1
fi

echo "✅ SpaceBalls environment active!"
echo "🎤 Starting Dark Helmet Voice Changer..."
echo ""
echo "🌐 Web interface will be available at:"
echo "   http://localhost:8000"
echo ""
echo "🛑 Press Ctrl+C to stop the voice changer"
echo "=========================================="
echo ""

# Run the voice changer
python run_voice_changer.py

echo ""
echo "🎭 Voice changer stopped. May the Schwartz be with you!"
