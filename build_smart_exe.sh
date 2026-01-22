#!/bin/bash

# Configuration
APP_NAME="HighFreqAnalyzer"
VENV_DIR="build_venv"

echo "=== Smart Build System ==="

# 1. Environment Setup
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python -m venv $VENV_DIR
    source $VENV_DIR/Scripts/activate
    pip install -r requirements.txt
    pip install pyinstaller packaging
else
    source $VENV_DIR/Scripts/activate
fi

# Clean previous builds
echo "Cleaning up..."
rm -rf dist build *.spec app_package.zip

# 2. Build Core App (Result: dist/main/...)
echo "Building Core Application (onedir mode)..."
# We rename the output directory to 'payload' to keep it clean inside the zip
python -m PyInstaller --noconsole --onedir --clean --name "payload" main.py

# 3. Zip the Core App
echo "Creating Application Package..."
cd dist
# Compress the 'payload' folder into 'app_package.zip'
# Windows built-in tar can create zips in recent versions, or python
python -c "import shutil; shutil.make_archive('../app_package', 'zip', 'payload')"
cd ..

# Verify Zip exists
if [ ! -f "app_package.zip" ]; then
    echo "Error: Failed to create app_package.zip"
    exit 1
fi

# 4. Build Launcher (Result: dist/HighFreqAnalyzer.exe)
echo "Building Launcher (onefile mode)..."
# --add-data "source;dest" (Windows separator is ;)
python -m PyInstaller --noconsole --onefile --clean \
    --add-data "app_package.zip;." \
    --name "$APP_NAME" \
    launcher.py

echo ""
echo "=== Build Complete ==="
echo "The final single-file executable is: dist/$APP_NAME.exe"
echo "You can distribute this single file."
