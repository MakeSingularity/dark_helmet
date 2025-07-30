#Deployment script for Linux/macOS with SpaceBalls virtual environment
#!/bin/bash
# Deploy Dark Helmet Voice Changer to Raspberry Pi using SpaceBalls virtual environment
PI_USER="rickmoranis"
PI_IP="192.168.1.103"  # Replace with your Pi's IP
PI_PATH="/home/rickmoranis/dark_helmet"
VENV_NAME="SpaceBalls"
VENV_PATH="$PI_PATH/$VENV_NAME"

echo "🚀 Deploying Dark Helmet Voice Changer to Raspberry Pi at $PI_IP..."
echo "Using SpaceBalls virtual environment"

# Copy source files
echo "📁 Copying source files..."
scp -r ../src/* $PI_USER@$PI_IP:$PI_PATH/

# Install/update requirements and run the voice changer
echo "🔧 Setting up environment and starting voice changer..."
ssh $PI_USER@$PI_IP "
    cd $PI_PATH &&
    source $VENV_PATH/bin/activate &&
    echo '🎭 SpaceBalls environment activated!' &&
    pip install --upgrade pip &&
    pip install -r requirements.txt &&
    echo '🎤 Starting Dark Helmet Voice Changer...' &&
    echo 'Web interface will be available at http://$PI_IP:8000' &&
    python run_voice_changer.py
"

echo "🎭 Deployment complete! May the Schwartz be with you!"