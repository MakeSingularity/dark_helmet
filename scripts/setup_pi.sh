#Script to configure Pi environment
#!/bin/bash
# Set up Raspberry Pi environment
PI_USER="rickmoranis"
PI_IP="192.168.1.103"
PI_PATH="/home/rickmoranis/dark_helmet"

echo "Setting up Raspberry Pi environment..."
ssh $PI_USER@$PI_IP "mkdir -p $PI_PATH && sudo apt update && sudo apt install python3-pip -y && pip3 install -r $PI_PATH/requirements.txt"