::Deployment script for Windows with SpaceBalls virtual environment
@echo off
set PI_USER=rickmoranis
set PI_IP=192.168.1.103
set PI_PATH=/home/rickmoranis/dark_helmet
set VENV_NAME=SpaceBalls
set VENV_PATH=%PI_PATH%/%VENV_NAME%

echo Deploying to Raspberry Pi at %PI_IP% with SpaceBalls environment...

:: Copy source files
scp -r ../src/* %PI_USER%@%PI_IP%:%PI_PATH%/

:: Install/update requirements and run the application
ssh %PI_USER%@%PI_IP% "cd %PI_PATH% && source %VENV_PATH%/bin/activate && pip install -r requirements.txt && python main.py"

echo Deployment complete!