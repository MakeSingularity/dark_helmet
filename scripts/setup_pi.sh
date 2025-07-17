#Script to configure Pi environment with SpaceBalls virtual environment
#!/bin/bash
# Set up Raspberry Pi environment with virtual environment
PI_USER="rickmoranis"
PI_IP="192.168.1.103"
PI_PATH="/home/rickmoranis/dark_helmet"
VENV_NAME="SpaceBalls"
VENV_PATH="$PI_PATH/$VENV_NAME"

echo "Setting up Raspberry Pi environment with SpaceBalls virtual environment..."

# Update system and install required system packages
ssh $PI_USER@$PI_IP "
    mkdir -p $PI_PATH && 
    sudo apt update && 
    sudo apt install python3-pip python3-venv python3-dev -y &&
    sudo apt install libsox-fmt-all portaudio19-dev libasound2-dev -y
"

# Create virtual environment and install Python packages
ssh $PI_USER@$PI_IP "
    cd $PI_PATH &&
    python3 -m venv $VENV_NAME &&
    source $VENV_PATH/bin/activate &&
    pip install --upgrade pip &&
    pip install numpy scipy sounddevice sox &&
    echo 'SpaceBalls virtual environment created successfully!'
"

echo "Raspberry Pi setup complete with SpaceBalls virtual environment!"
echo "Virtual environment location: $VENV_PATH"