#Deployment script for Linux/macOS
#!/bin/bash
# Deploy code to Raspberry Pi
PI_USER="rickmoranis"
PI_IP="192.168.1.103"  # Replace with your Pi's IP
PI_PATH="/home/rickmoranis/dark_helmet"

echo "Deploying to Raspberry Pi at $PI_IP..."
scp -r ../src/* $PI_USER@$PI_IP:$PI_PATH/
ssh $PI_USER@$PI_IP "cd $PI_PATH && python3 main.py"