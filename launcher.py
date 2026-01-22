
import sys
import os
import shutil
import zipfile
import subprocess
import threading
import time
import ctypes

# Try importing tkinter, handle failure
try:
    import tkinter as tk
    from tkinter import ttk
    TK_AVAILABLE = True
except ImportError:
    TK_AVAILABLE = False

# Configuration
APP_NAME = "HighFreqAnalyzer"
EXE_NAME = "main.exe" 
# EXE_NAME must match the output name of the inner app. 
# In build_smart_exe.sh we named it 'payload', so default exe name is 'payload.exe' unless specified?
# Wait, --name "payload" -> dist/payload/payload.exe usually.
# Let's verify what the inner exe is named. 
# PyInstaller --name "payload" -> dist/payload/payload.exe (on Windows).
# Updating EXE_NAME to match likely output or making it dynamic.

EXE_NAME = "payload.exe" # Based on --name "payload" in build script

def show_error(title, message):
    """Shows a native message box."""
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x10) # 0x10 = MB_ICONHAND

def get_app_data_path():
    """Returns the path to the hidden app data directory."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
    else:
        base = os.path.expanduser("~/.local/share")
    
    return os.path.join(base, APP_NAME)

def extract_zip(zip_path, extract_to, progress_callback=None):
    """Extracts zip with progress."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            total = len(zip_ref.infolist())
            for i, member in enumerate(zip_ref.infolist()):
                zip_ref.extract(member, extract_to)
                if progress_callback:
                    progress_callback((i / total) * 100)
    except Exception as e:
        show_error("Installation Error", f"Failed to extract files:\n{e}")
        return False
    return True

def run_app(app_dir):
    # Find exe recursively just in case
    exe_path = None
    for root, dirs, files in os.walk(app_dir):
        if EXE_NAME in files:
            exe_path = os.path.join(root, EXE_NAME)
            break
            
    if exe_path and os.path.exists(exe_path):
        subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))
    else:
        # Fallback check for 'main.exe' just in case user renamed it or script changed
        alt_path = os.path.join(app_dir, "main.exe")
        if os.path.exists(alt_path):
             subprocess.Popen([alt_path], cwd=os.path.dirname(alt_path))
        else:
             show_error("Launch Error", f"Could not find application executable ({EXE_NAME}) in:\n{app_dir}\n\nPlease try deleting the folder '{app_dir}' and running this launcher again.")

def main():
    try:
        # Helper to find the bundled zip file (PyInstaller --add-data)
        if getattr(sys, 'frozen', False):
            bundle_dir = sys._MEIPASS
        else:
            bundle_dir = os.path.dirname(os.path.abspath(__file__))
        
        zip_source = os.path.join(bundle_dir, "app_package.zip")
        if not os.path.exists(zip_source):
             # Maybe debugging mode?
             if not getattr(sys, 'frozen', False):
                 print("Warning: app_package.zip not found (dev mode)")
             else:
                 show_error("Error", "Corrupt installation: app_package.zip is missing.")
                 return

        install_dir = get_app_data_path()
        
        # Check if needs installation
        # 1. Dir must exist
        # 2. EXE must exist inside
        needs_install = True
        if os.path.exists(install_dir):
            for root, dirs, files in os.walk(install_dir):
                if EXE_NAME in files or "main.exe" in files:
                    needs_install = False
                    break
        
        if not needs_install:
            # Fast path
            run_app(install_dir)
            sys.exit(0)
            
        # Installation Path
        if not TK_AVAILABLE:
            show_error("Error", "Tkinter is required for setup but missing.")
            return

        root = tk.Tk()
        root.title(f"Initializing {APP_NAME}...")
        
        # Center window
        w, h = 300, 120
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")
        root.resizable(False, False)
        
        lbl = tk.Label(root, text="Preparing application...\nFirst run setup.", pady=10)
        lbl.pack()
        
        progress = ttk.Progressbar(root, orient="horizontal", length=250, mode="determinate")
        progress.pack(pady=10)
        
        def install_thread():
            # Clean up old dir if exists to ensure fresh install
            if os.path.exists(install_dir):
                try:
                    shutil.rmtree(install_dir)
                except Exception as e:
                    # Might be locked if app is running?
                    pass 
            
            if not os.path.exists(install_dir):
                os.makedirs(install_dir)
                
            def update_prog(val):
                progress['value'] = val
                root.update_idletasks()
                
            success = extract_zip(zip_source, install_dir, update_prog)
            
            if success:
                root.destroy()
                run_app(install_dir)
            else:
                lbl.config(text="Setup failed.")
                
        threading.Thread(target=install_thread, daemon=True).start()
        root.mainloop()
    
    except Exception as e:
        show_error("Critical Error", f"An unexpected error occurred:\n{e}")

if __name__ == "__main__":
    main()
