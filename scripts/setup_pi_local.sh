#!/bin/bash
# Quick setup script for creating SpaceBalls virtual environment on Raspberry Pi
# Run this script directly on the Pi

VENV_NAME="SpaceBalls"
PROJECT_PATH="/home/rickmoranis/dark_helmet"
VENV_PATH="$PROJECT_PATH/$VENV_NAME"

echo "Setting up SpaceBalls virtual environment on Raspberry Pi..."

# Create project directory if it doesn't exist
mkdir -p $PROJECT_PATH
cd $PROJECT_PATH

# Update system and install dependencies
sudo apt update
sudo apt install python3-pip python3-venv python3-dev -y
sudo apt install libsox-fmt-all portaudio19-dev libasound2-dev -y

# Create virtual environment
echo "Creating virtual environment '$VENV_NAME'..."
python3 -m venv $VENV_NAME

# Activate and install packages
source $VENV_PATH/bin/activate
pip install --upgrade pip

# Install common packages needed for the project
pip install numpy scipy sounddevice sox requests python-dotenv flask

echo ""
echo "SpaceBalls virtual environment setup complete!"
echo "Location: $VENV_PATH"
echo ""
echo "To activate the environment:"
echo "  cd $PROJECT_PATH"
echo "  source $VENV_NAME/bin/activate"
echo ""
echo "To deactivate:"
echo "  deactivate"
echo ""
echo "To set up network configuration (AP mode), run:"
echo "  sudo bash setup_network.sh"
