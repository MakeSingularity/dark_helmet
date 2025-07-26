::Deployment script for Windows with SpaceBalls virtual environment
@echo off
set PI_USER=rickmoranis
set PI_IP=192.168.1.103
set PI_PATH=/home/rickmoranis/dark_helmet
set VENV_NAME=SpaceBalls
set VENV_PATH=%PI_PATH%/%VENV_NAME%

echo 🚀 Deploying Dark Helmet Voice Changer to Raspberry Pi at %PI_IP%...
echo Using SpaceBalls virtual environment

:: Copy source files
echo 📁 Copying source files...
scp -r ../src/* %PI_USER%@%PI_IP%:%PI_PATH%/

:: Install/update requirements and run the voice changer
echo 🔧 Setting up environment and starting voice changer...
ssh %PI_USER%@%PI_IP% "cd %PI_PATH% && source %VENV_PATH%/bin/activate && echo '🎭 SpaceBalls environment activated!' && pip install --upgrade pip && pip install -r requirements.txt && echo '🎤 Starting Dark Helmet Voice Changer...' && echo 'Web interface will be available at http://%PI_IP%:8000' && python run_voice_changer.py"

echo 🎭 Deployment complete! May the Schwartz be with you!pt for Windows with SpaceBalls virtual environment
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