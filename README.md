# High Frequency Analyzer

High-resolution Spectrum Analyzer & Audio Player capable of visualizing ultrasonic frequencies up to 200kHz.
Built with Python, PyQt6, and PortAudio (sounddevice).

## Features
- **High Frequency Support**: Visualizes up to Nyquist frequency (e.g., 96kHz for 192kHz source).
- **Dual Mode**:
  - **File Player**: Browse and play high-res audio files (WAV, FLAC, etc.).
  - **Live Input**: Real-time analysis of Microphone/Line-in signals (ASIO/WASAPI support).
- **Fast Startup**: Single-exe distribution with self-extracting launcher logic.

## Requirements
- Windows 10/11
- Audio Interface supporting high sample rates (for >20kHz analysis)

## Installation (Dev)
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run app:
   ```bash
   python main.py
   ```

## Build (Windows)
Run the build script in Git Bash:
```bash
sh build_smart_exe.sh
```
Executable will be created in `dist/HighFreqAnalyzer.exe`.
