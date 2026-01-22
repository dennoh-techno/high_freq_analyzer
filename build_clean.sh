#!/bin/bash
echo "Creating a fresh virtual environment for build..."
python -m venv build_venv

echo "Activating virtual environment..."
source build_venv/Scripts/activate

echo ""
echo "Installing requirements..."
pip install -r requirements.txt
pip install pyinstaller

echo ""
echo "Building executable (clean)..."
# Use python -m PyInstaller to ensure we use the one in venv
python -m PyInstaller --noconsole --onefile --clean --name "HighFreqAnalyzer" main.py

echo ""
echo "Build complete. The executable is located in the 'dist' folder."
echo "Size should be optimized."
